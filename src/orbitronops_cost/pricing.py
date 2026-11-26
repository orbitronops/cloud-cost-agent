"""Sample price table for the cost agent.

These are SAMPLE prices, clearly labelled, used only so the demo can
produce a priced report from local files. They are NOT live AWS pricing:
real prices vary by region and change over time. A live audit prices
from the client's actual bill (Cost Explorer / CUR), never from this table.

Rates are USD per hour (instances) or per GB-month (storage).
"""
from __future__ import annotations

# Sample on-demand instance prices, USD / hour. Approximate, Nov 2026.
SAMPLE_INSTANCE_PRICES: dict[str, float] = {
    "t3.micro": 0.0104,
    "t3.small": 0.0208,
    "t3.medium": 0.0416,
    "t3.large": 0.0832,
    "m5.large": 0.096,
    "m5.xlarge": 0.192,
    "m5.2xlarge": 0.384,
    "c5.large": 0.085,
    "c5.xlarge": 0.17,
    "c5.2xlarge": 0.34,
    "r5.large": 0.126,
    "r5.xlarge": 0.252,
    "g5.xlarge": 1.006,
}

# Fallback rate for an instance type not in the table. The finding is
# flagged as an estimate, and no savings recommendation is priced on it.
FALLBACK_HOURLY_RATE = 0.10

# Sample EBS prices, USD / GB-month.
SAMPLE_VOLUME_PRICES: dict[str, float] = {
    "gp3": 0.08,
    "gp2": 0.10,
    "io1": 0.125,
    "io2": 0.125,
    "st1": 0.045,
    "sc1": 0.015,
}

SNAPSHOT_PRICE_PER_GB_MONTH = 0.05

# Sample discount assumptions (fractions of on-demand price saved).
SPOT_SAVINGS_FRACTION = 0.70  # Spot typically pays ~30% of on-demand.
RESERVED_SAVINGS_FRACTION = 0.40  # 1-year Reserved pays ~60% of on-demand.

# Thresholds used by the findings engine.
IDLE_CPU_PERCENT = 10.0  # below this, an instance counts as idle
IDLE_GPU_PERCENT = 10.0
OVERSIZED_CPU_PERCENT = 25.0  # below this, a busy instance may be oversized
OLD_SNAPSHOT_DAYS = 180  # snapshots older than this are flagged
REQUIRED_TAGS = ("env", "team", "cost-center")


def instance_hourly_rate(instance_type: str) -> tuple[float, bool]:
    """Return (hourly rate, is_known_type). Unknown types use the fallback."""
    rate = SAMPLE_INSTANCE_PRICES.get(instance_type)
    if rate is None:
        return FALLBACK_HOURLY_RATE, False
    return rate, True


def instance_monthly_cost(instance_type: str, hours_per_month: float) -> float:
    rate, _ = instance_hourly_rate(instance_type)
    return round(rate * hours_per_month, 2)


def volume_monthly_cost(volume_type: str, size_gb: float) -> float:
    rate = SAMPLE_VOLUME_PRICES.get(volume_type, SAMPLE_VOLUME_PRICES["gp3"])
    return round(rate * size_gb, 2)


def snapshot_monthly_cost(size_gb: float) -> float:
    return round(SNAPSHOT_PRICE_PER_GB_MONTH * size_gb, 2)


def spot_savings(monthly_cost: float) -> float:
    return round(monthly_cost * SPOT_SAVINGS_FRACTION, 2)


def reserved_savings(monthly_cost: float) -> float:
    return round(monthly_cost * RESERVED_SAVINGS_FRACTION, 2)


def downsize_savings(current_monthly: float, smaller_monthly: float) -> float:
    return round(max(0.0, current_monthly - smaller_monthly), 2)


def smaller_instance_type(instance_type: str) -> str | None:
    """One size down in the same family, or None if already smallest."""
    downsizes = {
        "m5.2xlarge": "m5.xlarge",
        "m5.xlarge": "m5.large",
        "c5.2xlarge": "c5.xlarge",
        "c5.xlarge": "c5.large",
        "r5.xlarge": "r5.large",
        "t3.large": "t3.medium",
        "t3.medium": "t3.small",
        "t3.small": "t3.micro",
    }
    return downsizes.get(instance_type)
