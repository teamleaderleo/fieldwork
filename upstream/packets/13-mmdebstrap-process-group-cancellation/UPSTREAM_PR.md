# Proposed upstream pull request

State: `not ready — clean current-upstream source branch and target-native regression pending`.

Public posting authorization: `false`.

## Proposed title

`coverage.py: terminate the selected backend process group on SIGINT`

## Draft body

### Summary

Start each selected coverage backend in a dedicated session/process group and send SIGTERM to that group when `coverage.py` receives SIGINT.

The current handler terminates only the immediate wrapper. Backend wrappers can own nested shells, pipelines, output followers, foreground operations, or privileged workers, so wrapper-only termination can leave work running after the driver acknowledges cancellation.

### Change

- import `signal`;
- pass `start_new_session=True` to the backend `Popen` call;
- on `KeyboardInterrupt`, send `SIGTERM` to the owned process group;
- tolerate a group that has already exited;
- wait for the wrapper;
- print `interrupted by SIGINT` and exit 130;
- leave ordinary result handling unchanged.

### Why the driver owns the group

`coverage.py` chooses the backend and can establish one operation boundary before backend code creates descendants. This avoids backend-specific process-tree discovery and covers descendants that remain in the selected group.

### Tests

The focused regression should compare parent-PID-only SIGINT across three variants:

- current wrapper-only termination: nested work can continue;
- status-only exit 130: nested work can still continue;
- process-group candidate: tested TERM-responsive in-group work stops, no later marker appears, and the driver exits 130.

It should retain an ordinary unsignaled success control.

Before publication, replace this paragraph with exact target-native commands and results from the clean current-upstream branch.

### Compatibility and scope

This change establishes group-wide SIGTERM delivery. It deliberately leaves stronger cleanup policy separate:

- descendants that create another process group or session;
- descendants that ignore or materially defer SIGTERM;
- repeated SIGINT during cleanup;
- timeout, survivor diagnostics, or SIGKILL escalation;
- direct `/dev/tty` behavior and full interactive QEMU/debvm coverage.

The initial repair keeps the existing signal choice and adds no escalation.

## Intended clean diff

Required product file:

- `coverage.py`

Required target-native regression file:

- path to be selected after inspecting the current upstream test convention; no target test path is claimed yet.

Excluded from the clean source branch:

- Fieldwork investigations, notes, receipts, and publishers;
- temporary workflows;
- Linux Fieldwork test modules;
- escalation research from issue #341 / PR #347.

## Publication checklist

- [ ] owned target fork admitted;
- [ ] branch `fix/coverage-backend-process-group-current-main` created from current exact upstream head;
- [ ] retained patch applied cleanly;
- [ ] target-native regression added;
- [ ] focused baseline/candidate execution recorded;
- [ ] ordinary project gates recorded;
- [ ] complete clean diff reviewed;
- [ ] duplicate search refreshed;
- [ ] project contribution and AI-disclosure policy checked;
- [ ] explicit public-contact authority granted.