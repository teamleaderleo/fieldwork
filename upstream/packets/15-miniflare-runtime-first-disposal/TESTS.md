# Tests — Miniflare runtime-first disposal

## In simple words

The repaired candidate has three real-runtime lifecycle controls, but the evidence is not yet clean enough for an owner decision. Most broad workflows passed, the Changeset Review failure is permission-only, four main-CI shards remain unclassified, and a dedicated focused test/typecheck carrier is queued.

Current test state: **FOCUSED EXECUTION QUEUED — BROAD RED SHARDS UNCLASSIFIED**

## Exact candidate target

Base: `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`  
Canonical branch: `teamleaderleo/workers-sdk:upstream/miniflare-runtime-first-disposal`  
Canonical source head: `d668e318f5e6b0c1e2cbd66ac4b46d8cddbca642`  
Canonical source PR: `teamleaderleo/workers-sdk#5`

Focused carrier PR: `teamleaderleo/workers-sdk#16`  
Focused carrier head: `0f9d818c3c9bfceb01d070d971e44e276e325055`  
Focused workflow: `30796108253`

## Exact source fence

- one commit ahead;
- zero commits behind;
- exactly three changed files;
- `136` additions and `4` deletions.

```text
.changeset/fuzzy-cats-dispose.md
packages/miniflare/src/index.ts
packages/miniflare/test/teardown-lifecycle.spec.ts
```

## Target-native controls

### Control 1 — rejected proxy cleanup

The first disposal receives an injected proxy rejection. The test records whether workerd `SIGKILL` was requested, restores the mock, always calls `mf.dispose()` again to finish the skipped Miniflare owners, and waits for the identified child exit.

Property: a rejected independent cleanup hook cannot skip runtime termination, and the test does not leak the rest of Miniflare teardown.

### Control 2 — pending proxy cleanup

The test holds proxy disposal pending, verifies workerd termination was requested before releasing the hook, releases it, and awaits complete disposal.

Property: a pending independent cleanup hook cannot delay initiation of runtime termination.

### Control 3 — later cleanup rejection

The test injects a later `DevRegistry.dispose()` rejection and confirms workerd termination already occurred.

Property: the observer distinguishes the pre-runtime ordering defect from generic later cleanup failure.

## Browser Rendering source control

`closeBrowserProcess()` receives an independent browser-process handle and CDP WebSocket endpoint. It attempts `Browser.close`; if graceful close fails or times out, it kills and waits for the browser process. No direct workerd dependency was found in that helper. This is source evidence, not target execution.

## Broad exact-head results

Canonical source head: `d668e318f5e6b0c1e2cbd66ac4b46d8cddbca642`

Passed:

- Validate PR Description `30756281511`;
- Semgrep `30756281508`;
- Local Explorer UI E2E `30756281551`;
- C3 E2E `30756281558`;
- CI Other Node Versions `30756281540`;
- Vite Plugin E2E `30756281594`;
- Wrangler E2E `30756281560`;
- Vite plugin playgrounds `30756281534`.

Changeset Review `30756281529` calculated the expected `miniflare` patch release. Its post step failed with `Resource not accessible by integration` while attempting to publish a review. Classification: GitHub permission/integration failure, not candidate content.

Main CI `30756281544` failed in four shards:

- Ubuntu package tests 1/3 — job `91518868989`;
- macOS package tests 1/3 — job `91518869121`;
- Windows package tests 1/3 — job `91518869093`;
- Windows fixture tests 5/6 — job `91518868992`.

The available connector did not expose useful failure logs for those jobs. They remain unclassified and cannot be represented as either candidate failures or unrelated noise.

## Focused exact-source carrier

Execution-only carrier #16 runs:

```text
pnpm install --frozen-lockfile
pnpm --filter miniflare test -- teardown-lifecycle.spec.ts
pnpm --filter miniflare check:type
```

The carrier contains the canonical three-file candidate plus one temporary workflow. At this refresh, focused run `30796108253` is queued. No focused pass is claimed.

## Acceptance rule

Advance the unit to an owner decision only when:

- the focused lifecycle controls and Miniflare type check execute at the exact canonical source;
- any focused failure is repaired rather than relabeled;
- the four broad red shards are classified enough to establish whether they touch the candidate;
- packet and source identities are synchronized afterward.
