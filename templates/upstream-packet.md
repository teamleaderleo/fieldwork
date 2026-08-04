# Upstream Packet: TITLE

Campaign:  
Target:  
State: `candidate`

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

## Tradeoffs and alternatives

Use prose for the judgment that code can't answer: compatibility, API shape, ownership, review cost, rejected designs, and why the narrow change is preferable.

## Recovery

State how the change could be reverted, disabled, or contained when recovery is relevant.

## Upstream context

Keep links quiet until contact is deliberate. When submitted, mark intentional direct references according to `REFERENCE_POLICY.md`.

## AI assistance

Describe how AI systems contributed to research or implementation, how outputs were checked, and any disclosure the target policy will require.

## Human accountability

```text
reproduced problem:           yes / no
reviewed every change:        yes / no
can defend implementation:    yes / no
ran stated verification:      yes / no
checked current policy:       yes / no
undisclosed upstream contact: no
```

## Maintainer decision requested

State the smallest concrete decision needed. Don't ask maintainers to infer the proposal from the dossier.