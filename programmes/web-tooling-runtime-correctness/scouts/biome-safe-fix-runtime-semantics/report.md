# Biome safe-fix runtime-semantics audit

## In simple words

This lane audits Biome JavaScript and TypeScript transformations labelled safe and checks whether they preserve realistic executable behaviour.

The first retained finding is `style/useObjectSpread`. Biome 2.5.6 marks its fix safe and converts `Object.assign()` calls whose first argument is an object literal into one flattened object literal. JavaScript does not treat those forms as equivalent when getters or setters are present, and the released binary changes both execution timing and property descriptors.

## Identity

- Fieldwork issue: #89
- Fieldwork PR: #97
- Parent scout: #27
- Programme: #15, Web tooling and runtime correctness
- Target hub: #6, Biome
- Worker: `chatgpt:gpt-5.6-thinking`
- Initial pass date: 2026-07-30
- Target release: `@biomejs/biome@2.5.6`
- Matching source revision: `biomejs/biome@d890b39c3ef21040bded453d9af91e1b301a0d67`
- Validation run: `30479636589`, job `90670032732`
- Upstream contact authorized: `no`
- Upstream interaction performed: `none`

## Finding 1: safe `useObjectSpread` flattens accessors

### State

`promote to focused finding after independent review`

### Confidence

High. Source inspection, the corresponding ESLint safety guard, native Node comparison, and the released Biome 2.5.6 binary all agree.

### Source boundary

`crates/biome_js_analyze/src/lint/style/use_object_spread.rs` declares `FixKind::Safe`. Its action iterates every `Object.assign()` argument and directly appends the members of every object-expression argument into the replacement object literal. There is no getter/setter guard.

### Why this is consequential

`Object.assign(target, source)` uses ordinary property assignment semantics on the target and reads source properties. Flattening object-literal members instead constructs a new literal definition list.

That distinction is observable:

- a setter on the first object literal is invoked by `Object.assign`, but is overwritten without invocation in the flattened literal;
- a getter on a later object literal is invoked by `Object.assign`, producing a data property, but remains a getter in the flattened literal;
- special object-literal `__proto__` syntax can also change prototype behaviour when flattened.

### Released-binary reproduction

The owned fixture ran on Ubuntu 24.04 with Node 22.23.1 and `@biomejs/biome@2.5.6`.

Before the fix:

```json
{"targetSetter":{"calls":2,"propertyKind":"accessor","value":null},"sourceGetter":{"readsBeforeValue":1,"readsAfterValue":1,"propertyKind":"data","value":7}}
```

Biome reported:

```text
Version: 2.5.6
Checked 1 file in 2ms. Fixed 1 file.
```

After the safe fix:

```json
{"targetSetter":{"calls":0,"propertyKind":"data","value":2},"sourceGetter":{"readsBeforeValue":0,"readsAfterValue":1,"propertyKind":"accessor","value":7}}
```

The run succeeded because the script requires before and after output to differ. The rewritten source visibly flattened both accessor-bearing object literals.

### Ecosystem comparison

Biome identifies the rule as corresponding to ESLint `prefer-object-spread`. ESLint's current implementation explicitly rejects autofixing multi-argument calls when any object-expression argument contains a getter or setter. Its tests classify those exact forms as valid/non-fixable. Biome copied much of the ESLint rule surface but does not implement this guard.

### Duplicate search

Targeted searches of current Biome issues did not surface an exact report for `useObjectSpread` changing getter/setter semantics. This is not an exhaustive guarantee, so duplicate search must be repeated before any upstream decision.

### Plausible correction

Decline the fix when a multi-argument `Object.assign()` contains an object-expression argument with a getter or setter. This mirrors the narrow ESLint guard, preserves the diagnostic if desired, and leaves ordinary data-property cases fixable.

A broader hardening pass should also decide whether special `__proto__` object-literal members require exclusion.

### Why this is stronger than the re-export case

- It is a direct single-expression runtime change.
- It uses ordinary JavaScript accessor behavior rather than deliberately order-sensitive module architecture.
- The source rule Biome cites already has the missing safety guard.
- A narrow correction exists without disabling the feature.

## First-pass surfaces ruled down

- `useWhile` only applies when both initializer and update are absent and performs a direct `for (; test;)` to `while (test)` replacement; no runtime divergence was retained in this pass.
- `useNodeAssertStrict` intentionally changes assertion semantics and is an opt-in policy rule; its behavior is the rule's explicit purpose rather than an omitted implementation guard.
- Re-export ordering remains the accepted organizer-policy caveat concluded in #27.
- Known upstream reports for named function `.name`, decorator metadata under `useImportType`, and import-extension rewriting remain excluded from novel-candidate work.

## Next source checks

- inspect other rules ported from ESLint for omitted autofix guards;
- prioritize property descriptors, coercion, computed-key evaluation, and control-flow transformations;
- test interactions among multiple safe fixes and repeated `check --write` passes;
- repeat current upstream issue and pull-request searches before promotion.

## Durable evidence

- Report: this file
- Reproduction: `reproductions/use-object-spread-accessors/`
- Pull request: #97
- Actions run: `30479636589`
- Job: `90670032732`
- Exact tested branch head: `bf6de4836589b6f8016c1f64b3e5c3449ba75d00`

## Upstream boundary

Upstream contact authorized: `no`

Interaction performed: `none`
