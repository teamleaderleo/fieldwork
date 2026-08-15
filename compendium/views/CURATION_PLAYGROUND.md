# Compendium curation playground

## In simple words

This view is for people who want to **poke around** rather than consume the compendium front-to-back.

There is intentionally no single correct reading order.

Pick a mode:

```text
I found a weird bug
→ search by symptom

I like state machines
→ browse ownership / authority / generation entries

I want a small organizing task
→ run the curation helper

I want to challenge the taxonomy
→ hunt counterexamples

I want a deeper engineering exercise
→ follow one case into its implementation and tests
```

## Poke mode 1 — symptom first

Try a phrase from a bug report rather than an entry name:

```text
node scripts/compendium-index.mjs search "works until restart"
node scripts/compendium-index.mjs search "timeout remote write unknown"
node scripts/compendium-index.mjs search "cleanup hid original error"
node scripts/compendium-index.mjs search "old callback changed new state"
node scripts/compendium-index.mjs search "green job proof skipped"
```

Open the nearest entry, then inspect its packet and cases.

## Poke mode 2 — graph first

Pick an entry and walk its typed edges:

```text
node scripts/compendium-index.mjs related <entry-id>
node scripts/compendium-index.mjs packet <entry-id> --depth 2
```

Look for:

- a bug species with no invariant;
- an invariant with no concrete violating species;
- a repair pattern with no regression pattern;
- a mature entry with weak counterexamples;
- an executable graduation that does not clearly identify the lesson it enforces.

## Poke mode 3 — organize something

Run:

```text
node scripts/compendium-curate.mjs
```

Choose one item from one queue. Treat it as a question, not a defect report.

Examples:

```text
graph orphan
→ intentionally standalone?
→ or missing useful relationship?
```

```text
thin candidate
→ find second case?
→ find counterexample?
→ narrow it?
→ retire it?
```

```text
mature entry without obvious limits section
→ boundary is implicit but adequate?
→ or maturity is hiding an assumption?
```

## Poke mode 4 — try to break a rule

The most valuable organizing work may be proving that a nice-looking rule is too broad.

Use [`COUNTEREXAMPLES.md`](COUNTEREXAMPLES.md) as inspiration.

Questions:

- Can I find a collection where live iteration is the contract?
- Can cleanup legitimately define whether the operation succeeded?
- Can a fixed unit be protocol-owned instead of an accidental magic constant?
- Can callback order intentionally define authority?
- Can an old generation safely publish because results are mergeable rather than exclusive?
- Can per-element mutation be the correct message contract?

If yes, record the boundary instead of forcing the case into the existing species.

## Poke mode 5 — follow one bug all the way down

Choose a case with retained implementation/test evidence and reconstruct:

```text
symptom
→ concrete failure sequence
→ violated invariant
→ competing explanations
→ discriminator
→ repair
→ regression
→ review correction
→ executable enforcement
```

Then ask which steps are reusable and which belong only to that project.

This is often the best way to create a new high-quality compendium entry.

## Poke mode 6 — teach through comparison

Pick two entries that sound similar and explain their decisive difference in a small table:

| Question | A | B |
| --- | --- | --- |
| owner | | |
| authoritative state | | |
| failure boundary | | |
| certainty after failure | | |
| legal repair | | |
| dangerous repair | | |

If the table reveals the same structure, consider a shared abstraction. If it reveals different legal repairs, preserve the split.

## Leave the place navigable

A useful poke should usually improve at least one of:

```text
findability
boundary clarity
case provenance
relationship quality
counterexample quality
maturity honesty
executable enforcement
```

Entry count by itself is not a success metric.

Start with [`../START_HERE.md`](../START_HERE.md) if you want the short onboarding path, and [`../CURATION.md`](../CURATION.md) for the curation rules.
