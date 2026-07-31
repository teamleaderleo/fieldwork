# F254-coverage-backend-process-group: cancellation must stop the complete selected backend

Finding state: `delivery-gate-ready`

Workstream: `G`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-coverage-backend-process-group/finding.md`  
Canonical implementation: `teamleaderleo/linux-fieldwork#313`  
Exact implementation head: `b3636990b6c71a239095aa5868ac64a888ad748e`  
Exact base or source revision: Linux Fieldwork main `782774b01002abf37878d834a54d0bbf8b226397`; imported `coverage.py` blob `9a522484aef05deae514a98e4b6adf5feb6c886d`; imported `run_null.sh` blob `e0a8c106f9d3d636baea286d2ab33834748dffc9`  
Strongest evidence class: process-lifecycle claims `model-executed`; complete multi-backend repository gate `target-test-prepared`  
Reviewed input generation: current Fieldwork/Linux protocols; Linux issue #306; merged status-only PR #204; PR #313 review `4828175488`  
Current review disposition: `EXECUTE`  
Desk routing: Delivery Desk #160 D2  
Upstream contact authorized: `no`

## In simple words

`coverage.py` starts one backend wrapper for each selected test. That wrapper may start several more processes: nested shells, pipelines, `tee`, a root command through sudo, a background log follower, or a QEMU-like foreground operation.

The earlier cancellation repair made parent-only SIGINT return 130. It still terminated only the immediate wrapper PID. The wrapper could exit while the real backend work continued.

The selected repair gives each backend invocation one dedicated session/process group and terminates that complete owned group before the coverage driver returns 130.

## Why we care

A supervisor can report cancellation while descendants continue to:

- modify shared files;
- run privileged commands;
- hold pipes or locks;
- write output after the caller moved on;
- interfere with the next test;
- become reparented and disappear from the original wait path.

Correct parent status and complete operation cleanup are separate correctness requirements.

## What happens if we leave it alone

The imported driver uses:

```python
proc = subprocess.Popen(argv)
try:
    proc.wait()
except KeyboardInterrupt:
    proc.terminate()
    proc.wait()
    break
```

The merged status-only repair replaces `break` with a diagnostic and `SystemExit(130)`. It keeps the same immediate-child `terminate()` call.

The exact null backend contains nested pipelines around:

```sh
env --chdir=./shared ... sh -x ./test.sh 2>&1 | tee shared/output.txt
```

Parent-PID-only SIGINT can therefore terminate the wrapper and leave the nested operation alive.

## Exact topology distinction

### Ordinary foreground-group Ctrl-C

The imported null topology is already clean when SIGINT reaches the whole foreground process group:

```text
wrapper status: -2
live group members after cancellation: 0
later-work marker: absent
```

The finding is not a general claim that interactive Ctrl-C leaks.

### Parent-PID-only SIGINT

When SIGINT targets only the Python coverage driver:

1. Python catches `KeyboardInterrupt`;
2. it sends TERM only to the wrapper PID;
3. it waits only that wrapper;
4. nested backend processes remain alive.

Reproduced results:

| Variant | Driver status | Live backend work | Later work |
| --- | ---: | ---: | --- |
| imported baseline | 0 | yes | yes after release |
| merged status-only PR #204 | 130 | yes | yes after release |
| process-group candidate | 130 | no | no |

The status-only repair is necessary but incomplete.

## Current finding

The coverage caller chooses the backend and must own one operation-wide identity.

The retained mechanism is:

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

The dedicated session makes the process group safe to signal. The caller does not need backend-specific process-tree discovery while descendants remain in that group.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Imported parent-only SIGINT can return 0 while backend work survives. | `model-executed` | exact null negative control | Supervisor-targeted delivery |
| Status-only PR #204 returns 130 while the same backend survives. | `model-executed` | exact patch comparison | Exact imported wrappers |
| Ordinary foreground-group Ctrl-C already stops the null backend. | `model-executed` | foreground-group control | One Linux shell topology |
| Group-owned candidate returns 130 with no live in-group work. | `model-executed` | null, QEMU-wrapper, and sudo matrices | Descendants must remain in group |
| Passwordless sudo root worker stays in the owned group in tested configuration. | `model-executed` | actual sudo/UID-0 matrix | Hosted/local sudoers may differ |
| New-session child retains inherited terminal fd input/output. | `model-executed` | PTY comparison | No controlling-tty `/dev/tty` claim |
| PR #313 is one commit and eight files over current main. | `source-read` | PR metadata and review `4828175488` | Exact generation |
| Exact multi-backend repository gate is prepared. | `target-test-prepared` | CI `30628112270` / 885 | Queued at this revision |

## Backend ownership map

### Null backend

Exact `run_null.sh` owns:

- wrapper shell;
- nested pipeline shells;
- `tee`;
- status-reader shell;
- generated `test.sh`.

Immediate-wrapper TERM leaves that pipeline alive. Group TERM stops it.

### QEMU wrapper

Exact `run_qemu.sh` owns:

- wrapper shell;
- background output follower;
- foreground `timeout --foreground debvm-run ...` operation;
- wrapper cleanup and guest-result interpretation.

The focused model replaces only the expensive foreground payload with a held disposable worker. Baseline/status-only leave it alive; group ownership stops it.

### Sudo backend

`Needs-Root: true` selects exact `run_null.sh SUDO` with:

```sh
sudo --preserve-env sh -x ./test.sh
```

The retained local negative control used actual passwordless Sudo 1.9.16p2 with `use_pty`:

