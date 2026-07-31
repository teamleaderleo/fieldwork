# F254-coverage-backend-process-group: cancellation must reach the selected backend group

Finding state: `delivery-gate-ready`

Workstream: `G`  
Canonical Fieldwork issue: `#254`  
Canonical implementation: `teamleaderleo/linux-fieldwork#313`  
Exact current implementation head: `dfc6d0503fb844f4c428ce16a567a9fdcd35280a`  
Exact executed mechanism head: `e90fc438f530f7bd78ffd6fd1ba24c665bd96913`  
Follow-up cleanup policy: `teamleaderleo/linux-fieldwork#341` / PR `#347` at `3f52a1411a892fa5eb4fff503b8042169a36274d`  
Imported source base: `782774b01002abf37878d834a54d0bbf8b226397`  
Imported `coverage.py` blob: `9a522484aef05deae514a98e4b6adf5feb6c886d`  
Imported `run_null.sh` blob: `e0a8c106f9d3d636baea286d2ab33834748dffc9`  
Exact mechanism gate: Linux Fieldwork CI `30632491641`, job `91161937871`, success  
Exact narrowed-head gate: Linux Fieldwork CI `30633602052` / 943, success  
Exact narrowed-head technical review: `4828885032`, content `ACCEPT`  
Current review disposition: `REVIEW READY — eligible non-author acceptance pending`  
Upstream contact authorized: `no`

## In simple words

`coverage.py` starts one backend wrapper for each selected test. That wrapper can own nested shells, pipelines, `tee`, a QEMU-style foreground operation, a log follower, or a privileged worker through sudo.

The earlier cancellation-status repair made parent-only SIGINT return 130, but it terminated only the immediate wrapper. Backend work could survive.

The selected repair creates one caller-owned session/process group before the backend starts, sends TERM to that group, waits for the wrapper, and returns 130.

This proves operation-wide TERM delivery. Complete quiescence is proven for the tested TERM-responsive null, QEMU-wrapper, and sudo topologies. It is not inferred for arbitrary descendants that ignore TERM, outlive the wrapper, or escape the group.

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

The caller selects the backend and owns the stable place to establish a dedicated signal boundary before backend code runs.

`proc.wait()` still waits only for the immediate wrapper. The no-survivor result comes from executable controls for responsive topologies, not from leader waiting alone.

## Executed three-way distinction

Parent-only SIGINT to the Python coverage driver produced:

| Variant | Final driver status | Backend state | Later work |
| --- | ---: | --- | --- |
| imported baseline | 0 after deliberate survivor release | live before release | yes |
| merged status-only PR #204 | 130 after deliberate survivor release | live before release | yes |
| group candidate | 130 | no live in-group work in tested topology | no |

For QEMU negative controls, the driver remains blocked while the foreground operation survives. The fixture records that state, releases the operation, and then observes final status. The candidate exits 130 without release because every modeled in-group process responds to TERM.

Ordinary foreground-group Ctrl-C was already clean in the imported null topology. The retained defect is supervisor-targeted parent-only delivery.

## Backend boundaries executed

### Null backend

The exact `run_null.sh` topology includes nested shells, a pipeline, `tee`, a status reader, and the generated test.

- baseline: status 0 after deliberate survivor release;
- status-only predecessor: status 130 after release;
- group candidate: status 130, no live pipeline, no later work;
- unsignaled candidate: success and clean group teardown.

### QEMU wrapper model

The exact `run_qemu.sh` wrapper includes a background output follower and a foreground `timeout --foreground debvm-run ...` operation. The model replaces only the expensive payload with a held disposable worker.

- baseline and status-only variants leave the foreground operation live and the driver blocked until release;
- the candidate delivers TERM to the modeled group and exits 130 with no live in-group member;
- the unsignaled candidate preserves guest-status success and clean teardown.

This proves group inheritance and responsive shutdown for the modeled operation. It does not execute real QEMU/debvm.

### Sudo model

The exact `run_null.sh SUDO` path executes with actual passwordless sudo when available. The controls require the wrapper, sudo command, and UID-0 worker to share the observed operation group.

- baseline and status-only variants retain privileged work until release;
- the candidate returns 130 with no live in-group privileged work;
- the unsignaled candidate succeeds and cleans the group;
- a hosted group escape fails the control.

The module skips only when `sudo -n true` is unavailable; CI 931 executed rather than skipped it.

## Claim-scoped evidence

