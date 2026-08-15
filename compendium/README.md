# Fieldwork compendium

## In simple words

Fieldwork has many exact investigations and a growing set of reusable lessons. This directory connects those two layers without pretending every investigation belongs to one category or can be reduced to one rule.

The compendium is derived memory. Existing findings, investigations, issues, experiments, tests, and review records remain the evidence. A compendium entry names a reusable structure, says where it applies and where it does not, and links back to the cases that taught it.

Working reader-facing title: **Fantastic Bugs and How to Find Them**.

The first design is deliberately inspectable without special tooling:

```text
case study / retained investigation
        ↓
reusable entry
        ↓
facets + typed relationships
        ↓
search / views / future skill retrieval
```

## What belongs here

Useful entry kinds include:

- `bug-species` — a recurring malformed execution or state relationship;
- `invariant` — a property that should survive relevant paths;
- `hunting-technique` — a reusable discriminator or probing method;
- `repair-pattern` — a recurring safe transformation with explicit assumptions;
- `regression-pattern` — a durable testing shape;
- `concept` — glossary material with domain-qualified meaning when needed;
- `anti-pattern` — a tempting approach that repeatedly creates or preserves bugs;
- `executable-graduation` — a lesson that became a type, assertion, state machine, test, schema, model, lint, or CI rule.

The vocabulary is provisional. Real cases should force it to split, merge, or grow.

## Case studies remain authoritative

Compendium entries summarize structure. They do not replace case evidence.

If an entry says:

```text
cleanup must not replace the selected terminal outcome
```

and a concrete investigation shows a narrower ordering, the investigation owns that concrete fact. The entry should be repaired, bounded, or split rather than rewriting the case to fit the abstraction.

A one-off investigation can remain valuable without producing any generic entry.

## Storage is not ontology

Do not mirror the conceptual taxonomy as a deep directory tree.

A bug can simultaneously concern lifecycle, persistence, distributed state, storage, resource ownership, retries, protocol semantics, or testing. Those are facets, not competing parents.

```text
physical layout: boring
conceptual relationships: rich
```

Entries therefore live in a relatively flat directory and carry structured metadata described in [`SCHEMA.md`](SCHEMA.md).

## Retrieval is a product goal

A useful compendium should eventually answer questions such as:

```text
What bugs can appear only after reopen or restart?

What patterns involve an external effect whose outcome is uncertain locally?

What should I probe when cleanup can race a successor?

Show cases where success was reported after only a subset of selected work completed.

Show the same bug structure in unrelated domains.
```

The intended progression is incremental:

```text
full-text search
→ normalized metadata
→ generated index
→ facet + relationship queries
→ semantic retrieval
→ bounded context packets for Fieldwork skills
```

The repository should earn each added layer. Markdown remains readable without the indexer.

## Maturity

Entries may use these working maturity labels:

- `candidate` — one good case or an early abstraction; actively challenge the generalization;
- `supported` — more than one supporting case or one especially strong reusable note plus explicit limits;
- `mature` — multiple distinct cases, useful counterexamples/limits, and a stable hunting/repair/test story.

Maturity is about confidence in the reusable structure, not severity of the underlying bug.

## Graduation ladder

The compendium should make it easy to notice when a lesson can become executable:

```text
L0 incident
   ↓
L1 explanation
   ↓
L2 invariant
   ↓
L3 reusable hunting question
   ↓
L4 cross-domain pattern
   ↓
L5 executable enforcement
```

Not every useful lesson should reach L5. Some engineering judgment is necessarily contextual.

## Seed relationship to existing work

- Fieldwork issue 908 owns the broad proposal and retrieval direction.
- Fieldwork issue 779 owns the campaign-journal versus durable-note distinction.
- Linux Fieldwork issue 675 owns the first large Linux/system extraction pass.
- `BUG_LENSES.md` remains the compact high-level guide for deciding which questions are worth asking.

The compendium should add case-backed memory and traversal without turning ordinary investigations into metadata chores.

## Local query helper

`node scripts/compendium-index.mjs validate` validates the current entry metadata and local relationships.

Other useful commands:

```text
node scripts/compendium-index.mjs list
node scripts/compendium-index.mjs list --kind bug-species
node scripts/compendium-index.mjs list --facet concerns=durability
node scripts/compendium-index.mjs show ambiguous-external-outcome
node scripts/compendium-index.mjs related ambiguous-external-outcome
node scripts/compendium-index.mjs search "cleanup terminal outcome"
```

This helper is intentionally small. It is a retrieval experiment, not a new service or canonical truth store.
