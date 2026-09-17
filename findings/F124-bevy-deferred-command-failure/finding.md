# Bevy executor-dependent deferred visibility after system failure

Finding ID: `F124-bevy-deferred-command-failure`  
State: `research-active / target-test-prepared`  
Owning issue: #124  
Stable source: Bevy `0.19.0` at `c6f634ca9f406d68ba5109d921247b654cb42c10`  
Development source: `25368b78ce5e9b15dc770cdf2af4595602cc8a7b`  
Upstream contact authorized: `false`

## In simple words

A system can queue a world change and then fail. Bevy runs queued changes later.

Current source predicts that the same failure can leave different world state depending on whether the schedule uses the single-threaded or multithreaded executor. With the default panic policy, the single-threaded executor unwinds before registering the failed system's queued changes, while the multithreaded executor registers and applies them before rethrowing.

## Why this is worth resolving

Executor selection is usually understood as an execution strategy. It should not silently become an application-level commit policy unless that difference is deliberate, documented, and testable.

For replay, recovery, editors, servers, and local-first applications, a receipt that says “the system failed” is incomplete when some queued changes may already be visible.

## Source evidence

### Single-threaded development executor

- runs the system without applying deferred buffers;
- sends returned errors and caught panics to the fallback handler;
- inserts the system into `unapplied_systems` only after the handler returns;
- therefore skips registration when the handler panics.

### Multithreaded development executor

- records completion separately from the system outcome;
- inserts every completed system into `unapplied_systems`;
- stores panic payloads independently;
- applies deferred buffers before rethrowing a stored panic.

### Default fallback handler

- defaults to severity-based handling;
- panic-severity errors and converted system panics invoke a handler that panics;
- the handler marks that panic as originating from error handling.

### Stable release

Bevy `0.19.0` already differs across executors for a system panic. Merged development PR `bevyengine/bevy#24240` routes panics through the fallback handler and makes continuation configurable, but its tests do not classify deferred command visibility.

## Source-predicted current-development behavior

| Outcome | Handler | Single | Multi |
| --- | --- | --- | --- |
| success | default | apply | apply |
| returned ignored error | default | apply | apply |
| panic | custom returning handler | apply | apply |
| returned panic-severity error | default panicking handler | discard before unwind | apply before unwind |
| panic | default panicking handler | discard before unwind | apply before unwind |

Evidence class: `source-read`. The matrix itself is `target-test-prepared` until native execution.

## Prepared evidence

Standalone crate:

`programmes/high-leverage-open-source/scouts/bevy-ecs-schedule-replay/probes/deferred-failure-visibility`

The crate runs all five outcomes against both built-in executors and asserts the source-predicted receipts against exact development source.

Local execution was blocked by worker-environment toolchain availability. No target result is claimed from that failure.

## Governing invariant under review

> Under one fallback-error policy, changing only the built-in schedule executor should not silently change whether deferred work from a failed producer becomes visible.

This invariant is provisional. Review may instead select and document executor-specific semantics, but the distinction must become explicit.

## Alternatives

1. **Always apply accepted deferred work.** Treat queuing as the commit boundary.
2. **Discard failed-producer deferred work.** Treat successful system completion as the commit boundary.
3. **Make failure disposition explicit.** Let error handling select apply or discard.

No repair alternative is selected before target execution and compatibility review.

## Main criticism

Bevy commands are deliberately deferred and are not documented as transactions. A system may queue cleanup, telemetry, or error-state publication before returning an error. Discarding all failed-producer buffers could be more surprising than applying them.

That criticism argues against assuming rollback. It does not justify executor-dependent results under the same policy.

## Edge cases still open

- a command itself panics while a buffer is being applied;
- multiple commands where one application fails;
- custom `Deferred` system parameters;
- an explicit `ApplyDeferred` node before a later failure;
- exclusive systems;
- handler changes during a schedule run;
- `no_std`, where panic-to-error conversion differs;
- successful unrelated systems whose buffers share one application boundary.

## Decision requested

Execute the prepared exact-source matrix and choose one:

- `ACCEPT CURRENT SEMANTICS AND DOCUMENT`;
- `REQUIRE EXECUTOR PARITY — ALWAYS APPLY`;
- `REQUIRE EXECUTOR PARITY — DISCARD FAILED PRODUCER`;
- `DESIGN EXPLICIT FAILURE DISPOSITION`;
- `STOP — PROBE OR SOURCE PREMISE INVALID`.

## Reopening and supersession

Any new source head, merged executor rewrite, explicit deferred-failure contract, or contradictory native result expires this finding's current disposition.
