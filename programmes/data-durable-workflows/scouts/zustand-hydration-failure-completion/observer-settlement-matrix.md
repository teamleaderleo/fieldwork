# Zustand hydration and observer settlement matrix

## In simple words

Zustand hydration has two jobs that currently run through one promise chain:

1. load and apply saved state;
2. tell user callbacks and listeners what happened.

Those jobs can fail independently. A storage read can fail before state changes, but a listener can also throw after state has already loaded successfully. The first owned repair made both kinds of failure reject the same `rehydrate()` promise. That can report hydration failure after hydration actually succeeded or let a callback error replace the real storage error.

This note separates the two settlements before another implementation is selected.

## Exact reviewed surface

- Released source base: `beca84e600e4e250f6b244d22878e72948f331c7`.
- Owned experiment: `teamleaderleo/zustand#1`.
- Reviewed owned head: `eca1824563646f253975b1d49420c1dd79d26b9d`.
- Work class: upstream-fork research.
- Current disposition: `HOLD` implementation acceptance.
- Upstream contact authorized: `false`.

## Two different owners

### Hydration-source settlement

This includes work required to obtain and apply persisted state:

- storage `getItem`;
- JSON parsing;
- migration;
- merge;
- applying the merged state;
- required persistence after migration.

A failure here means the requested hydration operation did not complete normally.

### Observer-delivery settlement

This includes user code called to observe the operation:

- the function returned by `onRehydrateStorage`;
- `onFinishHydration` listeners;
- any later diagnostic or telemetry hook.

A failure here does not necessarily mean hydration failed. State may already be committed and `hasHydrated` may already be true.

## Required cases

| Case | Hydration source | State committed | Success flag | Observer result | Question the contract must answer |
| --- | --- | --- | --- | --- | --- |
| storage read rejects | failed | no | false | error callback may run | Should explicit `rehydrate()` reject with the storage error? |
| JSON parse throws | failed | no | false | error callback may run | Same as storage failure, but synchronous thenable handling must settle correctly. |
| migration rejects | failed | no | false | error callback may run | Preserve the asynchronous migration error. |
| merge throws | failed | no | false | error callback may run | Preserve the merge error. |
| migrated state applies, required write fails | failed after state application | yes | currently false | error callback may run | Is this a failed hydration, a committed-but-unpersisted state, or a separate partial outcome? |
| success callback throws before success flag | source succeeded | yes | currently false | success observer failed | Must not silently reclassify the source operation without an explicit policy. |
| finish listener throws after success flag | source succeeded | yes | true | finish observer failed | `rehydrate()` must not accidentally say hydration failed after public success committed. |
| first of several finish listeners throws | source succeeded | yes | true or pending | later listeners may be skipped | Decide whether observer delivery is fail-fast or best-effort. |
| error callback throws | source failed | no or partial | false | error observer failed | Decide how to preserve the primary source error while exposing the callback error. |
| error callback starts a newer hydration | old source failed; new source starts | depends on new attempt | owned by newest attempt | callback changed generation | Recheck supersession after user code before settling the older explicit promise. |
| success callback starts a newer hydration | old source succeeded; new source starts | old state may be replaced | owned by newest attempt | callback changed generation | Define whether the older promise resolves normally or is classified as superseded. |

## Candidate outcome vocabulary

This is a research vocabulary, not a proposed public API.

### Source outcome

- `source_succeeded`
- `source_failed_before_commit`
- `source_failed_after_commit`
- `source_superseded`

### Observer outcome

- `observers_succeeded`
- `success_observer_failed`
- `error_observer_failed`
- `finish_listener_failed`
- `observer_started_new_attempt`

The public `rehydrate()` promise does not necessarily need to expose every combination. The implementation does need to know which combination occurred so one error cannot overwrite another by accident.

## Compatibility directions

### Direction A — promise represents source settlement only

- explicit `rehydrate()` rejects for current source failures;
- observer errors are isolated from the source promise and reported through another channel or rethrown outside it;
- successful source application cannot become a rejected hydration merely because an observer threw.

This is the clearest contract, but changing current callback exception propagation may be observable.

### Direction B — promise represents the whole operation including observers

- any observer error can reject;
- the promise must expose whether state committed despite rejection;
- primary and secondary errors need an explicit precedence or aggregation rule.

This preserves broad propagation but makes the promise a poor success signal unless partial outcomes become visible.

### Direction C — preserve current callback propagation and add a separate source result

- leave `rehydrate()` compatibility mostly unchanged;
- add an internal or public source-settlement channel;
- consumers that need truthful hydration outcome use the new channel.

This is wider and should not be selected without evidence that promise rejection is too disruptive.

## Recommended next experiment

Do not patch production source first. Add one focused characterization file against the current owned source that records, for every required case:

- promise settlement;
- concrete rejected error identity;
- state before and after;
- `hasHydrated` before and after;
- callback invocation order and arguments;
- finish-listener order;
- hydration generation before and after user code;
- whether a later retry succeeds.

Run the matrix against:

1. the released behavior;
2. the current rejection experiment;
3. one candidate that isolates observer delivery from source settlement.

The distinguishing result is whether the candidate can preserve source truth, observer visibility, retry recovery, and newest-attempt ownership without producing contradictory public signals.

## Stop condition

Stop this design pass when the matrix yields one explicit source-error rule, one observer-error rule, and one supersession rule that can be stated without contradiction and independently reviewed. Do not prepare upstream wording or mark the owned PR ready before that point.
