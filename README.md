# OrbitronOps Cloud Cost Agent

> **A cloud cost agent for AWS bills and resource inventories.**
> It reads a sample bill and inventory, finds the waste, prices it with a
> clearly labelled sample price table, and orders the recommendations by
> estimated savings — it never touches a live account or changes anything.

[![CI](https://github.com/orbitronops/cloud-cost-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/orbitronops/cloud-cost-agent/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Demo](https://img.shields.io/badge/status-demo%20%E2%80%94%20not%20client%20work-lightgrey.svg)](#status)

**By [OrbitronOps](https://www.orbitronops.com)** — Production AI Infrastructure on Kubernetes.
North Vancouver, BC · Canada Remote / BC Hybrid

---

## What this proves

A buyer doesn't have to take our word for it. They can run this in 2 minutes:

```bash
git clone https://github.com/orbitronops/cloud-cost-agent.git
cd cloud-cost-agent
PYTHONPATH=src python3 -m orbitronops_cost analyse --inventory examples/inventory-sample.json --bill examples/bill-sample.json
```

And get a priced report like this:

```
Account: sample-account (us-east-1)  ·  Month: 2026-10
Estimated monthly cost: $788.28 (Prices are SAMPLE prices — not live AWS pricing.)
Estimated monthly savings available: $415.44
Findings: 12
Bill total: $788.28 — matches the inventory cost.

  1. [HIGH] Idle instance i-gputrain01 (g5.xlarge)  ·  est. savings $120.72/mo
  2. [MEDIUM] On-demand instance i-batch01 could use Spot  ·  est. savings $86.87/mo
  3. [MEDIUM] Oversized instance i-api02 (m5.xlarge)  ·  est. savings $70.08/mo
  4. [MEDIUM] Idle instance i-idleweb01 (m5.large)  ·  est. savings $70.08/mo
  5. [MEDIUM] Steady-state instance i-api01 could use Reserved  ·  est. savings $28.03/mo
  ...
```

The full report is in [`examples/sample-report.md`](examples/sample-report.md).

No API key needed for the demo. No AWS account needed. No cloud bill.

## Why read-only first?

This is the OrbitronOps rule for cost work:

1. **Read-only first** — the demo reads local JSON files. A live audit reads the bill and the inventory; it never changes anything.
2. **No invented numbers** — cost figures use a clearly labelled sample price table. A real audit prices from the client's actual bill.
3. **Human review** — the report is a starting point for a human audit, not a verdict on its own. Every recommendation waits for a person to approve it.

That is how you ship a cost agent to a team without asking them to trust a black box — or a made-up saving.

## Quickstart

**Requirements:** Python 3.10+ only. No dependencies for the demo.

```bash
# 1. Clone
git clone https://github.com/orbitronops/cloud-cost-agent.git
cd cloud-cost-agent

# 2. Analyse the sample inventory and bill
PYTHONPATH=src python3 -m orbitronops_cost analyse --inventory examples/inventory-sample.json --bill examples/bill-sample.json

# 3. Get a Markdown report (see examples/sample-report.md for the output)
PYTHONPATH=src python3 -m orbitronops_cost analyse --inventory examples/inventory-sample.json --bill examples/bill-sample.json --format markdown --output reports/sample.md

# 4. Or JSON, for tooling
PYTHONPATH=src python3 -m orbitronops_cost analyse --inventory examples/inventory-sample.json --format json

# 5. Run the tests
python -m pytest -q
# or, with no pytest installed:
python -m unittest discover -s tests -v
```

### Try your own inventory

Copy an example and edit it:

```bash
cp examples/inventory-sample.json my-inventory.json
# edit my-inventory.json, then:
PYTHONPATH=src python3 -m orbitronops_cost analyse --inventory my-inventory.json
```

See [`examples/`](examples/) for the inventory and bill schemas, and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for how the checks and pricing work.

## How it works

```
Bill JSON + Inventory JSON → Findings engine → Priced findings (sample prices)
                                                → Report (text / Markdown / JSON)
```

| Waste found | Rule |
|---|---|
| Idle instance | avg CPU < 10% (GPU < 10% if present) |
| Oversized instance | avg CPU < 25%, smaller type exists in the same family |
| Spot candidate | fault-tolerant workload on on-demand |
| Reserved candidate | steady usage (CPU ≥ 25%) on on-demand |
| Unattached volume | no instance attached |
| gp2 volume | gp3 costs less per GB-month |
| Old snapshot | age > 180 days |
| Missing cost tags | any of `env`, `team`, `cost-center` absent |

The engine is deliberately deterministic for the demo — same input, same output, every time. Findings are ordered by estimated savings, highest first, and one resource never produces two competing savings numbers (idle beats oversized beats Spot / Reserved). Reserved instances are skipped for those checks: the spend is already committed.

Prices are **samples** (`src/orbitronops_cost/pricing.py`) — approximate, November 2026, labelled as such in the code and in every report. Unknown instance types fall back to $0.10/hour and get no savings recommendation priced on that fallback.

## Project layout

```
.
├── src/orbitronops_cost/    # the agent: models, findings, pricing, report, CLI
│   ├── models.py            # Inventory / Instance / Volume / Finding / CostReport
│   ├── pricing.py           # sample price table (labelled, never live pricing)
│   ├── findings.py          # deterministic waste-finding engine
│   ├── report.py            # text / Markdown / JSON report rendering
│   └── cli.py               # `python -m orbitronops_cost analyse --inventory <file>`
├── examples/                # sample bill + inventory + a sample report
│   ├── bill-sample.json     # fictional bill — matches the inventory cost
│   ├── inventory-sample.json # fictional resources — 8 instances, 3 volumes, 2 snapshots
│   └── sample-report.md     # actual Markdown report for the samples
├── tests/                   # pytest / unittest tests for every check
├── docs/
│   ├── ARCHITECTURE.md      # design, pricing model, extension points
│   └── SECURITY.md          # what the agent can / cannot do
├── .github/workflows/ci.yml # lint + tests on every push
├── Dockerfile               # run the demo in a container, no local Python needed
└── pyproject.toml
```

## Status

**Demo — not client work.**

OrbitronOps has not yet delivered a client cost audit using this agent, and no cost saving in this repo was achieved for a client. This repository is a working prototype built to show how we do cost work: the checks, the pricing model, and the report a client would actually get. No client names, no client results, and no client data appear anywhere in it.

If you want your bill and inventory analysed, talk to us: [orbitronops.com](https://www.orbitronops.com) · [LinkedIn](https://www.linkedin.com/company/orbitronops/)

## Roadmap

- [x] Deterministic waste checks + sample-price cost model + Markdown/JSON reports
- [ ] Live read-only AWS connector (Cost Explorer / CUR + EC2 / EBS APIs) — demo path keeps working with no credentials
- [ ] Real-bill pricing from Cost Explorer / CUR, replacing the sample price table for live audits
- [ ] CloudWatch utilisation instead of sample CPU figures
- [ ] More checks: idle load balancers, old AMIs, unattached EIPs, underused RDS
- [ ] Savings tracking: re-run after the actions are done and compare

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues and PRs welcome — please keep the read-only rule intact.

## License

MIT — see [LICENSE](LICENSE).
