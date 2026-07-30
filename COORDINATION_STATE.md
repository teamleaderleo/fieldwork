# Structured Coordination State

Status: draft implementation for #302  
Parent architecture: #300

## In simple words

A single word such as `ready` cannot say whether research is finished, which exact source was reviewed, whether target tests ran, whether the upstream pin is current, whether a temporary carrier is still active, or whether anyone has merge authority.

Each retained finding may therefore carry a `state.json` sidecar. The sidecar stores independent coordination facts. The canonical `finding.md` remains the human explanation.

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

- the current explanation;
- consequence and limits;
- governing invariant;
- alternatives and precedent;
- selected direction;
- reopening trigger;
- transition framing.

`state.json` owns:

- phase;
- work class;
- exact source and carrier identity;
- claim-scoped evidence receipts;
- review disposition and reviewed head;
- freshness;
- writer lease;
- authority;
- blocker and next transition.

Issue and PR comments remain routing events. They do not become another canonical state store.

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

Phase answers where the finding is in its lifecycle. It does not state evidence strength, review outcome, or authority.

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

The exact reviewed source head and disposition-bearing record inputs must be separate fields.

### Evidence level

Each claim records one of:

- `source-read`;
- `model-executed`;
- `target-test-prepared`;
- `target-executed`;
- `integration-executed`;
- `full-gate`.

One finding may contain claims at several levels.

### Authority

Authority is explicit and never inferred from technical readiness:

- merge;
- release;
- deploy;
- upstream contact;
- private or production data;
- material spending.

A `land-ready` finding may still have every authority value set to `false`.

## Canonical source and active carrier

The canonical source identifies the product branch and exact head under consideration.

The active carrier identifies temporary evidence-producing machinery. It includes an invariant identifier and purpose. The default is one active carrier per invariant.

A carrier may be replaced only after a classified harness/workflow defect, polluted diff, materially different execution purpose, or explicit retirement. Runner queue delay is not a replacement reason.

## Writer lease

Problem-space participation remains open. Mutation of one shared artifact does not.

A writer lease records:

- worker identity;
- mutable artifact path or branch;
- lease state;
- optional transfer record.

States:

- `active`;
- `released`;
- `stale`;
- `superseded`;
- `none`.

The validator rejects more than one active lease for the same artifact across tracked state files.

## Freshness

Freshness records:

- base head;
- public or external validity boundary;
- check time.

Historical execution remains evidence after the external source moves. Current, proposal-ready, accepted, and land-ready claims may expire.

## Precedence when records disagree

1. exact immutable source and workflow facts;
2. reviewed structured state at its recorded generation;
3. canonical finding at its exact PR/head;
4. live issue/PR metadata and routing comments;
5. generated Review Queue, Delivery Desk, and cockpit projections;
6. historical narrative and chat.

A lower layer does not silently overwrite a higher layer. The consistency controller reports the conflict and exact repair path.

## Legacy migration

Legacy words are interpreted conservatively:

| Legacy text | Default migration |
| --- | --- |
| `investigating` | `phase: research-active` |
| `ready-for-synthesis` | usually `phase: review-ready`; require canonical finding and exact evidence review |
| `needs-decision` | `comparative-evaluation-active` unless a non-delegable decision is proved |
| `blocked` | keep actual phase and set `blocker`; do not use blocker as the phase |
| `complete` | inspect transition; migrate to `review-ready`, `delivery-gate-ready`, `land-ready`, `stopped`, or `closed` |
| `negative-result` | usually `phase: stopped` with retained reason and reopening trigger |
| `ready` | insufficient; derive phase from canonical records or report a migration error |

Migration never rewrites historical issue comments. It adds a current normalized state.

## Validation rules

The validator checks at least:

- required fields and allowed values;
- authority values are explicit booleans;
- unfinished phases have a next transition;
- review-ready and later active phases identify a canonical finding;
- accepted and land-ready states identify an exact reviewed head;
- land-ready review head matches the canonical source head;
- active carriers identify a canonical source and purpose;
- no more than one active carrier exists per invariant;
- no more than one active writer lease exists per artifact;
- every evidence claim has a non-empty receipt;
- stopped or closed findings retain a reopening or closeout statement in the finding;
- technical state never toggles authority implicitly.

The first validator is intentionally local and deterministic. Generated GitHub-state reconciliation belongs to #304.

## Adoption

Adopt incrementally. A finding without `state.json` remains valid but is not eligible for generated current-state projections until materialized or explicitly marked as legacy input.

Pilot examples should cover:

- active comparative evaluation;
- current source plus execution carrier;
- stopped negative result;
- review-ready evidence packet;
- land-ready owned product delivery with merge authority still false.
