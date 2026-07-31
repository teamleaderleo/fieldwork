# F254-coverage-backend-process-group: cancellation must stop the complete selected backend

Finding state: `delivery-gate-ready`

Workstream: `G`  
Canonical Fieldwork issue: `#254`  
Canonical implementation: `teamleaderleo/linux-fieldwork#313`  
Exact implementation head: `e90fc438f530f7bd78ffd6fd1ba24c665bd96913`  
Imported source base: `782774b01002abf37878d834a54d0bbf8b226397`  
Imported `coverage.py` blob: `9a522484aef05deae514a98e4b6adf5feb6c886d`  
Imported `run_null.sh` blob: `e0a8c106f9d3d636baea286d2ab33834748dffc9`  
Exact target gate: Linux Fieldwork CI `30632491641`, job `91161937871`, success  
Exact technical review: `4828679890`, `ACCEPT` content disposition  
Current review disposition: `REVIEW READY — eligible non-author acceptance pending`  
Upstream contact authorized: `no`

## In simple words

`coverage.py` starts one backend wrapper for each selected test. That wrapper can own nested shells, pipelines, `tee`, a QEMU-style foreground operation, a log follower, or a privileged worker through sudo.

The earlier cancellation-status repair made parent-only SIGINT return 130, but it terminated only the immediate wrapper PID. The wrapper could finish or remain blocked while the real backend continued and performed later work.

The selected repair creates one caller-owned session/process group before the backend starts, signals that complete group, waits for the wrapper, and then returns 130.

## Selected mechanism

```python
proc = subprocess.Popen(argv, start_new_session=True)
...
try:
    os.killpg(proc.pid, signal.SIGTERM)
except ProcessLookupError:
    pass
proc.wait()
print("interrupted by SIGINT", file=sys.stderr)
raise SystemExit(130)
```

The caller selects the backend and therefore owns the safest stable place to create the operation identity. Descendant discovery is unnecessary while the backend tree remains in that group.

## Executed three-way distinction

Parent-only SIGINT to the Python coverage driver produced this exact distinction:

| Variant | Driver status | Live backend descendants | Later work |
| --- | ---: | ---: | --- |
| imported baseline | 0 after deliberate survivor release | yes before release | yes after release |
| merged status-only PR #204 | 130 after deliberate survivor release | yes before release | yes after release |
| group-owned candidate | 130 promptly | no | no |

Ordinary foreground-group Ctrl-C was already clean in the imported null topology. The retained defect is supervisor-targeted parent-only delivery.

## Backend boundaries executed

### Null backend

The exact `run_null.sh` topology includes nested shells, a pipeline, `tee`, a status reader, and the generated test. Immediate-wrapper TERM leaves work alive; owned-group TERM stops the complete selected operation.

### QEMU wrapper model

The exact `run_qemu.sh` wrapper includes a background output follower and a foreground `timeout --foreground debvm-run ...` operation. The focused model replaces only the expensive payload with a held disposable worker.

The baseline and status-only negative controls intentionally prove that the coverage driver remains blocked while the foreground operation survives. They release that operation only after observing the leak, then require final status 0 or 130 and later work. The group-owned candidate must return 130 without a release, with no surviving group and no later marker.

### Sudo model

The exact `run_null.sh SUDO` path executes with passwordless sudo when available. The negative control observes a UID-0 worker surviving wrapper-only termination while remaining inside the selected operation group. The candidate stops the wrapper, sudo monitor, and root worker together. The module skips only when `sudo -n true` is unavailable.

### Unsignaled success

Null, QEMU-wrapper, and sudo candidate runs remain successful without SIGINT and leave no live owned group.

### Terminal comparison

A new session retained inherited terminal file-descriptor input/output in the focused PTY comparison. No claim is made for `/dev/tty` or controlling-terminal behavior.

## Claim-scoped evidence

| Claim | Evidence class | Exact limit |
| --- | --- | --- |
| Baseline parent-only SIGINT can report success while backend work survives. | `target-executed` | disposable exact null/QEMU/sudo models on Linux CI 931 |
| Status-only PR #204 can report 130 while backend work survives. | `target-executed` | same exact models; survivors deliberately released after observation |
| Owned-group candidate returns 130 with no live in-group work or later work. | `target-executed` | descendants must remain in the selected group and respond to TERM |
| Ordinary foreground-group Ctrl-C is already clean. | `target-executed` | imported null shell topology |
| Nine-file repository carrier applies, compiles, and passes the full repository suite. | `target-executed` | Linux Fieldwork merge-ref CI 931; 359 tests |
| The candidate is ready for merge or public submission. | `not established` | final eligible non-author acceptance and separate authority remain pending |

