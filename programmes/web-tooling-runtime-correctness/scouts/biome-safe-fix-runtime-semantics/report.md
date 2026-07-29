# Biome safe-fix runtime-semantics audit

## In simple words

This lane audits Biome JavaScript and TypeScript transformations labelled safe and checks whether they preserve executable behaviour.

Three high-confidence, apparently unreported findings now survive self-review:

1. **`style/useObjectSpread`** is opt-in, but its safe fix flattens accessor-bearing `Object.assign()` calls and can suppress setters, delay or repeat getters, and change property descriptors.
2. **`style/useArrayLiterals`** is recommended and rewrites `Array(...args)` to `[...args]`. If the runtime argument list contains one number, a sparse array of that length becomes a dense one-element array containing the number.
3. **`complexity/noUselessStringConcat`** is opt-in and folds string-plus-number expressions using Rust floating-point formatting. JavaScript's exponent notation can therefore become a different decimal string.

All three reproduce with released `@biomejs/biome@2.5.6` under ordinary `lint --write`.

A fourth reproduced issue in `useSimplifiedLogicExpression` is **not novel**: upstream issue #8577 is already confirmed and an open PR proposes the same right-literal restriction. It is retained only as evidence that the same unsafe-to-safe batch promotion deserves scrutiny.

**Current conclusion:** promote the three novel cases for independent review as separate findings. Their mechanisms, exposure, severity, and corrections differ and should not be collapsed into one upstream report.

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
- Upstream contact authorized: `no`
- Upstream interaction performed: `none`

## Review method

Each candidate was challenged rather than accepted from a constructed before/after example.

The review checked:

- the released package;
- current and release-matching Biome source;
- native Node output;
- applicable ECMAScript behaviour;
- source-rule implementations where Biome claims parity;
- rule implementation and fix-classification history;
- open and closed upstream issues and pull requests;
- realistic destructive consequences and limiting conditions;
- the narrowest plausible correction.

No reviewed source or discussion intentionally accepts the three retained semantic changes as part of a safe fix.

---

## Finding 1: safe `useObjectSpread` flattens accessors

### State

`promotion-ready after independent review`

### Confidence

High. Biome source, ECMAScript semantics, ESLint's explicit guard, native Node output, and the released Biome binary agree.

### Source boundary

`crates/biome_js_analyze/src/lint/style/use_object_spread.rs` declares `FixKind::Safe` and identifies ESLint `prefer-object-spread` as the same source rule.

The applicability check verifies the global `Object.assign`, an object-expression first argument, and the absence of call-level spread arguments. It does not inspect object members for getters or setters.

The action directly appends members of every object-expression argument into one replacement object literal. Non-object expressions become object spreads.

References:

- https://redirect.github.com/biomejs/biome/blob/d890b39c3ef21040bded453d9af91e1b301a0d67/crates/biome_js_analyze/src/lint/style/use_object_spread.rs
- https://redirect.github.com/biomejs/biome/pull/6129

### Why the forms are not equivalent

For each enumerable source property, `Object.assign(target, source)` reads with `Get` and writes with `Set`.

Object-literal definitions construct properties directly. A getter or setter copied syntactically into the replacement remains an accessor.

Observable differences include:

- a target setter is invoked by `Object.assign`, but can be overwritten without invocation after flattening;
- a source getter is read during `Object.assign` and copied as data, but remains a live getter after flattening;
- descriptor category changes;
- side effects and exceptions move in time.

Specification references:

- https://tc39.es/ecma262/multipage/fundamental-objects.html#sec-object.assign
- https://tc39.es/ecma262/multipage/ecmascript-language-expressions.html#sec-object-initializer

### Released-binary result

Before:

```json
{"targetSetter":{"calls":2,"propertyKind":"accessor","value":null},"sourceGetter":{"readsBeforeValue":1,"readsAfterValue":1,"propertyKind":"data","value":7}}
```

After Biome's safe fix:

