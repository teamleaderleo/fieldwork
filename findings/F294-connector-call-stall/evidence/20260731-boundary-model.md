# Connector presentation and settlement boundary model — 2026-07-31

## In simple words

This small model tests two contracts separately: incomplete tool-call data must not become assistant text or dispatch a tool, and a runtime that ignores cancellation must still produce a bounded terminal receipt.

It is a synthetic model. It does not run the ChatGPT host, connector runtime, mobile client, or public Codex source, so it cannot identify which real component owned the observed incident.

## Question

Can a dependency-free event adapter and runtime supervisor make the desired presentation and settlement contracts explicit enough to distinguish later target-native failures?

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

## Cases

1. partial function-call arguments never render and never dispatch;
2. an unknown internal event is quarantined as a typed unsupported event without rendering its payload;
3. a completed call dispatches once even if completion is repeated;
4. a cooperative runtime settles after cancellation;
5. a non-settling runtime returns bounded `outcome_unknown` after the cancellation grace period;
6. late completion cannot rewrite an already emitted terminal receipt.

## Local preparation result

- Environment: Node `v22.16.0` in the assistant execution container.
- Result: all six cases passed before repository materialization.
- Evidence class: `model-executed`.
- Limit: this local result prepares the retained carrier but is not target-native public Codex or proprietary host execution.

## Distinguishing value

A later real-boundary fixture loses against this model when it:

- renders argument deltas or unknown event payloads as assistant text;
- dispatches before a completed call identity exists;
- dispatches one completed identity more than once;
- waits indefinitely after timeout and cancellation;
- reports plain cancellation when runtime outcome is still unknown;
- allows a late runtime result to rewrite a terminal receipt already shown to the caller.

A passing model does not establish that any production layer implements these rules. It only defines the expected contract and negative controls.

## Next transition

Run this exact canonical source on Node 22 and 24 through a workflow-only execution carrier, retain the receipts, then transfer the result back to PR #296. Keep the finding `comparative-evaluation-active` until a target-native or host-visible fixture locates or excludes the real owner.

Upstream contact authorized: `no`.
