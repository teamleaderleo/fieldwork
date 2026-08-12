# Upstream Packet: TITLE

Campaign:  
Target:  
State: `candidate`

> This packet is preparation-only. Fieldwork agents and automated workers must never submit, post, comment, review, react, or otherwise mutate a third-party upstream repository. A human must perform any upstream interaction manually outside Fieldwork automation.

## Internal dossier and maintainer-facing draft

This packet is the internal evidence dossier. The eventual maintainer-facing issue or pull-request body should usually be much shorter and should follow the target repository's own template and vocabulary.

A strong maintainer-facing draft normally does four things and then stops:

1. name the concrete bad behaviour and consequence;
2. explain the causal ownership, ordering, identity, or state mistake just far enough to make the repair understandable;
3. state the smallest change that restores the intended property;
4. name the regression or validation that distinguishes the fix from the old behaviour.

Add scope exclusions only when they prevent a likely misunderstanding. Prefer one specific non-goal over a general disclaimer.

Do **not** mechanically export Fieldwork process language into the public draft. Exact SHAs, evidence classes, carrier history, queue state, internal review receipts, discarded variants, and coordination mechanics belong here unless the target repository explicitly asks for them.

Match the target's house style. A repository that wants a three-paragraph bug-fix explanation should get three paragraphs; a repository with a structured checklist should get its checklist. Use the target's title convention too: name the repaired behaviour or mechanism, not the Fieldwork campaign or internal taxonomy. The technical invariant should survive the compression even when the headings do not.

Compression never overrides target-required checklists, changelog entries, contribution metadata, or AI-use disclosure. Include those exactly where the target policy requires them.

## Contribution lineage

Track substantive authorship and contribution separately from pull-request mechanics. A target repository may close one contribution PR and land the same work through a maintainer branch, factory PR, squash, cherry-pick, regenerated patch, or other repository-native flow. That administrative change does not by itself mean someone else independently did the work.

Classify the outcome from the evidence:

- **landed directly** — the submitted contribution itself was merged;
- **landed via target-managed successor, contribution lineage retained** — the landing materially incorporates the submitted implementation, reproduction, tests, analysis, or repair boundary, even if maintainers changed placement, wording, scope, or small implementation details;
- **independently displaced** — use this only when the successor was substantively independent and the record does not support material derivation from the submitted contribution.

When commit metadata names the contributor as an author or co-author, record that plainly. When the diff and history show material incorporation but formal metadata is different, describe the contribution accurately without inventing a percentage or claiming sole authorship. Do not use words like `superseded` or `replaced` in a way that implies the contribution was irrelevant when the target merely chose a different landing vehicle.

Preserve the exact contribution trail internally: submitted PR, reproduced behavior, tests, important review discussion, target-requested narrowing, successor landing, and any author/co-author metadata. This is historical accuracy, not credit inflation.

## Proposal

Begin with the smallest defensible statement:

> I propose changing X so that Y will remain true when Z happens.

If no change is justified yet, state the concrete question instead.

Write naturally. Contractions are welcome, and tense should tell the reader where each claim sits in time:

```text
current behaviour   → present tense
proposed effect     → future tense
completed evidence  → past tense
remaining work      → future tense
```

## Current and proposed behaviour

Prefer code, pseudocode, a sequence trace, or an arrow diagram when it'll express the mechanics more directly than prose.

```text
current:
input ──▶ step A ──failure──▶ stop
                          step B never runs

proposed:
input ──▶ settle A ──▶ settle B ──▶ publish failures
```

Use prose here only for details the representation doesn't capture.

## Consequence

State the demonstrated user, correctness, compatibility, security, performance, or operational consequence. Keep illustrative consequences labelled as illustrative.

## Reproduction

```text
source revision:
environment:
fixture:
command or invocation:
expected:
actual:
deterministic:
```

Explain what realistic property the reduction preserves and what it omits.

## Cause

State the demonstrated cause. Use a small code excerpt, state transition, or trace where useful. Label hypotheses and uncertainty clearly.

## Invariant

Write the property the change will preserve.

```text
Example: every admitted cleanup hook will settle before close() publishes failure.
```

## Scope

```text
included:
excluded:
```

Don't mix execution machinery, research notes, unrelated cleanup, or generated output into the product patch.

## Candidate implementation

```text
fork and branch:
base revision:
head revision:
changed components:
```

A compact pseudocode sketch is encouraged when it'll let a reviewer understand the patch before reading the diff.

## Verification

Show the evidence in the form closest to the claim: failing/passing regression, truth table, matrix, trace, benchmark, fault injection, or adversarial schedule. Don't turn a short receipt into a large bullet inventory.

For the maintainer-facing draft, compress this to the tests that explain the change. Keep exhaustive matrices and receipt bookkeeping in the internal dossier unless the target asks for them.

## Tradeoffs and alternatives

Use prose for the judgment that code can't answer: compatibility, API shape, ownership, review cost, rejected designs, and why the narrow change is preferable.

## Recovery

State how the change could be reverted, disabled, or contained when recovery is relevant.

## Upstream context

Keep links quiet while preparing the packet. If a human later submits upstream manually, Fieldwork may record that already-existing interaction according to `REFERENCE_POLICY.md`. The packet itself never authorizes an automated upstream write.

## AI assistance

Describe how AI systems contributed to research or implementation, how outputs were checked, and any disclosure the target policy will require.

## Human accountability

```text
reproduced problem:           yes / no
reviewed every change:        yes / no
can defend implementation:    yes / no
ran stated verification:      yes / no
checked current policy:       yes / no
automated upstream write:     no
```

## Maintainer decision requested

State the smallest concrete decision a human may eventually ask upstream maintainers to make. Don't ask maintainers to infer the proposal from the dossier.
