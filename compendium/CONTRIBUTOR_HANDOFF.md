# Contributor handoff

## In simple words

If somebody hands you this repository and says “go poke at the bug compendium,” this file is the durable handoff.

You do not need prior chat context.

## Current working surfaces

- broad design/coordination: Fieldwork issue `#908`;
- working generic implementation: draft PR `#909`;
- newcomer route: [`START_HERE.md`](START_HERE.md);
- curation rules: [`CURATION.md`](CURATION.md);
- reader views: [`views/`](views/README.md);
- structured query helper: `scripts/compendium-index.mjs`;
- read-only curation hints: `scripts/compendium-curate.mjs`;
- Linux/system seed: `teamleaderleo/linux-fieldwork#675` and its draft compendium PR.

## First commands

```text
node scripts/compendium-index.mjs validate
node scripts/compendium-index.mjs stats
node scripts/compendium-curate.mjs
```

Then choose one entry:

```text
node scripts/compendium-index.mjs show <id>
node scripts/compendium-index.mjs related <id>
node scripts/compendium-index.mjs packet <id>
```

## Your job is not “add entries”

Your job is to improve the usefulness and honesty of the knowledge graph.

Any of these can be a successful contribution:

```text
add a missing case
add a useful relation
improve search aliases
find a counterexample
split an over-broad species
merge true synonyms
lower unjustified maturity
clarify a repair boundary
record a negative result
connect an executable enforcement
prove an entry should remain case-specific
```

## The invariant for the compendium itself

```text
case evidence
    ↓
derived reusable claim
    ↓
retrieval / organization / learning views
```

Never reverse that authority:

```text
generic claim
    ↓
rewrite concrete case to fit it   ← wrong
```

## Before changing a reusable claim

Follow at least one concrete case and answer:

1. What state or result is authoritative?
2. Who owns the relevant transition?
3. Which failure/interruption boundary matters?
4. What is known versus unknown afterward?
5. Which repair is legal?
6. Which nearby repair would be dangerous?
7. What would falsify the abstraction?

## External boundary

Compendium work does not authorize third-party upstream mutation.

Read public upstream material when a retained case requires it, but do not comment, react, review, open/edit pull requests, or otherwise interact with third-party upstream projects without separate explicit authority.

## Leave a recoverable result

If you make a substantive split/merge/maturity/generalization decision, preserve a short receipt in the draft PR, owning issue, or a focused audit:

```text
change
cases compared
owner/invariant boundary
losing interpretation
retrieval effect
reopening trigger
```

The next contributor should be able to continue without asking what happened in a prior chat session.
