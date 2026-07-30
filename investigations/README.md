# Investigation Workspaces

## In simple words

This directory holds durable workspaces for investigations that span several findings, lanes, campaigns, source candidates, or final outputs. Each workspace has one front door, separate independently owned finding files, and an explicit canonical-output index.

The operating contract is [`INVESTIGATION_WORKSPACES.md`](../INVESTIGATION_WORKSPACES.md).

## Active workspaces

| Workspace | Parent issue | Purpose | Current state |
| --- | --- | --- | --- |
| [`239-codex-upstream-convergence/`](239-codex-upstream-convergence/) | [#239](https://github.com/teamleaderleo/fieldwork/issues/239) | Reconcile Codex upstream drift, overlapping lifecycle findings, source candidates, execution receipts, prior art, and proposal outputs | active |

## Rules

- `README.md` is the workspace front door and coordinator-owned current map.
- Workers write to distinct finding or evidence files.
- `canonical/README.md` declares which outputs are candidates, accepted, disputed, superseded, or retired.
- Several accepted outputs are allowed when their audiences or claim boundaries differ.
- Parent issues remain the live coordination surface.
- Campaigns, lanes, batches, source branches, and review records remain the authority owners for their bounded claims.
- Upstream contact requires separate explicit authorization.