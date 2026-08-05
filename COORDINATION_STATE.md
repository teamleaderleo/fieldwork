# Structured Coordination State

Status: draft implementation for #302  
Parent architecture: #300

## In simple words

A single word such as `ready` cannot say whether research is finished, which exact source was reviewed, whether target tests ran, whether an external source boundary is current, whether temporary execution machinery is still active, or whether anyone has authority to merge or contact upstream.

Each retained finding may therefore carry a `state.json` sidecar. The sidecar stores independent, executable coordination facts. The canonical `finding.md` remains the human technical explanation.

## Canonical files

```text
findings/F<issue>-<slug>/
├── finding.md
├── state.json
├── evidence/
├── alternatives/
├── artifacts/
└── reviews/
```

`finding.md` owns:

- current explanation and consequence;
- governing invariant;
- alternatives and precedent;
- selected direction;
- uncertainty and reopening trigger;
- transition framing.

`state.json` owns:

- compact human digest and priority;
- phase and work class;
- exact source and execution-carrier identity;
- claim-scoped evidence receipts;
- review disposition, reviewed head, and versioned reviewed inputs;
- source freshness;
- repository-scoped writer lease and transition generation;
- per-action authority records;
- blocker, next transition, and terminal record.

Issue and pull-request comments remain routing events. They are not another canonical state store.

## Independent axes

### Phase

- `research-active`;
- `comparative-evaluation-active`;
- `review-ready`;
- `design-decision-ready`;
- `delivery-gate-ready`;
- `land-ready`;
- `stopped`;
- `closed`.

Phase answers where the finding is in its lifecycle. It does not state evidence strength, review outcome, currentness, or authority.

Review-facing phases require:

- an exact 40-character lowercase Git review head;
- at least one versioned `record@generation` reviewed input;
- claim-scoped evidence;
- canonical source identity for technical work;
- equality between reviewed head and canonical source head when source exists.

An `ACCEPT` disposition is invalid whenever its reviewed head differs from canonical source, not only at the final landing phase.

`stopped` and `closed` require a terminal record, no active execution carrier, and no active writer lease.

### Work class

- `owned-product-delivery`;
- `upstream-fork-research`;
- `execution-carrier`;
- `evidence-documentation`;
- `blocked-sensitive`.

### Review disposition

- `ACCEPT`;
- `REPAIR`;
- `HOLD`;
- `EXECUTE`;
- `REJECT`;
- `none`.

The exact reviewed head and every disposition-bearing finding, issue, decision, or authority input are versioned independently.

### Evidence

Every consequence-bearing claim records:

- claim text;
- one evidence level;
- exact receipt or durable path;
- the limit of that evidence.

Levels:

- `source-read`;
- `model-executed`;
- `target-test-prepared`;
- `target-executed`;
- `integration-executed`;
- `full-gate`.

One finding may contain claims at several levels. Synthesis never upgrades them.

## Exact identity

Git source, carrier, review, and base revisions use full lowercase 40-character Git SHAs. Symbolic refs, short SHAs, branch names, and arbitrary strings are not exact identities.

A non-Git external freshness boundary is typed as:

```json
{
  "kind": "version | retrieval | git-sha",
  "value": "exact boundary value",
  "source": "what was observed"
}
```

Historical execution remains evidence after the external source moves. Currentness, review, proposal, and landing claims may expire.

## Canonical source and active carrier

The canonical source identifies the product branch and exact head under consideration.

The active carrier identifies temporary evidence-producing machinery and its exact purpose. It never becomes the merge or upstream candidate.

Default per invariant:

```text
one preferred canonical source
one active execution carrier
```

A carrier may be replaced only after a classified harness/workflow defect, polluted diff, materially different execution purpose, or explicit retirement. Runner queue delay alone is not a replacement reason.

## Writer lease

Problem-space participation remains open. Mutation of one shared artifact does not.

A non-empty writer lease records:

- state and current holder;
- repository;
- resource kind: branch, path, or record;
- resource identity;
- generation type and exact generation;
- acquisition and renewal timestamps;
- positive duration in seconds;
- monotonic transition number;
- previous generation and transfer record for takeover.

The collision key is:

```text
(repository, resource_kind, resource)
```

The same path in different repositories does not collide. The same resource in one repository cannot have two active leases.

The effective expiry boundary is:

```text
renewed_at + duration_seconds
```

The tracked validator checks that the lease is structurally renewable and takeover is generation-bound. A reconciliation controller compares the expiry boundary with a versioned observation time and classifies the lease as current or stale. It never infers a takeover silently.

A takeover increments `transition` and requires both `previous_generation` and a durable `transfer_record`. Force-pushing or silently rewriting another active branch remains prohibited.

## Authority

Authority is per action and fail-closed. Technical phase, review acceptance, green CI, or a parent initiative never grants authority.

Actions:

- merge;
- release;
- deploy;
- upstream contact;
- private or production data access;
- material spending.

Each action record contains:

- `state`: `denied` or `authorized`;
- exact action name;
- typed target, location, operation ID, and data class;
- versioned authority source and generation;
- issue time;
- expiry or revocation record.

A denied action has an empty target and source. An authorized action is invalid unless all scope and provenance fields are present. Data authority additionally identifies private, production, or regulated data.

Authority for one operation does not generalize to another PR, repository, follow-up message, deployment, dataset, or spend.

## Precedence when records disagree

1. exact immutable source and workflow facts;
2. reviewed structured state at its recorded generation;
3. canonical finding at its exact PR/head;
4. live issue/PR metadata and routing comments;
5. generated Review Queue, Delivery Desk, and cockpit projections;
6. historical narrative and chat.

A lower layer does not silently overwrite a higher layer. Reconciliation reports the conflict and exact repair path.

## Legacy migration

Legacy words are interpreted conservatively:

| Legacy text | Default migration |
| --- | --- |
| `investigating` | `phase: research-active` |
| `ready-for-synthesis` | usually `phase: review-ready`; require canonical finding and exact evidence review |
| `needs-decision` | `comparative-evaluation-active` unless a non-delegable decision is proved |
| `blocked` | preserve the actual phase and set `blocker` |
| `complete` | inspect the transition; migrate to an explicit review, delivery, landing, stopped, or closed phase |
| `negative-result` | usually `phase: stopped` with terminal reason and reopening trigger |
| `ready` | insufficient; derive phase from canonical records or report a migration error |

Migration never rewrites historical issue comments. It adds a current normalized record.

## Validation

The tracked validator and regressions reject at least:

- boolean values masquerading as integer schema versions or IDs;
- placeholder or timezone-naive timestamps;
- short or symbolic Git revisions;
- review-facing phases without exact identity, reviewed inputs, evidence, or source;
- stale accepted review/source relationships;
- terminal phases with active work;
- carriers without canonical source;
- duplicate state IDs, canonical paths, active carriers, or repository-scoped leases;
- active leases without exact generation, renewal, duration, and takeover provenance;
- authority that lacks action, target, operation, source generation, time, expiry, or revocation;
- evidence claims without receipts or limits.

The JSON Schema documents the interchange contract. The standard-library validator enforces cross-field and cross-record invariants without a network dependency. Live GitHub reconciliation belongs to #304.

## Adoption

Adopt incrementally. A finding without `state.json` remains valid but is not eligible for generated current-state projections until materialized or explicitly classified as legacy input.

Pilot examples should cover:

- active comparative evaluation;
- exact source plus one execution carrier;
- stopped negative result;
- review-ready evidence packet;
- land-ready owned delivery with merge authority still denied;
- explicit, bounded, expiring authority;
- clean lease transfer between workers.
