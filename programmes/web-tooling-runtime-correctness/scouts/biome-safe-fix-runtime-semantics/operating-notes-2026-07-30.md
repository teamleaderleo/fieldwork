# Biome safe-fix lane operating notes — 2026-07-30

State: `active-with-review-backpressure`

Fieldwork lane: #89  
Evidence PR: #97  
Upstream contact authorized: `false`

## Current promoted decisions

The lane currently has four independently reviewable candidates:

- #144 — `useObjectSpread` accessor semantics;
- #145 — `useArrayLiterals` dynamic spread arity;
- #146 — `noUselessStringConcat` JavaScript number formatting;
- #151 — `useFlatMap` Array subclass species, explicitly lower priority.

The known `useSimplifiedLogicExpression` case remains excluded because current upstream already owns the same defect and repair direction.

## Review-backpressure decision

Do not create another top-level candidate merely because a semantic difference is real.

Until the current candidates receive dispositions:

- continue source reading and released-package execution in this rolling lane;
- retain negative results and lower-priority edges here or in focused amendments;
- create a new candidate only when it clearly outranks, supersedes, or materially differs from the current queue and gives a reviewer one concrete decision;
- avoid activity-only issue comments;
- synchronize #89 and PR #97 only after a material result.

## Continuation instruction

The user has explicitly authorized continued bounded Biome investigation.

Proceed immediately within this lane without repeatedly asking whether to continue and without proposing scheduled work. Reconfirmation is required only when the next action would:

- contact Biome or another third party;
- use private, production, credentialed, or destructive execution;
- overlap another worker's owned output;
- broaden beyond safe-fix runtime semantics;
- require a human promotion or upstream-contact decision.

## Current exploration rules

Prioritize rules that:

- are classified safe and run under ordinary `lint --write` or editor safe fix-all;
- change executable JavaScript rather than only types or formatting;
- can alter evaluation count, exception timing, object identity, descriptors, sparse/dense structure, exact string data, module resolution, or framework metadata;
- have a realistic native-language or common-library trigger;
- admit a narrow correction or a clear safety-policy decision.

Stop or retain as a negative result when:

- the individual action is actually surfaced as unsafe;
- the rule only diagnoses and has no automatic fix;
- the exact issue is already reported;
- the difference depends on deliberately brittle architecture without a plausible boundary;
- whole-program or runtime type knowledge would be required and no narrow conservative guard exists.

## Recent negative results

### `useTemplate`

The symbol-conversion difference between string concatenation and template interpolation is real, but Biome already classifies this rule's fix as unsafe. No candidate.

### `useNumberToFixedDigitsArgument`

The receiver assumption can be wrong for decimal libraries, but the action is surfaced as unsafe and the repository test suite explicitly documents a `BigNumber` false positive. No candidate.

### `useForOf`

The rule currently provides a diagnostic without an automatic rewrite. No safe-fix candidate.

### `useOptionalChain`

The transformation is already classified unsafe. No safe-fix candidate.

### `useNullishCoalescing`

This is type-domain and safe-classified, but adjacent correctness is already represented by current upstream reports. Do not duplicate without a materially new boundary.

## Active experiment

### `useConst` and direct `eval`

Hypothesis:

```js
let value = 1;
eval("value = 2");
```

can become a different program if a safe fix changes `let` to `const`. The static semantic model does not visibly account for writes encoded inside direct-eval source text.

A released `@biomejs/biome@2.5.6` probe is now part of PR #97. Do not promote it until the exact rewrite and before/after output are retained and duplicate/history review is refreshed.

## Next technical surfaces

After the direct-eval result:

1. review recommended safe declaration and control-flow fixes for dynamic-scope or abrupt-completion gaps;
2. review safe removal of directives, labels, and boolean casts for `eval`, proxy, and coercion boundaries;
3. review regex/string escape fixes for exact source-value or regular-expression changes;
4. batch healthy-rule results instead of creating one note per rule.

No upstream contact occurred.
