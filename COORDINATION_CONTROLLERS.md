# Coordination Reconciliation Controllers

Status: draft implementation for #304  
Parent architecture: #300  
Structured input: #302 / PR #306  
Human views: #303 / PR #310

## In simple words

Tracked coordination state describes what Fieldwork currently believes. Live facts describe what GitHub currently exposes: branch heads, pull-request heads and states, checks, issue state text, and labels.

A reconciliation controller compares the two. It reports exact conflicts and backpressure. It does not silently accept work, upgrade evidence, grant authority, merge, or contact upstream.

## First controller set

`scripts/audit_coordination.py` consumes:

- validated `findings/**/state.json` records;
- one versioned live-facts JSON snapshot;
- an optional queued-carrier pressure threshold.

It emits:

- `audit.json` — deterministic machine-readable findings;
- `RISKS.md` — human-readable conflicts and backpressure;
- `RUNNING.md` — exact active carriers and observed check state.

## Implemented checks

### Canonical source freshness

- tracked branch is absent from the live snapshot;
- live branch head differs from the tracked canonical source head.

A head mismatch expires currentness. It does not erase historical execution receipts.

### Review freshness

- review disposition is active but the reviewed head differs from canonical source;
- reviewed or landing phase has no exact reviewed head;
- canonical source moved after the recorded review.

The controller reports expiration. It never performs semantic-identity proof automatically.

### Carrier consistency

- active carrier is absent from live facts;
- live PR is closed;
- live PR head differs from tracked carrier head;
- live PR base differs from the canonical source branch when both are in the same repository;
- no check information is available;
- checks are queued, in progress, failed, cancelled, or successful.

Queue delay is reported as backpressure, not as permission to create an equivalent carrier.

### Issue coordination consistency

When a state record names a parent issue and the snapshot contains that issue:

- issue `State:` text and live `state:*` label are compared;
- closed issue with an active finding is reported;
- missing state text or state label is reported as incomplete live coordination metadata.

The finding phase and issue coordination label remain separate concepts.

### Queue pressure

When the number of active carriers whose observed checks are entirely queued reaches the configured threshold, the controller emits one global queue-pressure finding.

Recommended response:

1. pause equivalent carrier creation;
2. finish source and complete-diff reviews;
3. classify upstream/base drift;
4. reconcile findings and receipts;
5. retire duplicates and stale branches;
6. preserve exact queued runs and next actions.

### Review pressure

When tracked `review-ready` and `land-ready` surfaces exceed the configured threshold, the controller reports review pressure. It does not block research automatically, but the recommended response is to finish, repair, supersede, or close existing review surfaces before opening equivalent promotion work.

## Live-facts boundary

The controller deliberately separates collection from reconciliation.

`coordination-live-facts.json` records:

- generation time;
- exact refs;
- pull-request state, head, base, and check summaries;
- issue state, body `State:` token, labels, and update time.

A collector may later obtain those facts through the GitHub API. The reconciler remains deterministic and testable without network access.

A missing live fact is reported as unknown, not invented.

## Severity

- `error` — tracked currentness or authority-bearing routing is contradicted by live facts;
- `warning` — evidence, metadata, or execution status is incomplete or blocked;
- `info` — observed queue/running state or recommended backpressure action.

Severity never changes technical acceptance by itself.

## Safe automation boundary

Controllers may:

- generate reports on owned branches;
- mark a projection stale;
- post compact risk pointers to owned coordination issues;
- propose exact repair actions;
- open owned repair PRs for coordination defects.

Controllers may not:

- accept or reject consequential technical work;
- infer merge, release, deployment, data, spending, or upstream authority;
- upgrade evidence;
- delete evidence;
- merge or contact upstream;
- silently choose among conflicting technical conclusions.

## Command

```bash
python3 scripts/audit_coordination.py \
  --facts path/to/coordination-live-facts.json \
  --output-dir generated/coordination-audit
```

The first implementation uses retained fixtures in CI. A live collector and scheduled projection can be added after the reconciliation rules receive exact-head review.
