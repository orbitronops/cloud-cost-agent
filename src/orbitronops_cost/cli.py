"""CLI: python -m orbitronops_cost analyse --inventory <file> [--bill <file>]"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running from a checkout without installing: `src` on sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orbitronops_cost.findings import analyse  # noqa: E402
from orbitronops_cost.models import BillSummary, Inventory  # noqa: E402
from orbitronops_cost.report import render_markdown, render_text  # noqa: E402


def _load_json(path: str, label: str):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"error: {label} file not found: {path}", file=sys.stderr)
        raise SystemExit(2)
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {path}: {exc}", file=sys.stderr)
        raise SystemExit(2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="orbitronops-cost",
        description="Cloud cost agent (OrbitronOps demo) — read-only analysis of sample data.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    analyse_cmd = sub.add_parser("analyse", help="Analyse a sample inventory.")
    analyse_cmd.add_argument("--inventory", required=True, help="Path to an inventory JSON file. See examples/.")
    analyse_cmd.add_argument("--bill", help="Optional path to a bill summary JSON file.")
    analyse_cmd.add_argument("--format", choices=["text", "json", "markdown"], default="text")
    analyse_cmd.add_argument("--output", help="Write the report to this file instead of stdout.")

    args = parser.parse_args(argv)

    if args.command == "analyse":
        inv = Inventory.from_dict(_load_json(args.inventory, "inventory"))
        bill = BillSummary.from_dict(_load_json(args.bill, "bill")) if args.bill else None
        report = analyse(inv, bill)

        if args.format == "json":
            output = json.dumps(report.to_dict(), indent=2)
        elif args.format == "markdown":
            output = render_markdown(report)
        else:
            output = render_text(report)

        if args.output:
            Path(args.output).write_text(output + "\n", encoding="utf-8")
            print(f"Report written to: {args.output}")
        else:
            print(output)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
