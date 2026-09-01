# cmux: journal-hook timeout and concurrency ownership disappear on mux SIGKILL

## Target

- Upstream: `manaflow-ai/cmux`
- Audited revision: `eaa899cb20bd411019744fbd2bdedeb397f3070b`
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

## Patch direction

Treat hook process ownership as a durable handoff problem separate from delivery idempotency.

A replacement mux needs enough persisted, PID-reuse-safe evidence to identify and terminate or otherwise fence a still-live prior attempt before admitting a retry under the same hook's concurrency budget. The existing process-scope marker and exact process identity machinery are useful ingredients, but the current delivery row does not retain the information required for a replacement dispatcher to reconstruct that ownership.

This deserves a separate patch from terminal input acknowledgement: different owner, different persistence needs, and a larger lifecycle change.