```json
{"targetSetter":{"calls":0,"propertyKind":"data","value":2},"sourceGetter":{"readsBeforeValue":0,"readsAfterValue":1,"propertyKind":"accessor","value":7}}
```

Biome reported `Checked 1 file in 2ms. Fixed 1 file.`

### Concrete destructive scenarios

#### Validation or normalization is bypassed

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

The original invokes validation. Flattening can replace the setter with an unchecked data property.

#### Reactive or invalidation work is skipped

A setter may mark a cache dirty, notify observers, synchronize another field, or register a mutation. The rewrite can preserve the visible value while silently omitting required state updates.

#### A snapshot getter becomes live and repeatable

```js
const request = Object.assign({}, {
  get nonce() {
    return issueNonce();
  },
});
```

The original stores one snapshot. The rewrite retains a getter, so repeated reads may issue multiple nonces, tokens, timestamps, sequence numbers, or queue items.

#### Failure timing moves

A getter that throws during construction becomes a getter that may throw later from an unrelated consumer. That can move failure beyond transaction or cleanup boundaries.

#### Descriptor-sensitive code changes

Reflection, mocking, serializers, dependency injection, and hardening code may inspect own-property descriptors. The released reproduction changes accessor descriptors into data descriptors and vice versa.

### Severity and exposure

The rule is not recommended and must be enabled. The affected calls also require object-literal accessors. Exposure is therefore narrow, but the runtime impact is direct.

Characterization: **opt-in rule, narrow trigger, high-confidence execution and object-shape change**.

### Ecosystem comparison

ESLint's `prefer-object-spread` explicitly declines multi-argument calls when any object-expression argument contains a getter or setter. Its tests classify the same target-setter and source-getter shapes as non-fixable.

- https://redirect.github.com/eslint/eslint/blob/main/lib/rules/prefer-object-spread.js
- https://redirect.github.com/eslint/eslint/blob/main/tests/lib/rules/prefer-object-spread.js

Biome's valid suite omits that accessor block.

### Why this likely happened

1. Biome issue #4319 requested ESLint `prefer-object-spread`.
2. PR #6129 implemented a fresh Rust transformation and marked it safe.
3. Review requested more ESLint tests.
4. More tests were added, but the accessor block remained absent.
5. The direct syntax flattening is correct for ordinary data properties but omitted the semantic exception.
6. A later bulk promotion moved the rule from nursery to stable `style` without a rule-specific semantic audit.

### Plausible correction

- Withhold the safe fix for multi-argument calls containing object-expression getters or setters.
- Retain ordinary data-property cases.
- Add ESLint's accessor fixtures to Biome's valid/non-fixable suite.
- The diagnostic may remain when the action is withheld.

### Adjacent hardening question: special `__proto__`

```js
const proto = { inherited: 42 };
Object.assign({}, { __proto__: proto });
```

The source literal changes its own prototype but contributes no enumerable `__proto__` property, so the target keeps its normal prototype. Flattening to `({ __proto__: proto })` gives the result the custom prototype.

This can alter inherited lookup and plain-object assumptions. ESLint's accessor guard does not cover it, so it remains a separate hardening question rather than part of the minimal accessor report.

---

## Finding 2: safe `useArrayLiterals` changes dynamic constructor arity

### State

`promotion-ready after independent review`

### Confidence

High. The rule's documentation, implementation, ECMAScript constructor semantics, ESLint's fix boundary, and released output agree.

### Source boundary

`crates/biome_js_analyze/src/lint/style/use_array_literals.rs` marks the rule recommended and its fix safe.

It explicitly reports:

```js
Array(...args);
```

and converts call arguments directly into array-literal elements:

```js
[...args];
```

The applicability check exempts a statically visible single non-spread argument such as `Array(3)`, but it cannot know how many values a spread produces at runtime.

Reference:

- https://redirect.github.com/biomejs/biome/blob/d890b39c3ef21040bded453d9af91e1b301a0d67/crates/biome_js_analyze/src/lint/style/use_array_literals.rs

