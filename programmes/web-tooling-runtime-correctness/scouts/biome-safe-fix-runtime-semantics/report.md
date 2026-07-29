# Biome safe-fix runtime-semantics audit

## In simple words

This lane audits Biome JavaScript and TypeScript transformations labelled safe and checks whether they preserve executable behaviour.

Two high-confidence findings now survive self-review:

1. **`style/useObjectSpread`** is opt-in, but its safe fix flattens accessor-bearing `Object.assign()` calls and can suppress setters, delay or repeat getters, and change property descriptors.
2. **`style/useArrayLiterals`** is recommended and its safe fix rewrites `Array(...args)` to `[...args]`. When the runtime argument list contains one number, this changes a sparse array of that length into a dense one-element array containing the number.

Both findings reproduce with released `@biomejs/biome@2.5.6` under ordinary `lint --write`. Both have narrow applicability corrections already demonstrated by the corresponding ESLint rules.

**Current conclusion:** retain both as promotion-ready defect candidates after independent review. `useObjectSpread` has narrower exposure because the rule is not recommended. `useArrayLiterals` has broader exposure because it is recommended, although the failing form still requires a spread argument whose runtime expansion is exactly one numeric value.

## Identity

- Fieldwork issue: #89
- Fieldwork PR: #97
- Parent scout: #27
- Programme: #15, Web tooling and runtime correctness
- Target hub: #6, Biome
- Worker: `chatgpt:gpt-5.6-thinking`
- Initial pass date: 2026-07-30
- Review and expansion date: 2026-07-30
- Target release: `@biomejs/biome@2.5.6`
- Matching source revision: `biomejs/biome@d890b39c3ef21040bded453d9af91e1b301a0d67`
- Latest combined validation run: `30487711008`, job `90697449948`
- Upstream contact authorized: `no`
- Upstream interaction performed: `none`

## Review method

The findings were challenged rather than accepted from the first minimized output.

For each retained case, this pass checked:

- the released package, not only a hand-written before/after model;
- current and release-matching Biome source;
- ECMAScript runtime semantics;
- the source rule Biome identifies as the same rule;
- implementation and safe-classification history;
- current open and closed issue and pull-request searches;
- realistic failure modes and limiting conditions;
- the narrowest plausible applicability correction.

The review also looked for reasons the behaviour might be intentional. No reviewed source or discussion was found that intentionally accepts either retained semantic change as part of a safe fix.

---

## Finding 1: safe `useObjectSpread` flattens accessors

### State

`promote after independent review`

### Confidence

High. Source inspection, ECMAScript semantics, ESLint's explicit guard, native Node comparison, and the released Biome binary agree.

### Source boundary

`crates/biome_js_analyze/src/lint/style/use_object_spread.rs` declares `FixKind::Safe` and identifies ESLint `prefer-object-spread` as the same source rule.

The applicability check verifies that:

- the callee is the global `Object.assign`;
- the first argument is an object expression;
- later call arguments are not spread arguments.

It does not inspect object-expression members for getters, setters, or other special property-definition semantics.

The action then appends the members of every object-expression argument directly into one replacement object literal. Non-object expressions become object spreads.

Source references:

- https://redirect.github.com/biomejs/biome/blob/d890b39c3ef21040bded453d9af91e1b301a0d67/crates/biome_js_analyze/src/lint/style/use_object_spread.rs
- https://redirect.github.com/biomejs/biome/pull/6129

### Why the forms are not equivalent

For each enumerable source property, `Object.assign(target, source)` reads with `Get` and writes to the target with `Set`.

Object-literal property definitions instead create properties while the new object is constructed. A getter or setter copied syntactically into the replacement remains an accessor definition.

Observable differences include:

- a setter on the first object literal is invoked by `Object.assign`, but overwritten without invocation in the flattened literal;
- a getter on a later object literal is invoked during `Object.assign` and copied as a data value, but remains a getter after flattening;
- descriptor kind changes between accessor and data property;
- side effects and exceptions move from construction time to later property access.

Specification references:

- https://tc39.es/ecma262/multipage/fundamental-objects.html#sec-object.assign
- https://tc39.es/ecma262/multipage/ecmascript-language-expressions.html#sec-object-initializer

### Released-binary reproduction

Before the fix:

```json
{"targetSetter":{"calls":2,"propertyKind":"accessor","value":null},"sourceGetter":{"readsBeforeValue":1,"readsAfterValue":1,"propertyKind":"data","value":7}}
```

Biome 2.5.6 reported:

```text
Checked 1 file in 2ms. Fixed 1 file.
```

