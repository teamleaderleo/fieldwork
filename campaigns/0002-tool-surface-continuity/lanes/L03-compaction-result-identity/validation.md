# Validation

Authoritative validation for the compact deterministic evidence artifact.

```bash
python3 campaigns/0002-tool-surface-continuity/lanes/L03-compaction-result-identity/artifacts/compaction_identity_fixture.py \
  --output campaigns/0002-tool-surface-continuity/lanes/L03-compaction-result-identity/artifacts/fixture-output.json
python3 -m py_compile \
  campaigns/0002-tool-surface-continuity/lanes/L03-compaction-result-identity/artifacts/compaction_identity_fixture.py
```

Result:

```text
15 cases passed
fixture-output.json sha256: daa012e0ad7d4c6b84a895511aa7cbebd041be22cd84c0cfe4c881b7242f7bb8
compaction_identity_fixture.py sha256: ff3a2e3ef931300fa634b7c27a8cca51b7dd73d5aa4d69172cf841562b5e6d04
```

The checksum in `report.md` was captured before the generated JSON was reduced to its review-focused form. This file and `artifacts/fixture-output.json` carry the authoritative checksum for fixture version 1.
