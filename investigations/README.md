# Investigation Workspaces

## In simple words

This directory holds durable workspaces for investigations that span several canonical findings, lanes, campaigns, source candidates, competing approaches, or outward-facing outputs. Each workspace has one front door, separate independently owned evidence notes, and an explicit canonical-output index.

The workspace operating contract is [`INVESTIGATION_WORKSPACES.md`](../INVESTIGATION_WORKSPACES.md). Canonical finding state and desk routing follow [`FINDINGS.md`](../FINDINGS.md). Technical alternatives and provisional selection follow [`DECISIONS.md`](../DECISIONS.md).

## Active workspaces

| Workspace | Parent issue | Purpose | Workspace phase | Current transition state |
| --- | --- | --- | --- | --- |
| [`239-codex-upstream-convergence/`](239-codex-upstream-convergence/) | [#239](https://github.com/teamleaderleo/fieldwork/issues/239) | Reconcile Codex upstream drift, overlapping lifecycle findings, source candidates, execution receipts, prior art, and proposal outputs | synthesize | research-active |

## Rules

- `README.md` is the workspace front door and coordinator-owned current map.
- Every retained investigation keeps one canonical `findings/F<issue>-<slug>/finding.md`.
- Workspace `findings/` files are subordinate evidence notes or comparisons and link their canonical finding.
- Workers write to distinct evidence-note, alternative, or receipt paths.
- Plausible technical alternatives remain `comparative-evaluation-active` while source research, prototypes, discriminating execution, or adversarial review can distinguish them.
- `design-decision-ready` is reserved for a genuine authority, private-context, material-cost, product-value, or irreversible-risk question under `DECISIONS.md`.
- `canonical/README.md` declares which outward-facing outputs are candidates, accepted, disputed, superseded, or retired.
- Output status, workspace phase, and finding transition state are separate concepts.
- Several accepted outputs are allowed when their audiences or claim boundaries differ.
- Parent issues remain the live coordination surface.
- Campaigns, lanes, batches, source branches, canonical findings, and review records remain the authority owners for their bounded claims.
- Upstream contact requires separate explicit authorization.