After the safe fix:

```json
{"targetSetter":{"calls":0,"propertyKind":"data","value":2},"sourceGetter":{"readsBeforeValue":0,"readsAfterValue":1,"propertyKind":"accessor","value":7}}
```

Latest retained output is in workflow run `30487711008`, job `90697449948`.

### Concrete destructive scenarios

These are consequences of the demonstrated mechanism, not claims about measured prevalence.

#### Validation or normalization setter is bypassed

```js
const config = Object.assign(
  {
    set timeout(value) {
      if (!Number.isFinite(value) || value < 0) throw new RangeError("timeout");
      this._timeout = Math.floor(value);
    },
  },
  userOptions,
);
```

The original invokes validation. Flattening can replace the setter with an unchecked `timeout` data property, allowing invalid configuration to pass silently.

#### Reactive or invalidation setter is skipped

A setter can mark a cache dirty, notify observers, update a registry, or synchronize a second field. Flattening can produce the final visible value while omitting the required side effect, leaving derived state stale.

#### Snapshot getter becomes a live getter

```js
const request = Object.assign({}, {
  get nonce() {
    return issueNonce();
  },
});
```

The original reads once and stores a snapshot. The flattened result retains the getter, so repeated reads may issue multiple nonces, tokens, timestamps, sequence numbers, or destructive queue reads.

#### Failure timing moves

A getter that throws during construction provides an early, local failure. After flattening, the same exception may occur much later when an unrelated consumer reads the property, complicating rollback and error attribution.

#### Descriptor-sensitive code changes

Reflection, mocking, serializers, dependency injection, and object-hardening code may distinguish data and accessor descriptors with `Object.getOwnPropertyDescriptor`. The released reproduction changes that descriptor category.

### Severity and exposure

This is not a default-on ecosystem-wide break:

- `useObjectSpread` is not recommended;
- users must enable it explicitly;
- the retained cases require accessor-bearing object literals.

It remains a meaningful safety defect because ordinary safe fix-all can suppress execution and change object shape. The appropriate wording is **narrow exposure, direct runtime impact, high-confidence missing applicability guard**.

### Ecosystem comparison

ESLint's `prefer-object-spread` implementation explicitly declines multi-argument calls when any object-expression argument contains a getter or setter. Its test suite includes the same target-setter and source-accessor shapes as non-fixable cases.

References:

- https://redirect.github.com/eslint/eslint/blob/main/lib/rules/prefer-object-spread.js
- https://redirect.github.com/eslint/eslint/blob/main/tests/lib/rules/prefer-object-spread.js

Biome's valid suite omits those accessor cases:

- https://redirect.github.com/biomejs/biome/blob/d890b39c3ef21040bded453d9af91e1b301a0d67/crates/biome_js_analyze/tests/specs/style/useObjectSpread/valid.js

### Why this likely happened

The history supports an incomplete port more strongly than an intentional tradeoff:

1. Biome issue #4319 requested implementation of ESLint `prefer-object-spread`.
2. PR #6129 implemented a fresh Rust transformation and marked it safe.
3. Review explicitly requested more ESLint tests.
4. More tests were added, but ESLint's accessor block was still omitted.
5. The direct syntax-flattening implementation is correct for ordinary data properties but skips the semantic exception encoded separately by ESLint.
6. A later bulk promotion moved the rule from nursery to stable `style` without a rule-specific semantic re-audit.

### Plausible correction

- When the call has more than one argument, decline the safe fix if any object-expression argument contains a getter or setter.
- Retain ordinary data-property cases.
- Add ESLint's accessor cases to Biome's valid/non-fixable regression suite.
- The diagnostic may remain even when the safe action is withheld.

### Adjacent hardening question: special `__proto__`

```js
const proto = { inherited: 42 };
Object.assign({}, { __proto__: proto });
```

The source object literal changes its own prototype but has no enumerable own `__proto__` property, so the `Object.assign` target keeps its normal prototype. Flattening to `({ __proto__: proto })` gives the result object the custom prototype.

That can change inherited lookup and prototype identity, and in security-sensitive code can undermine assumptions that a result is a plain object. ESLint's accessor guard does not cover this form, so it remains a separate hardening question rather than part of the minimal accessor packet.

---

## Finding 2: safe `useArrayLiterals` changes dynamic constructor arity

### State

`promote after independent review`

### Confidence

High. The rule's own documented target, source implementation, ECMAScript `Array` constructor semantics, ESLint's fix boundary, and released Biome output all agree.

### Source boundary

`crates/biome_js_analyze/src/lint/style/use_array_literals.rs` declares the rule recommended and its fix safe.

