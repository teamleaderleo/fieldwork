# SWC runtime semantics and recovery scout

## In simple words

This scout found one narrow recovery defect candidate and one broader JavaScript-semantics boundary worth sustained work.

The narrow candidate is in the Wasmtime plugin cache. A previous process can leave SWC's deterministic `.tmp` file behind. Current Wasmtime code sees that file, returns success from `store_cache`, and never creates the final cache entry. A dependency-free model reproduced that exact state transition. The owned-fork draft `teamleaderleo/swc#1` now contains a regression and a candidate repair at head `bce1d2e03f654d6aaaac77d76e2a818b3b743706`. Wasmer already solved the sibling problem with unique temporary files and cleanup, giving Wasmtime a nearby implementation precedent. This branch is promoted to Fieldwork campaign #719 while target execution remains pending.

The broader boundary is expression-effect analysis. SWC's shared helper treats every binary expression as effectful only when either operand is effectful. JavaScript operators can perform their own observable work. A Node probe executed `valueOf` through `+`, `-`, `<`, and loose `==`, a Proxy `has` trap through `in`, and `Symbol.hasInstance` through `instanceof`. The minifier's own `ignore_return_value` code already uses a narrower operator allowlist, which shows some local awareness of operator-specific risk; the shared helper still has a wider contract problem. A target-native contract test is prepared on `teamleaderleo/swc:fieldwork/expression-effect-contract` at `9ad27ab47b7f9a6c77bdcc67fac173efff2f78c8`.

The exponentiation lead was discarded: current fixtures already exercise the special NaN/infinity cases that initially looked suspicious.

## Assignment

- Worker: GPT-5.6 Sol
- Programme: `web-tooling-runtime-correctness`, Fieldwork #15
- Target hub: Fieldwork #717
- Scout: Fieldwork #718
- Promoted cache campaign: Fieldwork #719
- Target repository: https://github.com/swc-project/swc
- Owned fork: `teamleaderleo/swc`
- Pinned target revision: `5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- Retrieval date: 2026-08-09
- Intended claim scope: mechanism
- Upstream-contact authorization: `false`

## Execution boundary

GitHub source and history were available through the connected GitHub interface. The shell environment could not resolve `github.com`, so the full SWC checkout could not be cloned here. Target-native claims therefore remain `target-test-prepared` until an owned-fork run or CI receipt exists.

Dependency-free JavaScript and filesystem models were executed locally. Those claims are labeled `model-executed` and are kept separate from SWC target execution.

The owned-fork Wasmtime draft was opened to request a GitHub-runner receipt. The connected GitHub interface returned no pull-request workflow run for its earlier or current head. The draft therefore stays evidence-prepared rather than being described as green.

## Code map

### Expression effects and value-discarding compression

`crates/swc_ecma_utils/src/lib.rs` owns shared `ExprExt::may_have_side_effects` behavior. For `Expr::Bin`, the current decision is the disjunction of the two operands' effect classifications. The operator is not inspected there.

`crates/swc_ecma_minifier/src/compress/pure/mod.rs` and `compress/pure/misc.rs` simplify expressions whose result is unused. `ignore_return_value` is reached from unused expression statements, sequence elements, loop expressions, and other value-discarding contexts.

The binary-expression branch inside `ignore_return_value` is explicitly selective. It is willing to recursively discard/sequence operands for arithmetic, bitwise, shifts, equality, and relational operators, while `in`, `instanceof`, `/`, logical short-circuit operators, and other cases are handled separately or retained. That local allowlist should not be conflated with the broader shared `may_have_side_effects` contract.

SWC also ships an `instanceof` helper at `packages/helpers/esm/_instanceof.js` that explicitly reads and invokes `right[Symbol.hasInstance]`, confirming that SWC's compatibility layer recognizes the user-code callback built into that operator.

### Plugin filesystem cache

`crates/swc_plugin_runner/src/cache.rs` coordinates plugin cache lookup. On a filesystem miss it compiles the raw module, asks the runtime to store the compiled cache, records the hash for the current process, and keeps the compiled module in memory. A fresh process therefore depends on successful filesystem publication to avoid recompilation.

`crates/swc_plugin_backend_wasmtime/src/lib.rs::store_cache` at the pinned base serializes the module, derives one deterministic sibling temp path by appending `.tmp` to the cache extension, opens it with `create_new(true)`, and returns `Ok(())` when that temp path already exists. Its comment acknowledges that interrupted writes can leave the temp file behind.

`crates/swc_plugin_backend_wasmer/src/filesystem_cache.rs` now uses a different algorithm: a process id plus atomic counter creates a unique temporary path, write failures clean that path up, rename failures clean it up, and a concurrent-writer regression verifies that readers only see complete artifacts. Upstream PR 12100 introduced that Wasmer repair before this scout revision.

## Probe 1: operator-originated JavaScript effects

### Question

Which binary operators can execute observable user code even when evaluation of the operand expressions themselves is side-effect-free?

### Command

```sh
node -e "
const events=[];
const obj={
  valueOf(){ events.push('valueOf'); return 2; },
  toString(){ events.push('toString'); return '2'; }
};
void(obj+1);
void(obj-1);
void(obj<3);
void(obj==2);
const p=new Proxy({}, { has(){ events.push('has'); return false; } });
void('x' in p);
class C { static [Symbol.hasInstance](){ events.push('hasInstance'); return false; } }
void({} instanceof C);
console.log(JSON.stringify(events));
"
```

### Observed result

```json
["valueOf","valueOf","valueOf","valueOf","has","hasInstance"]
```

Evidence class: `model-executed`.

This establishes the JavaScript mechanism. It does not prove that every current SWC consumer of `may_have_side_effects` makes an invalid transformation for every listed operator.

### Current SWC context

An existing open upstream report, `swc-project/swc#11246`, demonstrates the `in` case with a Proxy `has` trap: a standalone `TRACK_MEMO_SYMBOL in obj` expression is removed under compression and the trap does not run. No equivalent current `instanceof` report was found during this scout.

