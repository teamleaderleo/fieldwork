# Local process model receipt — 2026-08-01

## In simple words

A Linux model repeated the central three-way distinction. Terminating only the wrapper allowed a descendant to perform later work. Signalling the caller-owned process group prevented that later work and returned 130.

The original run source remains preserved. A reviewed relocatable replay corrected fixture portability and readiness ordering, compiled successfully, and produced the same result.

## Exact environment

- date: 2026-08-01
- kernel: `Linux 6.12.13 x86_64`
- Python: `3.13.5`
- execution surface: disposable local files under `/tmp`; no network access
- evidence class: `model-executed`

## Retained test source

- [`harness_original.py`](../fixtures/local-process-model/harness_original.py) — exact first-run source with `/tmp/unit13-probe` root
- [`harness.py`](../fixtures/local-process-model/harness.py) — reviewed relocatable replay
- [`driver.py`](../fixtures/local-process-model/driver.py)
- [`wrapper.py`](../fixtures/local-process-model/wrapper.py)
- [`child.py`](../fixtures/local-process-model/child.py)
- [repeat instructions](../fixtures/local-process-model/README.md)

## Model

The driver starts a wrapper. The wrapper starts one child. The child waits 0.8 seconds and writes a `later-work` marker.

Three driver variants receive SIGINT on the driver PID only:

1. imported-style baseline: terminate and wait for the wrapper, then return 0;
2. status-only predecessor: terminate and wait for the wrapper, then return 130;
3. selected candidate: start the wrapper in a new session, send TERM to the process group, wait for the wrapper, then return 130.

## Original command

```sh
cd /tmp/unit13-probe
python3 harness.py
```

## Reviewed replay commands

```sh
cd upstream/packets/13-mmdebstrap-process-group-cancellation/fixtures/local-process-model
python3 -m py_compile child.py driver.py harness.py harness_original.py wrapper.py
python3 harness.py
```

Results:

- compilation: success;
- reviewed replay: success;
- temporary directories: removed by `TemporaryDirectory`;
- surviving fixture PIDs: killed in `finally` cleanup when present.

## Exact output

The initial run, closeout rerun, and reviewed relocatable replay produced the same output:

```text
variant=baseline rc=0 later_work=true child_live=false
variant=status rc=130 later_work=true child_live=false
variant=group rc=130 later_work=false child_live=false
```

The `child_live=false` observation was taken one second after SIGINT. In both losing variants the child had already completed and wrote the later-work marker. The selected group variant prevented that marker.

## Assertions

```python
assert results == [
    ("baseline", 0, True, False),
    ("status", 130, True, False),
    ("group", 130, False, False),
]
```

## Fixture repair classification

The original harness depended on an absolute `/tmp/unit13-probe` source path and waited only for `child-ready` before reading `wrapper-ready`. The reviewed replay:

- resolves sibling files from `__file__`;
- waits for both readiness markers;
- detects early driver exit;
- cleans driver, wrapper, and child processes after failures.

This is a packet-fixture repair. It changes no model process, candidate mechanism, expected status, or later-work assertion.

## Coverage boundary

This model establishes descendant later-work suppression for one TERM-responsive wrapper/child topology. It omits exact mmdebstrap wrappers, sudo, QEMU/debvm, terminal behavior, repeated SIGINT, TERM resistance, group escape, target-native tests, and ordinary upstream gates. The retained Linux Fieldwork controls cover exact imported wrappers more deeply.
