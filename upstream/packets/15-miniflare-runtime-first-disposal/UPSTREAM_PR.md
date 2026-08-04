# Upstream pull request draft

## In simple words

The source candidate is one clean three-file commit with the test-cleanup defect repaired. This draft remains private because Workers SDK guidance favors issue engagement for a non-trivial change and public contact has not been authorized. The repository owner decides whether to advance it after exact-head execution is available.

Status: **READY FOR OWNER DECISION — ISSUE FIRST — DO NOT OPEN PUBLICLY**

Public upstream contact authorized: `false`

## Proposed title

`[miniflare] Dispose workerd before awaiting teardown hooks`

## Proposed source

- base revision: `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`;
- prepared fork branch: `teamleaderleo/workers-sdk:upstream/miniflare-runtime-first-disposal`;
- exact source head: `d668e318f5e6b0c1e2cbd66ac4b46d8cddbca642`;
- relation: one commit ahead, zero behind.

Expected diff:

```text
.changeset/fuzzy-cats-dispose.md
packages/miniflare/src/index.ts
packages/miniflare/test/teardown-lifecycle.spec.ts
```

## Proposed body

### Summary

Start `Runtime.dispose()` before awaiting independent Miniflare teardown hooks so workerd termination is requested even when browser or proxy cleanup rejects or remains pending.

### Current behavior

`Miniflare.dispose()` awaits browser cleanup and proxy-client disposal before calling `Runtime.dispose()`. A rejected or unresolved earlier hook can prevent the owned workerd child from receiving its termination request.

### Change

- invoke `Runtime.dispose()` before awaiting browser and proxy cleanup;
- retain the runtime-exit promise;
- observe its rejection immediately to avoid transient unhandled rejection reporting;
- preserve completion order by awaiting browser cleanup, proxy cleanup, then runtime exit;
- add focused lifecycle controls for rejected, pending, and later cleanup hooks;
- ensure the rejected-proxy control always completes the remaining Miniflare teardown after restoring its mock;
- add a patch changeset for `miniflare`.

### Why this is narrow

`Runtime.dispose()` already clears the child reference, destroys child streams, and sends `SIGKILL` before returning its exit promise. The change moves initiation of that existing ownership action. It does not add a new kill path, public API, timeout policy, or error-aggregation contract.

Browser cleanup uses its own browser-process handle and CDP WebSocket endpoint. No direct dependency on a live workerd process was found in the cleanup helper.

### Tests

Focused controls:

- proxy cleanup rejection still requests workerd termination during the first disposal, then a second disposal completes remaining cleanup;
- pending proxy cleanup cannot delay the workerd termination request;
- a later registry-cleanup rejection confirms runtime termination already occurred.

Exact-head workflows triggered:

```text
CI: 30756281544 — pending
CI (Other Node Versions): 30756281540 — pending
Changeset Review: 30756281529 — pending
Semgrep OSS scan: 30756281508 — pending
```

No exact-head pass is claimed before execution.

### Compatibility

- no public API change;
- normal successful disposal still awaits browser cleanup, proxy cleanup, and runtime exit before later resources close;
- workerd termination initiation begins earlier;
- genuine browser cleanup remains independently owned;
- broad simultaneous-error aggregation remains outside this pull request.

### Checklist

- [x] Focused tests included.
- [x] Rejected-proxy test completes remaining cleanup.
- [x] Patch changeset included.
- [x] One-commit three-file source fence verified.
- [x] Browser helper source interaction reviewed.
- [ ] Exact-head focused and ordinary results recorded.
- [ ] Prior issue/discussion linked after authorization.
- [ ] Exact current base refreshed before opening.
- [ ] Repository owner approves advancement.
- [ ] Public-contact authorization recorded.

## Opening gate

Open a public pull request only after explicit owner authorization, issue engagement or maintainer direction, exact-head execution classification, current-main and overlap refresh, and confirmation that the clean source fence remains unchanged.
