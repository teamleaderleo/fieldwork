# Connector presentation and settlement boundary model — 2026-07-31

## In simple words

This small model tests two contracts separately: incomplete tool-call data must not become assistant text or dispatch a tool, and a runtime that ignores cancellation must still produce a bounded terminal receipt without inventing cancellation certainty.

It is a synthetic model. It does not run the ChatGPT host, connector runtime, mobile client, or public Codex source, so it cannot identify which real component owned the observed incident.

## Question

Can a dependency-free event adapter and runtime supervisor make the desired presentation, causality, privacy, and settlement contracts explicit enough to distinguish later target-native failures?

## Owned path

- Runner: `findings/F294-connector-call-stall/evidence/run_boundary_matrix.mjs`
- Retained workflow artifacts: `boundary-matrix.json`
- Canonical finding: `findings/F294-connector-call-stall/finding.md`

## Command

```sh
node findings/F294-connector-call-stall/evidence/run_boundary_matrix.mjs
```

To retain the JSON result:

```sh
RESULTS_DIR=/tmp/f294-results \
  node findings/F294-connector-call-stall/evidence/run_boundary_matrix.mjs
```

## Current receipt vocabulary

The repaired model distinguishes facts that the previous version collapsed:

- `completed`: runtime settled before the host deadline;
- `failed`: runtime failed before the host deadline, with a fixed content-minimised diagnostic;
- `cancelled`: runtime explicitly acknowledged the cancellation request;
- `settled_after_cancel_request`: runtime fulfilled after cancellation was requested, but causality is unconfirmed;
- `failed_after_cancel_request`: runtime rejected after cancellation was requested, but causality is unconfirmed;
- `outcome_unknown`: runtime did not settle during the bounded grace interval.

A host cancellation request is not proof that cancellation caused a later settlement or that remote effects stopped.

## Current cases

1. partial function-call arguments never render and never dispatch;
2. an unknown internal event is quarantined without rendering or retaining its payload;
3. a completed call dispatches once even if completion is repeated;
4. an explicitly cooperative runtime acknowledges cancellation and receives `cancelled`;
5. natural completion during the grace window remains `settled_after_cancel_request` rather than becoming cancellation;
6. independent failure during the grace window remains `failed_after_cancel_request`, with secret-shaped source text omitted;
7. a non-settling runtime returns bounded `outcome_unknown` after the cancellation grace period;
8. late completion cannot rewrite an already emitted terminal receipt;
9. failed-control diagnostics retain only a fixed code and error type, not exception messages or stacks.

## Superseded six-case execution receipt

The previous model generation did execute successfully and remains useful historical evidence for its narrower mechanics.

Canonical source head tested: `9fe73ef41ab8a9f56e430190a22d3b9017dc8b64`  
Execution carrier head: `d4e3902aac221a60e83885b6a42804558d8a25a8`  
Workflow: `30624540647`  
Platform: `ubuntu-24.04`

| Runtime | Job | Result | Artifact | Digest |
| --- | --- | --- | --- | --- |
| Node 22 | `91136627816` | old six-case model passed | `f294-connector-boundary-node-22`, artifact `8791564705` | `sha256:8340aabef008084893bc3562cb2e36c45e68eae791bf479fad2929c4440725d8` |
| Node 24 | `91136627821` | old six-case model passed | `f294-connector-boundary-node-24`, artifact `8791548565` | `sha256:375cf4910adb9b4791cb8e1ed0bdf47a97c1b9f13c816b8db1b35ad97debc032` |

Artifacts expire on 2026-08-30. Each contains one schema-version-1 report with six passing cases.

That receipt proves the old model was executable on Node 22 and 24. It does **not** clear the same-head review defects:

- every grace-window fulfillment or rejection was labelled `cancelled` without runtime acknowledgement;
- raw runtime error text and failed-control stacks could enter the uploaded JSON.

The old evidence therefore remains `model-executed / superseded-generation`. It must not be attributed to the repaired source.

## Exact repaired execution receipt

- Canonical source head: `3a0cf7b1b6eb579277ed8749fd5dd6f0d514a709`.
- Execution-only carrier: PR #351 at `bb5e8a7ccaa51ae68181a2b8845d9ba1f63b96f4`.
- Repaired model workflow: `30626853243`, success.
- Exact-head Fieldwork integrity: `30626853359`, success.
- Platform: `ubuntu-24.04`.
- Source/carrier fence: the carrier differed from the canonical source by `.github/workflows/fieldwork-f294-connector-boundaries-v2.yml` only.

