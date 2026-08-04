# Upstream Packet: TITLE

Campaign:  
Target:  
State: `candidate`

## Proposal

Begin with the smallest defensible statement:

> I propose changing X so that Y remains true when Z happens.

If no change is yet justified, state the concrete question instead.

## Current and proposed behaviour

Prefer code, pseudocode, a sequence trace, or an arrow diagram when it expresses the mechanics more directly than prose.

```text
current:
input ──▶ step A ──failure──▶ stop
                          step B never runs

proposed:
input ──▶ settle A ──▶ settle B ──▶ publish failures
```

Use prose here only for details the representation does not capture.

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

Write the property the change must preserve.

```text
Example: every admitted cleanup hook settles before close() publishes failure.
```

## Scope

```text
included:
excluded:
```

Do not mix execution machinery, research notes, unrelated cleanup, or generated output into the product patch.

## Candidate implementation

```text
fork and branch:
base revision:
head revision:
changed components:
```

A compact pseudocode sketch is encouraged when it lets a reviewer understand the patch before reading the diff.

## Verification

Show the evidence in the form closest to the claim: failing/passing regression, truth table, matrix, trace, benchmark, fault injection, or adversarial schedule. Do not turn a short receipt into a large bullet inventory.

## Tradeoffs and alternatives

Use prose for the judgment that code cannot answer: compatibility, API shape, ownership, review cost, rejected designs, and why the narrow change is preferable.

## Recovery

State how to revert, disable, or contain the change when recovery is relevant.

## Upstream context

Keep links quiet until contact is deliberate. When submitted, mark intentional direct references according to `REFERENCE_POLICY.md`.

## AI assistance

Describe how AI systems contributed to research or implementation, how outputs were checked, and any disclosure required by target policy.

## Human accountability

```text
reproduced problem:          yes / no
reviewed every change:       yes / no
can defend implementation:   yes / no
ran stated verification:     yes / no
checked current policy:      yes / no
undisclosed upstream contact:no
```

## Maintainer decision requested

State the smallest concrete decision needed. Do not ask maintainers to infer the proposal from the dossier.