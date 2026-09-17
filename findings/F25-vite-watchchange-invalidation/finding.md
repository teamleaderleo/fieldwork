# F25: Continue Vite invalidation after `watchChange` errors

Finding state: `delivery-gate-ready`

Workstream: `B — Browser, web tooling, and runtime boundaries`  
Canonical Fieldwork issue: `#25`  
Canonical implementation: `teamleaderleo/vite#4`  
Exact implementation head: `8b5d1ae237bf61031a7436ed8fb0fc1e436b6d78`  
Exact base revision: `8a245726944ed29225920d49be77c33c6e03afc8`  
Strongest evidence class: `target-executed` focused gate  
Current review disposition: `ACCEPT source direction; EXECUTE ordinary exact-head repository gates`  
Desk routing: `Review Queue #213 and Delivery Desk #160 D1`  
Upstream contact authorized: `no`

## In simple words

When Vite sees a file change, it first tells plugins through `watchChange`, then clears its own cached modules and runs hot-update logic.

A plugin error currently stops the whole file-change transaction. Vite logs the error, yet its own cache can stay stale. The candidate waits for every environment's plugin notification, logs each failure, and then continues into Vite-owned invalidation and HMR.

## Why we care

A real file change can be observed by the watcher while the next transform still returns old code. That is a correctness failure: developers see stale output even after editing the backing file.

Plugin failure should remain visible. It should not prevent the host from performing its own cache invalidation and update bookkeeping.

## What happens if we leave it alone

Any rejecting `watchChange` hook can abort the listener before module graph invalidation. A virtual module backed by the changed file can continue serving its previous transform result. The plugin error reaches the logger, which makes the transaction appear handled even though Vite-owned state remains stale.

The focused reproduction covers `change`. The candidate helper also handles `add` and `unlink`, but separate correctness controls for those event types remain desirable.

## Current finding

Vite should settle all environment-level `watchChange` notifications, log every rejection through the configured logger, and continue into the existing invalidation and HMR path. The change should remain at the server file-event boundary and avoid changing generic plugin-hook scheduling.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| A rejected `watchChange` hook can leave a virtual module's transform cache stale. | `target-executed` | Vite PR #1 reproduction | Focused `change` event |
| The candidate logs the original error and reaches invalidation and `hotUpdate`. | `target-executed` | Vite PR #4 focused regression | Final head lacks ordinary repository CI receipt |
| Shared helper source covers `change`, `add`, and `unlink`. | `source-read` | `packages/vite/src/node/server/index.ts` diff | Separate behavioral controls exist only for `change` |
| Generic hook ordering remains unchanged. | `source-read` | Candidate changes listener orchestration only | Does not prove compatibility across every plugin environment |

## System and ownership map

- The filesystem watcher emits `change`, `add`, or `unlink`.
- The server calls each environment's plugin container `watchChange` hook.
- Vite then owns public-file bookkeeping, module graph invalidation, and HMR propagation.
- A rejection from the first phase currently prevents the second phase.
- The candidate introduces `notifyWatchChange()` at the server boundary and uses `Promise.allSettled()` to preserve every rejection while continuing the transaction.

## Historical precedent

### Isolate watcher-listener promise failures

- Source: https://github.com/vitejs/vite/pull/22188
- Revision or date: merged April 2026 according to the retained investigation
- Principle supported: rejected `watchChange` hooks should be caught and logged for watcher events.
- Important difference: that change prevents dropped or unhandled listener promises. It still allows the plugin rejection to abort Vite-owned invalidation before the outer catch logs it. This finding handles the transactional continuation gap.

## Approaches considered

### Retained approach: settle environment notifications at the server boundary

This preserves plugin error reporting and keeps Vite-owned invalidation reliable. It also provides one shared path for all three filesystem event types.

### Declined: swallow the plugin error

The configured logger must still receive each rejection. Silent failure would hide plugin defects and complicate diagnosis.

### Declined: change `hookParallel` globally

The demonstrated defect belongs to one host transaction. Changing generic plugin scheduling could alter unrelated hooks and error semantics.

### Deferred: isolate failures within each individual plugin hook

Per-plugin continuation may be useful, but it changes the plugin-container contract and needs separate ordering and multiple-error analysis. The current candidate isolates environments and preserves existing container behavior.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Rejecting `watchChange` on a real file change | PR #4 regression | Error logged; invalidation and HMR continue |
| Virtual module cached before change | PR #4 regression | Cached `alpha` becomes `beta` after refresh |
| `hotUpdate` hook reachability | PR #4 regression | Hook reached after rejection |
| Original error identity | PR #4 regression | Exact error object reaches configured logger |
| No generic hook-order change | Complete diff | Existing plugin container untouched |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Add-event correctness after rejection | Source path shared but no dedicated state assertion | Add focused regression before land-ready |
| Unlink-event correctness after rejection | Source path shared but no dedicated state assertion | Add focused regression before land-ready |
| Multiple environments rejecting with ordering-sensitive logs | `allSettled` records all, ordering expectations untested | Compatibility test if logger order is contractually important |
| A hanging `watchChange` hook | Candidate awaits all notifications | Separate timeout/cancellation design finding |
| Bundled-development file-event semantics | Different engine and plugin support limits | Separate bundled-dev finding |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `teamleaderleo/vite@8b5d1ae237bf61031a7436ed8fb0fc1e436b6d78` | Branch workflow: install, format, build, focused Vitest regression, ESLint | Ubuntu, Node 24 | Passed before workflow self-removal | `target-executed` |
| Same head | Ordinary PR workflows | GitHub Actions | `action_required`; no ordinary exact-head execution receipt | none |

## Complete-diff and compatibility review

Changed-file fence:

- `packages/vite/src/node/server/index.ts`
- `packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js`

Complete-diff review found no source blocker. The target head still needs the ordinary repository CI matrix and Zizmor or equivalent current workflow gate. Separate add/unlink assertions would strengthen the shared helper claim.

## Current disposition and desk routing

- Finding state: `delivery-gate-ready`
- Review disposition: `ACCEPT source direction; EXECUTE ordinary exact-head gates`
- Review Queue entry: #213
- Delivery lane: `D1`
- Exact next transition: run ordinary Vite CI and workflow analysis at `8b5d1ae...`
- Clearing condition: green exact-head repository gate plus explicit add/unlink coverage decision
- User decision requested: none unless the team chooses to require dedicated add/unlink controls before the ordinary gate

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-29 | Vite PR #1 | Confirmed stale-cache mechanism after rejected `watchChange` |
| 2026-07-29 | Vite PR #4 | Added shared settled-notification helper and focused regression |
| 2026-07-30 | Exact-head review | Source accepted; evidence classified below full repository gate |

## References

- https://github.com/teamleaderleo/fieldwork/issues/25
- https://github.com/teamleaderleo/vite/pull/1
- https://github.com/teamleaderleo/vite/pull/4
- https://github.com/vitejs/vite/pull/22188
- Exact head `8b5d1ae237bf61031a7436ed8fb0fc1e436b6d78`
