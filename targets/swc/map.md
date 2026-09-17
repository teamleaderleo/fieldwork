# Target Map: SWC

Repository: https://redirect.github.com/swc-project/swc
Owned fork: `teamleaderleo/swc`
Pinned reconnaissance revision: `5bf27fd72e4667bac6cc86888b8facb8b91f8077`
Latest measured revision: `6c778430811853d4feee2ab3af1473669deb7b2a`
Target hub: #717

## In simple words

SWC parses, transforms, optimizes, minifies, and emits JavaScript and TypeScript, with Rust and JavaScript-facing APIs plus WebAssembly plugin runtimes. A small semantic mistake can change executable code; a lifecycle or cache mistake can turn build work into repeated cost or corrupted state.

The scout has promoted active campaigns for `instanceof` constant-fold correctness (#725), Wasmtime filesystem-cache recovery (#719), and mapped parameter/`arguments` ownership (#766). Unary operator effects remain a source-backed lead. The historical long binary-expression crash/slowdown lead has now been measured on current source and stopped as a negative result at the old few-thousand-term scale.

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

## Active campaign: `instanceof` constant folding (#725)

The original binary-operator investigation proved that several SWC paths can erase or simplify `instanceof` evaluation. Review then established a project-policy split that is now resolved for the current contribution.

The final contribution boundary is:

```text
unused instanceof
→ existing SWC/Terser compressor contract
→ unchanged

used instanceof
→ result must be correct
→ remove invalid operand-shape folds
```

The broad candidate originally changed shared effect classification, effect extraction, DCE/dead-branch cleanup, minifier ignored-result handling, and value folding. Maintainer feedback established that the discarded-result path is intentional Terser-compatible compressor behavior here, so those changes were removed.

A later review detour temporarily introduced an exception for operands whose values came from pure-marked expressions. The maintainer then clarified that the relevant `foo` was configured as pure and should be removed under the existing Terser behavior, and that the general rule is not to change tests under `tests/terser` for this contribution. That exception has been retired.

Current owned-fork head: `teamleaderleo/swc@9f838a578a2bf440d6cc92d3b0e4891da0a580de`. GitHub reports zero file differences from the earlier fold-only revision `a39678bd0226a394847605b6874b1eab7ad7f32c`.

Exact-head Fieldwork run `31988964177`, job `95268872348`, passed formatting/diff hygiene, the focused minifier used-result fixture, affected-package Clippy, and final diff hygiene. Fieldwork integrity run `31988964175`, job `95268872278`, also passed.

The active diff is nine files and changes no `tests/terser` expectation. The changeset remains `fix(es): Avoid incorrect instanceof constant folding`.

Durable review note: `programmes/web-tooling-runtime-correctness/scouts/swc-runtime-semantics-and-recovery/instanceof-review-reconciliation-2026-08-17.md`.

The pure-value detour remains useful research: strict JavaScript semantics do distinguish a pure producer from the semantic use of its returned value, but that fact does not override SWC's accepted compressor contract for an unused enclosing operation. Treat language semantics and optimizer-policy guarantees as separate questions.

## Active campaign: mapped parameter / `arguments` ownership (#766)

Current target execution has demonstrated that sloppy parameter/`arguments` aliasing depends on the declaring function, not merely the nested writer scope or the current identifier context.

The retained candidate carries declaring-function ownership on per-binding usage information so inline remapping can preserve the semantic owner. The candidate is target-green on the retained semantic matrix; remaining work is compression precision and coordination with active public implementation ownership.

Durable status: `campaigns/0766-swc-mapped-arguments-aliasing/STATUS.md`.

## Active campaign: Wasmtime cache recovery (#719)

Two independently testable recovery cases are retained:

1. an abandoned deterministic temporary path can interfere with later publication;
2. a final cache file rejected by Wasmtime deserialization is left in place, while the sibling backend has an explicit invalid-artifact cleanup rule.

The campaign remains bounded to recovery after an unusable filesystem artifact. Target-native execution is still the useful gate before any implementation promotion.

Durable status: `campaigns/0719-swc-wasmtime-cache-recovery/STATUS.md`.

## Retained lead: unary operator effects

A separate Node probe showed `Symbol.toPrimitive` callbacks for unary `+`, unary `-`, and `~` on object operands. Unary `+1n` throws `TypeError`; `!` and `void` are callback-free controls. `typeof` also has a temporal-dead-zone exception case.

Current source still routes shared expression-effect reasoning through `swc_ecma_utils`, with multiple minifier and optimization consumers. Do not promote a global purity change from the language-level observation alone. The next useful step is to identify one concrete destructive consumer, compare its behavior against SWC/Terser policy, and execute a target-native discriminator.

This lead stays separate from #725 so the current `instanceof` contribution remains bounded.

## Closed probe: long binary-expression resource scaling

The earlier scout retained long `+` chains because historical data showed rapidly increasing minifier cost and process failure after a partial performance repair.

That current-head measurement is now complete on exact source `6c778430811853d4feee2ab3af1473669deb7b2a`.

Fieldwork carrier #842, run `31489088182`, job `93771096892`, measured:

- left-deep mixed variable/string chains;
- left-deep literal-only chains;
- left-deep variable-only chains;
- balanced mixed controls;
- parse-only, preparation, compressor-only, and full-minify stages;
- controlled 8 MiB and 32 MiB process stacks.

All 152 measured processes exited successfully. Every 8 MiB-stack case passed through 4,000 repetitions, and the selected 32 MiB-stack extension passed through 6,000.

At 4,000 repetitions, compressor time was about 13 ms for mixed and variable-only chains, about 8 ms for balanced mixed, and about 51 ms for literal-only. At 6,000 with the larger stack, literal-only reached about 140 ms while the other families remained roughly 20–40 ms. Maximum RSS stayed below about 30 MiB in the extension.

The old mixed/variable crash pattern therefore does not reproduce at the previously interesting scale. Literal-only constant folding is measurably more expensive, but no consequential current boundary or owning function has been demonstrated.

Disposition: **negative result / stop implementation work**. Reopen only for a larger realistic workload, repeated benchmark showing consequential scaling, useful profile, or current failure under a declared runtime/stack configuration.

Durable result: `programmes/web-tooling-runtime-correctness/scouts/swc-runtime-semantics-and-recovery/long-concat-scaling-2026-08-11.md`.

## Evidence we can produce

- reduced JavaScript programs with runtime-observable callbacks or exceptions;
- utility-level and consumer-level target regressions in the owned fork;
- interrupted-writer and invalid-cache filesystem tests;
- focused crate tests and exact-head CI receipts;
- source-level consumer maps for value-discarding optimizations;
- controlled size/time/resource curves for generated source.

## Entry standard

A branch should identify an observable semantic, recovery, compatibility, or measured resource property; the likely owning code boundary; and an executable way to distinguish competing explanations. Existing public issues and recent fixes are context, not a task menu.

## Stop conditions

- source reading or a target-native test disproves the suspected behavior;
- the observation is already protected by an equivalent regression;
- the consequence depends on an unsupported usage claim;
- a proposed optimization has no measurement;
- the only remaining work is cosmetic documentation or style cleanup;
- a broad redesign is required before a bounded behavior has been demonstrated.

## Upstream boundary

Third-party upstream is read-only to automated Fieldwork workers. Candidate tests, patches, benchmarks, and human-facing packets belong in Fieldwork or `teamleaderleo/swc`; any upstream interaction is manual human work.
