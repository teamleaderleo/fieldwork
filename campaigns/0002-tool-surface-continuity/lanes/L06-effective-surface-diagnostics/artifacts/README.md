# Effective-surface receipt artifacts

## In simple words

These files turn the accepted campaign evidence into one privacy-safe diagnostic format. They classify the first observable divergence without retaining prompts, arguments, credentials, schemas, tool names, or provider payloads.

Files:

- `receipt.schema.json` — receipt data contract
- `fixtures.json` — eight normalized campaign receipts
- `classify_receipts.py` — classifier and privacy validator
- `test_classify_receipts.py` — focused tests
- `results/latest.json` — retained classification output
- `run-output.txt` and `test-output.txt` — retained command logs

Run the commands in the lane-level `commands.md`.
