# Proposed upstream issue

State: optional — direct pull request preferred after the clean target branch exists.

Public posting authorization: `false`.

## Title

`coverage.py` can leave the selected backend running after parent-only SIGINT

## Draft

When SIGINT is delivered directly to `coverage.py` instead of the foreground process group, the current handler terminates only the immediate backend wrapper:

```python
proc = subprocess.Popen(argv)
try:
    proc.wait()
except KeyboardInterrupt:
    proc.terminate()
    proc.wait()
    break
```

Nested work behind `run_null.sh`, `run_null.sh SUDO`, or `run_qemu.sh` can remain alive after the wrapper receives TERM. The `break` also enters the ordinary epilogue, so a cancelled run can return status 0.

A status-only repair that exits 130 fixes the false-success result while leaving the nested-backend survivor case intact.

A focused repair gives each selected backend a dedicated session/process group, sends TERM to that group when the coverage parent receives SIGINT, waits for the wrapper, reports the interruption, and exits 130:

```python
proc = subprocess.Popen(argv, start_new_session=True)
try:
    proc.wait()
except KeyboardInterrupt:
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    proc.wait()
    print("interrupted by SIGINT", file=sys.stderr)
    raise SystemExit(130)
```

Focused responsive-topology controls distinguish:

- imported baseline: status 0 after deliberate release, nested work survives and performs later work;
- status-only comparator: status 130 after release, nested work still survives;
- group candidate: status 130, no live responsive in-group work, no later-work marker;
- null, QEMU-wrapper, and passwordless-sudo paths;
- ordinary foreground-group and unsignaled success;
- cleanup and immediate rerun.

This issue would cover parent-only SIGINT and TERM-responsive work remaining inside the selected backend group. TERM-resistant descendants, repeated SIGINT during cleanup, timeout/escalation policy, and descendants that create another session remain separate questions.

## Evidence prepared internally

- exact canonical base executed: `77ec9be5417ee44c96343d2347145585da1b1f94`;
- canonical/imported `coverage.py` blob: `9a522484aef05deae514a98e4b6adf5feb6c886d`;
- upstream-root patch blob: `f1a2c75adfa009b6f1ac29e5a31bef526400444f`;
- zero-fuzz patch application and compilation: success twice;
- packet matrix: 6/6 twice;
- refined null/QEMU-wrapper/passwordless-sudo matrix: 14/14 twice, no skips;
- cleanup and immediate rerun: success;
- internal run: `30689911760`;
- final packet-head run: `30690101504`.

## Internal publication checklist

Before posting:

- create/select a controlled fork of canonical `josch/mmdebstrap`;
- refresh canonical `main` and record the exact base;
- create a clean target branch and commit;
- add an upstream-native regression;
- run focused and ordinary project gates;
- refresh overlap and contribution/AI policy;
- obtain independent clean-target review;
- replace internal run references with public candidate links where appropriate;
- obtain explicit authority for this exact public interaction.

No issue has been posted from this workspace.
