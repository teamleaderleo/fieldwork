# T3 OpenCode lifecycle CI run 03

Date: 2026-07-30

Fieldwork workflow run: `30493778539`

Target head under test: `8a409bc31a09c210ed5777221715302723e11340`

## Purpose

Run the reviewed lifecycle specifications without wall-clock waits or artificial deferred gates. This run is the campaign's deterministic pre-repair baseline.

## Results

All four jobs reached direct assertions. No test failed from a 60-second timeout.

### Steering affinity

The initial OpenCode prompt and two steering prompts reused one T3 turn as expected, but none supplied a caller-generated provider `messageID`.

Required repair boundary:

- every prompt receives a distinct valid OpenCode message ID;
- the ordered IDs can later be persisted under the single T3 turn;
- generating the IDs alone is a prerequisite, not full restart recovery.

### Restart reconciliation

All six recovery specifications failed directly:

- idle without matching terminal history emitted no exact interrupted result;
- matching terminal success was not classified;
- matching terminal failure was not classified;
- busy status did not restore the persisted exact active turn;
- a status snapshot failure was not consulted or propagated;
- a bounded history failure was not consulted or propagated.

Current resumed startup therefore restores the OpenCode session ID but not activity or outcome truth for the old T3 turn.

### Interrupt settlement

Six tests completed in 84 ms: five failed and one passed.

Observed failures:

- successful abort left adapter-local state `running` instead of `ready`;
- a stale explicit turn ID returned success and reached OpenCode abort;
- abort racing with idle emitted two terminal events for the same turn;
- concurrent duplicate callers invoked OpenCode abort twice;
- a delayed duplicate idle emitted a terminal result for the newer turn.

Observed existing safety:

- an abort transport failure preserved the active turn and emitted no terminal result.

### Reaper race

The reaper materialized an idle projection snapshot, the provider became active immediately afterward, and the stale decision still called `stopSession` for the thread.

This reproduces the check-then-stop race in a focused 20 ms test. The preferred repair should reuse optimistic or conditional state mutation rather than add an OpenCode-only lock.

## Candidate order established

1. caller-generated OpenCode prompt identity;
2. exact interruption settlement and stale-turn validation;
3. conditional reaper stop;
4. durable ordered provider-message affinity;
5. bounded restart reconciliation;
6. pending approval/question cleanup and recovery.

The first candidate can be implemented independently. The later candidates cross the adapter, ProviderService runtime payload, and shared projection boundaries and should remain separate until their own focused tests pass.

No upstream contact occurred.
