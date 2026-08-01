# Proposed upstream pull request

State: `draft complete — independent internal review and public authorization pending`.

Public posting authorization: `false`.

## Proposed title

`coverage: cancel the selected backend process group on SIGINT`

## Draft body

### Summary

Start each selected coverage backend in a dedicated session/process group. When SIGINT is delivered directly to `coverage.py`, send SIGTERM to that owned group, wait for the wrapper, print `interrupted by SIGINT`, and exit 130.

Previously, the handler terminated only the immediate wrapper and broke into the ordinary epilogue. That allowed a cancelled matrix to return status 0 and allowed nested backend work to survive even after a status-only 130 correction.

### Change

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

The driver owns the group because it selects the backend and can establish one stable operation boundary before wrapper code creates descendants.

### Test plan

Exact source identity:

```text
Base: 77ec9be5417ee44c96343d2347145585da1b1f94
Base coverage.py blob: 9a522484aef05deae514a98e4b6adf5feb6c886d
Candidate head: 431614b3af58ba4f70791aa1d42cf5b71c965dd2
Candidate coverage.py blob: 9e31f21cf37228257b5e0705d9ecb13b7a66e40f
Patch blob: f1a2c75adfa009b6f1ac29e5a31bef526400444f
Changed files: coverage.py only
```

Focused target execution:

```text
Run: 30706007117
Patch application: success, --fuzz=0
Patch result equals target candidate: yes
Candidate compilation: success
Packet matrix: 6/6, twice
Refined null/QEMU-wrapper/passwordless-sudo matrix: 14/14, twice
Skips: none
Actual passwordless-sudo controls: executed
Cleanup and immediate rerun: success
```

Project-native ordinary source slice:

```text
Run: 30706633832
Job: 91386769087
Entry point: ./coverage.sh help man version
First pass: 3/3
Immediate rerun: 3/3
Candidate compilation: success
```

The exact base has an unrelated pre-existing Black failure on canonical `tarfilter` blob `ad776167a8473d5d15dbe22e850f4f6db35cf278`. The ordinary gate isolated only that exact baseline blob while retaining real Black 26.5.1 enforcement for `coverage.py` and every other checked Python file.

### Regression shape

This is a source-only change.

The project test harness treats every non-dot `tests/` entry as a `coverage.txt`-indexed shell-template package scenario. Testing the outer coverage orchestrator from inside the same harness would require a recursive miniature coverage tree substantially larger than the product correction.

A deterministic baseline/status/group reproducer was run against the exact target source and is retained outside this clean source diff. A native recursive regression can be added if review requires it.

### Compatibility and scope

This establishes group-wide SIGTERM delivery for tested TERM-responsive work that remains inside the owned group.

It does not claim:

- cleanup of descendants that create another process group or session;
- cleanup of descendants that ignore or materially defer SIGTERM;
- repeated-SIGINT behavior during cleanup;
- timeout, survivor diagnostics, or SIGKILL escalation;
- direct `/dev/tty` behavior;
- real QEMU/debvm package operations;
- non-Linux behavior.

The patch keeps the existing signal choice and adds no escalation.

## Clean diff

- `coverage.py`: 8 additions, 3 deletions.

Excluded:

- Fieldwork investigations, packets, receipts, workflows, and fixtures;
- historical Linux Fieldwork test modules;
- stronger escalation research.

## Publication checklist

- [ ] explicit public-contact authorization recorded;
- [x] controlled canonical fork and exact snapshot exist;
- [x] clean candidate branch and head recorded;
- [x] clean one-file diff recorded;
- [x] retained patch applies with zero fuzz;
- [x] candidate source equals patch-materialized source;
- [x] focused target controls pass twice;
- [x] project-native ordinary source slice passes twice;
- [x] cleanup and immediate rerun pass;
- [x] source-only regression-shape decision recorded;
- [ ] eligible independent complete-diff review accepted;
- [ ] overlap and contribution/AI policy refreshed immediately before send;
- [ ] exact public links refreshed immediately before send.

No canonical-upstream pull request has been opened from this workspace.
