# Retained local process model

## In simple words

This directory retains both the exact original packet-time harness and a reviewed relocatable replay. Both produce the same three-way lifecycle result.

## Files

- `child.py`, `driver.py`, and `wrapper.py` — shared model processes;
- `harness_original.py` — exact source used for the first packet-time run, including its `/tmp/unit13-probe` path;
- `harness.py` — reviewed replay that runs directly from this directory, waits for both readiness markers, and guarantees cleanup after assertion or timeout failure.

## Reviewed replay

```sh
cd upstream/packets/13-mmdebstrap-process-group-cancellation/fixtures/local-process-model
python3 -m py_compile child.py driver.py harness.py harness_original.py wrapper.py
python3 harness.py
```

Expected output:

```text
variant=baseline rc=0 later_work=true child_live=false
variant=status rc=130 later_work=true child_live=false
variant=group rc=130 later_work=false child_live=false
```

## Original replay

The original harness requires a copy at `/tmp/unit13-probe`:

```sh
rm -rf /tmp/unit13-probe
mkdir -p /tmp/unit13-probe
cp child.py driver.py harness_original.py wrapper.py /tmp/unit13-probe/
cp /tmp/unit13-probe/harness_original.py /tmp/unit13-probe/harness.py
cd /tmp/unit13-probe
python3 harness.py
```

The reviewed replay changes fixture portability and readiness ordering only. It leaves the model processes, expected status values, later-work assertions, and selected mechanism unchanged.

This is a small Linux process model. Exact imported mmdebstrap wrapper controls and CI receipts remain linked from `../../TESTS.md`.
