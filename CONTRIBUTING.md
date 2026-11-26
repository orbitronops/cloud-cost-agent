# Contributing

Thanks for looking at this OrbitronOps demo.

## Ground rules

1. **Read-only stays read-only.** This agent analyses local sample files. No PR may add a live AWS call, a credential, or any mutating action (`terminate`, `stop`, `delete`, `modify`) to the CLI. The test `test_no_live_aws_calls_anywhere` enforces this.
2. **No fake client claims.** Do not add a case study, logo, testimonial, or "saved $X" claim for work that did not happen. This is a demo prototype. Prices in `pricing.py` are samples, never live AWS pricing.
3. **Every new check needs a test.** Add the resource to `examples/` if it is a good demo, and a test in `tests/test_cost.py`.

## Running it locally

```bash
PYTHONPATH=src python3 -m orbitronops_cost analyse --inventory examples/inventory-sample.json --bill examples/bill-sample.json
python -m pytest -q
```
