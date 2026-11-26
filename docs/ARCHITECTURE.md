# Architecture

## Design

```
Bill JSON + Inventory JSON → Findings engine → Priced findings (sample prices)
                                             → Report (text / Markdown / JSON)
```

The engine is deliberately deterministic for the demo — same input, same
output, every time. There is no LLM, no embeddings service, and no AWS
account involved. A future live connector would read the same shapes from
Cost Explorer / CUR and the EC2 / EBS APIs, and keep this engine unchanged.

## The findings engine

`src/orbitronops_cost/findings.py` runs, per resource, in this order:

| Check | Rule | Savings priced as |
|---|---|---|
| Idle instance | avg CPU < 10% (and GPU < 10% if present) | Full monthly cost (stop it) |
| Oversized instance | avg CPU < 25%, smaller type exists in the same family | Current − smaller monthly cost |
| Spot candidate | fault-tolerant, on-demand | 70% of monthly cost (sample assumption) |
| Reserved candidate | steady usage (CPU ≥ 25%), on-demand | 40% of monthly cost (sample assumption) |
| Unattached volume | no instance attached | Full monthly cost |
| gp2 volume | attached gp2 | gp2 − gp3 monthly cost |
| Old snapshot | age > 180 days | Full monthly cost |
| Missing cost tags | any of `env`, `team`, `cost-center` absent | $0 — visibility, not savings |

Rules are mutually exclusive per instance in a fixed priority: idle first,
then oversized, then Spot / Reserved. That keeps one resource from producing
two competing savings numbers. Reserved instances are skipped for
idle/oversized/Spot/Reserved checks — the spend is already committed, so
stopping one does not save money.

Findings are ordered by estimated savings, highest first (ties broken by
resource id, so the order is stable).

## The price table

`src/orbitronops_cost/pricing.py` holds a small table of sample instance
and storage prices, labelled as samples in code, in the report, and in the
README. Unknown instance types fall back to $0.10/hour, flagged as a
fallback: the cost is estimated, and no Spot / Reserved / oversized
recommendation is priced on it. A live audit replaces this table with the
client's actual bill — the engine does not change.

## Bill cross-check

When a bill summary is given (`--bill`), the report compares the bill total
with the cost computed from the inventory. The sample bill matches exactly
($788.28), so the cross-check passes. A mismatch is reported in the output,
never hidden — it usually means the inventory is incomplete or the bill
covers services the inventory does not list.

## Extension points

- **Live AWS connector** — read Cost Explorer / CUR for the bill and
  `describe-instances` / `describe-volumes` / `describe-snapshots` for the
  inventory. The findings engine takes the same dataclasses.
- **Real-bill pricing** — replace `pricing.py` with per-account rates from
  the bill; keep the fallback rule for unknown types.
- **Utilisation source** — replace the sample `avg_cpu_percent` with
  CloudWatch metrics; keep the same thresholds.
- **More checks** — idle load balancers, old AMIs, unattached EIPs,
  underused RDS. Each new check is one function plus one test.
