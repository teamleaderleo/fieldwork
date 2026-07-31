# F254-coverage-backend-process-group: cancellation must stop the complete selected backend

Finding state: `research-active`

Workstream: `G`  
Canonical Fieldwork issue: `#254`  
Canonical implementation: `teamleaderleo/linux-fieldwork#313`  
Exact implementation head: `02a55ca1bbb677fa8fa49cf0738e87369121a75b`  
Exact implementation base: `782774b01002abf37878d834a54d0bbf8b226397`  
Imported `coverage.py` blob: `9a522484aef05deae514a98e4b6adf5feb6c886d`  
Imported `run_null.sh` blob: `e0a8c106f9d3d636baea286d2ab33834748dffc9`  
Strongest evidence class: lifecycle distinction `model-executed`; complete repository candidate `target-test-active`  
Current review disposition: `EXECUTE REPAIR`  
Current target gate: Linux Fieldwork CI `30631360431` / 921, in progress  
Upstream contact authorized: `no`

## In simple words

`coverage.py` starts a backend wrapper for each selected test. That wrapper can own more processes: nested shells, pipelines, `tee`, a QEMU-style foreground operation, a log follower, or a privileged worker through sudo.

The earlier status repair made parent-only SIGINT return 130. It still terminated only the immediate wrapper. The wrapper could exit while the real backend continued and performed later work.

The selected mechanism starts each backend in its own session/process group, sends TERM to that owned group, waits for the wrapper, and then returns 130.

## Current conclusion

Correct cancellation status and complete operation cleanup are separate invariants.

The caller chooses the backend and should create one operation-wide identity before the child executable runs:

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

This avoids backend-specific descendant discovery while descendants remain in the selected group.

## Three-way lifecycle distinction

Parent-only SIGINT to the Python coverage driver produced the following retained model result:

| Variant | Driver status | Live backend work | Later work |
| --- | ---: | ---: | --- |
| imported baseline | 0 | yes | yes after release |
| merged status-only PR #204 | 130 | yes | yes after release |
| process-group candidate | 130 | no | no |

Ordinary foreground-group Ctrl-C was already clean in the exact null topology. The defect is specifically supervisor-targeted parent-only delivery.

## Backend boundaries covered

### Null backend

The exact `run_null.sh` topology includes nested shells, a pipeline, `tee`, a status reader, and the generated test. Immediate-wrapper TERM leaves work alive; owned-group TERM stops it.

### QEMU wrapper model

The exact wrapper includes a background output follower and a foreground `timeout --foreground debvm-run ...` operation. The focused model replaces only the expensive payload with a held disposable worker.

### Sudo model

The exact `run_null.sh SUDO` path was modeled with passwordless sudo when available. The retained negative control observed a UID-0 worker surviving wrapper-only termination while remaining in the selected operation group.

### Terminal comparison

A new session retained inherited terminal file-descriptor input/output in the focused PTY comparison. No claim is made for `/dev/tty` or controlling-terminal behavior.

## Evidence classes

| Claim | Evidence class | Limit |
| --- | --- | --- |
| Baseline parent-only SIGINT can return 0 while backend work survives. | `model-executed` | exact disposable null topology |
| Status-only PR #204 can return 130 while backend work survives. | `model-executed` | exact imported wrapper model |
| Ordinary foreground-group Ctrl-C is already clean. | `model-executed` | one Linux shell topology |
| Owned-group candidate returns 130 with no live in-group work in focused null/QEMU/sudo models. | `model-executed` | descendants must remain in the group |
| Current nine-file repository carrier applies, compiles, and passes every lifecycle control. | `target-test-active` | CI 921 has not settled |

## Current implementation packet

Linux Fieldwork PR #313 currently contains nine files:

- a test-only status-materialization patch;
- the process-group candidate patch;
- canonical null/QEMU/sudo evidence records;
- a reusable caller-ownership note;
- three executable lifecycle modules.

The product-source change remains a retained patch rather than a direct edit to imported source.

## Failed target generations

### CI 885 — historical status patch application

Run `30628112270` failed before lifecycle assertions. The three new modules reapplied historical PR #204 under a newly strict zero-fuzz rule. The existing historical test still passed under its original policy.

The repair retained PR #204 unchanged and materialized the status-only comparison from the pinned source.

Evidence class: `fixture-failure / no product execution`.

### CI 906 — malformed candidate patch header

Run `30629817016`, job `91153313705`, ran 255 tests. The unrelated 252 tests passed; all three new process-group classes errored in `setUpClass` before lifecycle assertions.

The shared candidate patch declared a second hunk as 12 old lines and 17 new lines while its body contained 10 old and 14 new lines. `patch` rejected it as malformed at line 29.

Head `02a55ca...` changes only that header to:

```diff
@@ -411,10 +412,14 @@ def main():
```

The target source, mechanism, fixtures, and expected lifecycle outcomes are unchanged.

Evidence class: `patch-syntax failure / no product execution`.

## Current execution gate

Linux Fieldwork CI `30631360431` / 921 is running on exact head `02a55ca...`.

Promotion requires the unchanged head to prove all of the following:

1. the candidate patch applies with zero fuzz and compiles;
2. the baseline and status-only negative controls retain live descendants and later work;
3. the group-owned null candidate returns 130 with no live backend and no later work;
4. the QEMU-wrapper model preserves the same three-way distinction;
5. the sudo model either passes with actual passwordless sudo or skips only for unavailable `sudo -n true`;
6. unsignaled candidate runs remain successful and leave no live group;
7. repository-wide tests remain green.

Until that gate passes, the implementation is neither `delivery-gate-ready` nor `land-ready`.

## Alternatives

### Immediate-wrapper termination — rejected

It can stop the wrapper while nested work survives.

### Status-only repair — retained as prerequisite, incomplete as cleanup

It reports cancellation correctly without owning the complete operation.

### Wrapper-specific descendant discovery — rejected

It couples the caller to changing shell, pipeline, sudo, and QEMU topologies.

### Same-session background group — rejected for terminal input

The PTY comparison stopped the background group under job-control rules.

### Dedicated session/process group — selected

It creates one safe caller-owned boundary before execution and retains inherited file-descriptor I/O in the focused model.

### Product TERM-to-KILL escalation — deferred

The proven descendants respond to TERM. Escalation is a separate policy decision and requires evidence of an uncooperative backend.

## Deferred edges

- descendants that call `setsid()` or otherwise escape the group;
- TERM-ignoring descendants;
- real QEMU/debvm execution;
- remote or external supervisors;
- `/dev/tty`-dependent behavior;
- non-Linux process semantics;
- product TERM-to-KILL escalation.

## Exact next transition

Inspect CI 921 on exact head `02a55ca...`.

- If the null/QEMU/sudo lifecycle controls execute and pass, complete-diff review the nine-file carrier and move the finding to `delivery-gate-ready`.
- If a fixture fails before lifecycle assertions, repair the fixture and keep the finding `research-active`.
- If the product mechanism fails, retain the contradiction and reopen the ownership model.

No merge, release, deployment, credentials, private-data access, spending, or public upstream interaction is authorized.

## References

- `teamleaderleo/linux-fieldwork#306`
- `teamleaderleo/linux-fieldwork#204`
- `teamleaderleo/linux-fieldwork#313`
- `teamleaderleo/fieldwork#254`
