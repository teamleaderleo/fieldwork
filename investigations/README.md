# Investigation Workspaces

## In simple words

This directory holds durable workspaces for investigations that span several canonical findings, lanes, campaigns, source candidates, or audience-specific outputs. Each workspace has one front door, separate independently owned evidence notes, and an explicit canonical-output index.

The operating contract is [`INVESTIGATION_WORKSPACES.md`](../INVESTIGATION_WORKSPACES.md). Canonical finding state and desk routing follow [`FINDINGS.md`](../FINDINGS.md).

## Active workspaces

Target-specific workspace rows are added by their own adoption pull requests. The stable protocol branch intentionally contains no target adoption.

| Workspace | Parent issue | Purpose | Issue state | Workspace phase | Canonical findings |
| --- | --- | --- | --- | --- | --- |
| _none in the stable protocol core_ | — | — | — | — | — |

## Rules

- `README.md` is the workspace front door and coordinator-owned current map.
- Every retained investigation keeps one canonical `findings/F<issue>-<slug>/finding.md`.
- Workspace `findings/` files are subordinate evidence notes or comparisons and link their canonical finding.
- Workers write to distinct evidence-note or receipt paths.
- `canonical/README.md` declares which audience-specific outputs are candidates, accepted, disputed, superseded, retired, or held.
- Issue state, output status, workspace phase, and finding state are separate concepts.
- Use `comparative-evaluation-active` while autonomous technical comparison can still distinguish alternatives.
- Several accepted outputs are allowed when their audiences or claim boundaries differ.
- Parent issues remain the live coordination surface.
- Campaigns, lanes, batches, source branches, canonical findings, and review records remain the authority owners for their bounded claims.
- Upstream contact requires separate explicit authorization.