| Runtime | Job | Result | Artifact | Artifact digest | JSON SHA-256 |
| --- | --- | --- | --- | --- | --- |
| Node 22.23.1 | `91144004050` | schema v2, exact `9/9` passed | `8792117981` | `sha256:db925d945281dbe8ed6dcebed9d357f6f2108156b1736fc047e0a8d74819d127` | `f1ebbce9d5532e4023dfd2dfed99315d62d5e48165efe5de9fbf58b5d27d8385` |
| Node 24.18.0 | `91144003927` | schema v2, exact `9/9` passed | `8792114882` | `sha256:0966d9ac21dac9e04ca1bba4f092ab8a46b50a981e75abc0dfe619d92c38ef28` | `dc24e185ffc0d7d0ae7eebf6afeb77ed78d70e0f7c17d7062ee3ee35040edb63` |

Both inspected artifacts contain:

- `schemaVersion: 2`;
- `evidenceClass: model-executed`;
- the same nine uniquely ordered passing cases;
- an explicit synthetic-model claim limit;
- no secret-shaped runtime text, provider failure message, failed-control source text, or stack;
- bounded non-settlement after approximately 41 ms in the synthetic control;
- an immutable terminal `outcome_unknown` receipt after late completion.

The runtime-version field accounts for the expected JSON byte difference. The semantic case names, statuses, receipt kinds, and fixed codes agree across Node 22 and 24.

Current evidence class: `model-executed` for the repaired schema-version-2 synthetic contract.

## What the repaired execution establishes

At the exact repaired source, the green matrix establishes only the synthetic contract:

- incomplete function-call argument fragments remain non-rendered and non-dispatched;
- unknown internal event payloads are quarantined without retained payload content;
- completed call identity enforces once-only dispatch;
- only an explicit runtime acknowledgement produces `cancelled`;
- late natural completion and late independent failure retain causality-neutral states;
- non-settling runtime work produces bounded `outcome_unknown`;
- late completion cannot rewrite an emitted receipt;
- secret-shaped runtime and failed-control text is absent from the retained JSON.

## What execution cannot establish

A passing synthetic model does not prove that ChatGPT, the connector runtime, mobile rendering, or public Codex implements these rules. It does not locate the observed production owner, reproduce the payload presentation, select a production timeout duration, prove runtime cleanup, prove remote-effect settlement, or establish safe replay semantics for state-changing tools.

## Distinguishing value

A later real-boundary fixture loses against this model when it:

- renders argument deltas or unknown event payloads as assistant text;
- dispatches before a completed call identity exists;
- dispatches one completed identity more than once;
- waits indefinitely after timeout and cancellation request;
- reports plain cancellation without a runtime acknowledgement;
- treats settlement after a cancellation request as proof that cancellation caused it;
- stores provider/private/secret-shaped runtime failure text in durable receipts;
- allows a late runtime result to rewrite a terminal receipt already shown to the caller.

## Evidence-minimisation boundary

Unknown event payloads, runtime error messages, and failed-control stacks are deliberately excluded from the repaired `boundary-matrix.json`. The retained result contains fixed codes, error types, synthetic case names, timings, and model outputs required to classify each control.

This model does not claim every production diagnostic must omit every message. It establishes that a durable cross-boundary receipt must not retain arbitrary provider or secret-shaped text by default.

## Carrier disposition

PR #351 completed the exact repaired generation and is now execution-only history. Its workflow must not become a delivery surface. The exact receipts are retained above; closing the carrier does not merge the workflow or upgrade the evidence beyond `model-executed`.

PR #344 remains the superseded six-case execution history.

## Next transition

Settle the target-native public Codex non-settling characterization through its current source and carrier, then compare the target-native settlement boundary with this synthetic contract. A host-visible fixture is still required to locate or exclude the proprietary presentation owner.

Keep the finding `comparative-evaluation-active` until target-native or host-visible evidence locates or excludes the real owner. No additional unchanged synthetic execution is warranted.

Upstream contact authorized: `no`.
