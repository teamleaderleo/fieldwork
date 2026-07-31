# Generated Coordination Views

Status: draft implementation for #303  
Parent architecture: #300  
Structured input: #302 / PR #306

## In simple words

Issues, pull requests, branches, workflow receipts, reviews, and canonical findings are the detailed event stream. A person should normally read a compact projection of that state instead of reconstructing it manually.

`render_coordination_views.py` reads validated `findings/**/state.json` records and generates deterministic Markdown views. It never accepts work, upgrades evidence, grants authority, merges, or contacts upstream.

## Views

- `CURRENT.md` — phone-sized cockpit: priorities, changes, blockers, human authority, risks, and next autonomous actions;
- `NOW.md` — material field changes from an optional previous snapshot;
- `DECISIONS.md` — `design-decision-ready` work and `land-ready` merge authority questions;
- `RUNNING.md` — active execution carriers and their exact canonical source;
- `REVIEW.md` — review-ready items, dispositions, exact reviewed heads, and evidence levels;
- `LANDING.md` — design, delivery-gate, and land-ready transitions;
- `RISKS.md` — repair/hold states, missing freshness, blockers, and suspicious source/carrier combinations;
- `ARCHIVE.md` — stopped and closed findings with terminal records;
- `state-snapshot.json` — normalized fields used to calculate a later `NOW` view.

## Current limits

The first version uses tracked state only. It does not query live GitHub workflow status, labels, comments, or branch heads. Live reconciliation belongs to #304.

Therefore:

- an active carrier appears in `RUNNING`, but queued versus executing status requires later enrichment;
- a tracked exact head remains only as current as its `freshness` record;
- validation conflicts stop generation rather than being silently repaired;
- a generated view is a read model, not a source of authority.

## Command

```bash
python3 scripts/render_coordination_views.py \
  --output-dir generated/coordination \
  --previous-snapshot path/to/previous-state-snapshot.json
```

Omit `--previous-snapshot` for an initial projection.

## Material change fields

`NOW.md` compares:

- phase;
- priority;
- review disposition and exact reviewed head;
- canonical source head;
- active carrier head and purpose;
- blocker;
- next transition;
- authority;
- terminal record.

Text-only changes outside those fields do not create global change noise.

## Human-facing contract

The default cockpit answers:

```text
Priority
Changed
Why it matters
Waiting or blocked
Needs human authority
Risk
Next autonomous action
```

Every line links to or names the canonical finding. Detailed reasoning remains in `finding.md` and evidence files.

## Future enrichment

#304 may add controllers that compare tracked state with:

- live GitHub heads and workflow runs;
- issue body and label generations;
- PR descriptions and complete diffs;
- Review Queue and Delivery Desk projections;
- duplicate carrier and stale writer-lease facts;
- exact external-source surveillance boundaries.

That enrichment must preserve the read-only authority boundary.
