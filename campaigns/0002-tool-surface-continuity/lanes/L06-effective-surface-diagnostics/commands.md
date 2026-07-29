# L06 commands and retained results

## In simple words

Run one dependency-free classifier and its unit tests. The retained output should classify eight privacy-safe receipts with zero expectation mismatches.

## Commands

```bash
cd campaigns/0002-tool-surface-continuity/lanes/L06-effective-surface-diagnostics/artifacts
python3 classify_receipts.py fixtures.json --output results/latest.json
python3 -W error::ResourceWarning -m unittest -v test_classify_receipts.py
python3 -m py_compile classify_receipts.py test_classify_receipts.py
```

## Environment

- Python 3 standard library only
- no network access
- no credentials or external mutations
- public target source remains read-only

## Retained result

```text
classified 8 receipts: 7 divergences, 1 healthy, 0 mismatches
7 tests passed
py_compile passed
```

The authoritative machine-readable result is `results/latest.json`.