The rule deliberately reports:

```js
Array(...args);
```

Its action converts each call argument directly into an array-literal element, producing:

```js
[...args];
```

The applicability check exempts a known single non-spread argument such as `Array(3)`, but it cannot know how many values a spread argument will produce at runtime.

Source reference:

- https://redirect.github.com/biomejs/biome/blob/d890b39c3ef21040bded453d9af91e1b301a0d67/crates/biome_js_analyze/src/lint/style/use_array_literals.rs

### Why the forms are not equivalent

The `Array` constructor has special one-number behaviour:

```js
Array(3)
```

creates a sparse array with `length === 3` and no own index properties.

An array literal does not have that constructor overload:

```js
[3]
```

creates a dense one-element array whose first element is `3`.

Therefore, when `args` evaluates to `[3]`:

```js
Array(...args)
```

and:

```js
[...args]
```

have different length, keys, membership, iteration, and downstream callback behaviour.

### Released-binary reproduction

Before the fix:

```json
{"length":3,"keys":[],"hasIndexZero":false,"first":null}
```

Biome 2.5.6 reported:

```text
Checked 1 file in 2ms. Fixed 1 file.
```

The rewritten source was:

```js
const result = [...args];
```

After the safe fix:

```json
{"length":1,"keys":["0"],"hasIndexZero":true,"first":3}
```

The reproduction passed in workflow run `30487711008`, job `90697449948` on Node 22.23.1.

### Concrete destructive scenarios

#### Capacity or length forwarding helper breaks

```js
function makeArray(...args) {
  return Array(...args);
}

const slots = makeArray(1_000_000);
```

The original returns an array with length one million. The safe fix returns `[1_000_000]`, whose length is one.

Code using the result as a slot table, bitmap companion, indexed work queue, or pre-sized logical container now has the wrong cardinality.

#### Generic factory changes its one-argument mode

A wrapper may intentionally preserve the dual API of `Array`: one numeric argument means length, while multiple arguments mean elements. Rewriting the forwarding call removes that runtime distinction.

#### Sparse-array callback behaviour changes

Array methods such as `map`, `forEach`, and `filter` skip holes. A dense `[3]` invokes callbacks once with value `3`; a sparse `Array(3)` invokes none of those callbacks for the three holes.

#### Key enumeration and serialization change

`Object.keys(Array(3))` is empty, while `Object.keys([3])` contains `"0"`. Code that distinguishes allocated slots from absent slots will see different data. JSON and iteration behaviour also differ.

### Severity and exposure

This rule is recommended, so the exposure is broader than the accessor finding. The failing condition is still specific:

- the constructor call contains spread syntax;
- after expansion, the total runtime argument count is exactly one;
- the sole value is numeric.

The impact can nevertheless be large because the numeric value directly controls the original array length. The appropriate wording is **recommended safe fix, narrow trigger, potentially large cardinality change**.

### Ecosystem comparison

Biome identifies ESLint `no-array-constructor` as the same source rule.

ESLint reports spread-bearing forms but deliberately withholds automatic fixing when dynamic spread arity may produce the special one-number case. It offers a reviewable suggestion instead. Its tests show `Array(...args)` and `new Array(...args)` with no automatic output.

References:

- https://redirect.github.com/eslint/eslint/blob/main/lib/rules/no-array-constructor.js
- https://redirect.github.com/eslint/eslint/blob/main/tests/lib/rules/no-array-constructor.js

ESLint still auto-fixes a form such as `Array(5, 6, ...args)` because two statically present arguments guarantee that the constructor cannot enter its one-number length mode.

### Why this likely happened

The history is unusually clear:

1. PR #4416 expanded `useArrayLiterals`, added the fix, and explicitly included `Array(...args)` as an invalid case.
2. That change described the fix as unsafe.
3. PR #6063 later upgraded a batch of unsafe fixes to safe, including `useArrayLiterals`.
4. The PR checklist described reviewing safe fixes in terms of trivia handling, and the test plan was snapshot updates.
5. No semantic guard was added for runtime spread arity.
6. The upgrade therefore changed classification without narrowing the already-dynamic transformation.

History references:

- https://redirect.github.com/biomejs/biome/pull/4416
- https://redirect.github.com/biomejs/biome/pull/6063

### Plausible correction

Mirror the established ESLint boundary:

- keep the diagnostic;
- do not offer an automatic safe fix when fewer than two non-spread arguments are statically present and spread arguments can make the runtime arity ambiguous;
- retain safe fixing for zero arguments and for calls guaranteed to have at least two arguments;
- optionally retain the ambiguous rewrite only as an unsafe or explicit suggestion.

