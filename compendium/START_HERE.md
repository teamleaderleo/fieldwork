# Start here: poke at the compendium

## In simple words

This is the easiest entry point for a future human or agent who wants to browse, challenge, organize, or extend the Fieldwork compendium without first reconstructing the whole repository.

You do **not** need to understand every entry. Pick one small thread, follow it into the evidence, and leave the structure a little clearer than you found it.

```text
browse
  ↓
pick one question
  ↓
follow entry → relations → cases
  ↓
check the evidence
  ↓
add / split / connect / challenge / graduate
```

The source investigations remain authoritative. The compendium is derived memory.

## Ten-minute orientation

1. Read [`README.md`](README.md) for the object model and retrieval commands.
2. Skim one reader-facing view, usually [`views/FANTASTIC_BUGS.md`](views/FANTASTIC_BUGS.md) or [`views/COUNTEREXAMPLES.md`](views/COUNTEREXAMPLES.md).
3. Run:

```text
node scripts/compendium-index.mjs stats
node scripts/compendium-index.mjs curate
```

4. Pick one entry that looks interesting.
5. Inspect it directly and then inspect its bounded neighborhood:

```text
node scripts/compendium-index.mjs show <entry-id>
node scripts/compendium-index.mjs related <entry-id>
node scripts/compendium-index.mjs packet <entry-id>
```

6. Follow at least one `cases` reference back to the concrete evidence before changing the reusable claim.

That is enough context to begin useful work.

## Good first contributions

You can improve the corpus without inventing a new grand taxonomy.

Useful small tasks include:

- add a missing typed relationship between two existing entries;
- add a concrete case to an existing entry after checking that the owner/invariant really matches;
- add an alias that makes realistic search language find the right entry;
- find two entries that sound similar and explain why they should remain separate;
- find one over-broad claim and add a counterexample or limit;
- split an entry that hides two different owners or commit boundaries;
- merge true synonyms while preserving useful aliases;
- improve a hunting question or regression shape from a concrete case;
- add a candidate entry from a retained investigation that teaches something reusable;
- connect a mature lesson to executable enforcement when a real test/type/assertion/CI rule exists.

## A useful task ladder

### Small

```text
search phrase misses obvious entry
→ add alias/facet wording
→ validate
```

```text
entry has evidence but no useful relation
→ connect it to invariant / technique / repair / counterexample
→ validate
```

### Medium

```text
one case appears to fit an existing species
→ compare owner + invariant + failure shape
→ add as supporting case or record why it differs
```

```text
two entries overlap heavily
→ compare legal repairs and counterexamples
→ split, merge, or clarify the boundary
```

### Deep

```text
pattern appears in unrelated domains
→ compare exact state machines
→ preserve mechanism-specific differences
→ decide whether generic maturity should increase
```

```text
reusable lesson already has executable enforcement
→ record an executable-graduation object
→ link exact evidence and limits
```

## The main question to keep asking

When two cases look alike, ask:

> **Is the same owner responsible for preserving the same invariant across the same meaningful failure boundary?**

Shared words such as `cleanup`, `generation`, `ownership`, `retry`, `publication`, and `terminal` are not enough.

For example:

```text
ack before required processing
    ≠
ack lost after remote mutation may have committed
```

The first often wants later acknowledgement. The second often needs identity, reconciliation, and explicit uncertainty.

## Before adding a new entry

Search first:

```text
node scripts/compendium-index.mjs search "plain words describing the failure"
node scripts/compendium-index.mjs list --kind bug-species
```

Then ask:

1. Is this actually reusable, or is the case study itself the right home?
2. What is the smallest reusable claim?
3. What concrete case supports it?
4. What would make the claim false?
5. Is there an existing entry with the same owner/invariant relationship?
6. Which repair becomes legal because of this classification?
7. What regression or discriminator would distinguish it from nearby species?

A new entry is optional. A clarified boundary is often more valuable.

## Evidence rules

Do not upgrade evidence while summarizing it.

```text
source-read            stays source-read
model-executed         stays model-executed
target-test-prepared   stays prepared
target-executed        stays executed
```

A compendium entry may summarize a case, but the case owns exact revisions, workflow receipts, environment limitations, review history, and current external status.

When the reusable entry and a concrete case disagree, repair or narrow the reusable entry.

## Maturity is challengeable

Maturity means confidence in the reusable abstraction, not importance.

- `candidate`: actively try to break it.
- `supported`: useful evidence exists, but keep looking for boundary cases.
- `mature`: several distinct cases, meaningful limits/counterexamples, and a stable hunting/repair/test story.

Anyone may propose lowering maturity when a new counterexample exposes a hidden assumption.

## Use the curation queue

`curate` is a deterministic, read-only hint generator:

```text
node scripts/compendium-index.mjs curate
node scripts/compendium-index.mjs curate --json
```

It highlights places worth inspecting, such as orphaned entries, thin candidates, mature entries that deserve a counterexample/limits check, and executable-graduation records with weak graph connections.

These are **review prompts**, not automatic defects. A reported item may be correct as-is.

## What not to do

Avoid turning the compendium into a second technical truth store.

Do not:

- rewrite a concrete case to make a generic pattern look cleaner;
- add a giant umbrella species because several entries use the same vocabulary;
- raise maturity from intuition alone;
- treat a green CI badge as technical acceptance;
- require every investigation to emit metadata;
- create a deep directory taxonomy that forces one canonical parent;
- dump an entire repository into one context packet;
- silently contact or modify third-party upstream projects while curating this corpus.

## Where to leave work

For the current seed, Fieldwork issue `#908` owns the broad compendium direction and draft PR `#909` owns the working generic implementation. Linux/system extraction is intentionally separate in `teamleaderleo/linux-fieldwork#675` and its draft compendium branch.

A future contributor should be able to start from this file, pick one bounded question, and make progress without reading prior chat history.
