"""Data models for the cloud cost agent. Plain dataclasses, no dependencies."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Instance:
    """One EC2 instance in the sample inventory."""

    id: str
    name: str = ""
    instance_type: str = ""
    purchase_type: str = "on-demand"  # on-demand | reserved | spot
    hours_per_month: float = 730.0
    avg_cpu_percent: float | None = None
    avg_gpu_percent: float | None = None
    fault_tolerant: bool = False  # safe to interrupt (batch, stateless workers)
    tags: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "Instance":
        return cls(
            id=str(data.get("id", "unknown")),
            name=str(data.get("name", "")),
            instance_type=str(data.get("instance_type", "")),
            purchase_type=str(data.get("purchase_type", "on-demand")),
            hours_per_month=float(data.get("hours_per_month", 730) or 0),
            avg_cpu_percent=data.get("avg_cpu_percent"),
            avg_gpu_percent=data.get("avg_gpu_percent"),
            fault_tolerant=bool(data.get("fault_tolerant", False)),
            tags=dict(data.get("tags", {}) or {}),
        )


@dataclass
class Volume:
    """One EBS volume in the sample inventory."""

    id: str
    size_gb: float = 0.0
    volume_type: str = "gp3"  # gp3 | gp2 | io1 | io2 | st1 | sc1
    attached_to: str = ""  # instance id, or "" when unattached

    @classmethod
    def from_dict(cls, data: dict) -> "Volume":
        return cls(
            id=str(data.get("id", "unknown")),
            size_gb=float(data.get("size_gb", 0) or 0),
            volume_type=str(data.get("volume_type", "gp3")),
            attached_to=str(data.get("attached_to", "")),
        )


@dataclass
class Snapshot:
    """One EBS snapshot in the sample inventory."""

    id: str
    size_gb: float = 0.0
    age_days: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "Snapshot":
        return cls(
            id=str(data.get("id", "unknown")),
            size_gb=float(data.get("size_gb", 0) or 0),
            age_days=int(data.get("age_days", 0) or 0),
        )


@dataclass
class Inventory:
    """A sample resource inventory. All data is fictional sample data."""

    account: str = "sample-account"
    region: str = "us-east-1"
    month: str = ""
    instances: list[Instance] = field(default_factory=list)
    volumes: list[Volume] = field(default_factory=list)
    snapshots: list[Snapshot] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Inventory":
        return cls(
            account=str(data.get("account", "sample-account")),
            region=str(data.get("region", "us-east-1")),
            month=str(data.get("month", "")),
            instances=[Instance.from_dict(i) for i in data.get("instances", [])],
            volumes=[Volume.from_dict(v) for v in data.get("volumes", [])],
            snapshots=[Snapshot.from_dict(s) for s in data.get("snapshots", [])],
        )


@dataclass
class BillSummary:
    """A sample monthly bill summary, used only as a cross-check."""

    account: str = "sample-account"
    month: str = ""
    total: float = 0.0
    by_service: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "BillSummary":
        return cls(
            account=str(data.get("account", "sample-account")),
            month=str(data.get("month", "")),
            total=float(data.get("total", 0) or 0),
            by_service=dict(data.get("by_service", {}) or {}),
        )


@dataclass
class Finding:
    """One waste finding. Advisory only — a human decides what happens next."""

    resource_id: str
    category: str  # idle | oversized | spot | reserved | unattached | storage | snapshot | tagging
    severity: str  # LOW | MEDIUM | HIGH
    title: str
    detail: str
    monthly_cost: float
    estimated_savings: float
    recommendation: str

    def to_dict(self) -> dict:
        return {
            "resource_id": self.resource_id,
            "category": self.category,
            "severity": self.severity,
            "title": self.title,
            "detail": self.detail,
            "monthly_cost": round(self.monthly_cost, 2),
            "estimated_savings": round(self.estimated_savings, 2),
            "recommendation": self.recommendation,
        }


@dataclass
class CostReport:
    """The agent's assessment. Estimates only — never a live bill."""

    account: str
    region: str
    month: str
    total_monthly_cost: float
    total_estimated_savings: float
    findings: list[Finding] = field(default_factory=list)
    bill_total: float | None = None
    bill_matches_inventory: bool | None = None
    live_aws_calls: int = 0  # always 0: the demo never calls AWS

    def to_dict(self) -> dict:
        return {
            "account": self.account,
            "region": self.region,
            "month": self.month,
            "total_monthly_cost": round(self.total_monthly_cost, 2),
            "total_estimated_savings": round(self.total_estimated_savings, 2),
            "findings": [f.to_dict() for f in self.findings],
            "bill_total": self.bill_total,
            "bill_matches_inventory": self.bill_matches_inventory,
            "live_aws_calls": self.live_aws_calls,
            "pricing_note": "Sample prices — see pricing.py. Not live AWS pricing.",
        }
