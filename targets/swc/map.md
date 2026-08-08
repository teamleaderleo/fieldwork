# Target Map: SWC

Repository: https://redirect.github.com/swc-project/swc
Owned fork: `teamleaderleo/swc`
Pinned reconnaissance revision: `5bf27fd72e4667bac6cc86888b8facb8b91f8077`
Target hub: #717

## In simple words

SWC parses, transforms, optimizes, minifies, and emits JavaScript and TypeScript, with Rust and JavaScript-facing APIs plus WebAssembly plugin runtimes. A small semantic mistake can change executable code; a lifecycle or cache mistake can turn build work into repeated cost or corrupted state.

The first scout is testing two independent boundaries discovered from current source: whether the minifier correctly preserves operations whose operator itself can execute user code, and whether plugin filesystem caches recover after interrupted writers. The map also keeps parser/codegen, transform compatibility, release boundaries, and measured resource behavior available for later scouts without assuming they contain defects.

## Important code surfaces

### JavaScript semantics

- `crates/swc_ecma_parser` — JavaScript and TypeScript parsing.
- `crates/swc_ecma_ast` — shared AST contracts.
- `crates/swc_ecma_codegen` — source emission.
- `crates/swc_ecma_utils` — shared expression analysis, including purity/effect helpers.
- `crates/swc_ecma_minifier` — constant evaluation, dead-code removal, inlining, compression, and mangling.
- `crates/swc_ecma_transforms_*` and `crates/swc_ecma_transformer` — compatibility and language transforms.
- resolver, hygiene, and fixer passes — identifier identity and AST normalization around transforms.

### Plugin execution and cache lifecycle

- `crates/swc_plugin_runner/src/cache.rs` — shared in-memory and filesystem cache orchestration.
- `crates/swc_plugin_runner/src/runtime.rs` — runtime cache contract.
- `crates/swc_plugin_backend_wasmer` — Wasmer compilation, serialization, and cache publication.
- `crates/swc_plugin_backend_wasmtime` — Wasmtime compilation, serialization, and cache publication.

### Other recurring boundaries

- React Compiler integration and its skip/gating path.
- Rust-crate version compatibility and `swc_core` exposure.
- JavaScript package typings and native-binding release coordination.
- parser/minifier/codegen performance and resource scaling on realistic source.

## Current scout

Fieldwork #718, `swc-runtime-semantics-and-recovery`, owns the initial reconnaissance at the pinned revision.

Current source-backed branches:

1. **Operator-originated effects in minification.** Shared expression-effect analysis treats a binary expression through its operands. `in` can invoke a Proxy `has` trap and `instanceof` can invoke `Symbol.hasInstance`; a value-discarding optimizer therefore needs an operator-aware contract before removing such expressions.
2. **Interrupted Wasmtime cache publication.** Wasmtime uses one deterministic `.tmp` sibling path and treats an existing temporary file as a successful store. Wasmer now uses unique temporary paths plus cleanup. The scout is testing whether Wasmtime can report successful publication while the final cache entry remains absent.
3. **Resource scaling.** Older reports describe steep cost or crashes on long binary-expression chains. This remains a current-main reproduction question, not an established present defect.

## Evidence we can produce

- reduced JavaScript programs with runtime-observable callbacks;
- minifier fixtures that compare original and transformed execution;
- target-native Rust regression tests in the owned fork;
- interrupted-writer and concurrent-writer filesystem tests;
- focused crate tests and exact-head CI receipts;
- source-level call maps for value-discarding optimizations;
- controlled size/time/resource curves for generated source.

## Entry standard

A branch should identify an observable semantic, recovery, compatibility, or measured resource property; the likely owning code boundary; and an executable way to distinguish the competing explanations. Existing upstream issues and recent fixes are context, not a task menu.

## Stop conditions

- source reading or a target-native test disproves the suspected behavior;
- the observation is already protected by an equivalent regression;
- the consequence depends on an unsupported usage claim;
- a proposed optimization has no measurement;
- the only remaining work is cosmetic documentation or style cleanup;
- a broad redesign is required before a bounded behavior has been demonstrated.

## Upstream boundary

Third-party upstream is read-only to automated Fieldwork workers. Candidate tests, patches, benchmarks, and human-facing packets belong in Fieldwork or `teamleaderleo/swc`; any upstream interaction is manual human work.
