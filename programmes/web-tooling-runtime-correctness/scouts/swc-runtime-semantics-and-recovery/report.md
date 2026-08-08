# SWC runtime semantics and recovery scout

## In simple words

This scout found one narrow recovery defect candidate and one broader JavaScript-semantics boundary worth sustained work.

The narrow candidate is in the Wasmtime plugin cache. A previous process can leave SWC's deterministic `.tmp` file behind. Current Wasmtime code sees that file, returns success from `store_cache`, and never creates the final cache entry. A dependency-free model reproduced that exact state transition, and a Rust regression is prepared in `teamleaderleo/swc` at commit `95a3fce5adc2b387eae539cecdfad418a5dd72aa`. Wasmer already solved the sibling problem with unique temporary files and cleanup, giving Wasmtime a nearby implementation precedent.

The broader boundary is minifier effect analysis. SWC's shared expression helper treats a binary expression as effectful when either operand is effectful. JavaScript operators can perform their own observable work: `in` can invoke a Proxy `has` trap and `instanceof` can invoke `Symbol.hasInstance`. A Node probe executed both callbacks. The existing `in` report upstream confirms that this can reach value-discarding minifier logic. The right next step is a target-native operator matrix and a review of the shared effect contract before choosing the narrowest correction.

The exponentiation lead was discarded: current fixtures already exercise the special NaN/infinity cases that initially looked suspicious.

## Assignment

- Worker: GPT-5.6 Sol
- Programme: `web-tooling-runtime-correctness`, Fieldwork #15
- Target hub: Fieldwork #717
- Scout: Fieldwork #718
- Target repository: https://github.com/swc-project/swc
- Owned fork: `teamleaderleo/swc`
- Pinned target revision: `5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- Retrieval date: 2026-08-09
- Intended claim scope: mechanism
- Upstream-contact authorization: `false`

## Execution boundary

GitHub source and history were available through the connected GitHub interface. The shell environment could not resolve `github.com`, so the full SWC checkout could not be cloned here. Target-native claims therefore remain `target-test-prepared` until an owned-fork run or CI receipt exists.

Dependency-free JavaScript and filesystem models were executed locally. Those claims are labeled `model-executed` and are kept separate from SWC target execution.

## Code map

### Expression effects and value-discarding compression

`crates/swc_ecma_utils/src/lib.rs` owns shared `ExprExt::may_have_side_effects` behavior. For `Expr::Bin`, the current decision is the disjunction of the two operands' effect classifications. The operator is not inspected there.

`crates/swc_ecma_minifier/src/compress/pure/mod.rs` and `compress/pure/misc.rs` consume expression-effect information while simplifying expressions whose result is unused. `ignore_return_value` is reached from unused expression statements, sequence elements, loop expressions, and other value-discarding contexts.

SWC also ships an `instanceof` helper at `packages/helpers/esm/_instanceof.js` that explicitly reads and invokes `right[Symbol.hasInstance]`, confirming that SWC's compatibility layer recognizes the user-code callback built into that operator.

### Plugin filesystem cache

`crates/swc_plugin_runner/src/cache.rs` coordinates plugin cache lookup. On a filesystem miss it compiles the raw module, asks the runtime to store the compiled cache, records the hash for the current process, and keeps the compiled module in memory. A fresh process therefore depends on successful filesystem publication to avoid recompilation.

`crates/swc_plugin_backend_wasmtime/src/lib.rs::store_cache` serializes the module, derives one deterministic sibling temp path by appending `.tmp` to the cache extension, opens it with `create_new(true)`, and returns `Ok(())` when that temp path already exists. Its comment acknowledges that interrupted writes can leave the temp file behind.

`crates/swc_plugin_backend_wasmer/src/filesystem_cache.rs` now uses a different algorithm: a process id plus atomic counter creates a unique temporary path, write failures clean that path up, rename failures clean it up, and a concurrent-writer regression verifies that readers only see complete artifacts. Upstream PR 12100 introduced that Wasmer repair before this scout revision.

## Probe 1: operator-originated JavaScript effects

### Question

Can `in` and `instanceof` execute observable user code even when their operand expressions are themselves simple references or values?

### Command

```sh
node - <<'NODE'
const events = [];
const proxy = new Proxy({}, {
  has(_target, key) {
    events.push(`has:${String(key)}`);
    return false;
  },
});

'x' in proxy;

class C {
  static [Symbol.hasInstance](value) {
    events.push(`hasInstance:${String(value)}`);
    return false;
  }
}

({}) instanceof C;
console.log(JSON.stringify(events));
NODE
```

### Observed result

```json
["has:x","hasInstance:[object Object]"]
```

Evidence class: `model-executed`.

This establishes the JavaScript mechanism only. It does not by itself prove every current SWC minifier path drops both expressions.

### Current SWC context

An existing open upstream report, `swc-project/swc#11246`, demonstrates the `in` case with a Proxy `has` trap: a standalone `TRACK_MEMO_SYMBOL in obj` expression is removed under compression and the trap does not run. No equivalent current `instanceof` report was found during this scout.

The likely owning boundary is shared effect analysis plus value-discarding compression. A correction limited to two operators may still be too narrow because JavaScript coercion in other operators can invoke `Symbol.toPrimitive`, `valueOf`, or `toString`. The next investigation should define the intended contract of `may_have_side_effects` before changing it globally.

## Probe 2: stale Wasmtime temporary cache file

### Question

What does the current Wasmtime store algorithm do when an interrupted earlier writer left its deterministic temp path behind while the final cache path is absent?

### Model

