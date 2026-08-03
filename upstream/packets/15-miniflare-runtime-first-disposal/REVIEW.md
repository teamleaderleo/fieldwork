# Review — Miniflare runtime-first disposal

## In simple words

The Miniflare source mechanism survives source review and the regression-test cleanup defect has been repaired. It is not yet ready for the repository owner’s decision: four broad CI shards remain unclassified, and the exact focused lifecycle test plus Miniflare type check are queued on a dedicated execution carrier.

Review date: `2026-08-03`

Current state: **EXECUTION UNDER SCRUTINY — DO NOT PRESENT FOR OWNER ADVANCEMENT YET**

Work class: **upstream-fork research**  
Canonical delivery surface: `teamleaderleo/workers-sdk#5`  
Canonical branch: `upstream/miniflare-runtime-first-disposal`

## Revision audit

- pinned base: `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`;
- exact clean head: `d668e318f5e6b0c1e2cbd66ac4b46d8cddbca642`;
- relation: one commit ahead, zero behind;
- changed files: three;
- diff size: `136` additions, `4` deletions;
- focused carrier: `teamleaderleo/workers-sdk#16`;
- focused carrier head: `0f9d818c3c9bfceb01d070d971e44e276e325055`;
- focused run: `30796108253` — queued at refresh.

## Correctness review

### Ownership invariant

Accepted at source level. `Runtime` owns the workerd child. Starting `Runtime.dispose()` before independent awaits ensures the termination request is not skipped or indefinitely delayed by browser or proxy cleanup.

### Synchronous throw and rejection observation

Accepted within scope. The invocation becomes a retained promise, and an immediate rejection observer prevents transient unhandled rejection reporting if an earlier hook exits first. Full simultaneous-error aggregation remains outside this unit.

### Completion order

Accepted. Browser and proxy cleanup retain their existing relative order. Runtime exit is still awaited before runtime and dev-registry dispatchers close.

### Browser Rendering interaction

Accepted only as source design. `closeBrowserProcess()` operates on an independently retained browser-process handle and CDP endpoint, attempts `Browser.close`, and falls back to killing and waiting for the browser process. No direct live-workerd dependency was found. Target execution is still required before presenting the candidate as proven.

### Test cleanup

Repaired at source level. The rejected-proxy test now restores the mock, always performs a second Miniflare disposal to finish the skipped owners, and waits for the identified child exit. The prior review defect no longer exists in the canonical head.

## Broad workflow classification

Passed:

- Validate PR Description;
- Semgrep;
- Local Explorer UI E2E;
- C3 E2E;
- CI Other Node Versions;
- Vite Plugin E2E;
- Wrangler E2E;
- Vite plugin playgrounds.

Changeset Review calculated a valid `miniflare` patch release, then failed in its GitHub-posting step with `Resource not accessible by integration`. This is permission noise rather than a candidate-content rejection.

Main CI run `30756281544` has four unresolved red shards:

- Ubuntu package tests 1/3 — `91518868989`;
- macOS package tests 1/3 — `91518869121`;
- Windows package tests 1/3 — `91518869093`;
- Windows fixture tests 5/6 — `91518868992`.

The connector did not return useful logs for those jobs. They remain unclassified. Green unrelated workflows do not clear them, and red job summaries do not prove the candidate is defective.

## Focused execution

Execution-only PR #16 runs the exact discriminating commands over the canonical source:

```text
pnpm install --frozen-lockfile
pnpm --filter miniflare test -- teardown-lifecycle.spec.ts
pnpm --filter miniflare check:type
```

At this review generation, run `30796108253` is queued. The carrier is not a delivery candidate and must be closed after evidence transfer.

## Current judgment

Do not ask the owner to approve advancement yet. The source case is credible, but the exact focused execution has not run and four broad red shards remain unresolved. When the focused carrier completes, repair any candidate failure directly; if it passes, classify the broad shards and then resubmit the packet for owner judgment.

## Contact boundary

Public upstream interaction authorized: `false`.  
Public upstream interaction performed: `false`.
