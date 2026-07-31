# Workstream H exact handoff

Workspace phase: `handoff`  
Canonical finding states: cache `closed`; output-root safety `closed`; tarfilter compatibility `closed`; package variance `stopped`; ecosystem overlap `stopped`  
Research continuity: adjacent avenues retained in `research-avenues.md`; `closed` and `stopped` do not erase nearby questions  
Upstream contact authorized: no

## Source and branch heads

- Fieldwork protocol base: PR #283, branch `integration/canonical-findings-workspaces-2026-07-31`, head `23ef5d6e1d955eb7a8984a0491dc99a5e08a1d81`.
- Fieldwork finding branch: `docs/h-linux-storage-findings-20260731`; live head belongs in PR metadata because this file's own commit advances it.
- Linux Fieldwork observed main before closeout repair: `63e7bbff2d2dc6da4078f9f72d02cd4330b1a09a`.
- Linux closeout-record repair: PR #249, branch `repair/h-durable-record-state-20260731`, head `fed2b03cb3a584f0e3f2f2db5c58e6a2f0102023`, merged as `d7aebcf38459fd3f4791c1ce5da1ec446d6d3296`.

## Canonical implementation receipts

| Unit | Exact source head | Workflow | Outcome | Merge |
| --- | --- | --- | --- | --- |
| cache composition | `5e69cd25e62d0e86364459d97c9df8568ff84187` | Linux Fieldwork CI `30580697438` / 612 | success | `8d9f7fa92f0cb2f553ca3578b78d7e04f4e4167f` |
| LF-23 output-root guard | `6251a11fd30b26d29451e5ee292a6186344429a1` | Linux Fieldwork CI `30580869813` / 620 | success | `12dd20f6965d11024afc6cbbcb2f039d53e4beef` |
| tarfilter regex translator | `4555c5c250c1afedb3947fd1a7b5a0323bd9d262` | Linux Fieldwork CI `30579057679` / 577 | success | `1a1952a78f79b2473f1f9513c1d5820f58987594` |
| tarfilter group controls | `bb0a79dec47958c6b865d4b382a44baff17ab736` | Linux Fieldwork CI `30582215292` / 634 | success | `ed49c01a85e9d363626db5d2973a33b67209e13b` |
| package variance corpus | `7c67db4942ff9f5863a20af42c443f456783ddf5` | Linux CI `30543908605` / 293; LF-12 `30543908611` / 6 | success; success | `c730b8ef2e90e07ad18b5835b225a8b41e22420a` |
| ecosystem overlap record | `d9c09cb81c1258612dda601b5bf5f6b703833b8a` | Linux Fieldwork CI `30581903516` / 629 | success | `d256fd697457eac29862e1073d974813a488725c` |
| durable closeout record repair | `fed2b03cb3a584f0e3f2f2db5c58e6a2f0102023` | Linux Fieldwork CI `30592017920` / 720 | success | `d7aebcf38459fd3f4791c1ce5da1ec446d6d3296` |

## Current execution

- Linux Fieldwork PR #249 completed CI run `30592017920` / 720 successfully and merged without head movement.
- Fieldwork protocol PR #283 completed integrity run `30591290799` / 1230 successfully at `23ef5d6e1d955eb7a8984a0491dc99a5e08a1d81`.
- Fieldwork finding PR #308 pre-synchronization head `81a38cd7cdfcac3448b61579a38ecc5fa6ad9a92` completed integrity run `30595659828` / 1282 successfully. The current metadata-only synchronization advances that head, so PR metadata must retain the replacement exact-head receipt before review-ready promotion.

## Review and disposition

- Cache, LF-23, and tarfilter product/proof work are locally merged and technically closed only within their bounded claims.
- The package-variance defect premise is rejected for the retained fixture; the negative result is stopped and reusable, while broader package/toolchain questions remain in the avenues ledger.
- The PPMd implementation is stopped because an equivalent active public fix existed at the exact 2026-07-31 refresh boundary; release adoption, downstream retirement, and semantic divergence remain retained avenues.
- `research-avenues.md` records concrete adjacent questions, why they may matter, existing evidence, smallest safe probes, and reopening triggers across cache races/durability, destructive-path capabilities, archive language/metadata, broader reproducibility, public-state expiry, and evidence automation.
- A skipped job, missing privilege, unavailable environment, safety restriction, policy boundary, or prohibited public interaction must be preserved as a blocker or evidence limit, not converted into a technical negative result.
- Linux PR #249 is merged documentation evidence. It changes no product source and no product execution claim depends on it.
- This Fieldwork stack adds one workspace, one handoff, five canonical findings, and one research-avenues ledger on top of PR #283. It requires replacement exact-head Fieldwork integrity after this synchronization plus eligible independent complete-diff review.

## Blockers and smallest next actions

1. Read the replacement exact-head Fieldwork integrity run for the synchronized PR #308 head. Classify any failure before editing.
2. Confirm protocol PR #283 remains at `23ef5d6e1d955eb7a8984a0491dc99a5e08a1d81`. Reconcile against current inputs if it moves; rebase only for overlapping or materially governing movement or a current-base promotion package.
3. Review the complete eight-file Markdown diff, including continuity semantics and every exact Linux receipt.
4. Route the unchanged green head to an eligible independent reviewer through Review Queue #213 or the owning issue.
5. During future exploration, append any new avenue before stopping: question, consequence, source/environment boundary, evidence, blocker, smallest safe probe, reopening trigger, and authority state.
6. Do not merge either pull request without explicit authority.

## Expiry conditions

- Any head movement expires exact-head review for the moved branch.
- Public overlap state for libarchive expires immediately when the public head or status changes.
- A new source candidate, implementation, or broader claim must update the relevant finding before promotion.
- A skipped workflow is not product evidence; the LF-23 cancellation probe remained skipped on the harness-safety composition head.
- An interruption does not expire a retained avenue if the blocker and continuation point are recorded precisely.
- File-disjoint parent movement may use an explicit semantic-identity proof, but an old receipt remains historical until affected review identities are renewed.

## Public interaction

Only read-only public source and pull-request state were inspected. No issue, pull request, comment, review, reaction, message, patch submission, release, deployment, or other public upstream interaction occurred.
