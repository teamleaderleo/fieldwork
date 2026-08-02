# Tests — Miniflare runtime-first disposal

## In simple words

The clean candidate contains three real-runtime lifecycle controls. Review repaired the rejected-proxy control so it always completes the remaining Miniflare teardown after the injected failure, rather than only awaiting the killed workerd child. Exact-head repository workflows were triggered for the repaired one-commit source and are pending.

Current test state: **SOURCE AND TEST REPAIRED — EXACT-HEAD EXECUTION PENDING**

## Exact candidate target

Base: `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`  
Canonical branch: `teamleaderleo/workers-sdk:upstream/miniflare-runtime-first-disposal`  
Canonical source head: `d668e318f5e6b0c1e2cbd66ac4b46d8cddbca642`  
Canonical source PR: `teamleaderleo/workers-sdk#5`

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

Setup:

- construct and ready a real Miniflare instance;
- inject one rejection from `ProxyClient.prototype.dispose()`;
- observe `ChildProcess.prototype.kill()` for a workerd child;
- call `mf.dispose()` and retain the injected rejection.

Candidate assertion:

- the first disposal requested workerd `SIGKILL`;
- after restoring the proxy mock, the test always calls `mf.dispose()` again to complete the remaining cleanup;
- the killed child is identified and its exit is awaited.

Review correction:

The previous test only called the second disposal when no killed child was found. On the passing candidate path, it therefore awaited child exit but left later Miniflare cleanup unfinished. The repaired test makes the second disposal unconditional after mock restoration.

Property: a rejected independent cleanup hook cannot skip the runtime termination request, and the test itself does not leak the remainder of the teardown lifecycle.

### Control 2 — pending proxy cleanup

The test keeps proxy disposal pending, verifies workerd termination was requested before releasing the hook, then releases it and awaits complete disposal.

Property: a pending independent cleanup hook cannot delay initiation of runtime termination.

### Control 3 — later cleanup rejection

The test injects a `DevRegistry.dispose()` rejection and confirms the workerd kill request already occurred, then restores the mock and performs best-effort repeated disposal.

Property: the observer distinguishes the pre-runtime ordering defect from a generic later cleanup failure.

## Browser Rendering source control

`closeBrowserProcess()` receives an independent browser-process handle and CDP WebSocket endpoint. It attempts `Browser.close`; if graceful close fails or times out, it kills and waits for the browser process. No direct workerd dependency is present in that helper. This narrows the interaction risk, while exact target execution remains desirable.

## Historical evidence

- materialization run/job `30674559186` / `91299001548` succeeded and established the original clean branch; it did not execute the target assertion;
- A001 dependency-free Node models established the sequential rejection, pending-hook, and later-failure control-flow behavior;
- prior source heads and carriers are historical after the test-cleanup repair and one-commit resquash.

## Exact-head workflows

Canonical source head: `d668e318f5e6b0c1e2cbd66ac4b46d8cddbca642`

| Workflow | Run | State at refresh |
| --- | ---: | --- |
| CI | `30756281544` | pending |
| CI (Other Node Versions) | `30756281540` | pending |
| Changeset Review | `30756281529` | pending |
| Semgrep OSS scan | `30756281508` | pending |

Other repository integration workflows were triggered or skipped according to path filters. Each completed result must be classified by whether it built or executed the Miniflare source and focused file. No pass is claimed yet.

## Exact commands to retain when execution is available

```text
pnpm install --frozen-lockfile
pnpm --filter miniflare test -- teardown-lifecycle.spec.ts
pnpm --filter miniflare check:type
```

Record exact source head, runner environment, assertion count, run/job, and result. Classify installation, setup, fixture, timeout, and unrelated-package failures separately.

## Current judgment

The implementation and test-cleanup defects are repaired. Pending exact-head execution is an evidence boundary. The packet is ready for the repository owner’s decision rather than another repair label.
