# Biome safe-fix runtime-semantics audit

## In simple words

This lane audits Biome JavaScript and TypeScript transformations labelled safe and checks whether they preserve realistic executable behaviour.

The first retained finding is `style/useObjectSpread`. Biome 2.5.6 marks its fix safe and converts `Object.assign()` calls whose first argument is an object literal into one flattened object literal. JavaScript does not treat those forms as equivalent when getters or setters are present, and the released binary changes execution timing, setter invocation, and property descriptors.

**Current conclusion:** this is a high-confidence Biome defect candidate. The rule is not recommended and must be enabled explicitly, which limits default exposure. Once enabled, however, its safe fix may be applied automatically by `--write` or editor fix-all actions without review. That conflicts with Biome's documented safe-fix contract.

## Identity

- Fieldwork issue: #89
- Fieldwork PR: #97
- Parent scout: #27
- Programme: #15, Web tooling and runtime correctness
- Target hub: #6, Biome
- Worker: `chatgpt:gpt-5.6-thinking`
- Initial pass date: 2026-07-30
- Follow-up synthesis date: 2026-07-30
- Target release: `@biomejs/biome@2.5.6`
- Matching source revision: `biomejs/biome@d890b39c3ef21040bded453d9af91e1b301a0d67`
- Validation run: `30479636589`, job `90670032732`
- Upstream contact authorized: `no`
- Upstream interaction performed: `none`

## Finding 1: safe `useObjectSpread` flattens accessors

### State

`promote to focused finding after independent review`

### Confidence

High. Source inspection, ECMAScript semantics, the corresponding ESLint safety guard, native Node comparison, and the released Biome 2.5.6 binary all agree.

### Source boundary

`crates/biome_js_analyze/src/lint/style/use_object_spread.rs` declares `FixKind::Safe` and identifies ESLint `prefer-object-spread` as the same source rule.

The rule's applicability check verifies that:

- the callee is the global `Object.assign`;
- the first argument is an object expression;
- later call arguments are not spread arguments.

It does not inspect object-expression members for getters, setters, or other property-definition semantics.

The action then iterates every argument and directly appends the members of each object-expression argument into the replacement object literal. Non-object expressions become object spreads. There is no accessor guard.

Source references:

- https://redirect.github.com/biomejs/biome/blob/d890b39c3ef21040bded453d9af91e1b301a0d67/crates/biome_js_analyze/src/lint/style/use_object_spread.rs
- https://redirect.github.com/biomejs/biome/pull/6129

### Why this is consequential

`Object.assign(target, source)` and object-literal construction use different abstract operations.

For each enumerable source property, `Object.assign`:

1. reads the source property with `Get`;
2. writes it to the target with `Set`.

Object-literal data properties and spread properties instead define own data properties on the newly constructed object. Getter and setter definitions remain accessor definitions when copied syntactically into the new literal.

That distinction is observable:

- a setter on the first object literal is invoked by `Object.assign`, but is overwritten without invocation in the flattened literal;
- a getter on a later object literal is invoked by `Object.assign`, producing a data property, but remains a getter in the flattened literal;
- descriptor kind changes between accessor and data property;
- side-effect timing changes from construction time to later property access.

Specification references:

- `Object.assign`: https://tc39.es/ecma262/multipage/fundamental-objects.html#sec-object.assign
- object initializers and property-definition evaluation: https://tc39.es/ecma262/multipage/ecmascript-language-expressions.html#sec-object-initializer

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

### Severity and exposure

This is not a default-on ecosystem-wide break:

- `useObjectSpread` is not recommended;
- users must explicitly enable the rule or its group;
- the affected forms require accessor-bearing object literals.

It is still a meaningful safety defect:

- Biome documents safe fixes as guaranteed not to change code semantics;
- safe fixes can be applied without explicit review from the CLI or on save;
- this fix can suppress setter calls, delay getter calls, and change property descriptors.

The appropriate characterization is **narrow blast radius, concrete runtime impact, high-confidence safety misclassification or missing applicability guard**.

## Ecosystem comparison

Biome identifies this rule as the same as ESLint `prefer-object-spread`.

ESLint's implementation explicitly declines the transformation when a multi-argument `Object.assign` call contains an object-expression getter or setter. Its test suite classifies the exact target-setter and source-accessor forms as valid/non-fixable.

References:

- ESLint implementation: https://redirect.github.com/eslint/eslint/blob/main/lib/rules/prefer-object-spread.js
- ESLint regression cases: https://redirect.github.com/eslint/eslint/blob/main/tests/lib/rules/prefer-object-spread.js

Biome's current valid suite contains only basic call-shape exclusions and does not contain ESLint's accessor cases:

- https://redirect.github.com/biomejs/biome/blob/d890b39c3ef21040bded453d9af91e1b301a0d67/crates/biome_js_analyze/tests/specs/style/useObjectSpread/valid.js

## Why this likely happened

The available project history supports an implementation omission more strongly than an intentional semantic tradeoff.

1. Biome issue #4319 requested implementation of ESLint `prefer-object-spread`.
2. PR #6129 implemented a fresh Rust transformation and marked its fix safe.
3. During review, a maintainer explicitly observed that ESLint had substantially more tests and requested that more be added.
4. The author replied that more ESLint tests had been added, but the final Biome suite still omitted ESLint's getter/setter block.
5. The implementation flattens syntax nodes directly, which is simple and correct for ordinary data-property literals but skips the semantic exception that ESLint encodes separately.
6. A later bulk promotion moved the rule from nursery to stable `style`; that PR's stated test plan was that CI should remain green and did not re-audit this rule's safe-fix semantics.

History references:

