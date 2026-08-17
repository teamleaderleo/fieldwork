# SWC `instanceof` review reconciliation — 2026-08-17

## In simple words

The public review cycle clarified the final boundary of the `instanceof` contribution.

The original Fieldwork candidate treated two different behaviors as one semantic family: discarding an unused `instanceof` operation, and folding a used `instanceof` result from operand shape alone. Maintainer feedback established that the discarded-result path is intentional Terser-compatible compressor policy for this contribution. The surviving implementation therefore fixes only the independent wrong-value constant folding.

A later review detour briefly reopened that boundary. After the fold-only revision restored the Terser `pure_funcs` expectation, a maintainer comment said the restoration seemed wrong. Fieldwork interpreted that as a request to preserve `instanceof` when an operand value came from a pure-marked expression and built a narrow exception around that interpretation.

The maintainer then clarified that they had not noticed `foo` was configured as pure. Their intended result is the original Terser behavior: the pure `foo()` call is removed, and the general rule is not to change test cases under `tests/terser`.

That clarification retires the pure-marked exception. The owned fork now uses a normal forward commit to restore the exact fold-only tree.

Public issue: https://redirect.github.com/swc-project/swc/issues/12111  
Public contribution: https://redirect.github.com/swc-project/swc/pull/12110  
Automated upstream contact: `none`

## Revision history

Pinned contribution base: `5bf27fd72e4667bac6cc86888b8facb8b91f8077`.

Relevant owned-fork revisions:

- `a8ee1a6def602867739fc4427b992f90c9bfefe5` — broad semantic-preservation candidate;
- `a39678bd0226a394847605b6874b1eab7ad7f32c` — first fold-only narrowing;
- later revisions — temporary pure-marked-value exception created from the ambiguous review interpretation;
- `9f838a578a2bf440d6cc92d3b0e4891da0a580de` — forward cleanup restoring the fold-only tree.

GitHub reports zero file differences between `a39678bd0226a394847605b6874b1eab7ad7f32c` and `9f838a578a2bf440d6cc92d3b0e4891da0a580de`. The history records the detour, while the current source state is exactly the earlier fold-only source state.

## Current repair boundary

The contribution now does only this:

- remove `instanceof` folds that infer a boolean from operand category alone;
- keep SWC-owned regressions for used-result cases such as a null-prototype object against `Object`;
- keep discarded-result handling unchanged;
- keep `pure_funcs` behavior unchanged;
- keep every `tests/terser` expectation unchanged;
- keep `in` / `pure_getters` separate.

The compact model is:

```text
unused instanceof
→ existing SWC/Terser compressor contract
→ leave it alone

used instanceof
→ result must be correct
→ do not infer true/false from operand shape without a valid proof
```

## What the pure-value detour established

The discarded implementation was still useful research.

From strict JavaScript semantics, marking an operand-producing expression pure does not imply that its produced value is irrelevant to an enclosing operator. The value can still participate in `instanceof`, and evaluating the enclosing operator can have observable behavior.

That semantic argument remains valid. It simply does not define the compressor contract SWC is choosing to preserve here. Under the inherited policy, once the unused enclosing `instanceof` is considered discardable, a pure operand may also disappear.

The retained lessons are:

1. language-level observability and the compressor's accepted preservation contract are separate questions;
2. `pure` describes a producer's removable effects, not a general theorem that every semantic use of its produced value is irrelevant;
3. imported Terser fixtures should be treated as compatibility expectations unless maintainers explicitly choose to diverge;
4. a review comment can itself depend on a missed fixture condition, so a later maintainer clarification may legitimately reverse the interpretation without invalidating the underlying research.

## Exact-head evidence

Current owned-fork head: `9f838a578a2bf440d6cc92d3b0e4891da0a580de`.

Fieldwork carrier run `31988964177`, job `95268872348`, passed on that exact head:

- exact candidate identity and diff hygiene;
- `cargo fmt --all -- --check`;
- the focused minifier used-result fixture;
- Clippy with warnings denied for `swc_ecma_transforms_optimization`;
- Clippy with warnings denied for `swc_ecma_minifier`;
- final diff hygiene.

Fieldwork integrity run `31988964175`, job `95268872278`, also passed.

The current diff from the pinned contribution base is nine files. No `tests/terser` file is changed.

The changeset already matches the final scope:

```text
fix(es): Avoid incorrect `instanceof` constant folding
```

## Disposition

**FOLD-ONLY CONTRIBUTION ACTIVE / REVIEW CLARIFICATION RECONCILED.**

No implementation work is required by the latest review comment. Remaining public actions are human-owned: update the public PR description so it no longer describes the retired pure-marked exception, reply to the clarification, and wait for review of the remaining fold-only diff.

Do not reintroduce discarded-result, pure-marked-value, shared effect-analysis, DCE, dead-branch, or Terser-expectation changes into this contribution without new explicit target direction.
