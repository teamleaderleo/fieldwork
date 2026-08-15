# Compendium curation guide

## In simple words

Curation is the work of keeping the compendium useful as the case corpus grows.

The goal is not maximum entry count. The goal is a graph where a future investigator can find a nearby reusable idea, understand its limits, and reach the concrete evidence quickly.

```text
more cases
   ↓
pressure existing abstractions
   ↓
split / merge / connect / bound / graduate
   ↓
better retrieval and better engineering questions
```

## Curation is different from evidence creation

A case study may require source reading, target execution, review, or a real implementation experiment.

Curation operates on what those cases already support. It may discover that more evidence is required, but it must not manufacture that evidence by rewriting the summary.

## Five recurring curation moves

### 1. Connect

Add a typed relationship when the connection changes how a reader should investigate or repair the problem.

Good:

```text
bug species --violates--> invariant
bug species --detected-by--> hunting technique
bug species --repaired-by--> repair pattern
lesson --graduated-to--> executable constraint
```

Weak:

```text
entry --related-to--> every entry sharing the word "cleanup"
```

Relationship density is useful only when edges carry meaning.

### 2. Split

Split when one entry hides different owners, commit boundaries, certainty states, or legal repairs.

Strong split signal:

```text
same symptom
+ different authoritative owner
+ different safe repair
= probably different species
```

Examples of distinctions already worth preserving:

```text
premature acknowledgement
!=
ambiguous remote outcome

stale generation publication
!=
recycled generation ABA

cleanup result precedence
!=
cleanup never settles
```

### 3. Merge

Merge when two names describe the same reusable state relationship and differ only in wording or source-project vocabulary.

Before merging, check:

- owner;
- invariant;
- failure boundary;
- certainty model;
- legal repair;
- regression shape;
- counterexamples.

Preserve useful old wording as aliases.

### 4. Bound

A good entry says where it stops applying.

Useful limits include:

- a protocol explicitly owns the constant that otherwise looks hard-coded;
- a collection intentionally has live-membership semantics;
- cleanup is part of the commit rather than secondary work;
- callback registration order is the documented authority;
- repeated retry loops own genuinely different logical effects;
- normalization is the protocol-defined identity rather than information loss.

Counterexamples make the corpus more trustworthy.

### 5. Graduate

When a reusable lesson becomes mechanically enforced, record the transition rather than merely updating prose.

Possible graduation targets:

```text
test
assertion
type/state machine
schema
lint
CI check
property-based model
model checker
```

An executable graduation should link to exact evidence and retain its scope limits.

## Maturity review

Maturity is intentionally revisable.

### Candidate

Usually one strong case or a promising abstraction.

Curation priority:

- find a sibling case;
- find a counterexample;
- test whether the owner/invariant survives another domain;
- decide whether the entry is actually too broad.

### Supported

Useful structure with meaningful evidence.

Curation priority:

- search for mechanism-diverse cases;
- improve limits;
- strengthen relations to invariants/techniques/repairs;
- look for a realistic retrieval phrase that should surface it.

### Mature

Several distinct cases plus stable limits and investigation/repair story.

Curation priority:

- challenge it with counterexamples;
- keep it from becoming an umbrella category;
- look for executable graduation;
- lower maturity if a hidden assumption appears.

## A review matrix for two similar entries

Use this before merging or generalizing:

| Question | Entry A | Entry B |
| --- | --- | --- |
| What state is authoritative? | | |
| Who owns the transition? | | |
| What makes the bad state observable? | | |
| Which interruption/failure boundary matters? | | |
| What is known vs unknown afterward? | | |
| What repair is legal? | | |
| What repair would be dangerous? | | |
| What regression distinguishes the bug? | | |
| What counterexample stops the analogy? | | |

If the decisive rows differ, prefer related entries over one universal species.

## Retrieval-driven curation

The compendium is a retrieval product, so test it in problem language.

Do not only query exact entry names.

Try phrases a person would say while debugging:

```text
"worked until restart"
"timeout but remote write may have happened"
"cleanup error hid original result"
"old async callback changed new state"
"green job but proof test skipped"
"same filename means different object"
```

If the right entry exists but cannot be found, improve aliases, facets, summaries, or relationships before inventing another search system.

## Read-only curation hints

Run:

```text
node scripts/compendium-index.mjs curate
```

or machine-readable:

```text
node scripts/compendium-index.mjs curate --json
```

The queues are intentionally heuristic. They highlight review opportunities such as:

- graph-orphaned entries;
- candidate entries with one or zero concrete cases;
- mature entries whose prose lacks an obvious limits/counterexample section;
- entries with very little graph connectivity;
- executable-graduation records that are weakly linked back into the conceptual graph.

A curation hint is not a validation failure. Some intentionally narrow entries should remain sparse.

## When to add tooling

Prefer adding tooling when it protects a stable corpus rule or makes retrieval measurably better.

Good reasons:

- duplicate IDs or broken relation targets;
- machine-readable output contract;
- bounded context packets;
- deterministic generated index;
- recurring curation checks that would otherwise be forgotten.

Weak reasons:

- making the directory look more sophisticated;
- replacing readable Markdown with a database prematurely;
- adding opaque ranking before lexical/facet retrieval has been pressure-tested;
- making every heuristic a hard CI failure.

## Curation receipt

For a substantive reclassification, leave enough explanation that another contributor can recover the decision:

```text
What changed?
Which cases were compared?
Which owner/invariant boundary decided it?
Which alternative classification lost, and why?
Did maturity change?
Which realistic retrieval query improves?
What would reopen the decision?
```

The explanation can live in the branch/PR/owning issue. It does not need to become permanent prose inside every entry.

## Success condition

A healthy compendium should make this loop cheap:

```text
new bug or investigation
→ search in plain language
→ find nearby patterns and counterexamples
→ inspect 1-5 concrete cases
→ ask better questions sooner
→ add newly learned structure back into the corpus
```

That loop matters more than the raw number of entries.