The direct source mismatch is broader than those two operators: `may_have_side_effects` treats every `Expr::Bin` identically after operand inspection, while ECMAScript arithmetic, relational comparison, loose equality, `in`, and `instanceof` can perform conversions, callbacks, or throws at the operator step. Strict equality is a useful negative control because it does not perform object-to-primitive coercion.

### Prepared target contract

Owned fork branch: `fieldwork/expression-effect-contract`
Commit: `9ad27ab47b7f9a6c77bdcc67fac173efff2f78c8`
File: `crates/swc_ecma_utils/tests/operator_effects.rs`

The prepared integration test uses the existing parser dev dependency and asks the shared helper directly about:

- `in` and `instanceof` callback-capable expressions;
- `+`, `-`, `<`, and loose `==` with a pure object literal that defines `valueOf`;
- primitive `1 + 2`, strict equality, and boolean short-circuit controls.

Evidence class: `target-test-prepared`.

### Next semantics question

A global conservative change could reduce optimization throughout SWC. Before implementation, classify operators by their actual evaluation semantics and inspect all important consumers of `may_have_side_effects`. The useful correction may be:

- operator-aware shared analysis with primitive/type proofs;
- a more explicit distinction between "evaluating children is pure" and "evaluating the whole expression is pure";
- or narrower consumer-side protection where full conservatism would cost too much.

The target-native contract branch exists to expose that design choice, not to predetermine it.

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

### Prepared target regression and candidate

Owned fork branch: `fieldwork/wasmtime-cache-recovery`
Draft: `teamleaderleo/swc#1`
Current candidate head: `bce1d2e03f654d6aaaac77d76e2a818b3b743706`
Regression: `crates/swc_plugin_backend_wasmtime/tests/stale_temp_cache.rs`
Candidate helper: `crates/swc_plugin_backend_wasmtime/src/filesystem_cache.rs`

