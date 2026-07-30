# Vite container cleanup ownership follow-up

State: `candidate-created`

Batch: `B20260730-001`

Canonical candidate: #165

Parent review hub: #88

Synthesis PR: #112

Workers SDK branch: `fieldwork/teardown-lifecycle-hardening`

Reviewed Workers SDK head: `c7dd4411bf474a09f87cd1575594e7aaa8e1cacd`

Upstream contact authorized: `false`

Upstream contact performed: `false`

## Purpose

Retain the Vite dev/preview container-cleanup findings discovered during the A001 lifecycle review as a separate candidate rather than burying them inside Miniflare teardown notes.

This note is a coordination and evidence record. The production patch remains unapplied.

## Source findings

### Cleanup ownership is installed after preparation

`prepareContainerImagesForDev()` processes configured images sequentially. A later build, pull, duplicate-tag cleanup, exposed-port check, or egress-image pull can reject after earlier image work completed.

The Vite dev and preview plugins currently install the current session's `containerImageTags` cleanup ownership only after the whole preparation call resolves. A rejection therefore leaves the caller without a current-session tag set in its close/exit cleanup path.

This proves late ownership registration. It does not prove a running container exists on every preparation failure path.

### One same-mode server can replace another exit owner

Both Vite plugin modules use one module-global `exitCallback` slot. Every plugin instance that completes container preparation replaces that callback.

The package's exported `cloudflare()` function creates a new `PluginContext` and plugin array on every call. Multiple plugin instances are therefore representable in one Node.js process.

For two dev servers, or two preview servers, the most recently prepared same-mode instance replaces the earlier instance's force-exit callback. On process exit, the earlier callback is no longer reachable through the listener.

Ordinary CLI use commonly creates one server, so real-world incidence is unknown. Programmatic Vite use, tests, orchestrators, and multiple server instances are the primary integration surfaces.

### Failed dev restart cleanup can lose old tags

The dev plugin invokes `cleanupContainers()` during restart but ignores the boolean result. After the next successful preparation, it replaces `containerImageTags` with the new tag set.

When restart cleanup fails, this replacement can discard the only retry record for the old tags. The current patch candidate preserves old tags and unions them with newly prepared tags until cleanup eventually succeeds.

### Preview close lacks container cleanup

The preview plugin closes Miniflare and the Vite preview server programmatically but currently relies on process exit for container cleanup. A prerendering or programmatic-close flow can therefore leave cleanup deferred until the host process exits.

## Executed models

### Early registration and retry ownership

`container-build-cleanup.mjs` passed:

- ownership registration before asynchronous preparation;
- cleanup after preparation failure while preserving the original error;
- clearing tags after successful cleanup;
- warning and retaining tags after failed cleanup so close/exit can retry.

### Per-instance exit and restart registry

Executed:

```sh
node /tmp/vite-exit-cleanup-registry.mjs
```

The executed content is identical to the committed Workers SDK artifact:

`fieldwork-experiments/teardown-lifecycle-hardening/vite-exit-cleanup-registry.mjs`

Output:

```text
PASS: a single exit slot loses earlier cleanup ownership
PASS: a per-instance registry cleans every live server owner
PASS: failed cleanup retains ownership for an exit retry
PASS: successful close unregisters and avoids duplicate cleanup
PASS: preparation failure preserves its original error
PASS: failed restart cleanup retains old tags alongside new tags
```

Evidence class: `model-executed` plus `source-read`.

No package or plugin test executed.

## Draft repair artifacts

Workers SDK branch artifacts:

- `container-build-cleanup.mjs`
- `container-build-cleanup.patch`
- `preview-container-close.patch`
- `vite-exit-cleanup-registry.mjs`
- `vite-exit-cleanup-registry.patch`
- `adjacent-lifecycle-review.md`

`vite-exit-cleanup-registry.patch` is the current implementation candidate. It supersedes the narrower patches for review by combining:

- a per-instance callback registry instead of one module-global slot;
- tag ownership before asynchronous image preparation;
- retained old tags unioned with new tags after failed restart cleanup;
- preparation-failure cleanup with exact primary-error preservation;
- preview programmatic-close cleanup;
- warnings and retained retry ownership when cleanup returns `false`;
- unregistering only after successful final cleanup;
- continued registration across dev restarts.

The patch is not applied to production source.

## Required package/plugin evidence

1. Two dev plugin/server instances with distinct tags both receive force-exit cleanup.
2. Two preview plugin/server instances with distinct tags both receive force-exit cleanup.
3. Successful close unregisters one owner without disturbing another.
4. Failed cleanup remains registered and succeeds during a later exit retry.
5. A later preparation failure triggers cleanup and preserves the exact preparation error.
6. Programmatic preview close cleans containers while the host process continues.
7. Dev restart cleanup failure retains old tags; later preparation adds new tags; a later retry cleans both.
8. Cleanup failure produces a useful warning without replacing the primary error.

Intended test area:

- `packages/vite-plugin-cloudflare/src/__tests__/`
- mocked `prepareContainerImagesForDev()` and `cleanupContainers()`;
- package command determined after matching existing Vitest conventions.

## Coordination placement

- Candidate issue #165 is the canonical review/disposition surface for this finding.
- Batch issue #88 remains the parent Workers SDK review hub.
- PR #112 remains the batch synthesis snapshot.
- Meta issue #87 owns the generated coordination-board convention.

The established filtering convention is sufficient; no new ad hoc label is needed:

- `state:ready`
- `type:lane`
- `parallel-safe`
- `target:workers-sdk`
- `programme:sdk-integration-lifecycle`

The future generated board should discover #165 from those labels and report its exact head, evidence class, canonical parent, and package-execution blocker.

## Boundary

This candidate is separate from the first Miniflare runtime-first patch. It should not enlarge that implementation slice.

No live Docker/container reproduction was performed. No upstream issue, pull request, comment, review, reaction, or message was created.
