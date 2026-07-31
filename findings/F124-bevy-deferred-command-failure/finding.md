# Bevy executor-dependent deferred visibility after system failure

Finding ID: `F124-bevy-deferred-command-failure`  
Finding state: `comparative-evaluation-active`  
Strongest evidence class: `source-read`; exact native matrix is `target-test-prepared`  
Owning issue: #124  
Stable source: Bevy `0.19.0` at `c6f634ca9f406d68ba5109d921247b654cb42c10`  
Development source: `25368b78ce5e9b15dc770cdf2af4595602cc8a7b`  
Upstream contact authorized: `false`

## In simple words

A system can queue a world change and then fail. Bevy applies queued changes later.

Current source predicts that the same failure can leave different world state depending on whether the schedule uses the single-threaded or multithreaded executor. With the default panic policy, the single-threaded executor unwinds before registering the failed system's queued changes, while the multithreaded executor registers and applies them before rethrowing.

The first bounded question is whether exact native execution confirms that source prediction. If it does, a second technical comparison must select and validate the narrowest compatible contract. That comparison remains autonomous; it is not a user-choice menu.

## Why this is worth resolving

Executor selection is normally an execution strategy. It should not silently become an application-level commit policy unless that difference is deliberate, documented, and testable.

For replay, recovery, editors, servers, and local-first applications, a receipt saying “the system failed” is incomplete when queued changes may already be visible.

## Source evidence

### Single-threaded development executor

- runs the system without applying deferred buffers;
- sends returned errors and caught panics to the fallback handler;
- inserts the system into `unapplied_systems` only after the handler returns;
- skips registration when the handler panics.

### Multithreaded development executor

- records completion separately from system outcome;
- inserts every completed system into `unapplied_systems`;
- stores panic payloads separately;
- applies deferred buffers before rethrowing a stored panic.

### Default fallback handler

- defaults to severity-based handling;
- panic-severity errors and converted system panics invoke a panicking handler;
- the handler marks that panic as originating from error handling.

### Stable release and merged development change

Bevy `0.19.0` already differs across executors for a system panic. Merged development PR `bevyengine/bevy#24240` routes panics through the fallback handler and makes continuation configurable, but its tests do not classify deferred command visibility.

## Source-predicted development behavior

| Outcome | Handler | Single | Multi |
| --- | --- | --- | --- |
| success | default | apply | apply |
| returned ignored error | default | apply | apply |
| panic | custom returning handler | apply | apply |
| returned panic-severity error | default panicking handler | discard before unwind | apply before unwind |
| panic | default panicking handler | discard before unwind | apply before unwind |

This table is `source-read`. The exact matrix remains `target-test-prepared` until native execution.

## Prepared characterization

Standalone crate:

`programmes/high-leverage-open-source/scouts/bevy-ecs-schedule-replay/probes/deferred-failure-visibility`

The crate runs all five outcomes against both built-in executors and asserts the source-predicted receipts against exact development source.

Local execution was blocked by worker-environment toolchain availability. That is environment evidence only and carries no Bevy result.

## Governing questions and invariants

### Characterization question

Under the same system outcome and fallback handler, does executor selection change whether commands queued before failure become visible?

### Compatibility invariant under comparison

Under one fallback-error policy, changing only the built-in executor should not silently change deferred visibility unless executor-specific commit semantics are an intentional, documented public contract.

This invariant is provisional. Source history, existing APIs, and target execution may instead support explicit executor-specific semantics, but the distinction must be intentional and observable.

## Decision criteria

Apply these criteria before selecting a repair:

1. identical or explicitly documented visibility under both built-in executors;
2. clear behavior for returned error, system panic, handler panic, and deferred-command panic;
3. compatibility with existing `Commands` and custom `Deferred` users;
4. no loss of unrelated successful systems' buffers;
5. truthful diagnostics and replay receipts;
6. predictable behavior at explicit `ApplyDeferred` boundaries;
7. bounded implementation and test surface;
8. `std` and `no_std` differences stated explicitly;
9. reversibility and migration cost;
10. consistency with Bevy's existing error-handler and schedule architecture.

## Alternatives under autonomous comparison

### A — retain executor-specific semantics and document them

Treat executor choice as part of the deferred visibility contract. This has the smallest source change but the highest semantic surprise and documentation burden.

### B — always apply accepted deferred work

Treat successful queuing as the commit boundary. This matches current returning-handler behavior and the multithreaded panic path. It requires the single-threaded executor to retain buffers before invoking a potentially panicking handler.

### C — discard failed-producer deferred work

Treat successful system completion as the commit boundary. This provides transaction-like parity but may discard intentionally queued cleanup, telemetry, or failure-state publication. It requires retaining outcome in completion state and clearing only failed-producer buffers.

### D — make failure disposition explicit

Let error handling choose apply or discard. This is expressive and potentially most compatible, but it widens API and ownership authority and may require a larger design process.

### E — stop with a retained negative result

Use only if native execution disproves the source prediction or the premise is superseded by current source.

## Discriminating work

1. execute the exact native five-by-two matrix;
2. classify any mismatch as probe defect, source drift, or real behavior;
3. inspect first-party command/error tests and history for implicit apply/discard guarantees;
4. locate representative callers that queue cleanup or error-state commands before failure;
5. instantiate minimal source/test sketches for B and C if the divergence executes;
6. analyze D as a paper/API alternative unless a bounded prototype adds evidence;
7. compare all viable options under the criteria above;
8. seek adversarial review identifying compatibility counterexamples and a reversing test;
9. select a provisional winner and retain losing reasons and reopening triggers.

## Main criticism

Bevy commands are deliberately deferred and are not documented as transactions. A system may queue cleanup, telemetry, or error-state publication before returning an error. Discarding all failed-producer buffers could be more surprising than applying them.

That criticism defeats an automatic rollback assumption. It does not justify accidental executor-dependent results under the same policy.

A separate criticism applies to always-apply: a failed producer may have queued state that assumes later code completed successfully. Applying it can publish partial work. Representative caller and boundary research must distinguish these risks.

## Edge cases still open

- a command itself panics while a buffer is being applied;
- multiple commands where one application fails;
- custom `Deferred` system parameters;
- explicit `ApplyDeferred` before a later failure;
- exclusive systems;
- handler changes during a schedule run;
- `no_std` panic-to-error differences;
- successful unrelated systems sharing one application boundary.

## Current disposition

- Finding state: `comparative-evaluation-active`
- Review disposition: `EXECUTE`
- Exact next transition: run the prepared native matrix, retain exact receipts, then continue the compatibility and candidate comparison above without waiting for user preference.
- Characterization stop: if the matrix disproves the source prediction after probe review, retain the negative result and stop or narrow the finding.
- Selection stop: when one option wins under the recorded criteria or a genuinely non-delegable authority/value boundary is identified.
- Non-delegable human decision: none currently identified.

## Reopening and supersession

A new source head, executor rewrite, explicit deferred-failure contract, contradictory native result, or representative compatibility evidence can reopen or supersede the current comparison.