| Claim | Evidence class | Exact limit |
| --- | --- | --- |
| Baseline parent-only SIGINT can report success while backend work survives. | `target-executed` | disposable exact null/QEMU/sudo models on CI 931 |
| Status-only PR #204 can report 130 while backend work survives. | `target-executed` | same models; survivors deliberately released after observation |
| Candidate sends TERM to one dedicated backend group. | `target-executed` | exact patch and Linux/POSIX group semantics |
| Candidate returns 130 with no live in-group work or later work. | `target-executed` | tested descendants remain in the group and respond to TERM |
| Arbitrary TERM-resistant/group-escaping descendants are fully drained. | `not established` | owned by #341 / comparison PR #347 |
| Nine-file repository carrier applies, compiles, and passes the full suite. | `target-executed` | mechanism CI 931; 359 tests; narrowed-head CI 943 |
| Candidate is ready for merge/public submission. | `not established` | eligible acceptance and separate authority remain pending |

## Exact execution receipt

Mechanism CI `30632491641`, job `91161937871`, executed head `e90fc438f530f7bd78ffd6fd1ba24c665bd96913` on the current PR merge ref.

It passed:

1. both retained patch carriers and all three candidate hunks;
2. Python compilation;
3. all 359 repository tests;
4. null baseline/status-only/candidate/foreground-group/unsignaled controls;
5. QEMU baseline/status-only/candidate/unsignaled controls;
6. sudo baseline/status-only/candidate/unsignaled controls;
7. shell syntax and command-help checks.

The later implementation commits changed only three evidence documents and the reusable process note. They narrowed the claim and linked follow-up #341. Current-head CI `30633602052` / 943 passed on exact head `dfc6d0503fb844f4c428ce16a567a9fdcd35280a`.

Complete current-head review `4828885032` found no remaining source-visible repair. Same-account review does not satisfy eligible independence.

## Carrier repair history

- CI 885: historical status fixture policy; no candidate lifecycle execution;
- CI 906: malformed candidate hunk counts; no candidate lifecycle execution;
- CI 921: stale noncontiguous patch context; no candidate lifecycle execution;
- CI 927: every candidate positive control passed; two QEMU negatives deadlocked because release occurred after waiting for the deliberately blocked driver;
- CI 931: repaired ordering and complete green repository gate.

None contradicted the selected group-delivery mechanism.

## Alternatives and separated policy

### Immediate-wrapper termination — rejected

It can stop the wrapper while nested backend work survives.

### Status-only repair — retained prerequisite, incomplete lifecycle control

It reports cancellation correctly without delivering cancellation to the complete selected group.

### Wrapper-specific descendant discovery — rejected

It couples the caller to changing shell, pipeline, sudo, and QEMU details.

### Dedicated session/process group — selected

It creates one caller-owned signal boundary before execution and retains inherited file-descriptor I/O in the focused model.

### TERM resistance, repeated SIGINT, diagnostics, and escalation — separate

Issue #341 / PR #347 proves that:

- the current policy can return 130 while a TERM-resistant descendant survives after wrapper exit;
- a second SIGINT can interrupt the cleanup wait and leave wrapper/descendant alive;
- ignoring later SIGINT alone can wait indefinitely;
- bounded diagnostics can return while survivors remain;
- bounded TERM-to-KILL is the only compared synthetic policy that drains the in-group topology, but it remains unselected without real-backend necessity and compatibility evidence;
- a descendant that calls `setsid()` remains outside the group boundary.

Those findings narrow this claim; they do not reopen the green responsive-topology result.

## Exact next transition

1. obtain one eligible non-author complete-diff acceptance for Linux PR #313 exact head `dfc6d050...`;
2. if the product patch, tests, or claim boundary moves, expire the corresponding receipt;
3. only separate internal merge authority may land the candidate;
4. retain #341/#347 as the reopening matrix unless real TERM-resistant backend evidence justifies a separate policy candidate;
5. public upstream submission remains prohibited unless explicitly authorized.

No merge, release, deployment, credentials, private-data access, spending, or public upstream interaction is authorized.

## References

- `teamleaderleo/linux-fieldwork#204`
- `teamleaderleo/linux-fieldwork#306`
- `teamleaderleo/linux-fieldwork#313`
- `teamleaderleo/linux-fieldwork#341`
- `teamleaderleo/linux-fieldwork#347`
- `teamleaderleo/fieldwork#254`