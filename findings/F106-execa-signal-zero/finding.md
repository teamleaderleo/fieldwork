# F106: Preserve signal zero when Execa kills descendants

Finding state: `closed`

Workstream: `B — Browser, web tooling, and runtime boundaries`  
Canonical Fieldwork issue: `#106`  
Canonical implementation: `teamleaderleo/execa#1`  
Exact implementation head: `dc73ffcd1765666f77fb39775af73abec08c5bb5`  
Exact base revision: `499fe800361e6b383b0085f635a69fd27e6cf447`  
Strongest evidence class: `target-executed` focused cross-platform matrix  
Current review disposition: `ACCEPT owned-fork implementation candidate; HOLD upstream promotion`  
Desk routing: `no active desk; retained closeout`  
Upstream contact authorized: `no`

## In simple words

Signal `0` asks, “Is this process alive?” It is supposed to check without killing anything.

Execa's descendant-kill option used a forceful Windows `taskkill` path for every signal. That could turn the harmless check into process-tree termination. The repair handles signal `0` before choosing either platform's descendant-termination adapter.

## Why we care

A liveness check must never become a kill request. Code that probes a process before deciding what to do could unexpectedly terminate the process and its children on Windows.

## What happens if we leave it alone

With `killDescendants: true`, `subprocess.kill(0)` can reach `taskkill /T /F` on Windows. The caller asks for a non-destructive existence check and receives destructive process-tree behavior.

## Current finding

Signal `0` should call the native direct-child `ChildProcess.kill(0)` check on every platform. Non-zero signals continue through the existing Unix process-group or Windows descendant-termination adapter.

## Historical precedent

### Execa Windows descendant termination

- Source: https://github.com/sindresorhus/execa/pull/1258
- Principle supported: Windows descendant termination deliberately uses `taskkill /T /F`, with fallback behavior when `taskkill` is unavailable or fails.
- Important difference: the precedent introduced the destructive tree-termination path and did not special-case the non-terminating signal `0`.

### Node.js child-process signal zero contract

- Source: https://nodejs.org/api/child_process.html#subprocesskillsignal
- Principle supported: signal `0` can test for process existence without sending a terminating signal.
- Important difference: Execa's descendant adapter adds process-tree semantics that Node's direct-child method does not own.

## Approaches considered

### Retained approach: shared dispatcher guard

The dispatcher sees the normalized signal before selecting a platform adapter. This makes the contract platform-independent and leaves all non-zero behavior unchanged.

### Declined: Windows-only special case inside `taskkill`

That would encode a general signal contract in one platform adapter and leave Unix process-group behavior dependent on platform-specific implementation.

### Declined: treat signal zero as descendant-group liveness

The library's native return value describes the direct child. Defining process-tree membership or descendant liveness would require a different public contract and platform model.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Windows adapter selection | Deterministic test | `taskkill` not called for signal `0` |
| Live parent and descendant | Process-tree test | Both remain alive after signal `0` |
| Delayed force kill | Timed control | `forceKillAfterDelay` does not terminate later |
| Ordinary non-zero kill | Existing and new tests | Tree still terminates |
| Ubuntu Node 22/24/26 | Fieldwork matrix `30491600304` | Passed |
| Hosted Windows Node 22/24/26 | Same matrix | Passed with real `taskkill.exe` path |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Asynchronous `taskkill` launch-error observability | Different failure-reporting question | New finding if evidence appears |
| Process-tree escape through new groups or sessions | Operating-system ownership limitation | Separate process-ownership campaign |
| PID reuse | Wider process identity problem | Separate safety finding |
| Windows job-object ownership | Larger architectural alternative | Design campaign if requested |
| Ordinary full repository gate at exact head | Focused matrix is retained evidence class | Required only before a landing/submission decision |

## Current disposition and desk routing

- Finding state: `closed`
- Review disposition: `ACCEPT owned-fork candidate; HOLD any upstream transition`
- Review Queue entry: none active
- Delivery lane: `not-entered`
- Exact next transition: none without a new user request to prepare landing or upstream submission
- Clearing condition: not applicable
- User decision requested: none

This is the example of a completed finding that does **not** belong on a decision desk. The technical question is settled inside the owned research scope. Only a new delivery or upstream request would reopen action.

## References

- https://github.com/teamleaderleo/fieldwork/issues/106
- https://github.com/teamleaderleo/execa/pull/1
- https://github.com/sindresorhus/execa/pull/1258
- https://nodejs.org/api/child_process.html#subprocesskillsignal
- Fieldwork workflow `30491600304`