## Exact execution receipt

Linux Fieldwork CI `30632491641`, job `91161937871`, executed PR #313 exact head `e90fc438f530f7bd78ffd6fd1ba24c665bd96913` on the current PR merge ref.

It passed:

1. changed retained-patch validation;
2. all three candidate hunks and the status-only comparison carrier;
3. Python compilation;
4. all 359 discovered repository unit tests;
5. null, QEMU-wrapper, and sudo baseline/status-only/candidate controls;
6. all unsignaled-success controls;
7. shell syntax and command-help checks.

The merge-ref execution also exercised the newer live-main CI workflow, unified-diff validator, and repository test inventory rather than assuming the eight post-branch main commits were irrelevant.

Technical complete-diff review `4828679890` found no remaining source-visible repair and classified the exact nine-file carrier `REVIEW READY`.

## Carrier repair history

Earlier failures are retained because they explain the final evidence boundary; none contradicted the selected product mechanism.

### CI 885 — historical status fixture policy

Run `30628112270` stopped while reapplying historical PR #204 under a newly strict zero-fuzz rule. The repair materialized the status-only comparison from pinned source without changing its behavior.

Evidence class: `fixture failure / no candidate lifecycle execution`.

### CI 906 — malformed candidate hunk counts

Run `30629817016`, job `91153313705`, ran 255 tests; 252 unrelated tests passed. All three new classes stopped in setup because the retained candidate hunk declared counts that did not match its body.

Evidence class: `patch-syntax failure / no candidate lifecycle execution`.

### CI 921 — stale noncontiguous context

Run `30631360431`, job `91158225453`, validated and compiled the candidate, then ran 299 tests. The 296 unrelated tests passed. The three new classes stopped because the patch retained `argv` context that was not contiguous with the process block.

Evidence class: `patch-context failure / no candidate lifecycle execution`.

### CI 927 — QEMU negative-control ordering

Run `30631985578`, job `91160290707`, validated both patches, compiled, and ran 359 tests. Every candidate positive/ordinary-success control passed. Only the QEMU baseline and status-only negative controls deadlocked because they waited for the coverage driver before releasing the foreground operation that the driver correctly awaited.

Evidence class: `candidate product evidence plus negative-control fixture-order failure`.

Head `e90fc438...` repaired only that test ordering. CI 931 then passed the complete suite.

## Alternatives

### Immediate-wrapper termination — rejected

It can stop the wrapper while nested backend work survives.

### Status-only repair — retained prerequisite, incomplete cleanup

It reports cancellation correctly without owning the complete operation.

### Wrapper-specific descendant discovery — rejected

It couples the caller to changing shell, pipeline, sudo, and QEMU implementation details.

### Same-session background group — rejected for terminal input

The PTY comparison stopped the background group under job-control rules.

### Dedicated session/process group — selected

It creates one caller-owned boundary before execution and retains inherited file-descriptor I/O in the focused model.

### Product TERM-to-KILL escalation — deferred

The executed descendants respond to TERM. Escalation is a separate policy decision requiring evidence of an uncooperative backend.

## Deferred and reopening edges

Reopen if evidence shows any of the following materially affects the selected contract:

- descendants call `setsid()` or otherwise escape the group;
- descendants ignore TERM indefinitely;
- a real QEMU/debvm topology differs from the disposable model;
- a remote or external supervisor owns descendants outside the local group;
- `/dev/tty` or controlling-terminal behavior is required;
- non-Linux process semantics need support;
- product TERM-to-KILL escalation becomes necessary.

## Exact next transition

1. obtain one eligible non-author complete-diff acceptance for Linux Fieldwork PR #313 at exact head `e90fc438...`;
2. if the head/base/nine-file fence moves, expire CI 931 review promotion and rerun/review the exact generation;
3. only after acceptance and separate internal merge authority may the implementation move to `land-ready`;
4. public upstream submission remains separately prohibited unless explicitly authorized.

No merge, release, deployment, credentials, private-data access, spending, or public upstream interaction is authorized.

## References

- `teamleaderleo/linux-fieldwork#306`
- `teamleaderleo/linux-fieldwork#204`
- `teamleaderleo/linux-fieldwork#313`
- `teamleaderleo/fieldwork#254`