### Why the forms are not equivalent

`Array(3)` creates a sparse array with length three and no own indexed properties. `[3]` creates a dense one-element array containing `3`.

Therefore, with `args = [3]`, `Array(...args)` and `[...args]` differ in length, keys, membership, iteration, and callback behaviour.

### Released-binary result

Before:

```json
{"length":3,"keys":[],"hasIndexZero":false,"first":null}
```

Biome rewrote the call to:

```js
const result = [...args];
```

After:

```json
{"length":1,"keys":["0"],"hasIndexZero":true,"first":3}
```

Biome reported `Checked 1 file in 2ms. Fixed 1 file.`

### Concrete destructive scenarios

#### A length-forwarding helper breaks

```js
function makeArray(...args) {
  return Array(...args);
}

const slots = makeArray(1_000_000);
```

The original returns a sparse array with length one million. The rewrite returns a one-element array containing `1_000_000`.

A slot table, indexed work queue, bitmap companion, or capacity representation now has the wrong cardinality.

#### A generic factory loses its dual mode

A wrapper may intentionally preserve `Array`'s API: one number means length, while multiple arguments mean elements. Rewriting the forwarding call removes that runtime distinction.

#### Sparse callback behaviour changes

`map`, `forEach`, and `filter` skip holes. A dense `[3]` invokes callbacks once; sparse `Array(3)` invokes none for its holes.

#### Enumeration and serialization change

`Object.keys(Array(3))` is empty; `Object.keys([3])` contains `"0"`. Membership checks, iteration, and serialized output can change.

### Severity and exposure

This rule is recommended, so exposure is broader than the accessor finding. The trigger remains specific: spread expansion must yield exactly one numeric value.

The numeric value directly controls the original length, so the magnitude of the cardinality error can be large.

Characterization: **recommended safe fix, narrow runtime trigger, potentially large array-shape change**.

### Ecosystem comparison

ESLint's `no-array-constructor` reports ambiguous spread forms but withholds automatic fixing and offers a suggestion. It auto-fixes forms such as `Array(5, 6, ...args)` because two statically present arguments guarantee element mode.

- https://redirect.github.com/eslint/eslint/blob/main/lib/rules/no-array-constructor.js
- https://redirect.github.com/eslint/eslint/blob/main/tests/lib/rules/no-array-constructor.js

### Why this likely happened

1. PR #4416 expanded the rule, included `Array(...args)`, and introduced the fix as unsafe.
2. PR #6063 later mass-upgraded multiple unsafe fixes to safe, including this rule.
3. The upgrade checklist emphasized trivia handling and snapshot updates.
4. No runtime spread-arity guard was added.

### Plausible correction

- Keep the diagnostic.
- Withhold automatic safe fixing when spread syntax makes runtime arity capable of entering the one-number length mode.
- Retain safe fixing for zero arguments and calls guaranteed to have at least two arguments.
- Offer ambiguous cases only as unsafe or explicit suggestions.

Regression controls should include `Array(...args)`, `new Array(...args)`, `Array(5, ...args)`, and safe `Array(5, 6, ...args)`.

---

## Finding 3: safe `noUselessStringConcat` changes numeric strings

### State

`promotion-ready after independent review`

### Confidence

High. The source conversion is explicit and released Biome changes native Node output for both large and small exponent-form numbers.

### Source boundary

`crates/biome_js_analyze/src/lint/complexity/no_useless_string_concat.rs` marks the rule safe. Unlike ESLint's source rule, Biome deliberately extends the rule to concatenate strings with numeric literals.

The fix parses the JavaScript numeric literal as a host floating-point value and calls Rust `to_string()` before constructing a replacement JavaScript string literal.

Reference:

- https://redirect.github.com/biomejs/biome/blob/d890b39c3ef21040bded453d9af91e1b301a0d67/crates/biome_js_analyze/src/lint/complexity/no_useless_string_concat.rs