- seven live members shared the operation group;
- the generated test ran as UID 0;
- killing only the wrapper left six members alive and reparented;
- releasing the FIFO allowed the root test to perform later work.

The repository module runs only when `sudo -n true` succeeds. It requires the wrapper, sudo command, and root worker to share the observed group. A group escape is a test failure, not a silent assumption.

## Alternatives and what made them lose

### Immediate-wrapper termination — rejected

The wrapper exits while nested backend work survives.

### Status-only repair — retained as prerequisite, rejected as complete answer

It reports 130 but does not own the operation.

### Teach each wrapper to discover descendants — rejected

It couples the caller to changing backend-specific shell, pipeline, sudo, and QEMU topologies.

### Same-session background process group — rejected for terminal input

A pseudo-terminal comparison found that a same-session background group stopped on input under job-control rules.

### Dedicated session/process group — selected

It creates one safe caller-owned operation boundary before the child executable runs. In the PTY model, inherited terminal file-descriptor input/output remained usable, though the child had no controlling-terminal association.

### Product TERM-to-KILL escalation — deferred

The proven descendants respond to TERM. Escalation changes policy and is not needed for this bounded repair. Fixture teardown may escalate only to prevent test leakage after an assertion failure.

## Edge cases covered

| Case | Evidence | Result |
| --- | --- | --- |
| Null baseline parent-only SIGINT | exact wrapper model | driver 0, live pipeline, later work |
| Null status-only repair | exact wrapper model | driver 130, live pipeline, later work |
| Null group candidate | exact wrapper model | driver 130, no live backend, no later work |
| Foreground-group SIGINT | exact null control | already clean |
| QEMU-wrapper baseline/status/candidate | exact wrapper plus held foreground payload | same three-way distinction |
| Sudo baseline/status/candidate | actual passwordless sudo and UID-0 test | same three-way distinction |
| Unsignaled null/QEMU/sudo candidate | focused modules | normal success and no live group |
| Process accounting | Linux `/proc` | live-versus-zombie distinction |
| Patch application and source | focused modules | zero fuzz and Python compilation |
| Failure cleanup | test teardown | registered driver/group cleanup; fixture-only escalation |

## Edge cases deferred or outside scope

| Edge case | Why outside scope | Reopening trigger |
| --- | --- | --- |
| Descendant calls `setsid()` or creates another group | escapes selected boundary | observed surviving work |
| TERM-ignoring descendant | can block product wait | concrete uncooperative backend |
| Real QEMU/debvm execution | expensive integration | contradictory wrapper model or delivery need |
| Remote or privileged external supervisor | not in local group | backend delegation evidence |
| `/dev/tty`-specific debug behavior | new session lacks controlling tty | interactive debug regression |
| TERM-to-KILL product escalation | separate policy | cancellation timeout evidence |
| Non-Linux process semantics | `/proc` and POSIX group contract | platform expansion |

## Exact execution and receipts

| Repository/head | Gate | Result | Evidence class |
| --- | --- | --- | --- |
| local exact null topology | baseline/status/group/foreground/success | distinguished as expected | `model-executed` |
| local exact QEMU wrapper model | baseline/status/group/success | distinguished as expected | `model-executed` |
| local actual sudo topology | wrapper-only negative control | UID-0 worker survived and continued | `model-executed` |
| local PTY comparison | new session vs same-session group | inherited fd I/O retained only in selected form | `model-executed` |
| PR #313 `b3636990…` | complete review `4828175488` | no source-visible repair | `source-read` |
| same head | Linux CI `30628112270` / 885 | queued | `target-test-prepared` |

## Complete-diff and compatibility review

- Direct relation: one commit ahead of current Linux main, zero behind at generation time.
- File fence: product patch, three investigation records, reusable note, null/QEMU/sudo executable modules.
- Imported product source is not edited directly; the patch is retained as candidate material.
- Compatibility surfaces reviewed: status versus lifecycle, group identity, foreground group, sudo monitor/PTY, inherited terminal fd I/O, live/zombie accounting, ordinary success.
- Unchanged: backend command selection, ordinary result handling, real QEMU command, sudo policy, product escalation.

## Current disposition and desk routing

- Finding state: `delivery-gate-ready`
- Review disposition: `EXECUTE`
- Delivery lane: `D2`
- Exact next transition: classify CI `30628112270`; if green and unchanged, mark Linux PR #313 `land-ready`
- Clearing condition: null/QEMU/sudo matrices, zero-fuzz patching, compilation, repository discovery, unchanged eight-file fence
- User decision requested: none

## Changes to the canonical conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-31 | merged PR #204 | corrected parent cancellation status to 130 for one immediate-worker model |
| 2026-07-31 | Linux #306 null topology | proved status-only repair leaves nested pipeline alive |
| 2026-07-31 | foreground-group control | narrowed defect to parent-PID-only supervisor delivery |
| 2026-07-31 | QEMU wrapper model | proved caller group contains wrapper, background follower, and foreground operation |
| 2026-07-31 | sudo model | proved privileged root pipeline also survives wrapper-only cancellation and remains in selected group |
| 2026-07-31 | PR #313 | materialized one current-main eight-file multi-backend carrier |

## References

- https://github.com/teamleaderleo/linux-fieldwork/issues/306
- https://github.com/teamleaderleo/linux-fieldwork/pull/204
- https://github.com/teamleaderleo/linux-fieldwork/pull/313
- https://github.com/teamleaderleo/fieldwork/issues/254
