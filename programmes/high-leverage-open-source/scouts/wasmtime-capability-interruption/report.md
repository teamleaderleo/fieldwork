# Wasmtime interruption and host-effect ownership

Date: 2026-07-30

Fieldwork lane: #117  
Programme: #114  
Upstream contact authorized: `false`

## In simple words

Wasmtime gives an embedding several different controls that can stop or limit WebAssembly work, but they do not all mean the same thing.

- Epoch interruption stops instrumented guest execution when WebAssembly reaches an epoch check.
- Fuel provides deterministic guest-instruction accounting.
- Dropping an active asynchronous call drops the suspended Wasmtime and host futures.
- A host effect completed before that cancellation point is not rolled back.
- Resource limiters govern selected WebAssembly instance resources, not every allocation made by the store or embedding.
- Memory or table growth denial may appear to the guest as ordinary `-1` failure or as a trap, depending on limiter policy.

The first integration requirement is therefore a receipt boundary, not a runtime patch: record guest interruption, host-call entry, committed host effects, call-future cancellation, and final reconciliation separately.

## Evidence class

- Wasmtime source and repository tests: `source-read`.
- Fieldwork probe below: `target-test-prepared`.
- Target execution: not yet performed.
- Owned integration execution: not yet performed.

No defect is claimed in this pass.

## Exact source

Repository: `bytecodealliance/wasmtime`  
Reviewed source revision: `12e1636852a6e797e94b0213a5a2a98f72a4fb8f`  
Workspace version at that revision: `48.0.0`

Primary source surfaces:

- `crates/wasmtime/src/runtime/store.rs`
- `crates/wasmtime/src/runtime/func.rs`
- `crates/wasmtime/src/runtime/limits.rs`
- `tests/all/epoch_interruption.rs`
- `tests/all/async_functions.rs`

## Source-confirmed ownership map

### Epoch interruption

`Store::set_epoch_deadline` sets a deadline relative to the engine epoch. When epoch interruption is enabled and the deadline is reached, configured behavior can trap, yield, or invoke a callback.

The API explicitly describes epoch interruption as coarse-grained. A trap occurs when instrumented WebAssembly reaches an epoch check. It is not a deterministic fixed-duration deadline and does not describe rollback of earlier host work.

Repository tests place checks at function entries and loop headers and confirm interruption of an infinite guest loop after another thread increments the engine epoch.

### Fuel

Fuel is the deterministic guest-compute mechanism. The repository distinguishes it from epoch interruption and supports async yielding at configured fuel intervals.

Fuel should be recorded as guest execution accounting. It should not be used as evidence that a host call did not commit an external effect.

### Asynchronous host functions and future cancellation

`Func::new_async` runs the host future to completion when the call remains live.

The repository's `cancel_during_run` test polls an asynchronous call until its host future is suspended, drops the call future, and verifies that Rust values captured by that host future are dropped. This establishes cancellation-by-future-drop for the in-process host future.

That guarantee is cleanup, not rollback. A host function can update durable or external state before its first suspension point. Dropping the future can release local ownership while the already-completed effect remains. An embedding must therefore record effect identity before returning an ambiguous caller result.

### Resource limiters

`ResourceLimiter` and `ResourceLimiterAsync` cover WebAssembly instance resources such as memories, tables, and instance counts. Their documentation explicitly excludes all store and embedding allocations.

A denied `memory.grow` or `table.grow` normally returns failure to WebAssembly. A limiter error or `trap_on_grow_failure` can convert the same growth boundary into a trap.

The terminal receipt must distinguish:

- guest-observed grow failure;
- limiter-policy trap;
- allocator failure after the limiter allowed growth;
- unrelated embedder memory pressure.

## Prepared probe

Path: `programmes/high-leverage-open-source/scouts/wasmtime-capability-interruption/probe/`

The probe is pinned to the reviewed Wasmtime Git revision and prepares three cases:

1. **Epoch interruption:** increment the engine epoch while a guest runs an infinite loop and require the call to trap.
2. **Host-effect ambiguity:** enter an async host function, mark a synthetic effect committed, suspend forever, poll once, then drop the outer Wasmtime call future. Require the host future's drop guard to run while the committed-effect marker remains true.
3. **Resource-limit outcomes:** deny a one-page memory growth once as ordinary `-1`, then repeat with `trap_on_grow_failure(true)` and require a trap.

Expected evidence class after a successful run: `target-executed` for this exact source revision. It would still not be an owned integration or a sandbox-security result.

## Candidate receipt vocabulary

A Wasmtime-backed runner should record at least:

- module or component content hash;
- Wasmtime source or release identity;
- engine configuration hash;
- store or attempt identity;
- granted WASI and host capabilities;
- interruption mechanism: `fuel`, `epoch`, outer future cancellation, process death, or none;
- guest terminal result: completed, trapped, grow denied, resource trap, or unavailable;
- host-call phase: not entered, entered, effect committed, response produced, or unknown;
- host-effect receipt or reconciliation key;
- whether the call future was dropped;
- whether host cleanup completed;
- whether a retry is authorized, forbidden, or requires reconciliation.

## Strongest current conclusion

Wasmtime provides useful guest execution and in-process future-lifecycle controls, but an embedding must not collapse them into one generic timeout state.

A caller-visible timeout can coexist with a committed host effect. The host application owns idempotency, reconciliation, and retry authority for that effect.

## Negative results and limits

- No evidence currently supports a Wasmtime defect.
- No WASI filesystem, network, clock, random, or socket capability matrix has been executed.
- No process-death or pooled-instance test has run.
- No claim is made that dropping a Rust future cancels an external operation already detached from that future.
- No broad sandbox-security conclusion follows from the prepared probe.
- No upstream issue, pull request, comment, reaction, or message was created.

## Next bounded work

1. Execute the prepared probe at the exact source revision.
2. Add one control where the host effect occurs after a cancellation point and therefore must not commit.
3. Add a detached-task negative control proving that dropping the host future does not cancel work deliberately spawned outside it.
4. Add a WASI preview 2 file-write fixture with an operation receipt and process-death boundary.
5. Compare fresh and pooled stores only after the standalone terminal vocabulary is stable.

Stop before an owned Smolrunner adapter until these standalone outcomes are executed and reviewed.