Add regression cases covering:

- `Array(...args)` with `args = [3]`;
- `new Array(...args)` with `args = [3]`;
- `Array(5, ...args)` where `args` may be empty;
- safe control `Array(5, 6, ...args)`.

---

## Explored candidate: `useFlatMap`

`complexity/useFlatMap` is recommended, marked safe, and rewrites `.map(callback).flat()` to `.flatMap(callback)` based only on member names and argument counts.

Two semantic concerns exist:

1. A custom receiver may implement `map` and return an object with `flat`, while its `flatMap` method is absent or behaves differently.
2. Even built-in Array subclassing can differ through `Symbol.species`: `map().flat()` performs species creation twice, while `flatMap()` performs it once.

A native Node probe using only Array subclasses produced different result constructors (`Third` for `map().flat()`, `Second` for `flatMap()`).

This is not promoted yet because:

- the upstream Unicorn source rule also accepts a broad receiver heuristic, although it skips some known non-array receivers;
- the practical prevalence and intended safety convention need more review;
- no released-Biome fixture is retained in Fieldwork yet.

Current disposition: **keep as a scoped follow-up, not a finding**.

## Other reviewed work and coordination notes

### Fieldwork review queue PR #105

The review queue correctly identifies the Biome work as needing independent semantic review, but its pinned report revision predates this expansion. Its Biome card should be revised to:

- cite the latest report head;
- split `useObjectSpread` and `useArrayLiterals` into separate review decisions;
- preserve their different exposure profiles;
- mention the retained `useFlatMap` candidate only as unpromoted exploration.

### First-pass negatives retained

- `useWhile` only applies when both initializer and update are absent; no runtime divergence was retained.
- `useNodeAssertStrict` intentionally requests stricter assertion behaviour; the semantic change is the rule's stated policy rather than a hidden applicability error.
- Re-export ordering remains the accepted organizer-policy caveat from #27.
- Existing reports for named function `.name`, decorator metadata under `useImportType`, and import-extension rewriting remain excluded from novel-candidate work.

## Duplicate search

Repeated targeted searches of current open and closed Biome issues and pull requests did not surface exact reports for:

- `useObjectSpread` changing getter or setter semantics;
- `useArrayLiterals` changing `Array(...args)` when spread expansion yields one number.

Queries covered rule names, source-rule names, safe-fix terms, accessors, sparse arrays, spread arguments, runtime arity, length, and constructor semantics.

No exact duplicate surfaced. This is a targeted search, not a mathematical guarantee, and should be repeated immediately before any authorized upstream submission.

## Biome linter issue-template requirements

Biome's `.github/ISSUE_TEMPLATE/02_lint_bug.yml` says reports that do not follow the template will be closed. It requires:

1. environment output from `biome rage --linter`;
2. the rule name;
3. a playground link, or a reproduction repository when the playground is insufficient;
4. expected result;
5. Code of Conduct confirmation.

The eventual reporter should provide separate reports because the rules, mechanisms, exposure, and fixes differ.

### Packet for `useObjectSpread`

- Rule: `useObjectSpread`
- Minimal target-setter or source-getter case
- Before and after runtime output and descriptors
- Safe-fix source classification and unconditional flattening
- ESLint accessor guard and regression tests
- Expected result: no safe action for accessor-bearing multi-argument calls

### Packet for `useArrayLiterals`

- Rule: `useArrayLiterals`
- `const args = [3]; const result = Array(...args);`
- Before and after length, keys, membership, and first value
- Safe/recommended source classification and direct argument-to-element conversion
- ESLint's suggestion-only treatment of ambiguous spread forms
- Expected result: no automatic safe fix when runtime spread arity can enter `Array`'s one-number length mode

Do not contact upstream without separate authorization.

## Durable evidence

- Report: this file
- Accessor reproduction: `reproductions/use-object-spread-accessors/`
- Array-spread reproduction: `reproductions/use-array-literals-spread/`
- Pull request: #97
- Latest workflow run: `30487711008`
- Latest reproduction job: `90697449948`
- Workflow branch head tested: `aacff17809100979c497553d0b3ccc80e549b24a`

## Disposition

- `useObjectSpread` accessors: `promotion-ready after independent review`
- `useArrayLiterals` spread arity: `promotion-ready after independent review`
- `useFlatMap` receiver/species semantics: `retain as unpromoted follow-up`
- Upstream contact: `not authorized`

## Upstream boundary

Upstream contact authorized: `no`

Interaction performed: `none`
