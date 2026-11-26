"""Deterministic waste-finding engine. Reads local sample data only.

No AWS calls, no credentials, no mutations. Every finding is priced
from the sample price table in pricing.py and labelled as an estimate.
"""
from __future__ import annotations

from .models import BillSummary, CostReport, Finding, Inventory
from .pricing import (
    IDLE_CPU_PERCENT,
    IDLE_GPU_PERCENT,
    OLD_SNAPSHOT_DAYS,
    OVERSIZED_CPU_PERCENT,
    REQUIRED_TAGS,
    downsize_savings,
    instance_hourly_rate,
    instance_monthly_cost,
    reserved_savings,
    smaller_instance_type,
    snapshot_monthly_cost,
    spot_savings,
    volume_monthly_cost,
)


def _severity(savings: float) -> str:
    if savings >= 100:
        return "HIGH"
    if savings >= 20:
        return "MEDIUM"
    return "LOW"


def _analyse_instances(inv: Inventory) -> tuple[list[Finding], float]:
    findings: list[Finding] = []
    total = 0.0
    for inst in inv.instances:
        rate, known = instance_hourly_rate(inst.instance_type)
        monthly = round(rate * inst.hours_per_month, 2)
        total += monthly
        cpu = inst.avg_cpu_percent
        gpu = inst.avg_gpu_percent

        # Missing cost tags: a finding with no savings, so untagged spend
        # is visible in the report instead of silently unallocated.
        missing = [t for t in REQUIRED_TAGS if t not in inst.tags]
        if missing:
            findings.append(
                Finding(
                    resource_id=inst.id,
                    category="tagging",
                    severity="LOW",
                    title=f"Instance {inst.id} is missing cost tags",
                    detail=f"Missing tags: {', '.join(missing)}. "
                    "Untagged spend cannot be attributed to a team or cost centre.",
                    monthly_cost=monthly,
                    estimated_savings=0.0,
                    recommendation=f"Add tags ({', '.join(missing)}) to {inst.id}.",
                )
            )

        if inst.purchase_type == "reserved":
            # Already committed spend: stopping it does not save money,
            # so idle/oversized checks do not apply.
            continue

        is_idle = (
            cpu is not None
            and cpu < IDLE_CPU_PERCENT
            and (gpu is None or gpu < IDLE_GPU_PERCENT)
        )
        if is_idle:
            findings.append(
                Finding(
                    resource_id=inst.id,
                    category="idle",
                    severity=_severity(monthly),
                    title=f"Idle instance {inst.id} ({inst.instance_type})",
                    detail=f"Average CPU {cpu}%"
                    + (f", GPU {gpu}%" if gpu is not None else "")
                    + f" over the month; monthly cost ${monthly:.2f} (sample price).",
                    monthly_cost=monthly,
                    estimated_savings=monthly,
                    recommendation=f"Stop or remove {inst.id} after confirming "
                    "nothing depends on it, or downsize it to a smaller type.",
                )
            )
            continue

        if cpu is not None and cpu < OVERSIZED_CPU_PERCENT:
            smaller = smaller_instance_type(inst.instance_type)
            if smaller is not None and known:
                smaller_monthly = instance_monthly_cost(
                    smaller, inst.hours_per_month
                )
                savings = downsize_savings(monthly, smaller_monthly)
                if savings > 0:
                    findings.append(
                        Finding(
                            resource_id=inst.id,
                            category="oversized",
                            severity=_severity(savings),
                            title=f"Oversized instance {inst.id} ({inst.instance_type})",
                            detail=f"Average CPU {cpu}% — well below the "
                            f"{OVERSIZED_CPU_PERCENT:.0f}% oversized threshold; "
                            f"a {smaller} would cost ${smaller_monthly:.2f}/mo.",
                            monthly_cost=monthly,
                            estimated_savings=savings,
                            recommendation=f"Downsize {inst.id} from "
                            f"{inst.instance_type} to {smaller} and watch CPU.",
                        )
                    )
                    continue

        # Spot / Reserved savings are only priced when the instance type
        # is in the sample price table. An unknown type is costed at the
        # fallback rate, which is too rough to base a recommendation on.
        if known and inst.fault_tolerant and inst.purchase_type == "on-demand":
            savings = spot_savings(monthly)
            findings.append(
                Finding(
                    resource_id=inst.id,
                    category="spot",
                    severity=_severity(savings),
                    title=f"On-demand instance {inst.id} could use Spot",
                    detail=f"Fault-tolerant workload on on-demand "
                    f"{inst.instance_type}; Spot saves ~70% (sample assumption).",
                    monthly_cost=monthly,
                    estimated_savings=savings,
                    recommendation=f"Move {inst.id} to Spot instances "
                    "with a diversified instance-type pool.",
                )
            )
        elif known and inst.purchase_type == "on-demand" and cpu is not None and cpu >= OVERSIZED_CPU_PERCENT:
            savings = reserved_savings(monthly)
            findings.append(
                Finding(
                    resource_id=inst.id,
                    category="reserved",
                    severity=_severity(savings),
                    title=f"Steady-state instance {inst.id} could use Reserved",
                    detail=f"Average CPU {cpu}% — steady usage on on-demand "
                    f"{inst.instance_type}; a 1-year Reserved instance "
                    "saves ~40% (sample assumption).",
                    monthly_cost=monthly,
                    estimated_savings=savings,
                    recommendation=f"Buy a 1-year Reserved instance for {inst.id} "
                    "once the sizing is confirmed.",
                )
            )
    return findings, total


