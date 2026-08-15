# Learning paths through the compendium

## In simple words

The compendium can also be used as a self-directed systems/debugging curriculum.

A learning path is only a view over the same entries and cases. It does not create a new hierarchy or make the ordering mandatory.

## Path 1 — ownership and publication

Start with:

```text
ownership-before-publication
→ publication-before-ownership
→ failure-window-interruption
→ paired failure/success lifecycle controls
```

Questions to carry:

- What makes state visible?
- What prevents reuse?
- What if execution stops between the two?
- Does the success path eventually retire the predecessor?

Then compare the storage cases with non-storage publication and generation cases.

## Path 2 — uncertainty after external effects

Start with:

```text
ambiguous-external-outcome
→ remote-effect-certainty
→ unknown-outcome-requires-reconciliation-before-retry
→ reconciliation
```

Questions:

- Was the mutation dispatched?
- What proves absence?
- What proves commit?
- What identity survives retry/recovery?
- Which observations can resolve uncertainty?

Then contrast with `acknowledge-before-processing`, where the replay source is removed too early but the remote outcome is not intrinsically ambiguous.

## Path 3 — lifecycle authority

Start with:

```text
proxy-signal-for-authoritative-state
→ authoritative-state
→ authoritative-state-gates-next-transition
→ terminal-state-revokes-producer-authority
```

Questions:

- Who owns the transition?
- Which event is authoritative?
- Which symptoms are merely correlated?
- Which old producers remain capable of acting after terminal state?

## Path 4 — generations and stale asynchronous work

Start with:

```text
stale-generation-publication
→ fence-publication-by-generation
→ recycled-generation-aba
→ collection-must-account-for-latent-callback-references
```

Questions:

- Can an identifier be reused?
- Can old work finish after replacement?
- Is finishing allowed but publication forbidden?
- What references can still produce callbacks after apparent cleanup?

## Path 5 — completion and truthful success

Start with:

```text
success-implies-complete-selected-work
→ false-success-after-incomplete-work
→ suite-green-while-discriminator-skipped
```

Then deliberately separate product completeness from evidence completeness.

Questions:

- What work did the operation claim to select?
- Did every selected item reach a terminal disposition?
- Did the proof test itself execute?
- Can an aggregate status hide missing work?

## Path 6 — cleanup and result precedence

Start with:

```text
selected-terminal-outcome-survives-cleanup
→ cleanup-replaces-selected-outcome
→ resource-has-one-cleanup-owner
→ cleanup-owner-not-transferred
```

Questions:

- When is the primary result selected?
- Is cleanup part of success or secondary work?
- Who owns retry after cleanup failure?
- Did cleanup ownership transfer with the resource?

Counterexample exercise: find an API where cleanup is part of the commit and therefore *must* affect success.

## Path 7 — representation and identity

Start with:

```text
semantic-identity
→ normalization-erases-semantic-distinction
→ validated-identity-goes-stale-before-use
→ fingerprint-consumes-authoritative-representation
```

Questions:

- Which representation defines equality for this operation?
- Did normalization erase information before validation?
- Can the validated object change before use?
- Is a fingerprint hashing the bytes whose identity it claims?

Then compare with Linux representation-layer cases where plausible physical state can leak through after logical metadata failure.

## Path 8 — fanout, callbacks, and reentry

Start with:

```text
fanout-iterates-live-membership
→ snapshot-opening-membership
→ opening-membership-fanout-regression
→ shared-terminal-operation-self-dependency
```

Questions:

- Is membership defined at operation start or live throughout iteration?
- Can callbacks mutate the collection?
- Can a child return the operation that is waiting on that child?
- Which concurrent callers should legitimately share completion?

This path includes the first executable-graduation example.

## Path 9 — transaction boundaries

Start with:

```text
element-loop-becomes-accidental-transaction-boundary
```

Then follow related invariants/repair patterns around validation, ownership, and publication.

Questions:

- What does one request/message claim to update?
- Is validation complete before mutation begins?
- Does a late invalid element leave partial committed state?
- Is per-element commit actually the documented contract?

## Path 10 — proof and review discipline

Start with:

```text
suite-green-while-discriminator-skipped
→ classify-red-gate-at-first-failing-boundary
```

Then inspect retained Fieldwork evidence-audit cases.

Questions:

- Did the intended test exist and run?
- Where exactly did a red gate fail?
- Did changed code execute before the failure?
- Is the receipt source, target-native, integration, or publication evidence?

## Turn any path into an exercise

For each entry:

1. explain the invariant in your own words;
2. draw the state transition in 3–7 arrows;
3. identify one dangerous intermediate state;
4. follow one concrete case;
5. predict a regression test before reading the retained one;
6. find one counterexample or limit;
7. explain how you would know the repair is complete.

That makes the compendium useful as both investigation memory and practical systems training.
