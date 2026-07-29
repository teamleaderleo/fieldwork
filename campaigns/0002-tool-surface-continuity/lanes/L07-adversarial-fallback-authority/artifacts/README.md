# L07 Synthetic Fallback Authority Case Pack

This directory contains a deterministic, zero-dependency model of capability-loss fallback decisions. It compares an availability-only selector with an authority-aware selector across shell, protocol, browser or Computer Use, substitute connector, and subagent paths.

## Safety

- synthetic resource and credential labels only;
- zero network calls;
- zero external mutations;
- reversible mutation descriptions only;
- no secrets, account identifiers, private prompts, or production data.

## Run

From the lane directory:

```bash
python3 artifacts/fallback_authority_harness.py \
  --cases artifacts/cases.json \
  --output artifacts/results.json
```

Validate syntax and determinism:

```bash
python3 -m py_compile artifacts/fallback_authority_harness.py
python3 artifacts/fallback_authority_harness.py --cases artifacts/cases.json --output /tmp/l07-results-1.json
python3 artifacts/fallback_authority_harness.py --cases artifacts/cases.json --output /tmp/l07-results-2.json
cmp /tmp/l07-results-1.json /tmp/l07-results-2.json
cmp /tmp/l07-results-1.json artifacts/results.json
```

Validated environment:

- Python 3.13.5
- Linux 6.12.13 x86_64, glibc 2.41

Expected aggregate result:

```json
{
  "case_count": 13,
  "availability_first_silent_reroutes": 13,
  "authority_guarded_counts": {
    "allow_equivalent": 5,
    "fail_closed": 3,
    "require_explicit_approval": 5
  },
  "all_expectations_passed": true,
  "failed_cases": []
}
```

Expected `results.json` SHA-256:

```text
244ff2c6958c40e58391b3caff4fa856836b87b220e5d20fb26d71206e6b129e
```

## Files

- `fallback_authority_harness.py` — deterministic comparison logic.
- `cases.json` — six benign reads followed by seven reversible or ambiguity-focused mutation cases.
- `results.json` — retained machine-readable output.
