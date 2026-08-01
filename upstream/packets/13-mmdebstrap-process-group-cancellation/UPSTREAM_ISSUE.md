# Proposed upstream issue

State: optional — a direct pull request is preferred once the clean source branch and target-native regression exist.

Public posting authorization: `false`.

## Title

`coverage.py can leave backend descendants running after SIGINT`

## Draft

When SIGINT is delivered to the `coverage.py` process itself, its `KeyboardInterrupt` handler terminates and waits for only the immediate backend wrapper:

```python
proc = subprocess.Popen(argv)
try:
    proc.wait()
except KeyboardInterrupt:
    proc.terminate()
    proc.wait()
    break
```

Some backend wrappers own nested shells, pipelines, output followers, foreground operations, or privileged workers. Terminating the wrapper PID alone can leave those descendants running after the coverage driver has acknowledged the interruption.

A status-only change that exits with 130 fixes the suite result while preserving the descendant-survival behavior. The cancellation boundary therefore needs to cover the selected backend operation, not only its immediate wrapper.

A focused direction is to start each backend in a dedicated session/process group and send SIGTERM to that group when the driver catches SIGINT:

```python
proc = subprocess.Popen(argv, start_new_session=True)
...
os.killpg(proc.pid, signal.SIGTERM)
```

Expected behavior:

- parent-only SIGINT reaches the complete in-group backend operation;
- the driver waits for the wrapper and exits 130 with an interruption diagnostic;
- ordinary unsignaled runs preserve their current result handling.

The tested responsive null, QEMU-wrapper, and sudo topologies settle without later work under this approach. Descendants that create another group/session or resist SIGTERM require separate policy and should stay outside the initial repair.

A pull request can include a focused regression that distinguishes:

1. current wrapper-only termination, where nested work survives;
2. status-only exit 130, where nested work still survives;
3. group-wide termination, where tested responsive in-group work stops and the driver returns 130.

## Internal publication notes

Before posting:

- refresh the exact upstream head and source lines;
- materialize the clean target-source branch;
- run target-native focused and ordinary gates;
- replace internal evidence wording with target-native receipts;
- follow current project contribution and AI-disclosure policy;
- obtain explicit authority for this exact public interaction.