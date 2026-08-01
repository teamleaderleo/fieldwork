# F379 — Pull-request checkout and gate evidence identity

Issue: #379  
State: `execute`  
Work class: evidence reliability / repository gate  
Canonical pull request: #380  
Repair input head: `97a08852140047e4f9a37a5d4bdc37d4dd9dce7e`  
Upstream contact authorized: `no`

## In simple words

A pull-request check may execute the proposed commit itself or GitHub's generated merge for one pull-request event. A push check executes the pushed event commit. These are different Git objects with different claims.

The evidence receipt also needs to say which base generation constructed a pull-request event, which base branch tip was observed later, whether the named technical commands passed, and whether the result can support a reusable evidence claim. A typed checkout identity alone cannot turn a failed gate into reusable evidence.

## Confirmed predecessor defect

Fieldwork's earlier integrity workflow used the generated pull-request merge by default while coordination records often described its result as exact-head execution. PR #378 established the mismatch:

| Identity | SHA |
| --- | --- |
| declared pull-request head | `c642af5e7b934055e8ba6389acddbc8f73be1c58` |
| event base | `c247681f80d3504045e5b34dd99aeda4907a2829` |
| generated merge checkout | `63eed97c9fd3d350502b50e4ecd6ba91614287c5` |

Run `30635730689`, job `91172725027`, tested the generated merge. That is merge-ref integration evidence for the two named parents.

## Retained checkout contract

- literal proposed head → `exact-head`;
- generated pull-request merge with ordered parents `[event base, head]` → `synthetic-merge-ref`;
- every other internally valid checkout → `other-checkout`.

Names and workflow labels do not establish those classes. Exact SHA and parent identity do.

## Repair selected after complete review

Reviews `4829961152` and `4830554342` found three remaining receipt gaps in the predecessor generation.

### 1. Event base and observed base are separate facts

For pull requests, schema v2 records:

- `event_base_sha` — `github.event.pull_request.base.sha`, which governed construction of the event merge;
- `observed_base_sha` — the branch tip read when the receipt is created;
- `base_current` — exact equality between those generations.

Synthetic merge classification uses `event_base_sha` and ordered parents. A later base move leaves a valid historical merge identity with `base_current: false`. It does not erase the event identity or create a current integration claim.

`current_integration_evidence` is true only for a successful synthetic merge gate whose event base still equals the observed branch tip.

### 2. Technical gate outcome is inside the receipt

Each workflow command is a separate named step. Schema v2 records:

- `technical_gate_name`;
- every command and its exact step outcome;
- aggregate `technical_gate_outcome`;
- `reusable_evidence`.

Checkout classification remains independent. Reusable evidence requires a successful named command set and an accepted checkout class. A valid identity with a failed command remains a typed failed receipt.

### 3. Review carry-forward is byte exact

A prior disposition can carry forward without fresh review only when every disposition-relevant reviewed path is byte-identical and every named governing input generation is unchanged. The receipt must record old/new generations and blobs, governing-input equality, and `changed reviewed paths: none`.

Changed reviewed bytes or governing inputs require a fresh receipt. File-disjoint movement is supporting evidence only.

## Push identity boundary

Push receipts record `event_before_sha` as event metadata rather than calling it a base or parent. They also record one explicit update state:

- `branch-created` for an all-zero `before` SHA;
- `forced-update` when the event says the push was forced;
- `ordinary-update` otherwise.

This field does not infer ancestry beyond the event facts. Branch-deletion execution remains outside the current workflow.

## Prepared controls

The focused suite covers:

- exact head and synthetic merge classification;
- reversed and unrelated merges;
- moved-base historical merge identity with `base_current: false`;
- moved-base literal-head execution without a current integration claim;
- valid identity plus failed technical gate producing `reusable_evidence: false`;
- exact command outcomes and aggregate gate outcome;
- malformed SHA, type, event/ref, branch metadata, and expected-mode rejection;
- duplicate and self-parent rejection;
- unknown and missing receipt-field rejection;
- push branch creation, forced update, and ordinary update states;
- ordinary and optimized Python parity.

Local model execution before publication passed 14/14 focused controls. The repository workflow remains the controlling evidence surface for the committed generation.

## Historical execution retained

Predecessor head `97a08852140047e4f9a37a5d4bdc37d4dd9dce7e` passed run `30642857359`:

- literal-head job `91196868451` classified the source head as `exact-head`;
- merge-ref job `91196868387` classified merge `754b64c8a71b13d44fe0c2b3f4ea5983ed86066f` with ordered parents `[041d29ab9c5e5859cb69518a432354be71b67af8, 97a08852140047e4f9a37a5d4bdc37d4dd9dce7e]` as `synthetic-merge-ref`.

Those runs support the retained checkout distinction. Schema-v2 currentness and technical-outcome claims require execution on the repaired head.

## Current transition

1. execute literal-head and generated merge-ref jobs on the repaired PR #380 head;
2. inspect the uploaded schema-v2 input, typed receipt, and raw parent identity from both jobs;
3. verify the receipt names each technical command and outcome;
4. verify `event_base_sha`, `observed_base_sha`, `base_current`, and `current_integration_evidence` against the live event;
5. synchronize PR #380, issue #379, review queue #213, and Delivery Desk #160 from the exact result;
6. request eligible independent complete-diff review only after every controlling job is complete.

## Limits

- sibling head and merge artifacts remain correlated by run and exact identities rather than one atomic combined receipt;
- fork permission behavior, merge queues, reusable-workflow provenance, branch deletion, branch-protection policy, and gate-scheduling optimization remain separate work;
- a successful checkout identity says nothing beyond the named technical command set;
- merge and external authority remain separate.

No merge, release, deployment, credentials, private data, spending, writer transfer, or public-upstream interaction follows from this finding.
