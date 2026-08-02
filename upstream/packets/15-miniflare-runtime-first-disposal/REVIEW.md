# Review — Miniflare runtime-first disposal

## In simple words

The Miniflare ownership repair is isolated on one clean three-file commit. Complete-diff review found and fixed a regression-test cleanup leak: the passing candidate path observed and awaited the killed workerd child but skipped a second `mf.dispose()`, leaving unrelated Miniflare teardown unfinished. The corrected test now always finishes teardown after restoring the injected proxy failure. The technical candidate is ready for the repository owner’s decision; exact-head workflows remain pending.

Review date: `2026-08-03`

Current state: **ACCEPT FOR OWNER DECISION — source repaired; exact-head execution pending**

Work class: **upstream-fork research**  
Canonical delivery surface: `teamleaderleo/workers-sdk#5`  
Canonical branch: `upstream/miniflare-runtime-first-disposal`

## Revision audit

- pinned base: `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`;
- exact clean head: `d668e318f5e6b0c1e2cbd66ac4b46d8cddbca642`;
- relation: one commit ahead, zero behind;
- changed files: three;
- diff size: `136` additions, `4` deletions;
- retired materialization run/job: `30674559186` / `91299001548`, success.

Exact candidate inventory:

```text
.changeset/fuzzy-cats-dispose.md
packages/miniflare/src/index.ts
packages/miniflare/test/teardown-lifecycle.spec.ts
```

## Evidence audit

| Claim | Evidence class | Limit |
| --- | --- | --- |
| base awaits browser and proxy cleanup before runtime disposal | `source-read` | exact pinned source ordering |
| `Runtime.dispose()` requests workerd termination before returning | `source-read` | child exit remains asynchronous |
| early rejection or pending cleanup can skip/delay later ownership work | `model-executed` | dependency-free control-flow models |
| corrected three-file candidate exists on one commit | `source-read` | exact-head execution pending |
| three real-runtime controls exist and clean up their own fixtures | `target-test-prepared` | exact-head execution pending |
| browser helper owns its process handle and CDP endpoint independently | `source-read` | target runtime interaction still not executed at clean head |

## Correctness review

### Ownership invariant

Accepted. `Runtime` owns the workerd child. Starting `Runtime.dispose()` before independent awaits ensures the termination request is not skipped or indefinitely delayed by browser or proxy cleanup.

### Synchronous throw and rejection observation

Accepted within scope. The invocation is normalized into a retained promise, and an immediate rejection observer prevents transient unhandled rejection reporting if an earlier hook exits first. Full simultaneous-error aggregation remains outside this unit.

### Completion order

Accepted. Browser and proxy cleanup retain their existing relative await order. Runtime exit is still awaited before runtime/dev-registry dispatchers close.

### Browser Rendering interaction

Accepted for source design. `closeBrowserProcess()` operates on an independently retained browser-process handle and WebSocket endpoint, attempts a CDP `Browser.close`, and falls back to killing/waiting for the browser process. No direct need for a live workerd process was found. Exact target execution remains an evidence improvement, not a known design defect.

### Repeated disposal

Accepted. `Runtime.dispose()` clears its child reference before kill/wait, and the repaired first test uses a second Miniflare disposal to finish the remaining teardown after the injected proxy failure.

## Test review

### Rejected proxy cleanup

Repaired and accepted. The prior candidate already observed `SIGKILL` and awaited the killed child, but on the successful candidate path it conditionally skipped the second `mf.dispose()`. That only completed the child owner, not the rest of Miniflare cleanup. The test now restores the proxy mock and always performs a second disposal before asserting and waiting for child exit.

### Pending proxy cleanup

Accepted. The test observes kill initiation while the proxy hook remains pending, releases the hook, and awaits complete disposal.

### Later cleanup negative control

Accepted. A `DevRegistry.dispose()` rejection occurs after runtime disposal and distinguishes the pre-runtime ordering defect from generic later cleanup failure.

## Change-fence review

- [x] one commit over exact base;
- [x] exactly three files;
- [x] no workflow, experiment, packet, or carrier machinery;
- [x] changeset names `miniflare` as a patch;
- [x] no aggregation or adjacent lifecycle implementation;
- [x] source PR synchronized to the repaired exact head;
- [x] complete current diff reviewed;
- [ ] exact-head workflows have executed.

## Exact-head workflows

Triggered for `d668e318f5e6b0c1e2cbd66ac4b46d8cddbca642`:

- CI `30756281544`;
- CI (Other Node Versions) `30756281540`;
- Changeset Review `30756281529`;
- Semgrep OSS scan `30756281508`.

No exact-head pass is claimed before execution. Queued or pending workflows do not imply a source repair remains.

## Owner decision surface

The technical source and test repair are complete. The repository owner decides whether to advance the candidate once exact-head evidence is available. Before public interaction, refresh current main and overlap, follow the target’s issue-first contribution policy, and record explicit authorization.

## Contact boundary

Public upstream contact authorized: `false`.  
Public upstream contact performed: `false`.