The regression creates a stale legacy temp file, compiles the minimal valid empty WebAssembly module, calls the real Wasmtime `Runtime::store_cache`, and asserts that successful publication creates the final cache path. Under the pinned base algorithm the assertion should fail.

The candidate replaces the fixed temp path with unique same-directory `.<pid>.<counter>.tmp` files, writes the complete serialized module before rename, cleans temporary files on failure, and preserves the Windows case where another writer has already published the final path.

The regression deliberately requires only successful final publication. It does not require the obsolete legacy temp file to survive, leaving cleanup policy open to future implementations.

Evidence class: `target-test-prepared` for both regression and candidate. No CI run was returned for the current draft head.

### Consequence boundary

Within one process, the compiled module remains available in memory. Across a fresh process, the missing final cache entry means the filesystem lookup misses again and compilation can repeat. The scout establishes the cache lifecycle path from source; frequency and real-world cost remain unmeasured.

### Promotion

Fieldwork #719 now owns this bounded cache-recovery campaign. Promotion happened because the source behavior, lifecycle consequence, owning boundary, executed model, regression path, sibling precedent, and candidate repair are all concrete. Production readiness still depends on target execution and exact-head review.

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

Consequence: a store can report success while publishing no reusable filesystem artifact, causing repeated compilation across later processes until the stale temp collision ceases.

Likely owner: `crates/swc_plugin_backend_wasmtime::store_cache`, with `swc_plugin_runner` as the lifecycle caller.

Evidence now: `source-read`, `model-executed`, `target-test-prepared`.

Current work: campaign #719 and owned draft `teamleaderleo/swc#1` contain the prepared regression and candidate repair.

Next evidence: execute the regression on the unfixed base, execute the candidate at exact head, then run focused crate tests, formatting, clippy, and complete-diff review.

Recommendation: continue campaign #719; hold readiness until target-native receipts exist.

### 2. Binary-operator effect contract

Consequence: callers of shared effect analysis can incorrectly treat an expression as safely discardable or movable even when the operator performs coercion, callbacks, or throws.

Likely owner: `swc_ecma_utils` effect analysis plus each consequential consumer that assumes its result covers whole-expression evaluation.

Evidence now: `source-read`, `model-executed`, `target-test-prepared`; the `in` case also has an existing upstream reproduction.

Current work: owned branch `fieldwork/expression-effect-contract` carries a direct utility-level contract test.

Next evidence: execute that test on the pinned base, map consumers, classify operator semantics and primitive proofs, then decide whether the correction belongs globally or in selected optimization paths.

Recommendation: retain as a high-priority finding and promote after the target-native contract run establishes the affected set.

### 3. Minifier long-expression resource scaling

Consequence if reproduced: excessive latency, memory growth, or process failure on generated but valid JavaScript.

Likely owner: unknown until profiling identifies the repeated pass or recursion boundary.

Evidence now: historical report only for behavior; current source revision unexecuted.

Recommendation: run a separate performance probe before creating implementation work.

## Uncertainty and limits

- Both Rust branches are prepared without target execution receipts in this environment.
- The filesystem model preserves the fixed-temp collision and publication decision; it omits Wasmtime serialization internals and operating-system-specific rename behavior.
- The JavaScript operator probe proves callbacks/coercion, while each consequential SWC transformation still needs a target-native discriminator.
- A global effect-analysis correction can affect optimization rate throughout SWC, so negative controls and size/performance checks belong in review.
- No ecosystem frequency claim is supported by this scout.

## Recommendation

Keep SWC as a recurring target under `web-tooling-runtime-correctness`.

Continue campaign #719 for Wasmtime cache recovery. Carry binary-operator effects as the next semantics branch with its direct helper-level test. Preserve the long-expression case as an independent performance probe. The exponentiation branch is closed as a negative result.

Automated upstream contact remained prohibited throughout the scout. No upstream mutation was attempted or performed.
