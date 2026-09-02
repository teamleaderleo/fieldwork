# Review — cmux Blaxel create response-loss

Date: 2026-09-01  
Fieldwork assignment: #928  
Fieldwork PR: #930  
Reviewer: `chatgpt:gpt-5.6-sol` (self-review; not independent acceptance)  
Work class: evidence / documentation with owned-fork execution preparation  
Upstream contact authorized: `false`

## In simple words

The source finding is ready to retain: cmux can lose the identity of an execution-ambiguous Blaxel create while marking the logical row failed and immediately permitting the same idempotency key to reach provider create again.

The practical duplicate-provider-state consequence is now backed by a focused DB-backed target test, but that test is still queued for execution. The correct next transition is **EXECUTE**, not production repair and not an evidence upgrade.

## Exact reviewed inputs

- investigated upstream revision: `eaa899cb20bd411019744fbd2bdedeb397f3070b`;
- current upstream continuity point: `2ead47750ab2f47c13972d0709d99cdcbaa8ad73`;
- continuity comparison: seven commits ahead; none changes `web/services/vms/drivers/blaxel.ts`, `workflows.ts`, `repository.ts`, `providerGateway.ts`, `reaper.ts`, `vm-blaxel-fetch-retry.test.ts`, or `vm-workflows.test.ts`;
- retained report: `report.md` in this scout directory;
- prepared target regression: owned `teamleaderleo/cmux` PR #14, exact test head `6c268876c5695621ca2b4a227cd9b1fb6da5c0fb`;
- execution carrier: owned `teamleaderleo/cmux` PR #15, workflow run `33549149038`;
- execution state at review: queued with no runner assigned.

## Claim review

### Retain — source-level recovery gap

Supported as `source-read`.

The Blaxel adapter treats POST transport failure as execution-ambiguous and deliberately does not replay it. The provider machine name is generated inside one create invocation and does not become durable unless a `VMHandle` returns. The workflow maps provider-create failure to `provider_create_unavailable`; the repository makes that failure immediately same-key retryable and clears the old row's idempotency key before inserting the retry generation. User listing and normal provider-status reconciliation require a durable provider id.

Those facts are sufficient to retain the recovery gap without claiming that a live provider actually produced the response-loss interleaving during this run.

### Execute — duplicate `{A,B}` consequence

Supported as `target-test-prepared`, not `target-executed`.

PR #14 uses real `createVm`, `listUserVms`, `VmRepositoryLive`, and migrated Postgres while keeping provider state independently observable. Its ambiguous case records A in provider state and then returns a provider-operation error before any `VMHandle(A)` exists locally. It verifies the first row is failed with `provider_vm_id = NULL`, retries the same key, records B, verifies B is the only CMUX-visible machine, verifies provider state contains both A and B, and only then raises the expected RED assertion.

The negative control keeps the same retry policy but fails before recording a remote effect; the retry then produces only B. That makes ambiguous remote commit, rather than retry alone, the discriminator.

Run `33549149038` must reach those assertions before this claim can become `target-executed`. Queue admission does not count.

## Repair-boundary review

The report's repair owner remains correct, with one refinement from the current source re-read.

`cloud_vms` already has durable `provider_metadata`, so a repair does not require a separate store merely to retain create intent. The missing contract is temporal and cross-generation:

```text
persist exact provider create identity
        ↓
perform remote create
        ↓
ambiguous result? preserve identity + indeterminate ownership
        ↓
resolve/adopt/compensate exact identity
        ↓
only then permit a new provider effect
```

Current `beginCreate` clears a retryable failed row's idempotency key before inserting a successor row. Therefore storing an attempted identity only on R1 does not close the gap unless retry resolution reuses R1 or explicitly transfers/adopts that identity before the handoff.

A bounded Blaxel repair should preserve blind-POST replay protection and add exact read-after-ambiguity. A reaper-only or listing-only change would leave the create transaction unresolved.

## Adjacent scope check

E2B, Daytona, and both Freestyle create paths also receive provider-generated machine IDs only after their SDK create calls return. Current cmux does not pass a shared provider-create identity through `CreateOptions`.

This is an adjacent lead, not a promoted cross-provider defect. Provider SDK/API idempotency and response-loss semantics have not been established for those providers. Do not widen #928 or a first repair on that basis alone.

## Other cmux work checked

The nearby active recovery/identity work is complementary rather than duplicate:

- #927: persistent-generation compatibility and terminal-input ambiguity;
- #929: remote authorization publication/rotation and stale single-use deletion;
- #931: retired controller/tunnel/socket ownership after successor publication;
- #934: Cloud fork cloning machine-scoped identity.

#928 differs because the first remote effect becomes identity-less locally before the successor create begins.

A separate review of owned `teamleaderleo/cmux` PR #17 found its current-main refresh clean at the file-diff level but reversed the required regression ancestry (`base -> fix -> test`) and left stale commit identities in the PR description. A HOLD note was recorded there; its owner should rebuild `base -> test-only RED -> fix` before review promotion.

## Disposition

**EXECUTE** for #928.

Accept the source report for Fieldwork retention. Keep the practical `{A,B}` outcome at `target-test-prepared` until the exact DB-backed run executes for the intended reason. If it does, update the report/evidence class and prepare a clean current-upstream red→green Blaxel repair. If it does not, classify the failure as harness or premise evidence before changing product code.

## Upstream boundary

`manaflow-ai/cmux` remained read-only. No upstream issue, pull request, comment, review, reaction, branch, or source mutation was performed.