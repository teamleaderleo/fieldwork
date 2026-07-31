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

## Repaired generation

- Previous canonical model head: `9fe73ef41ab8a9f56e430190a22d3b9017dc8b64`.
- Repair source commit: `82908b7a1660c111525db161175ea7a86aea6736`.
- Receipt-document composition commit: `9c8823901d778f7855877e9c4f2b4f93200fb79e`.
- Repair reason: preserve cancellation causality and remove arbitrary runtime/control failure text from durable artifacts.
- Current evidence class: `target-test-prepared` for the repaired nine-case generation until exact Node 22 and 24 receipts exist.

## What a repaired execution can establish

At the exact repaired source, a green matrix can establish only the synthetic contract:

- incomplete function-call argument fragments remain non-rendered and non-dispatched;
- unknown internal event payloads are quarantined without retained payload content;
- completed call identity enforces once-only dispatch;
- only an explicit runtime acknowledgement produces `cancelled`;
- late natural completion and late independent failure retain causality-neutral states;
- non-settling runtime work produces bounded `outcome_unknown`;
- late completion cannot rewrite an emitted receipt;
- secret-shaped runtime and failed-control text is absent from the retained JSON.

Evidence class after exact execution: `model-executed`.

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

PR #344 completed the old generation and is now stale relative to the repaired canonical source. Even if its old receipts are green, it cannot promote the repaired model. A fresh workflow-only carrier must pin the repaired exact head, require schema version 2 and nine cases, run Node 22 and 24, inspect retained artifacts, and remain excluded from delivery.

## Next transition

Create one fresh execution carrier over the repaired canonical head, retain and inspect both schema-version-2 artifacts, and transfer only those receipts to PR #296. In parallel, settle the target-native public Codex characterization in source PR #110 through execution carrier #111. Compare the synthetic and target-native settlement evidence without claiming either locates the proprietary presentation owner.

Keep the finding `comparative-evaluation-active` until a target-native or host-visible fixture locates or excludes the real owner.

Upstream contact authorized: `no`.
