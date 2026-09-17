# Pattern-atlas migration audit — 2026-08-15

## In simple words

Fieldwork issue #657 already contains a compact cross-repository “pattern atlas.” Rather than replace or duplicate it blindly, this audit maps its twelve rules into the new compendium object model.

The result is useful: some atlas rules are best represented as invariants, some as bug species or anti-patterns, some as hunting/evidence techniques, and some as relationships between those objects. This is evidence that one flat “list of rules” was carrying several different knowledge kinds.

## Atlas-to-compendium map

| Atlas rule | Compendium representation | Current status |
|---|---|---|
| define equivalence at exact observation surface | `equivalence-matches-observation-surface` + `premature-equivalence-collapse` | materialized |
| fence non-destructive operations before destructive adapters | `classify-operation-before-destructive-adapter` + `probe-routed-through-destructive-adapter` | materialized |
| validate/authorize/resolve whole message before mutation | `validate-whole-logical-update-before-mutation` + `element-loop-becomes-accidental-transaction-boundary` | materialized |
| globally monotonic generations when identities may be reclaimed | `generation-identity-must-not-be-reused-while-stale-work-can-return` + `recycled-generation-aba` | materialized |
| GC must account for latent callback references | `collection-must-account-for-latent-callback-references` + `gc-forgets-latent-callback-owner` | materialized |
| committed state stronger than callback ancestry | `committed-state-outranks-callback-ancestry` + `callback-order-used-as-authority` | materialized |
| private setup rolls back before public publication | `private-construction-before-publication` | materialized as repair pattern |
| preserve exact bytes when byte representation is authority | `fingerprint-consumes-authoritative-representation` + `lossy-preprocessing-before-fingerprint` | materialized |
| retry only failures owned by existing retry authority | `one-owner-controls-retry-budget` + `stack-a-second-retry-loop` | materialized |
| cleanup errors secondary only after primary outcome selected | existing `selected-terminal-outcome-survives-cleanup` / `cleanup-replaces-selected-outcome` | already materialized |
| required discriminators fail closed on skip | `required-discriminator-must-not-skip-green` + `suite-green-while-discriminator-skipped` | materialized |
| classify broad red gates at exact failing boundary | `classify-red-gate-at-first-failing-boundary` | materialized as technique |

## What this migration taught us

### One prose rule often contains two objects

For example:

```text
“generations must not be reused while stale work can return”
```

contains both:

```text
invariant:
generation identity must not collide across live old/new lifetimes
```

and:

```text
bug species:
record GC resets per-key generation → old callback matches recreated generation
```

Keeping those separate lets another repair satisfy the invariant without inheriting the original mechanism.

### Anti-patterns are useful first-class objects

The atlas contains several “tempting repair” lessons:

```text
normalize because abstract semantics match
stack a second retry loop
use callback order as authority
hash a convenient decoded view
```

Those fit poorly as either bug species or invariants. `anti-pattern` is therefore earning its place in the schema rather than existing only as a planned type.

### Evidence rules belong in the same graph

The util-linux skipped discriminator and libarchive broad red gate are not runtime product bugs, but they affect which engineering conclusions are legal.

The compendium therefore covers two grammars:

```text
software execution grammar
+
evidence / proof grammar
```

A future Fieldwork skill should be able to retrieve both when a question moves from bug reproduction into candidate validation.

### A repair pattern can connect several species without becoming a universal law

`private-construction-before-publication` relates naturally to publication ordering, atomic final-name publication, fresh-install rollback, and staged metadata construction.

Its limits matter just as much:

- readers must not observe the private area as authoritative;
- streaming/incremental interfaces may have a different publication contract;
- failure after publication needs a separate recovery policy;
- cleanup of a failed unpublished generation must not delete an older valid published generation.

## Entries deliberately not collapsed

### `recycled-generation-aba` versus `stale-generation-publication`

```text
recycled-generation-aba:
old and new lifetime receive colliding generation identity

stale-generation-publication:
old generation identity remains distinct but still has global publication authority
```

The first is identity reuse. The second is missing publication fencing. A global monotonic counter fixes one but does not automatically fix the other.

### `callback-order-used-as-authority` versus `stale-generation-publication`

Callback ancestry can be the *reason* stale publication is accepted, but the callback-order anti-pattern also appears in systems where publication is notification/state selection rather than replacement generations.

### `element-loop-becomes-accidental-transaction-boundary` versus `false-success-after-incomplete-work`

A partial request can correctly return failure and still be broken because some earlier elements committed. This is atomicity, not false success.

### `suite-green-while-discriminator-skipped` versus `false-success-after-incomplete-work`

They share a completeness/truthfulness structure, but one is evidence classification and the other is product/API behavior. Keep them linked conceptually without pretending the same repair boundary applies.

## New views justified by the migration

The migration already motivated:

- `views/COUNTEREXAMPLES.md` — rules that intentionally stop at an owner/contract boundary;
- `views/EVIDENCE_AND_GATES.md` — proof grammar around skipped/failed CI;
- the existing bestiary and glossary views.

A future view worth adding after more cases arrive is a **transaction/publication atlas** joining:

```text
private construction
whole-message validation
ownership before publication
commit points
stale generation fencing
post-commit rollback limits
```

without claiming they form one universal transaction protocol.

## Next pressure test

Do not mine another existing summary only for confirmation. Prefer cases that challenge this mapping:

- an incremental request where per-element commit is correct;
- a callback-order API where registration order really is authoritative;
- a bounded generation scheme with proven quiescence before reuse;
- an intentionally canonical fingerprint where preprocessing is part of the identity contract;
- nested retries that genuinely own separate logical effects;
- a broad CI red gate that *does* fail because changed code executed.

Those cases should either sharpen the entries or prove that an apparently reusable rule was over-generalized.
