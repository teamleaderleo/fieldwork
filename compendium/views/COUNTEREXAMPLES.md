# Counterexamples — where the tempting rule stops

## In simple words

A useful compendium should help reject bad analogies as often as it helps recognize good ones.

This view collects limits that prevent a reusable rule from turning into a slogan.

## “Equivalent enough” can still be observably different

Tempting rule:

```text
class tokens denote the same set
→ normalize order/duplicates
```

Counterexample shape from the retained React work:

```text
semantic token matching may agree
but literal class attribute remains observable
through className / getAttribute / mutation observers / exact selectors
```

Lesson: equivalence is defined at the observation surface, not by whichever abstraction makes the optimization convenient.

See `equivalence-matches-observation-surface` and `premature-equivalence-collapse`.

## A fixed 4K constant can be correct

Tempting rule:

```text
hard-coded page/granule size
→ hidden host-page assumption
→ replace with dynamic host page size
```

Counterexample from the Linux granularity investigation: one backend can legitimately define its protocol unit as fixed 4K even while another backend uses host page granularity.

Lesson: the owner of the representation decides the unit. “Make constants dynamic” is not an invariant.

See the Linux `implicit-granularity-mismatch` entry and #617 case.

## Sharing one terminal promise is often the correct design

Tempting rule after finding a reentry deadlock:

```text
shared shutdown promise caused the cycle
→ never share terminal promises
```

Counterexample: unrelated concurrent callers often *should* join the same terminal operation and observe one settlement.

The defect requires a dependency cycle:

```text
P waits for child
child reenters owner
child waits for P
```

Lesson: preserve the useful shared owner while fencing callback ancestry/self-dependency.

See `shared-terminal-operation-self-dependency`.

## Old work finishing is not the same as stale publication

Tempting rule:

```text
new generation exists
→ cancel/ignore every old operation immediately
```

Counterexample: an in-flight operation can legitimately retain the runtime/generation captured when it began while **future** requests use the new generation.

The bug is old work regaining shared future-publication authority, not old work merely completing.

See `stale-generation-publication`, `only-current-generation-may-publish`, and `fence-publication-by-generation`.

## Snapshotting a collection is contract-dependent

Tempting rule:

```text
callback can mutate collection during iteration
→ always snapshot
```

Counterexample: some APIs intentionally define live-membership iteration where removals should affect the current operation.

Snapshotting is correct only when the operation promises opening-set completeness or equivalent attempt-all semantics.

See `fanout-iterates-live-membership` and `snapshot-opening-membership`.

## Revalidation is not a universal filesystem race repair

Tempting rule:

```text
validated pathname can change
→ just validate again immediately before action
```

Counterexample: on a hostile namespace/filesystem boundary, the path can still change after the last pathname check. The correct authority mechanism may require descriptor-relative operations, no-follow primitives, namespace isolation, or another capability-bearing identity.

Revalidation is useful only within a threat model where its residual race is acceptable.

See `validated-identity-goes-stale-before-use` and `validated-identity-must-match-used-identity`.

## Cleanup errors are not always secondary

Tempting rule:

```text
primary work succeeded
→ cleanup error must never change result
```

Counterexample: some APIs define the “cleanup” phase as a required commit/finalization step. If that step is necessary to make success truthful, its failure legitimately means the operation did not succeed.

The distinction is whether cleanup happens **after** the authoritative result exists or participates in establishing that result.

See `selected-terminal-outcome-survives-cleanup` and `commit-point`.

## Normalization can be exactly correct

Tempting rule after finding over-normalization:

```text
normalization destroys identity
→ preserve every original byte/token
```

Counterexample: protocols frequently define canonical forms and equivalence classes intentionally. A canonical fingerprint or normalized path can be the authoritative representation.

The right rule is contract-relative:

```text
normalize exactly the equivalences the contract defines
```

See `normalization-preserves-semantic-identity`, `equivalence-matches-observation-surface`, and `fingerprint-consumes-authoritative-representation`.

## A skipped test can be perfectly fine

Tempting rule:

```text
skip = CI failure
```

Counterexample: optional platform/capability tests may be explicitly unsupported in an environment and contribute nothing to the claim under review.

The problem appears only when a skipped test is the required discriminator and the aggregate green result is promoted as evidence for that behavior.

See `required-discriminator-must-not-skip-green`.

## The meta-rule

When a pattern sounds elegant, ask:

```text
What would make this rule wrong?
Which owner/contract decides that?
Do we have a case or negative control for the boundary?
```

Counterexamples are not cleanup work for the bestiary. They are part of the bestiary's ability to choose the correct repair.
