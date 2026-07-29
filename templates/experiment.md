# Experiment: <short name>

Experiment ID: `EXP-YYYYMMDD-short-name`

State: `draft | running | complete | negative-result | blocked | promoted`

Claim scope: `mechanism | interface | integration | operational | ecosystem`

Integration context: none or path to context dossier

Related batch, campaign, lane, or finding: none

Owner:

Date:

## Question

State one bounded question whose possible outcomes can be distinguished by this experiment.

## Why this experiment

Explain what decision, hypothesis, or larger investigation this result informs.

## Scope boundary

State what level the experiment actually supports. Separate the isolated mechanism from any wider integration or operational claim.

## Sources and environment

For each consequential source, record its title, stable URL, version or revision, retrieval date, exact supported claim, and evidence label.

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

## Wider integration context

Leave this section mechanism-only when appropriate.

When asserting wider usefulness or consequence, link `templates/integration-context.md` or an existing dossier and summarize:

- where the mechanism sits in the workflow;
- who or what depends on it;
- how failure propagates;
- which use cases are documented, observed, inferred, or illustrative;
- what the toy model preserves and omits.

## Uncertainty and threats to validity

Record nondeterminism, environment dependence, missing cases, weak controls, competing explanations, and alternative architectures that could produce a different integration result.

## Reproduction status

- [ ] Exact command recorded
- [ ] Source revisions or versions recorded
- [ ] Evidence labels used for wider claims
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
- preserve as a regression fixture;
- add or revise an integration-context dossier.

## Boundaries

- Upstream contact remains unauthorized unless explicitly recorded otherwise.
- No secrets, production payloads, or proprietary inputs were retained.
- Mechanism evidence is not presented as integration or operational proof without supporting context.