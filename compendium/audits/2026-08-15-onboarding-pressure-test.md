# Onboarding pressure test — 2026-08-15

## In simple words

The compendium should be useful to someone who did not participate in the conversations that created it.

This audit asks whether a future human or agent can arrive cold, choose a bounded organizing task, reach the evidence, and leave a recoverable result without first reconstructing the whole history.

## Target newcomer flow

```text
repo link
→ compendium/START_HERE.md
→ one reader-facing view
→ stats + curation hints
→ one entry
→ bounded packet
→ one concrete case
→ one small contribution
```

The intended time to first useful question is measured in minutes, not hours.

## New surfaces added for this pressure test

- `compendium/START_HERE.md` — short onboarding path;
- `compendium/CURATION.md` — split/merge/bound/graduation rules;
- `compendium/views/CURATION_PLAYGROUND.md` — several ways to explore without a canonical reading order;
- `scripts/compendium-curate.mjs` — deterministic read-only review hints;
- CI smoke coverage for machine-readable curation output.

## What a newcomer should be able to do without chat history

### Find something

Use plain-language search or a curated view rather than guessing directory names.

### Understand what kind of object it is

Recover kind, maturity, facets, aliases, relations, cases, summary, and source path.

### Reach evidence

Follow `cases` back to the retained issue/investigation/finding rather than treating the compendium prose as proof.

### Make a bounded change

Examples:

- add an alias;
- add a relationship;
- add a supporting case;
- record a counterexample;
- clarify a split;
- lower maturity;
- create a candidate abstraction;
- record executable graduation.

### Know when to stop

A newcomer should be explicitly told that sparse entries, failed analogies, negative results, and case-specific lessons can all be correct outcomes.

## Curation helper contract

The helper emits **questions**, not defects.

Current queues include:

```text
missing-case-evidence
graph-orphans
thin-candidates
supported-evidence-review
mature-boundary-review
low-connectivity
weakly-linked-executable-graduations
```

These should never become hard CI failures merely because the list is non-empty.

A healthy corpus can intentionally contain:

- standalone concepts;
- candidate abstractions with one case;
- sparse executable records;
- supported entries whose evidence is one unusually strong retained note.

The queue exists to direct attention, not to optimize metrics.

## Social scaling assumption

Future contributors should not need one central curator to assign every task.

The compendium is designed for many small independent passes:

```text
person A improves search aliases
person B challenges one mature pattern
person C extracts a Linux case
person D connects a repair to a regression
person E finds two entries should remain separate
```

The graph and case references provide the shared coordination substrate.

## Failure modes to watch

### Taxonomy gardening without evidence

Symptom: many new names, few concrete cases.

Response: follow the case-study boundary and prefer clarification over entry count.

### Curation-score gaming

Symptom: adding meaningless `related-to` edges to clear `low-connectivity` hints.

Response: relation semantics matter more than degree.

### Maturity inflation

Symptom: `mature` becomes shorthand for “sounds important.”

Response: require distinct cases, useful limits/counterexamples, and a stable investigation/repair story.

### Newcomer context explosion

Symptom: one task requires reading dozens of files and historical threads.

Response: prefer bounded packets and 1–5 evidence carriers; widen only when the question requires it.

### Generic layer erases domain provenance

Symptom: Linux/system cases get rewritten into generic Fieldwork prose and lose exact execution boundaries.

Response: keep source cases authoritative and retain domain-specific compendium seeds where useful.

### One canonical organizer

Symptom: contributors wait for someone to tell them what to classify next.

Response: expose deterministic review prompts and multiple exploration modes.

## What this does not solve

The current onboarding path does not yet provide:

- generated GitHub issue task cards;
- semantic ranking;
- cross-repository automatic case resolution;
- a browser UI;
- contribution ownership/lease machinery;
- automatic maturity decisions;
- automatic split/merge proposals.

Those should be added only if real use demonstrates a need.

## Next pressure test

Hand only `compendium/START_HERE.md` to a fresh contributor or agent and ask them to:

1. choose one curation hint;
2. explain whether it is a real problem;
3. follow one evidence case;
4. make or propose one bounded improvement;
5. state what would falsify their classification.

If they need hidden chat context to do that, the onboarding surface is incomplete.
