# Retrieval pressure tests — 2026-08-15

## In simple words

The first compendium should earn its structure by helping with realistic investigation questions. This file records the first smoke tests and a larger set of queries that should pressure the seed as more cases arrive.

The current CI smoke test deliberately asks in problem language rather than by exact entry ID:

```text
external effect retry
selected work success
```

It also checks one explicit relationship traversal from `publication-before-ownership` to the violated `ownership-before-publication` invariant.

## Executable smoke tests

Fieldwork integrity currently requires:

```text
search "external effect retry"
    → includes ambiguous-external-outcome

search "selected work success"
    → includes false-success-after-incomplete-work

related publication-before-ownership
    → includes ownership-before-publication
```

These are intentionally tiny. They prove the local index can retrieve by mixed prose/facet content and traverse a typed relation; they do not prove ranking quality.

## Realistic questions to test next

### “The corruption only appears after restart.”

Desired neighborhood:

- publication before ownership;
- durable ownership/reachability concepts;
- failure-window interruption;
- reopen/reconciliation techniques;
- Linux QCOW case evidence.

A weak result would return every entry containing the word `restart` without preferring publication/durability relationships.

### “The command returned success even though some selected objects were skipped.”

Desired neighborhood:

- false success after incomplete work;
- success implies complete selected work;
- aggregate/coverage concepts;
- the uv audit case;
- false clean certification as a structurally similar but domain-different case.

### “A mutation timed out. Is it safe to retry?”

Desired neighborhood:

- ambiguous external outcome;
- unknown outcome requires reconciliation before retry;
- stable operation identity / idempotency / reconciliation concepts;
- Codex/MCP/connector cases;
- a warning that premature-message-ack is a different family.

### “Cleanup failed after I already knew the real error.”

Desired neighborhood:

- cleanup replaces selected outcome;
- selected terminal outcome survives cleanup;
- process/signal and async cleanup cases;
- an explicit distinction from cleanup non-settlement/liveness.

### “The test waits for the service to disappear and then immediately reuses state.”

Desired neighborhood:

- proxy signal for authoritative state;
- authoritative state gates next transition;
- lifecycle testing cases;
- owner-issued terminal event technique.

### “The API returned, but an old stream is still consuming input.”

Desired neighborhood:

- terminal authority leak;
- terminal state revokes producer authority;
- active producer cleanup/retirement techniques;
- React/MCP cases.

## Ranking weaknesses in the version-1 helper

The current helper is intentionally crude:

```text
one query term found anywhere = one point
```

It has no stemming, phrase weighting, relationship expansion, case-body indexing, synonym graph, or semantic similarity. That is useful at this stage because poor retrieval is easy to attribute to the model rather than to an opaque ranker.

Expected early problems:

- common terms such as `state`, `failure`, and `cleanup` will have low precision;
- exact synonyms need aliases until semantic retrieval exists;
- relation traversal is explicit rather than automatically mixed into search;
- case evidence is referenced but not indexed deeply;
- cross-repository entries are not yet one unified index.

## What would justify the next retrieval layer

Add complexity only when a concrete query fails for a reason the current structured/full-text approach cannot cheaply solve.

Likely progression:

```text
1. term weighting / exact phrase preference
2. query over aliases and facets with OR/AND controls
3. bounded relationship expansion
4. generated cross-repository index
5. semantic similarity over entry prose
6. hybrid retrieval packet for a Fieldwork skill
```

The important metric is not search cleverness. It is whether a retrieved packet helps form a better discriminator, avoid a known bad repair, or connect a new case to relevant prior evidence without flooding context.

## Counterexample requirement

Future retrieval trials should include queries where the best answer is **two related-but-distinct species**.

For example:

```text
"acknowledgement failed"
```

should not automatically collapse:

```text
acknowledge before processing
```

with:

```text
ambiguous external outcome after possible commit
```

A useful compendium sometimes answers: “these look similar; the commit/ownership boundary tells you which one you have.”