- implementation request: https://redirect.github.com/biomejs/biome/issues/4319
- implementation PR and review: https://redirect.github.com/biomejs/biome/pull/6129
- bulk promotion PR: https://redirect.github.com/biomejs/biome/pull/7137

### Alternative explanations considered

**"The rule is opt-in, so semantic changes are accepted."**

Opt-in status can justify offering an opinionated diagnostic. It does not justify classifying a runtime-changing rewrite as safe. Biome distinguishes rule enablement from fix safety and allows unsafe fixes to remain available for manual review.

**"Object spread is generally preferred, so the rewrite is close enough."**

The style preference is reasonable, and ordinary data-property cases are usually equivalent. The finding concerns the automatic applicability boundary, not the existence of the rule.

**"Safe is only a loose recommendation."**

Biome's current linter documentation states that safe fixes are guaranteed not to change semantics and can be applied without explicit review. Unsafe fixes are the category intended for transformations that may change semantics.

**"The different behaviour is too artificial."**

Getters and setters are standard object-literal features. The reproduction needs no proxy, framework, bundler, global mutation, or deliberately order-sensitive module graph.

No reviewed source or discussion was found that intentionally accepts accessor changes for this rule.

## Plausible correction

The narrowest established correction is:

- when the call has more than one argument, decline the fix if any object-expression argument contains a getter or setter;
- retain the existing transformation for ordinary data-property object literals;
- add the corresponding ESLint valid/non-fixable cases to Biome's regression suite.

This mirrors ESLint's guard and directly fixes the demonstrated accessor cases.

The diagnostic could remain, but the automatic fix should not be offered as safe where the transformation is not semantics-preserving.

## Adjacent hardening question: special `__proto__`

A separate native-Node check confirms another difference in the same flattening strategy:

```js
const proto = { inherited: 42 };
Object.assign({}, { __proto__: proto });
```

The source object literal changes its own prototype but has no enumerable own `__proto__` property, so `Object.assign` leaves the target's prototype unchanged. Flattening produces:

```js
({ __proto__: proto });
```

which gives the result object the custom prototype. This changes inherited lookup and the object's prototype identity.

ESLint's current accessor guard does not appear to cover this form. Therefore, matching ESLint is a strong minimal fix for the proven accessor bug, but it should not be treated as a complete proof that all flattenable object expressions commute with `Object.assign`.

Keep this as a hardening question during review rather than expanding the minimal accessor report unless released-Biome evidence is added to the retained reproduction.

## Duplicate search

Repeated targeted searches of current open and closed Biome issues and pull requests did not surface an exact report for `useObjectSpread` changing getter/setter semantics. Queries covered:

- `useObjectSpread` with getter, setter, accessor, and safe-fix terms;
- `Object.assign` with getter, setter, spread, and runtime-behaviour terms;
- `prefer-object-spread` parity and fixes.

No exact duplicate surfaced. This remains a targeted search rather than a mathematical guarantee.

## Biome linter issue-template requirements

Biome's current `.github/ISSUE_TEMPLATE/02_lint_bug.yml` states that reports not following the template will be closed. It requires:

1. **Environment information** — output of `biome rage --linter`, reviewed for sensitive data.
2. **Rule name** — `useObjectSpread`.
3. **Playground link** — required; alternatively the template recommends `npm create @biomejs/biome-reproduction` when the playground is insufficient.
4. **Expected result** — a concise statement of the required behaviour.
5. **Code of Conduct** — confirmation checkbox.

Template reference:

- https://redirect.github.com/biomejs/biome/blob/main/.github/ISSUE_TEMPLATE/02_lint_bug.yml

### Evidence packet for later human synthesis

The eventual reporter should supply, in their own words:

- exact `biome rage --linter` output from the reporting environment;
- rule name `useObjectSpread`;
- the smallest target-setter or source-getter reproduction;
- the exact before/after output;
- the fact that ordinary `lint --write` applies the change as a safe fix;
- the current Biome source lines showing `FixKind::Safe` and unconditional object-expression flattening;
- ESLint's accessor guard and tests as implementation precedent;
- expected result: no safe fix should be offered for multi-argument accessor-bearing calls, or the fix should be classified unsafe until its applicability is narrowed.

Do not post or contact upstream from this lane without separate authorization.

## Why this is stronger than the re-export case

- It is a direct single-expression runtime change.
- It uses ordinary JavaScript accessor behaviour rather than deliberately order-sensitive module architecture.
- Biome identifies the rule as the same as an ESLint rule that already contains the missing guard.
- A narrow correction exists without disabling the feature.
- Biome's documented safe-fix contract directly covers the disputed behaviour.

## First-pass surfaces ruled down

- `useWhile` only applies when both initializer and update are absent and performs a direct `for (; test;)` to `while (test)` replacement; no runtime divergence was retained in this pass.
- `useNodeAssertStrict` intentionally changes assertion semantics and is an opt-in policy rule; its behaviour is the rule's explicit purpose rather than an omitted implementation guard.
- Re-export ordering remains the accepted organizer-policy caveat concluded in #27.
- Known upstream reports for named function `.name`, decorator metadata under `useImportType`, and import-extension rewriting remain excluded from novel-candidate work.

## Next source checks

- independently review the accessor guard and whether the diagnostic should remain without a fix;
- decide whether to add released-Biome coverage for special `__proto__` before broadening the finding;
- inspect other ESLint-sourced rules for omitted autofix guards;
- prioritize property descriptors, coercion, computed-key evaluation, and control-flow transformations;
- test interactions among multiple safe fixes and repeated `check --write` passes;
- repeat current upstream issue and pull-request searches immediately before any authorized upstream action.

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