### Why the forms are not equivalent

JavaScript defines its own number-to-string representation. For the retained values:

```js
"large:" + 1e21;
"small:" + 1e-7;
```

Node produces exponent notation. Rust's host formatter chooses expanded decimal notation.

The numeric values are equal; the strings are not.

### Released-binary result

Before:

```json
{"large":"large:1e+21","small":"small:1e-7"}
```

Biome rewrote the source to:

```js
const large = "large:1000000000000000000000";
const small = "small:0.0000001";
```

After:

```json
{"large":"large:1000000000000000000000","small":"small:0.0000001"}
```

Biome reported `Checked 1 file in 2ms. Fixed 1 file.`

### Concrete destructive scenarios

#### Cache and database keys split

```js
const key = "expires:" + 1e21;
```

After rewrite, existing and newly generated keys use different bytes. That can produce cache misses, duplicate records, failed lookups, or orphaned data.

#### Signed or canonical requests change

A query parameter, canonical payload, or signature input may depend on JavaScript's exact string conversion. Rewriting the literal can change the transmitted value or make signatures disagree with another producer.

#### Protocol and persistence fields drift

Event IDs, version tags, metric labels, filenames, snapshot values, and serialized fields can be externally visible contracts even when both strings describe the same number.

#### Comparison behaviour changes

Code comparing against an expected exponent-form string now fails despite no source author requesting a representation change.

### Severity and exposure

The rule is not recommended and the retained trigger requires string concatenation with a numeric literal whose JavaScript rendering differs from Rust's rendering.

The result is nonetheless literal data replacement, not a hidden timing edge case. Once written, the changed string may cross storage, network, or identity boundaries.

Characterization: **opt-in rule, narrow numeric-format trigger, direct string-data mutation**.

### Why this likely happened

1. PR #2720 introduced the rule and intentionally extended ESLint behaviour to string-plus-number folding.
2. The implementation aimed to fix only cases considered statically safe, but used host `f64::to_string()` as a proxy for JavaScript number coercion.
3. PR #2748 explicitly classified the fix as unsafe.
4. PR #6063 later mass-upgraded it to safe without replacing the host formatting algorithm or restricting numeric operands.

References:

- https://redirect.github.com/biomejs/biome/pull/2720
- https://redirect.github.com/biomejs/biome/pull/2748
- https://redirect.github.com/biomejs/biome/pull/6063

### Plausible correction

The narrowest safe choices are:

- do not fold numeric operands as a safe fix; or
- implement the exact ECMAScript number-to-string algorithm and prove parity over edge cases.

The first option is simpler and aligns with the source ESLint rule's narrower surface. Numeric folding could remain an unsafe action if desired.

Regression cases should cover `1e21`, `1e-7`, exponent signs, boundary values around JavaScript's decimal/exponent thresholds, and representative precision edges.

---

## Known reproduced case: `useSimplifiedLogicExpression`

Released Biome also rewrites right-side boolean literals unsafely:

```js
effect(false) || true; // becomes true; call deleted
effect(true) && false; // becomes false; call deleted
"value" && true;      // becomes "value" instead of true
0 || false;            // becomes 0 instead of false
```

The retained run changed:

```json
{"calls":2,"orResult":true,"andResult":false,"truthyAnd":true,"falsyOr":false}
```

to:

```json
{"calls":0,"orResult":true,"andResult":false,"truthyAnd":"value","falsyOr":0}
```

This is not a novel finding:

- upstream issue #8577 is open and labelled confirmed;
- PR #8976 is open and removes right-side boolean simplification;
- other attempted PRs addressed the same issue.

The case remains useful because `useSimplifiedLogicExpression`, `useArrayLiterals`, and `noUselessStringConcat` were all included in PR #6063's batch unsafe-to-safe promotion. It strengthens the process-level conclusion that semantic review in that batch was incomplete.

Do not create a duplicate finding or upstream report for this case.

---

