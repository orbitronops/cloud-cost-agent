"""Report rendering: text, Markdown, and JSON. Estimates only."""
from __future__ import annotations

from .models import CostReport

PRICING_NOTE = "Prices are SAMPLE prices (see pricing.py) — not live AWS pricing."


def render_text(report: CostReport) -> str:
    lines = [
        f"Account: {report.account} ({report.region})  ·  Month: {report.month or 'sample'}",
        f"Estimated monthly cost: ${report.total_monthly_cost:.2f} ({PRICING_NOTE})",
        f"Estimated monthly savings available: ${report.total_estimated_savings:.2f}",
        f"Findings: {len(report.findings)}",
    ]
    if report.bill_total is not None:
        match = "matches" if report.bill_matches_inventory else "DOES NOT match"
        lines.append(
            f"Bill total: ${report.bill_total:.2f} — {match} the inventory cost."
        )
    lines.append("")
    for i, f in enumerate(report.findings, 1):
        lines.append(
            f"  {i}. [{f.severity}] {f.title}  ·  est. savings ${f.estimated_savings:.2f}/mo"
        )
        lines.append(f"     {f.detail}")
        lines.append(f"     Recommendation: {f.recommendation}")
    lines += [
        "",
        "No AWS calls were made. No resources were changed.",
        "A human reviews every recommendation before anything is done.",
    ]
    return "\n".join(lines)


def render_markdown(report: CostReport) -> str:
    lines = [
        f"# Cloud Cost Report — {report.account}",
        "",
        f"- **Region:** {report.region}",
        f"- **Month:** {report.month or 'sample'}",
        f"- **Estimated monthly cost:** ${report.total_monthly_cost:.2f}",
        f"- **Estimated monthly savings available:** ${report.total_estimated_savings:.2f}",
        f"- **Findings:** {len(report.findings)}",
        "",
        f"> {PRICING_NOTE}",
        "",
    ]
    if report.bill_total is not None:
        match = "matches" if report.bill_matches_inventory else "does NOT match"
        lines.append(
            f"Bill total **${report.bill_total:.2f}** {match} the inventory cost."
        )
        lines.append("")
    lines += ["## Findings (ordered by estimated savings)", ""]
    lines.append("| # | Finding | Severity | Est. savings / mo |")
    lines.append("|---|---|---|---|")
    for i, f in enumerate(report.findings, 1):
        lines.append(
            f"| {i} | {f.title} | {f.severity} | ${f.estimated_savings:.2f} |"
        )
    lines.append("")
    for i, f in enumerate(report.findings, 1):
        lines.append(f"### {i}. {f.title}")
        lines.append("")
        lines.append(f"- **Resource:** `{f.resource_id}` — category `{f.category}`")
        lines.append(f"- **Monthly cost:** ${f.monthly_cost:.2f}")
        lines.append(f"- **Estimated savings:** ${f.estimated_savings:.2f}/mo")
        lines.append(f"- **Detail:** {f.detail}")
        lines.append(f"- **Recommendation:** {f.recommendation}")
        lines.append("")
    lines += [
        "## Notes",
        "",
        "- No AWS calls were made. No resources were changed.",
        "- A human reviews every recommendation before anything is done.",
        "",
    ]
    return "\n".join(lines)
