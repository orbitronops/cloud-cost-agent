# Security

## What the agent can do

- Read an inventory JSON file and an optional bill JSON file you give it.
- Print a cost report (text, Markdown, or JSON).

## What the agent cannot do

- It has no network access in the demo path.
- It cannot call any AWS API, and it stores no credentials. There is no
  place to put an access key in the demo.
- It cannot stop, terminate, modify, or delete any resource. There is no
  execution path at all in v0.1.0 — findings are recommendations in a
  report, and a human reviews every one before anything is done.
- It cannot see a real bill. The sample files are fictional; the prices
  in `pricing.py` are samples, clearly labelled, and never presented as
  live AWS pricing.

## Human-in-the-loop

Every report ends with the same two lines:

- "No AWS calls were made. No resources were changed."
- "A human reviews every recommendation before anything is done."

A future live connector must keep that gate: propose, log, wait for a named
approver, then (and only then) act, and log that too.

## Reporting a problem

Open an issue in this repo. Do not include real AWS account IDs, real
billing data, or real credentials in any issue or example.
