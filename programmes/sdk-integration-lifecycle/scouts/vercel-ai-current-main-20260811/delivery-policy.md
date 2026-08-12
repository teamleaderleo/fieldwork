## In simple words

Current Vercel AI contribution policy explicitly values high-quality issues, reproductions, and failing tests, and asks contributors to consider issue-first before investing in a full bug-fix implementation. That fits the current Fieldwork packet: #794 and #814 both have exact target evidence and owned-fork candidates, while public contact remains a separate human decision.

If a human later chooses a pull request, every package behavior change needs a patch changeset and signed commits. The current contribution guide and pull-request template do not expose a separate AI-assistance disclosure checkbox or required field.

This record describes delivery policy only. It does not authorize any third-party interaction.

## Sources

Repository: `vercel/ai`  
Public head inspected: `05a3679dc166edfa864bba00d7fb5247f723e5df`  
Retrieved: 2026-08-11  
Upstream contact authorized: `false`

### `CONTRIBUTING.md`

Documented policy:

- AI SDK maintenance is increasingly automated.
- High-quality issues, minimal reproductions, failing tests, precise context, and focused changes are emphasized as valuable contributions.
- Before investing in a full bug-fix implementation, contributors are asked to consider opening or improving an issue first.
- Focused pull requests remain welcome.
- Any package API or behavior change requires a **patch** changeset unless maintainers request another release level.
- Commits submitted in pull requests must be signed.
- PR titles follow package-scoped forms such as `fix(package-name): description`.

### `.github/pull_request_template.md`

Current checklist includes:

- signed commits;
- tests added/updated;
- docs added/updated where applicable;
- patch changeset for relevant packages;
- author self-review.

The template also asks for background, summary, end-to-end verification where relevant, future work, and related issues/contributor credit.

No dedicated AI-assistance disclosure field was found in the current contribution guide or PR template during this pass.

## Delivery implication for current candidates

### #794 — usage normalization

The strongest human-facing packet can lead with the executed inconsistency and recorded provider payload, then show the losing reasoning-floor alternative and the selected conservative-envelope candidate if its exact gates complete.

Because the proposal changes normalized usage semantics, a patch changeset is required for any eventual PR.

### #814 — Claude permission-kind parity

The strongest human-facing packet can lead with the exact public catalog/bridge mismatch and the executed Bash/PowerShell + Read/CronList differentials, then show the shared bridge-authority/parity candidate if its build and package tests complete.

Because the proposal changes package behavior, a patch changeset is required for any eventual PR.

## Boundary

Fieldwork agents may prepare issue text, PR text, reproductions, patches, and manual steps. A human must perform any Vercel upstream issue or pull-request interaction manually outside automation.
