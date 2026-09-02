# cmux: journal-hook timeout and concurrency ownership disappear on mux SIGKILL

## In simple words

cmux can start a hook with a one-second timeout and a one-at-a-time concurrency limit, then lose the only live owner of those limits if the mux process is killed hard. The already-started hook can keep running, and the replacement mux can start the retry because the durable delivery row says the prior attempt was interrupted but does not contain enough process identity to reclaim it.

This is separate from the documented at-least-once hook contract. Retrying an interrupted delivery is intentional; losing the configured lifetime and concurrency fence for the previous process is the narrower ownership problem.

The latest source check keeps this finding live at mechanism scope. Current upstream strengthened Unix hook containment so descendants cannot escape the assigned process group as easily, but the process-scope marker, exact root identity, tracker registration, and timeout enforcement still live inside the mux process. A current-head SIGKILL execution probe remains the next gate before implementation.

## Target

- Upstream: `manaflow-ai/cmux`
- Audited revision: `eaa899cb20bd411019744fbd2bdedeb397f3070b`
- Current source revalidation: `9e2dd50957936153ca0da61d2f079937674f9375`
- Audit date: 2026-09-01

## Finding

The journal-hook delivery contract intentionally provides exactly-once scheduling and at-least-once external process execution. The scheduling identity is `(hook_id, manifest_version, event_id)`, and the hook receives that stable identity for downstream deduplication.

The separate failure is process lifetime ownership: hook timeout and `max_parallel` enforcement live only in the mux process. A hard mux crash can leave an already-started hook child alive beyond its configured timeout while a replacement mux starts a retry for the same durable delivery.

## Deterministic reproduction

Manifest configuration:

```json
{
  "exec": {
    "timeout_ms": 1000,
    "max_parallel": 1
  }
}
```

The hook executable stayed alive indefinitely and recorded its PID plus the supplied cmux delivery identity.

Sequence:

1. Schedule one source event.
2. Wait for hook attempt 1 to start.
3. `SIGKILL` the mux.
4. Observe attempt 1 survive and become reparented.
5. Wait beyond twice the configured 1000 ms timeout; attempt 1 is still alive.
6. Restart the same session.
7. Replacement dispatcher sees the durable row in `executing` and starts attempt 2.
8. Attempt 1 and attempt 2 are simultaneously live although the manifest says `max_parallel: 1`.
9. Attempt 2 obeys its own timeout; the orphaned attempt 1 continues until explicit external cleanup.

Both attempts carried the same stable correlation/delivery identity, as expected for at-least-once process execution.

## Why this is distinct from duplicate delivery

Duplicate process execution after a crash is part of the documented contract. The external sink is expected to use the stable delivery identity when it needs exactly-once downstream effects.

The ownership defect is narrower:

- `timeout_ms` ceases to bound the lifetime of the already-started process after mux death;
- `max_parallel` is recomputed from replacement-process in-memory state and does not count the surviving orphan;
- therefore the configured execution budget can be violated even when downstream effects are perfectly idempotent.

## Source boundary

The dispatcher persists delivery state as `scheduled` / `executing` / completed outcomes. A replacement dispatcher intentionally includes `executing` rows in pending work so interrupted attempts can be retried.

Each live worker owns a `UnixProcessScope`. On normal timeout or daemon shutdown that scope kills the hook process group and tracked descendants. The scope's authoritative process identity, marker, deadline, and tracker registration are process-memory state. `SIGKILL` removes the mux before its drop/shutdown path can terminate the owned hook tree.

### Current-head revalidation

At `9e2dd50957936153ca0da61d2f079937674f9375`, `journal_hooks.rs` still prepares, configures, binds, terminates, and drops `UnixProcessScope` entirely inside the live delivery worker. Shutdown still documents that `executing` rows remain durable for replacement retry.

`unix_process_scope.rs` has since gained stronger Linux process-group fencing and more robust exact descendant tracking. Those changes reduce escape from an owned scope while its daemon is alive. They do not persist the scope marker, root `ProcessIdentity`, tracker registration, or deadline into the journal delivery row, and they do not create an external owner that survives mux `SIGKILL`.

So the adjacent implementation changed in a useful way without resolving the crash-handoff question. The original runtime result is retained as audited-revision evidence; current-head implementation work waits on a fresh SIGKILL discriminator.

## Patch direction

Treat hook process ownership as a durable handoff problem separate from delivery idempotency.

A replacement mux needs enough persisted, PID-reuse-safe evidence to identify and terminate or otherwise fence a still-live prior attempt before admitting a retry under the same hook's concurrency budget. The existing process-scope marker and exact process identity machinery are useful ingredients, but the current delivery row does not retain the information required for a replacement dispatcher to reconstruct that ownership.

This deserves a separate patch from terminal input acknowledgement: different owner, different persistence needs, and a larger lifecycle change.

## Status

**CURRENT-HEAD REGRESSION REQUIRED BEFORE PATCH.** The audited runtime failure remains established at `eaa899cb…`; current source still has the same ownership boundary, with stronger containment. No hook lifecycle code has been changed on the fork in this lane yet.

Third-party upstream remains read-only.
