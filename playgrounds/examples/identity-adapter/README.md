# Identity Adapter Example

This tiny adapter exists to demonstrate and test the canonical playground case runner.

It reads one JSON value from standard input and writes the same value to standard output.

Run the smoke pack:

```text
python3 scripts/run_playground_cases.py \
  --pack playgrounds/cases/identity-smoke.json \
  --adapter "python3 playgrounds/examples/identity-adapter/run.py"
```

A successful run reports three passed cases. This example is a harness fixture, not a research result.
