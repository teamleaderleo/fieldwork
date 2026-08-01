# Retained local process model

These four Python files are the exact source used for the packet-time model on 2026-08-01.

The executed `harness.py` intentionally records its original absolute source root, `/tmp/unit13-probe`. To repeat the exact command:

```sh
rm -rf /tmp/unit13-probe
mkdir -p /tmp/unit13-probe
cp child.py driver.py harness.py wrapper.py /tmp/unit13-probe/
cd /tmp/unit13-probe
python3 harness.py
```

Expected output:

```text
variant=baseline rc=0 later_work=true child_live=false
variant=status rc=130 later_work=true child_live=false
variant=group rc=130 later_work=false child_live=false
```

This is a small Linux process model. The exact imported mmdebstrap wrapper controls and their CI receipts remain linked from `../../TESTS.md`.
