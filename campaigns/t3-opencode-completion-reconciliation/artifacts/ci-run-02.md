# T3 OpenCode lifecycle CI run 02

Date: 2026-07-30

Fieldwork workflow run: `30493515208`

Target head under test: `54acd60d1506c878911202697652eae8826e1907`

## Result

The restart and reaper harness repairs worked. Those jobs completed with direct assertions rather than wall-clock timeouts.

### Restart reconciliation

All six cases failed quickly against current production behavior:

- no exact terminal event was emitted for an idle recovered turn with no matching history;
- matching successful history was not classified;
- matching failed history was not classified;
- a busy provider snapshot did not restore the persisted active T3 turn;
- a status snapshot failure was not consulted or propagated;
- a bounded history failure was not consulted or propagated.

The first three failures were missing exact completion events. The busy case returned `ready` instead of `running`. The injected status and history failures did not fail `startSession`.

### Reaper race

The reduced check-then-stop specification completed in 20 ms and observed `stopSession` for the target thread after the provider became active immediately following the idle projection snapshot.

This is executable evidence of a stale-decision race in `ProviderSessionReaper`.

### Interrupt settlement

Fast observed failures remained:

- abort success left adapter-local session status `running` rather than `ready`;
- a stale explicit turn ID was accepted;
- abort racing with idle emitted an ordinary completed result instead of one interrupted terminal result;
- delayed idle completed the newer turn.

Abort transport failure continued to preserve the active turn.

The duplicate-interrupt test still contained a harness ordering problem: it could release the fake abort before either caller installed its waiter. That case was simplified to concurrent immediate abort calls, preserving the one-abort/one-terminal invariant without an artificial gate.

### Steering affinity

The prompt message identity failure remained unchanged.

## Next target head

`8a409bc31a09c210ed5777221715302723e11340`

Run 03 should contain no intentional timing waits. It is expected to leave only direct product assertions.

No upstream contact occurred.
