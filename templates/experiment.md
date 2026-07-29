# Experiment: <short name>

Experiment ID: `EXP-YYYYMMDD-short-name`

State: `draft | running | complete | negative-result | blocked | promoted`

Related batch, campaign, lane, or finding: none

Owner:

Date:

## Question

State one bounded question whose possible outcomes can be distinguished by this experiment.

## Why this experiment

Explain what decision, hypothesis, or larger investigation this result informs.

## Sources and environment

- system or package:
- exact revision or version:
- retrieval date:
- OS and architecture:
- runtime and version:
- dependency lock or installation command:
- relevant configuration:
- network policy:

## Inputs

List synthetic fixtures and canonical case packs used. Record exclusions and any redaction.

## Command

```text
<exact command>
```

## Distinguishing outcomes

| Observation | Interpretation |
|---|---|
| | |

## Procedure

List the exact steps. Keep setup, execution, and cleanup distinguishable.

## Actual result

Describe what happened without overstating the conclusion.

## Raw evidence

- machine-readable result:
- retained logs or traces:
- fixtures:
- repeated-run information:

## Interpretation

State which hypothesis the result supports, weakens, or leaves unresolved.

## Uncertainty and threats to validity

Record nondeterminism, environment dependence, missing cases, weak controls, and competing explanations.

## Reproduction status

- [ ] Exact command recorded
- [ ] Source revisions or versions recorded
- [ ] Deterministic in the declared environment
- [ ] Repeated run available
- [ ] Independent reproduction available
- [ ] Cross-platform result available
- [ ] Negative result

## Disposition

Choose one:

- discard as disposable scratch;
- retain as a completed experiment;
- repeat under another environment;
- promote to a finding;
- attach to a batch probe;
- promote to a campaign lane;
- preserve as a regression fixture.

## Boundaries

- Upstream contact remains unauthorized unless explicitly recorded otherwise.
- No secrets, production payloads, or proprietary inputs were retained.
