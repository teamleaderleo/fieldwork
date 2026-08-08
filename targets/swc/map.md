# Target Map: SWC

Repository: https://redirect.github.com/swc-project/swc
Owned fork: `teamleaderleo/swc`
Pinned reconnaissance revision: `5bf27fd72e4667bac6cc86888b8facb8b91f8077`
Target hub: #717

## In simple words

SWC parses, transforms, optimizes, minifies, and emits JavaScript and TypeScript, with Rust and JavaScript-facing APIs plus WebAssembly plugin runtimes. A small semantic mistake can change executable code; a lifecycle or cache mistake can turn build work into repeated cost or corrupted state.

The first scout has now promoted two active campaigns: binary operator effects during optimization (#725) and Wasmtime filesystem-cache recovery (#719). Separate leads remain for unary operator effects and current-head resource scaling on very deep binary expressions.

## Important code surfaces

### JavaScript semantics

- `crates/swc_ecma_parser` — JavaScript and TypeScript parsing.
- `crates/swc_ecma_ast` — shared AST contracts.
- `crates/swc_ecma_codegen` — source emission.
- `crates/swc_ecma_utils` — shared expression analysis, including purity/effect helpers and effect extraction.
- `crates/swc_ecma_minifier` — constant evaluation, dead-code removal, inlining, compression, mangling, and value-discarding rewrites.
- `crates/swc_ecma_transforms_optimization` — expression simplification and DCE paths that also consume shared effect analysis.
- resolver, hygiene, and fixer passes — identifier identity and AST normalization around transforms.

### Plugin execution and cache lifecycle

- `crates/swc_plugin_runner/src/cache.rs` — shared in-memory and filesystem cache orchestration.
- `crates/swc_plugin_runner/src/runtime.rs` — runtime cache contract.
- `crates/swc_plugin_backend_wasmer` — Wasmer compilation, invalid-cache deletion, and atomic cache publication.
- `crates/swc_plugin_backend_wasmtime` — Wasmtime compilation, deserialization, and cache publication.

### Other recurring boundaries

- React Compiler integration and its skip/gating path.
- Rust-crate version compatibility and `swc_core` exposure.
- JavaScript package typings and native-binding release coordination.
- parser/minifier/codegen performance and resource scaling on realistic source.

## Active campaign: binary operator effects (#725)

At the pinned revision:

- `may_have_side_effects` classifies every binary expression from its operands only;
- `ExprCtx::extract_side_effects_to` preserves short-circuit binaries whole but decomposes other binary operators into child effects;
- minifier `ignore_return_value` independently treats arithmetic, exponentiation, bitwise/shift, loose/strict equality, and relational expressions as reducible when their values are discarded;
- the expression simplifier uses `extract_side_effects_to` while folding statically selected array elements.

Node probes established operator-originated object coercion across arithmetic, bitwise/shift, relational, and loose-equality families; property-key and Proxy hooks for `in`; `Symbol.hasInstance` for `instanceof`; and pure-literal numeric-domain exceptions. Strict equality is the clean operator-level control.

Owned discriminators:

- `teamleaderleo/swc#2` — utility classification and extraction contract;
- `teamleaderleo/swc#4` — end-to-end expression-simplifier array-member regression.

Durable status: `campaigns/0725-swc-binary-operator-effects/STATUS.md`.

## Active campaign: Wasmtime cache recovery (#719)

Two independent recovery cases are retained:

1. an abandoned deterministic `.tmp` path can make the current Wasmtime store report success while the final cache is absent;
2. a final cache file rejected by Wasmtime deserialization is left in place, while the Wasmer sibling explicitly removes rejected cache files.

Owned discriminators:

- `teamleaderleo/swc#1` — stale-temporary-file publication candidate;
- `teamleaderleo/swc#3` — rejected-final-cache test-only contract.

Durable status: `campaigns/0719-swc-wasmtime-cache-recovery/STATUS.md`.

## Retained lead: unary operator effects

A separate Node probe showed `Symbol.toPrimitive` callbacks for unary `+`, unary `-`, and `~` on object operands. Unary `+1n` throws `TypeError`; `!` and `void` are callback-free controls. `typeof` also has a temporal-dead-zone exception case.

SWC's shared unary effect classification and value-discarding paths should be mapped before promotion. This lead stays separate from #725 so the binary campaign remains bounded.

## Retained lead: deep binary-expression resource scaling

The historical long-chain report received a performance repair in `swc-project/swc@1434571477f5f8576a268a2bd32631eb9ce77229`. That change profiled recursive visiting plus `remove_invalid`, `remove_invalid_bin`, and string analysis, reduced one measured case from 2.17s to 0.77s, and explicitly left recursive visiting as remaining cost.

Current-head behavior therefore needs a fresh size/time/resource curve before any new performance campaign is justified. The present environment cannot execute an SWC checkout, so this remains a reproduction lead rather than a current defect claim.

## Evidence we can produce

- reduced JavaScript programs with runtime-observable callbacks or exceptions;
- utility-level and consumer-level target regressions in the owned fork;
- interrupted-writer and invalid-cache filesystem tests;
- focused crate tests and exact-head CI receipts when execution becomes available;
- source-level consumer maps for value-discarding optimizations;
- controlled size/time/resource curves for generated source.

## Entry standard

A branch should identify an observable semantic, recovery, compatibility, or measured resource property; the likely owning code boundary; and an executable way to distinguish competing explanations. Existing upstream issues and recent fixes are context, not a task menu.

## Stop conditions

- source reading or a target-native test disproves the suspected behavior;
- the observation is already protected by an equivalent regression;
- the consequence depends on an unsupported usage claim;
- a proposed optimization has no measurement;
- the only remaining work is cosmetic documentation or style cleanup;
- a broad redesign is required before a bounded behavior has been demonstrated.

## Upstream boundary

Third-party upstream is read-only to automated Fieldwork workers. Candidate tests, patches, benchmarks, and human-facing packets belong in Fieldwork or `teamleaderleo/swc`; any upstream interaction is manual human work.