def _analyse_storage(inv: Inventory) -> tuple[list[Finding], float]:
    findings: list[Finding] = []
    total = 0.0
    for vol in inv.volumes:
        monthly = volume_monthly_cost(vol.volume_type, vol.size_gb)
        total += monthly
        if not vol.attached_to:
            findings.append(
                Finding(
                    resource_id=vol.id,
                    category="unattached",
                    severity=_severity(monthly),
                    title=f"Unattached volume {vol.id}",
                    detail=f"{vol.size_gb:.0f} GB {vol.volume_type} with no "
                    f"instance attached; monthly cost ${monthly:.2f} (sample price).",
                    monthly_cost=monthly,
                    estimated_savings=monthly,
                    recommendation=f"Snapshot {vol.id} if the data is needed, "
                    "then delete the volume.",
                )
            )
        elif vol.volume_type == "gp2":
            gp3_monthly = volume_monthly_cost("gp3", vol.size_gb)
            savings = round(monthly - gp3_monthly, 2)
            if savings > 0:
                findings.append(
                    Finding(
                        resource_id=vol.id,
                        category="storage",
                        severity=_severity(savings),
                        title=f"Volume {vol.id} is gp2 — gp3 is cheaper",
                        detail=f"{vol.size_gb:.0f} GB gp2 at ${monthly:.2f}/mo; "
                        f"gp3 would cost ${gp3_monthly:.2f}/mo.",
                        monthly_cost=monthly,
                        estimated_savings=savings,
                        recommendation=f"Migrate {vol.id} from gp2 to gp3.",
                    )
                )
    for snap in inv.snapshots:
        monthly = snapshot_monthly_cost(snap.size_gb)
        total += monthly
        if snap.age_days > OLD_SNAPSHOT_DAYS:
            findings.append(
                Finding(
                    resource_id=snap.id,
                    category="snapshot",
                    severity=_severity(monthly),
                    title=f"Old snapshot {snap.id} ({snap.age_days} days)",
                    detail=f"{snap.size_gb:.0f} GB snapshot, {snap.age_days} days old; "
                    f"monthly cost ${monthly:.2f} (sample price).",
                    monthly_cost=monthly,
                    estimated_savings=monthly,
                    recommendation=f"Confirm {snap.id} is not needed for "
                    "recovery, then delete it.",
                )
            )
    return findings, total


def analyse(inv: Inventory, bill: BillSummary | None = None) -> CostReport:
    """Analyse one sample inventory (and optionally a sample bill)."""
    findings: list[Finding] = []
    inst_findings, inst_total = _analyse_instances(inv)
    stor_findings, stor_total = _analyse_storage(inv)
    findings += inst_findings + stor_findings

    # Recommendations ordered by estimated savings, highest first.
    findings.sort(key=lambda f: (-f.estimated_savings, f.resource_id))

    total_cost = round(inst_total + stor_total, 2)
    total_savings = round(sum(f.estimated_savings for f in findings), 2)

    bill_total = None
    bill_matches = None
    if bill is not None:
        bill_total = round(bill.total, 2)
        bill_matches = abs(bill.total - total_cost) < 1.00

    return CostReport(
        account=inv.account,
        region=inv.region,
        month=inv.month,
        total_monthly_cost=total_cost,
        total_estimated_savings=total_savings,
        findings=findings,
        bill_total=bill_total,
        bill_matches_inventory=bill_matches,
        live_aws_calls=0,
    )