## Explored candidate: `useFlatMap`

`complexity/useFlatMap` is recommended and marked safe, but rewrites `.map(callback).flat()` based primarily on syntax.

Potential differences include:

- custom receivers whose `map`, `flat`, and `flatMap` methods are not equivalent;
- Array subclasses with `Symbol.species`, where `map().flat()` performs species construction twice and `flatMap()` once.

A native Node subclass probe produced different result constructors.

This is not promoted because the source Unicorn rule also accepts a broad receiver heuristic, practical prevalence and policy need more review, and no released-Biome fixture is retained here.

Disposition: `unpromoted follow-up`.

## Other reviewed surfaces

- `useNumericLiterals` validates a static string and radix before constructing a literal; no semantic defect was retained in this pass.
- `useExponentiationOperator` restricts itself to the global `Math.pow`, exactly two expression arguments, and detailed precedence handling; no semantic defect was retained.
- `useWhile` remained a negative result under its narrow applicability.
- `useNodeAssertStrict` is an explicit policy transformation rather than an omitted safety guard.
- Re-export ordering remains the accepted organizer-policy caveat from #27.

## Other Fieldwork review

Fieldwork PR #105's Biome review card was reviewed. It was asked to:

- update its stale evidence pin;
- split the novel Biome findings into separate review decisions;
- preserve their different exposure profiles;
- keep `useFlatMap` explicitly unpromoted;
- avoid treating the known logical issue as novel.

## Duplicate search

Repeated searches of current open and closed Biome issues and pull requests found no exact reports for:

- `useObjectSpread` accessor flattening;
- `useArrayLiterals` dynamic spread arity;
- `noUselessStringConcat` host-number formatting.

The same search did find the existing confirmed `useSimplifiedLogicExpression` report, preventing a duplicate claim.

Duplicate search is targeted rather than mathematically exhaustive and must be repeated immediately before any authorized submission.

## Issue-template requirements

Biome's linter bug template requires:

1. `biome rage --linter` environment output;
2. the rule name;
3. a playground link or reproduction repository;
4. expected result;
5. Code of Conduct confirmation.

The eventual reporter should prepare **three separate issue packets** because these are separate rules and mechanisms.

### `useObjectSpread` packet

- smallest target-setter or source-getter case;
- before/after output and descriptors;
- safe classification and unconditional flattening;
- ESLint accessor guard and tests;
- expected result: no safe action for accessor-bearing calls.

### `useArrayLiterals` packet

- `const args = [3]; const result = Array(...args);`;
- before/after length, keys, membership, and value;
- recommended/safe classification;
- ESLint suggestion-only handling of ambiguous spread forms;
- expected result: no automatic safe fix when runtime arity may enter length mode.

### `noUselessStringConcat` packet

- the `1e21` and `1e-7` cases;
- exact before/after strings;
- source use of host `to_string()`;
- original unsafe classification and later batch promotion;
- expected result: preserve ECMAScript string conversion or withhold numeric safe fixing.

No upstream contact is authorized from this lane.

## Durable evidence

- Report: this file
- Accessor reproduction: `reproductions/use-object-spread-accessors/`
- Array-spread reproduction: `reproductions/use-array-literals-spread/`
- Numeric-string reproduction: `reproductions/no-useless-string-concat-numbers/`
- Known logical reproduction: `reproductions/use-simplified-logic-side-effects/`
- Pull request: #97
- Last fully captured combined run: `30488365081`, job `90699671671`

## Disposition

- `useObjectSpread` accessors: `promotion-ready after independent review`
- `useArrayLiterals` spread arity: `promotion-ready after independent review`
- `noUselessStringConcat` numeric formatting: `promotion-ready after independent review`
- `useSimplifiedLogicExpression`: `known upstream bug; do not duplicate`
- `useFlatMap`: `retain as unpromoted follow-up`
- upstream contact: `not authorized`

## Upstream boundary

Upstream contact authorized: `no`

Interaction performed: `none`
