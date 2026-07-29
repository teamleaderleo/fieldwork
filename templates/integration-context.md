# Integration Context: TITLE

Context ID:
Owner:
Date:
Target label:
Target hub:
Owned testbeds used:
Related experiments:
Related batch or campaign:
Claim scope: mechanism | interface | integration | operational | ecosystem

## In simple words

- What mechanism or boundary is this about?
- Where does it sit in a larger workflow?
- Who or what could depend on it?
- What consequence is documented, observed, inferred, illustrative, or unknown?
- What decision can currently be made?

## Context question

What wider claim or use requires evidence beyond the isolated mechanism?

## Change thesis

- current behaviour:
- consequence:
- candidate improvement:
- evidence boundary:

## System role

Where does the tested mechanism sit in the larger workflow?

## Actors and workflow

```text
actor or component
→ boundary under test
→ dependent component
→ durable or user-visible consequence
```

Describe callers, intermediaries, state owners, operators, and affected users.

## Contract boundaries

Record relevant:

- inputs and outputs;
- state and side effects;
- ordering and concurrency;
- retry and timeout behaviour;
- persistence and recovery;
- identity, correlation, and ownership;
- compatibility and version boundaries.

## Representative scenarios

For each scenario, state whether it is documented, observed, inferred, or illustrative.

### Scenario 1

- Evidence label:
- Starting state:
- Trigger:
- Component sequence:
- Expected result:
- Failure result:
- User or operator consequence:
- Smallest model preserving the important property:

## Owned-repository evidence

| Testbed or neutral id | Revision and branch | Scenario | Observation | What it supports | Limitation |
|---|---|---|---|---|---|
| | | | | | |

Do not present one owned application as proof of general adoption.

## Failure propagation

What changes outside the isolated component when the mechanism fails?

## Operational visibility

What traces, logs, metrics, audit records, state checks, or user-visible symptoms would reveal the outcome?

## Deployment assumptions

- topology:
- concurrency:
- storage:
- network and failure model:
- versions:
- security and privacy boundaries:

## Real-world evidence

| Claim | Label | Source | Version/date | Retrieved | Section/path | Limitations |
|---|---|---|---|---|---|---|
| | Normative / Documented / Observed / Inferred / Illustrative / Unknown | | | | | |

Use primary sources where available. Wrap external GitHub interaction references under `REFERENCE_POLICY.md`.

## Mapping to tests and trials

| Wider property | Experiment, case, or testbed trial | What it demonstrates | What it does not demonstrate |
|---|---|---|---|
| | | | |

## Competing architectures

Could a different architecture, contract, deployment, or state model produce a different result?

## Open assumptions

List every wider claim that remains plausible but unverified.

## Decisions enabled

What can be responsibly decided from this context?

## Promotion status

- [ ] Plain-language block updated
- [ ] Target hub and label recorded
- [ ] Mechanism finding only
- [ ] Integration claim supported
- [ ] Operational claim supported
- [ ] Additional context research required
- [ ] Suitable for campaign synthesis
- [ ] Suitable for upstream packet after explicit authorization