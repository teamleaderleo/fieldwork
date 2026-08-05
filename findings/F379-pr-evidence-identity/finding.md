# F379 — Pull-request checkout and gate evidence identity

Issue: #379  
State: `execute`  
Work class: evidence reliability / repository gate  
Canonical pull request: #380  
Failed schema-v2 head: `a8a523383ef93f8357076a6ee6d315899d518604`  
Upstream contact authorized: `no`

## In simple words

A pull-request check may execute the proposed commit itself or GitHub's generated
merge commit. The generated merge has three different base facts that must not be
collapsed:

1. the base SHA stored in the pull-request event payload;
2. the generated merge commit's actual first parent;
3. the base branch tip observed when the receipt is assembled.

Run `30694467599` proved that these values can differ. All technical commands
passed, but the merge receipt rejected a valid generated merge because schema v2
assumed the event payload base must equal the merge commit's first parent.

## Exact failed execution

At exact head `a8a523383ef93f8357076a6ee6d315899d518604`:

### Literal-head job

- job `91354817450`: success;
- interaction-reference tests: success;
- Fieldwork integrity: success;
- identity tests: 14/14;
- literal-head receipt: success.

### Merge-ref job

- job `91354817416`: failure in receipt assembly only;
- generated merge checkout:
  `eeb80abb3a81d9121acedb53781ab3dac299a3c8`;
- generated merge first parent:
  `041d29ab9c5e5859cb69518a432354be71b67af8`;
- proposed head:
  `a8a523383ef93f8357076a6ee6d315899d518604`;
- pull-request event payload base:
  `c247681f80d3504045e5b34dd99aeda4907a2829`;
- interaction-reference tests: success;
- Fieldwork integrity: success;
- identity tests: 14/14;
- receipt failure:
  `expected synthetic-merge-ref, observed other-checkout`;
- partial input artifact: `8817811126`.

This is an evidence-model defect, not a product or repository-integrity failure.

## Schema-v3 contract

### Checkout classification

- literal proposed head → `exact-head`;
- generated pull-request object with ordered parents
  `[actual merge base, proposed head]` → `synthetic-merge-ref`;
- every other internally valid checkout → `other-checkout`.

Classification uses the checked-out object, event object, proposed head, and
actual ordered parents. It does not require the event payload base to equal the
generated merge's first parent.

### Pull-request base identities

Schema v3 records:

- `event_base_sha` — the base SHA supplied by the pull-request event payload;
- `merge_base_sha` — the generated merge commit's actual first parent;
- `observed_base_sha` — the base branch tip observed while assembling the
  receipt;
- `event_base_current` — event payload base equals observed base;
- `merge_base_current` — actual merge first parent equals observed base;
- `event_merge_base_match` — event payload base equals actual merge first
  parent.

A generated merge remains valid historical integration evidence for its actual
ordered parents even when the event payload base differs. Current integration
requires a successful technical gate and `merge_base_current: true`.

A literal-head receipt retains event and observed base facts, but has no
`merge_base_sha` or current-integration claim.

### Technical gate outcome

Each receipt records:

- `technical_gate_name`;
- every command and exact step outcome;
- aggregate `technical_gate_outcome`;
- `reusable_evidence`;
- `current_integration_evidence` where applicable.

Checkout identity and technical success remain independent. A valid checkout
with a failed command is a typed failed receipt, not reusable evidence.

### Push identity

Push receipts retain:

- `event_before_sha`;
- `branch-created`, `forced-update`, or `ordinary-update`;
- no invented pull-request or merge-base values.

### Strict JSON admission

The command-line tool rejects duplicate object members and non-standard JSON
constants such as `NaN` and infinities before schema validation. Admission
failure produces no output receipt.

## Prepared controls

The focused suite now covers:

- literal-head and generated-merge classification;
- the exact stale-event-payload/current-merge shape from run `30694467599`;
- a historical merge whose actual first parent is no longer current;
- reversed, unrelated, duplicate, and self-parent controls;
- valid identity plus failed technical gate;
- exact command outcomes and aggregate gate outcome;
- malformed SHA, type, event/ref, branch, and expected-mode rejection;
- unknown and missing receipt fields;
- duplicate JSON members and non-standard constants with no output artifact;
- push branch creation, forced update, and ordinary update;
- ordinary and optimized Python parity.

Local execution before publication passed 16/16 focused controls. The committed
repository workflow remains the controlling evidence surface.

## Review carry-forward boundary

A prior disposition carries forward only when every disposition-relevant
reviewed path is byte-identical and every named governing input generation is
unchanged. Changed reviewed bytes or governing inputs require a fresh review.
File-disjoint movement is supporting evidence only.

## Current transition

1. publish schema v3 on PR #380;
2. execute literal-head and generated merge-ref jobs on that exact head;
3. inspect each input, typed receipt, and raw parent identity;
4. verify event payload base, actual merge first parent, observed base,
   currentness fields, command outcomes, reusable-evidence result, and
   current-integration result;
5. synchronize issue #379, PR #380, #213, and #160;
6. request eligible independent complete-diff review only after every
   controlling job is complete.

## Limits

- sibling head and merge artifacts remain correlated by run and exact identities
  rather than one atomic combined receipt;
- fork permission behavior, merge queues, reusable-workflow provenance, branch
  deletion, branch-protection policy, and scheduling remain separate;
- a successful receipt supports only its named technical command set;
- merge and external authority remain separate.

No merge, release, deployment, credentials, private data, spending, writer
transfer, or public-upstream interaction follows from this finding.
