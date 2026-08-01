# Proposed upstream pull request

State: `not ready — clean controlled-fork source branch, upstream-native regression, ordinary gate, and final target review pending`.

Public posting authorization: `false`.

## Proposed title

`coverage: cancel the selected backend process group on SIGINT`

## Draft body

### Summary

Start each selected coverage backend in a dedicated session/process group. When SIGINT is delivered directly to `coverage.py`, send SIGTERM to that owned group, wait for the wrapper, print `interrupted by SIGINT`, and exit 130.

The current handler terminates only the immediate wrapper and breaks into the ordinary epilogue. That permits two wrong outcomes:

- a cancelled matrix can return status 0;
- nested work behind null, sudo, or QEMU wrappers can survive even after a status-only 130 correction.

### Change

- import `signal`;
- pass `start_new_session=True` to the backend `Popen` call;
- on `KeyboardInterrupt`, send `SIGTERM` to the owned process group;
- tolerate a group that already exited;
- wait for the wrapper;
- print `interrupted by SIGINT`;
- exit 130;
- leave ordinary result handling unchanged.

### Why the driver owns the group

`coverage.py` chooses the backend and can establish one operation boundary before backend code creates descendants. This avoids backend-specific process-tree discovery and covers descendants that remain in the selected group.

### Tests

Internal current-source execution used canonical mmdebstrap `main@77ec9be5417ee44c96343d2347145585da1b1f94` with `coverage.py` blob `9a522484aef05deae514a98e4b6adf5feb6c886d`.

```text
Patch blob: f1a2c75adfa009b6f1ac29e5a31bef526400444f
Patch application: success, --fuzz=0, twice
Python compilation: success
Packet null/source/status matrix: 6/6, twice
Refined null/QEMU-wrapper/passwordless-sudo matrix: 14/14, twice
Skips: none
Passwordless-sudo root-worker controls: executed
Unsignaled controls: success
Cleanup and immediate rerun: success
Internal run: 30689911760
Final packet-head run: 30690101504
```

Before publication, replace this internal receipt with exact commands and results from the clean controlled-fork candidate branch, including the upstream-native regression and project ordinary gate.

### Compatibility and scope

This change establishes group-wide SIGTERM delivery for tested TERM-responsive work remaining inside the owned group. It deliberately leaves stronger cleanup policy separate:

- descendants that create another process group or session;
- descendants that ignore or materially defer SIGTERM;
- repeated SIGINT during cleanup;
- timeout, survivor diagnostics, or SIGKILL escalation;
- direct `/dev/tty` behavior;
- real QEMU/debvm and prepared-mirror package operations;
- non-Linux execution.

The patch keeps the existing signal choice and adds no escalation.

## Intended clean diff

Required product file:

- `coverage.py`

Required target-native regression:

- path to be selected under the canonical repository's test convention.

Excluded from the clean source branch:

- Fieldwork investigations, notes, packets, receipts, and workflows;
- historical Linux Fieldwork test modules;
- escalation research from issue #341 / PR #347.

## Publication checklist

- [ ] explicit public-contact authorization recorded;
- [ ] controlled canonical fork selected or created;
- [ ] candidate branch created from refreshed exact canonical `main`;
- [ ] exact candidate commit/head recorded;
- [x] retained patch applies with zero fuzz to executed canonical base;
- [x] focused internal controls pass on executed canonical source;
- [x] cleanup and immediate rerun pass;
- [ ] upstream-native regression committed and passed on candidate branch;
- [ ] project-declared ordinary source gate passed;
- [ ] complete clean target diff independently reviewed;
- [ ] overlap and contribution/AI policy refreshed;
- [ ] links refreshed immediately before sending.

No upstream pull request has been opened from this workspace.
