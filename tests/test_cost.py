"""Tests for the cloud cost agent. Plain pytest-style functions."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from orbitronops_cost.findings import analyse  # noqa: E402
from orbitronops_cost.models import BillSummary, Inventory  # noqa: E402
from orbitronops_cost.pricing import (  # noqa: E402
    FALLBACK_HOURLY_RATE,
    instance_hourly_rate,
    instance_monthly_cost,
    reserved_savings,
    spot_savings,
)
from orbitronops_cost.report import render_markdown, render_text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_INV = json.loads((ROOT / "examples" / "inventory-sample.json").read_text())
SAMPLE_BILL = json.loads((ROOT / "examples" / "bill-sample.json").read_text())


def _inv(**overrides):
    data = json.loads(json.dumps(SAMPLE_INV))
    data.update(overrides)
    return Inventory.from_dict(data)


def test_sample_totals():
    report = analyse(_inv(), BillSummary.from_dict(SAMPLE_BILL))
    assert report.total_monthly_cost == 788.28
    assert report.total_estimated_savings == 415.44
    assert report.bill_total == 788.28
    assert report.bill_matches_inventory is True


def test_idle_instance_detection():
    report = analyse(_inv())
    idle = [f for f in report.findings if f.category == "idle"]
    ids = {f.resource_id for f in idle}
    assert ids == {"i-idleweb01", "i-devbox", "i-gputrain01"}
    gpu = next(f for f in idle if f.resource_id == "i-gputrain01")
    assert gpu.estimated_savings == 120.72
    assert gpu.severity == "HIGH"


def test_unattached_volume_detection():
    report = analyse(_inv())
    unattached = [f for f in report.findings if f.category == "unattached"]
    assert len(unattached) == 1
    assert unattached[0].resource_id == "vol-001"
    assert unattached[0].estimated_savings == 8.00


def test_savings_math_spot_and_reserved():
    assert spot_savings(124.10) == 86.87
    assert reserved_savings(70.08) == 28.03
    report = analyse(_inv())
    spot = next(f for f in report.findings if f.category == "spot")
    assert spot.resource_id == "i-batch01"
    assert spot.estimated_savings == 86.87
    reserved = next(f for f in report.findings if f.category == "reserved")
    assert reserved.resource_id == "i-api01"
    assert reserved.estimated_savings == 28.03


def test_oversized_downsize_math():
    report = analyse(_inv())
    over = next(f for f in report.findings if f.category == "oversized")
    assert over.resource_id == "i-api02"
    assert over.estimated_savings == 70.08  # m5.xlarge 140.16 - m5.large 70.08
    assert "m5.large" in over.recommendation


def test_recommendations_ordered_by_savings():
    report = analyse(_inv())
    savings = [f.estimated_savings for f in report.findings]
    assert savings == sorted(savings, reverse=True)
    assert report.findings[0].resource_id == "i-gputrain01"
    assert report.findings[0].estimated_savings == 120.72


def test_unknown_instance_type_fallback():
    rate, known = instance_hourly_rate("z9.mega")
    assert known is False
    assert rate == FALLBACK_HOURLY_RATE
    assert instance_monthly_cost("z9.mega", 730) == 73.00
    # No savings recommendation is priced on the fallback rate.
    report = analyse(_inv())
    priced = [f for f in report.findings if f.resource_id == "i-unknownbox"]
    assert priced == []


def test_missing_tag_detection():
    report = analyse(_inv())
    tagged = [f for f in report.findings if f.category == "tagging"]
    ids = {f.resource_id for f in tagged}
    assert ids == {"i-idleweb01", "i-devbox", "i-gputrain01"}
    assert all(f.estimated_savings == 0.0 for f in tagged)
    assert all("cost-center" in f.detail for f in tagged)


def test_old_snapshot_and_gp2_findings():
    report = analyse(_inv())
    snap = next(f for f in report.findings if f.category == "snapshot")
    assert snap.resource_id == "snap-001"
    assert snap.estimated_savings == 15.00
    gp2 = next(f for f in report.findings if f.category == "storage")
    assert gp2.resource_id == "vol-002"
    assert gp2.estimated_savings == 10.00


def test_empty_inventory_handling():
    report = analyse(Inventory.from_dict({}))
    assert report.total_monthly_cost == 0.0
    assert report.total_estimated_savings == 0.0
    assert report.findings == []
    assert report.live_aws_calls == 0


def test_json_output_valid_and_no_live_aws_calls():
    report = analyse(_inv(), BillSummary.from_dict(SAMPLE_BILL))
    data = json.loads(json.dumps(report.to_dict()))
    assert data["total_monthly_cost"] == 788.28
    assert data["live_aws_calls"] == 0
    assert len(data["findings"]) == 12
    assert data["pricing_note"].startswith("Sample prices")


def test_report_renders_cost_and_savings():
    report = analyse(_inv(), BillSummary.from_dict(SAMPLE_BILL))
    text = render_text(report)
    assert "$788.28" in text
    assert "$415.44" in text
    assert "No AWS calls were made" in text
    md = render_markdown(report)
    assert "# Cloud Cost Report" in md
    assert "$415.44" in md


def test_no_live_aws_calls_anywhere():
    """The demo never imports an AWS SDK or touches the network."""
    src = ROOT / "src"
    for path in src.rglob("*.py"):
        text = path.read_text()
        assert "boto3" not in text
        assert "botocore" not in text
        assert "requests." not in text
        assert "urllib" not in text
    report = analyse(_inv())
    assert report.live_aws_calls == 0


def test_cli_runs_on_samples():
    r = subprocess.run(
        [sys.executable, "-m", "orbitronops_cost", "analyse",
         "--inventory", str(ROOT / "examples" / "inventory-sample.json"),
         "--bill", str(ROOT / "examples" / "bill-sample.json")],
        cwd=ROOT, env={"PYTHONPATH": str(ROOT / "src"), "PATH": "/usr/bin:/bin"},
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, r.stderr
    assert "$788.28" in r.stdout
    assert "$415.44" in r.stdout
