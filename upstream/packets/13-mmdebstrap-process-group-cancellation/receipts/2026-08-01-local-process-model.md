# Local process model receipt — 2026-08-01

## In simple words

A fresh Linux model repeated the central three-way distinction. Terminating only the wrapper allowed a descendant to perform later work. Signalling the caller-owned process group prevented that later work and returned 130.

## Exact environment

- date: 2026-08-01
- kernel: `Linux 6.12.13 x86_64`
- Python: `3.13.5`
- execution surface: disposable local files under `/tmp`; no network access
- evidence class: `model-executed`

## Model

The driver starts a wrapper. The wrapper starts one child. The child waits 0.8 seconds and writes a `later-work` marker.

Three driver variants receive SIGINT on the driver PID only:

1. imported-style baseline: terminate and wait for the wrapper, then return 0;
2. status-only predecessor: terminate and wait for the wrapper, then return 130;
3. selected candidate: start the wrapper in a new session, send TERM to the process group, wait for the wrapper, then return 130.

## Command

```sh
cd /tmp/unit13-probe
python3 harness.py
```

## Exact output

```text
variant=baseline rc=0 later_work=true child_live=false
variant=status rc=130 later_work=true child_live=false
variant=group rc=130 later_work=false child_live=false
```

The `child_live=false` observation was taken one second after SIGINT. In both losing variants the child had already completed and wrote the later-work marker. The selected group variant prevented that marker.

## Assertions

```python
assert results[0][1:] == (0, True, False)
assert results[1][1:] == (130, True, False)
assert results[2][1:] == (130, False, False)
```

## Coverage boundary

This model establishes descendant later-work suppression for one TERM-responsive wrapper/child topology. It omits exact mmdebstrap wrappers, sudo, QEMU/debvm, terminal behavior, repeated SIGINT, TERM resistance, group escape, target-native tests, and ordinary upstream gates. The retained Linux Fieldwork controls cover exact imported wrappers more deeply.