The model reproduced the filesystem decisions in `WasmtimeRuntime::store_cache`: derive the fixed `.tmp` path, attempt `create_new`, treat `AlreadyExists` as success, otherwise write and rename.

### Distinguishing setup

```text
before store:
  final cache  = absent
  fixed .tmp   = present, containing partial bytes

expected recovery property:
  a successful store leaves a final cache entry

current modeled transition:
  open fixed .tmp with create_new
      -> AlreadyExists
      -> return Ok
      -> final cache remains absent
      -> stale .tmp remains present
```

### Observed model result

```json
{
  "outcome": "ok-existing-temp",
  "final_exists": false,
  "tmp_exists": true,
  "tmp_bytes": "partial"
}
```

Evidence class: `model-executed`.

### Prepared target regression

Owned fork branch: `fieldwork/wasmtime-cache-recovery`
Commit: `95a3fce5adc2b387eae539cecdfad418a5dd72aa`
File: `crates/swc_plugin_backend_wasmtime/tests/stale_temp_cache.rs`

The test creates a stale legacy temp file, compiles the minimal valid empty WebAssembly module, calls the real Wasmtime `Runtime::store_cache`, and asserts that successful publication creates the final cache path. Under the source-read algorithm the assertion should fail.

Evidence class: `target-test-prepared`.

### Consequence boundary

Within one process, the compiled module remains available in memory. Across a fresh process, the missing final cache entry means the filesystem lookup misses again and compilation can repeat. The scout establishes the cache lifecycle path from source; frequency and real-world cost remain unmeasured.

### Candidate correction

Port the Wasmer unique-temp publication behavior to Wasmtime, or factor an equivalent shared helper if that produces a smaller ownership model. Preserve same-directory rename so publication stays atomic, clean temporary files on failure, and retain the Windows collision behavior where an already-published final cache file is success.

The Wasmer implementation is the preferred starting precedent because it already survived review in the same repository and has concurrent-writer coverage.

## Probe 3: exponentiation special values — negative result

The initial source read noticed that `JsNumber::pow` has an ECMAScript-specific special case for a base with absolute value `1` and an infinite exponent, while one minifier path calls Rust `powf` directly.

Current `pow_spec` fixtures already enumerate `Math.pow` and `**` over NaN, infinities, `1`, `-1`, zero, negative zero, and ordinary values. Expected outputs preserve the NaN cases. That existing coverage defeats the original hypothesis as a useful current branch.

Disposition: stop this lead unless future target execution exposes a mismatch outside the covered matrix.

Evidence class: `source-read`.

## Probe 4: long binary-expression resource scaling — retained lead

An older upstream report describes rapidly increasing compression time and eventual process failure on generated long binary-expression chains. Current source has changed substantially since that report.

No present-revision target run was available in this environment, so the scout does not call this a current defect. A future bounded performance probe should generate a size series, record wall time and peak memory, identify the dominating pass, and stop if growth is now ordinary or bounded.

Evidence class: `source-read` for historical/context material; current target behavior `Unknown`.

## Ranked branch candidates

### 1. Wasmtime interrupted-writer cache recovery

Consequence: a store can report success while publishing no reusable filesystem artifact, causing repeated compilation across later processes until the stale temp file is removed.

Likely owner: `crates/swc_plugin_backend_wasmtime::store_cache`, with `swc_plugin_runner` as the lifecycle caller.

Evidence now: `source-read`, `model-executed`, `target-test-prepared`.

Next evidence: execute the prepared regression on the exact owned-fork head, then implement unique temporary publication and run `cargo test -p swc_plugin_backend_wasmtime`, formatting, and the repository-required lint gate.

Recommendation: promote to a bounded campaign once target execution confirms the prepared assertion.

### 2. Minifier operator-effect contract

Consequence: value-discarding optimization can erase JavaScript callbacks or exceptions performed by an operator even when its operands look pure.

Likely owner: shared `swc_ecma_utils` effect analysis and the minifier consumers that use it to discard values.

Evidence now: `source-read`, `model-executed`; the `in` case also has an existing upstream reproduction.

Next evidence: target-native fixtures for `in`, `instanceof`, and negative controls; trace coercion-capable operators before choosing a shared or minifier-local correction.

Recommendation: retain as a finding and open a focused semantics campaign after the current-main target matrix identifies the exact affected set.

### 3. Minifier long-expression resource scaling

Consequence if reproduced: excessive latency, memory growth, or process failure on generated but valid JavaScript.

Likely owner: unknown until profiling identifies the repeated pass or recursion boundary.

Evidence now: historical report only for behavior; current source revision unexecuted.

Recommendation: run a separate performance probe before creating implementation work.

## Uncertainty and limits

- The Wasmtime regression is prepared but has no target execution receipt yet.
- The filesystem model preserves the fixed-temp collision and publication decision; it omits Wasmtime serialization internals and operating-system-specific rename behavior.
- The operator probe proves JavaScript callbacks, while the exact current SWC behavior for `instanceof` still needs a minifier run.
- A global effect-analysis correction can affect optimization rate throughout SWC, so target-native negative controls and size/performance checks belong in review.
- No ecosystem frequency claim is supported by this scout.

## Recommendation

Keep SWC as a recurring target under `web-tooling-runtime-correctness`.

Advance Wasmtime cache recovery first because its current behavior, lifecycle consequence, owning boundary, sibling precedent, and regression path are narrow. Carry the operator-effect work as the next semantics branch, with target execution determining whether it becomes one campaign or several smaller corrections. Preserve the long-expression case as an independent performance probe.

Automated upstream contact remained prohibited throughout the scout. No upstream mutation was attempted or performed.
