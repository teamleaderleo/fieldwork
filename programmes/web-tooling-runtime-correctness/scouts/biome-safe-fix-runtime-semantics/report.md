# Biome safe-fix runtime-semantics audit

## In simple words

This lane audits Biome JavaScript and TypeScript transformations labelled safe and checks whether they preserve realistic executable behaviour.

The first retained candidate is `style/useObjectSpread`. Biome 2.5.6 marks its fix safe and converts `Object.assign()` calls whose first argument is an object literal into one flattened object literal. JavaScript does not treat those forms as equivalent when getters or setters are present.

## Identity

- Fieldwork issue: #89
- Parent scout: #27
- Programme: #15, Web tooling and runtime correctness
- Target hub: #6, Biome
- Worker: `chatgpt:gpt-5.6-thinking`
- Initial pass date: 2026-07-30
- Target release: `@biomejs/biome@2.5.6`
- Matching source revision: `biomejs/biome@d890b39c3ef21040bded453d9af91e1b301a0d67`
- Upstream contact authorized: `no`
- Upstream interaction performed: `none`

## Current finding candidate: `useObjectSpread` flattens accessors

### Source boundary

`crates/biome_js_analyze/src/lint/style/use_object_spread.rs` declares `FixKind::Safe`. Its action iterates every `Object.assign()` argument and directly appends the members of every object-expression argument into the replacement object literal. There is no getter/setter guard.

### Why this is consequential

`Object.assign(target, source)` uses ordinary property assignment semantics on the target and reads source properties. Flattening object-literal members instead constructs a new literal definition list.

That distinction is observable:

- a setter on the first object literal is invoked by `Object.assign`, but is overwritten without invocation in the flattened literal;
- a getter on a later object literal is invoked by `Object.assign`, producing a data property, but remains a getter in the flattened literal;
- special object-literal `__proto__` syntax can also change prototype behaviour when flattened.

### Ecosystem comparison

Biome identifies the rule as corresponding to ESLint `prefer-object-spread`. ESLint's current implementation explicitly rejects autofixing multi-argument calls when any object-expression argument contains a getter or setter. Its tests classify those exact forms as valid/non-fixable. Biome copied much of the ESLint rule surface but does not implement this guard.

### Initial executable evidence

A local native Node 22 comparison of the source-supported before and after forms produced:

- target setter: before `calls=2` and the property remains an accessor; after `calls=0` and the property becomes a data property with value `2`;
- source getter: before the getter is read during assignment and the result owns a data property; after the result retains the getter;
- `__proto__` object-literal and data-property cases also produced different prototypes or own-property shapes.

The owned reproduction under `reproductions/use-object-spread-accessors/` runs the released Biome binary to confirm the exact emitted rewrite.

### Current assessment

`retain as a high-confidence candidate pending released-binary confirmation`

This is stronger than the prior re-export-order caveat because it is:

- a direct single-expression runtime change;
- a realistic JavaScript accessor pattern;
- a documented divergence from the guard in the source rule Biome cites;
- narrowly correctable by declining the fix when any flattened object expression contains an accessor, while preserving the diagnostic or other safe cases.

## First-pass surfaces ruled down

- `useNodeAssertStrict` intentionally changes assertion semantics and is an opt-in policy rule; its safe classification may be broad, but the behaviour is the rule's explicit purpose rather than an implementation oversight.
- Re-export ordering remains the accepted organizer-policy caveat concluded in #27.
- Known upstream reports for named function `.name`, decorator metadata under `useImportType`, and import-extension rewriting remain excluded from novel-candidate work.

## Next source checks

- verify the released Biome output and exact diagnostic classification;
- inspect other rules ported from ESLint for omitted autofix guards;
- prioritize object property, coercion, and control-flow transformations with executable comparisons;
- search upstream issues and pull requests again before any promotion decision.

## Upstream boundary

Upstream contact authorized: `no`

Interaction performed: `none`
