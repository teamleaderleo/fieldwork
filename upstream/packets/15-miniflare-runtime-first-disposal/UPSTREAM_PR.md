# Upstream pull request draft

Status: **DRAFT — ISSUE FIRST — DO NOT OPEN PUBLICLY**

Public upstream contact authorized: `false`

## Proposed title

`[miniflare] Dispose workerd before awaiting teardown hooks`

## Proposed source

Base revision: `cloudflare/workers-sdk@95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`

Prepared fork branch:

`teamleaderleo/workers-sdk:upstream/miniflare-runtime-first-disposal`

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
- preserve the existing completion order by awaiting browser cleanup, proxy cleanup, then the retained runtime-exit promise;
- add focused lifecycle controls for rejected, pending, and later cleanup hooks;
- add a patch changeset for `miniflare`.

### Why this is narrow

`Runtime.dispose()` already clears the child reference, destroys child streams, and sends `SIGKILL` before returning its exit promise. The change moves initiation of that existing ownership action. It does not add a new kill path, public API, timeout policy, or error-aggregation contract.

### Tests

Focused controls:

- proxy cleanup rejection still requests workerd termination during the first disposal;
- pending proxy cleanup cannot delay the workerd termination request;
- a later registry-cleanup rejection confirms runtime termination already occurred.

Before opening, include exact baseline and candidate commands and links here.

```text
Baseline: PENDING
Candidate focused tests: PENDING
Miniflare type check: PENDING
Miniflare package tests: PENDING
Repository check: PENDING
```

### Compatibility

- no public API change;
- normal successful disposal still awaits browser cleanup, proxy cleanup, and runtime exit before later resources are closed;
- the workerd termination request begins earlier;
- broad simultaneous-error aggregation remains outside this pull request.

### Related work

- `#12025` made `Runtime.dispose()` close child streams and send `SIGKILL` immediately.
- `#13078` made temporary-directory cleanup best-effort after runtime shutdown.
- `#14727` bounded Browser Rendering shutdown.
- `#14903` reports a live workerd child after parallel Vitest execution; this pull request does not claim that report shares this cause.

### Checklist

- [ ] Tests included and executed.
- [ ] Patch changeset included.
- [ ] Public documentation unnecessary because this is internal teardown behavior.
- [ ] Prior issue/discussion linked.
- [ ] Exact current base refreshed before opening.

## Open-review concerns

1. Confirm browser shutdown does not require a live workerd process.
2. Confirm the retained runtime promise and attached rejection observer match repository error-reporting expectations.
3. Confirm maintainers accept preserving earlier-hook error precedence while deferring multi-error aggregation.
4. Confirm the test's `ChildProcess.kill()` spy is stable across supported platforms.

## Opening gate

Open a public pull request only after:

- explicit upstream-contact authorization;
- issue engagement or maintainer direction;
- exact clean source commit exists;
- baseline and candidate focused controls are recorded;
- ordinary checks are recorded;
- the source-only diff fence is verified;
- packet self-review moves from `HOLD`.
