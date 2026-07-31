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
- Limit: this local result prepared the retained carrier but was not target-native public Codex or proprietary host execution.

## Retained execution receipt

Canonical source head tested: `9fe73ef41ab8a9f56e430190a22d3b9017dc8b64`  
Execution carrier head: `d4e3902aac221a60e83885b6a42804558d8a25a8`  
Workflow: `30624540647`  
Platform: `ubuntu-24.04`

| Runtime | Job | Result | Artifact | Digest |
| --- | --- | --- | --- | --- |
| Node 22 | `91136627816` | all six cases passed; carrier fence, retained-result check, diff hygiene, and upload passed | `f294-connector-boundary-node-22`, artifact `8791564705` | `sha256:8340aabef008084893bc3562cb2e36c45e68eae791bf479fad2929c4440725d8` |
| Node 24 | `91136627821` | all six cases passed; carrier fence, retained-result check, diff hygiene, and upload passed | `f294-connector-boundary-node-24`, artifact `8791548565` | `sha256:375cf4910adb9b4791cb8e1ed0bdf47a97c1b9f13c816b8db1b35ad97debc032` |

Artifacts expire on 2026-08-30. Each contains one `boundary-matrix.json` report with evidence class `model-executed` and six passing cases.

## What the execution establishes

At the exact canonical model head, the synthetic contract is executable on Node 22 and 24:

- incomplete function-call argument fragments can remain non-rendered and non-dispatched;
- unknown internal event payloads can be quarantined without becoming assistant text;
- completed call identity can enforce once-only dispatch;
- cooperative cancellation can settle;
- a runtime that never settles after cancellation can produce bounded `outcome_unknown`;
- a late runtime result need not rewrite an emitted terminal receipt.

Evidence class: `model-executed`.

## What the execution does not establish

The passing model does not prove that ChatGPT, the connector runtime, mobile rendering, or public Codex implements these rules. It does not locate the observed production owner, reproduce the payload presentation, select a timeout duration, or establish safe replay semantics for state-changing tools.

## Distinguishing value

A later real-boundary fixture loses against this model when it:

- renders argument deltas or unknown event payloads as assistant text;
- dispatches before a completed call identity exists;
- dispatches one completed identity more than once;
- waits indefinitely after timeout and cancellation;
- reports plain cancellation when runtime outcome is still unknown;
- allows a late runtime result to rewrite a terminal receipt already shown to the caller.

## Carrier disposition

The workflow-only carrier has completed its purpose. This canonical source branch contains no `.github/workflows/fieldwork-f294-connector-boundaries.yml` file. After this receipt commit and exact-head Fieldwork integrity, PR #344 may close as an execution carrier; its branch is not a delivery candidate.

## Next transition

Settle the target-native public Codex characterization in owned source PR #110 through execution carrier #111. Then update the canonical finding once with both the `model-executed` and `target-executed` results, compare production settlement designs, and keep presentation ownership separate.

Upstream contact authorized: `no`.
