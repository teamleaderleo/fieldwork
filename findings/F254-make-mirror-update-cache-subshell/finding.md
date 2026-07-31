# F254-make-mirror-update-cache-subshell: a subshell must not cancel its parent-owned proxy and continue

Finding state: `delivery-gate-ready`

Workstream: `G`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-make-mirror-update-cache-subshell/finding.md`  
Canonical implementation: `teamleaderleo/linux-fieldwork#267`  
Exact implementation head: `c066db4046626cbed0b1c186cb52b9dffa72554a`  
Exact base or source revision: Linux Fieldwork main `da52cbfdabe84744017d1a5286314620d4d3286e`; imported `make_mirror.sh` blob `6c4be092edcf23b56b63a3befe238c099c45f590`  
Strongest evidence class: lifecycle claims `model-executed`; current imported-source gate `target-test-prepared`  
Reviewed input generation: current Fieldwork/Linux protocols; Linux #231; merged #224; historical #238/#259; PR #267 review `4824709149`  
Current review disposition: `EXECUTE`  
Desk routing: Delivery Desk #160 D2  
Upstream contact authorized: `no`

## In simple words

`make_mirror.sh` runs `update_cache()` in a separate shell process at the end of a pipeline. That worker owns a temporary APT directory, but it uses a caching proxy owned by the top-level mirror process.

The imported worker trap used one cleanup-only action for normal exit and signals. A TERM delivered only to the worker could kill the parent's proxy, clean the worker directory, return to later commands, clean again on exit, and report status 0.

PR #267 is the current-main generation of the focused repair. It is directly ahead of live main by one commit and four files. The retained patch and two executable tests are byte-identical to the earlier carriers; only the investigation README records the current generation.

## Why we care

The old behavior can turn cancellation into success, run later package/cache work after a stop request, execute cleanup twice, and let one process kill a child it does not own. The parent may then continue or fail later for an unrelated proxy error.

The exact occurrence frequency is unknown. The observed path requires signal delivery to the `update_cache` shell rather than only to the top-level owner or whole process group.

## What happens if we leave it alone

The imported function contains:

```sh
update_cache() (
  ...
  trap 'kill "$PROXYPID" || :;cleanupapt' EXIT INT TERM
  ...
)
```

A handled worker signal can be deferred during a foreground wait, kill the inherited parent-owned proxy, remove worker-owned APT state, return to later commands, run cleanup again, and return 0 to the parent pipeline.

## Current finding

The worker should own only its APT root and result. The top-level shell should remain the sole owner of proxy shutdown and reaping.

The retained contract is:

- ordinary EXIT cleanup captures `$?`, clears traps, contains cleanup errors, and exits with the primary status;
- INT/QUIT/TERM clear traps, clean the worker-owned APT root once, and exit 130/131/143;
- no worker path signals `$PROXYPID`;
- ordinary success still calls `cleanupapt` explicitly and clears all worker traps;
- the nonzero last-command pipeline result remains fatal under top-level `set -e`;
- top-level owner cleanup stops and waits for the proxy.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Imported source assigns one cleanup-only action to EXIT, INT, and TERM inside `update_cache()`. | `source-read` | blob `6c4be092…`; exact baseline assertion | Pinned source only |
| Worker-only TERM can return 0, run later work, clean twice, and kill the proxy. | `model-executed` | baseline in ownership regression | Reduced harness, no actual APT |
| Candidate INT/QUIT/TERM return 130/131/143 through the parent pipeline, clean once, omit later work, and leave proxy retirement to the parent. | `model-executed` | ownership and signal matrices | Real `/bin/sh`, disposable processes/files |
| Ordinary failure 42 and TERM 143 survive cleanup failure 74. | `model-executed` | precedence controls | Reduced cleanup function |
| Immediate unsignaled reruns succeed without retained APT marker or proxy. | `model-executed` | retained rerun controls | Disposable runtime paths |
| PR #267 is a clean current-main four-file generation. | `source-read` | compare `da52cbfd…` to `c066db40…`; review `4824709149` | Exact relation at this head |
| Complete imported source and repository gate pass. | `target-test-prepared` | CI `30596903218` / 772 | Queued at this revision |

## System and ownership map

- Parent entrypoint: top-level `make_mirror.sh`.
- Worker entrypoint: parenthesized `update_cache()` as the final pipeline command.
- Worker-owned state: `$rootdir` and temporary APT configuration, lists, cache, status, and locks.
- Parent-owned state: caching-proxy PID, cache publication, and top-level result.
- Current cross-owner action: worker trap signals inherited `$PROXYPID`.
- Candidate propagation: worker exits nonzero; pipeline is nonzero; top-level `set -e` exits; parent EXIT cleanup stops and waits for proxy.

## Historical precedent

### Merged top-level mirror-owner repair

- Source: https://github.com/teamleaderleo/linux-fieldwork/pull/224
- Revision: merge `386f5c8dbb01e5de1af45ac0eb325ee8567722e3`
- Principle: every child and cleanup resource needs one owner; cleanup-only signal handlers must terminate.
- Difference: #224 owns top-level launches; this finding owns worker APT state and result.

### Historical focused carriers

- Source: https://github.com/teamleaderleo/linux-fieldwork/pull/238 and https://github.com/teamleaderleo/linux-fieldwork/pull/259
- Revisions: `f6966f0c…` and `d270f558…`
- Principle: exact patch and real-shell matrices establish the worker ownership contract.
- Difference: both became historical delivery surfaces after base drift; #267 preserves exact technical blobs on live main.

## Approaches considered

### Retained: worker cleans worker state; parent cleans proxy

This matches the process/state ownership split and uses the existing top-level `set -e`/EXIT path to retire the proxy.

### Declined: worker still kills proxy but exits 143

This fixes false success while preserving cross-owner child management and possible duplicate/racing cleanup.

### Declined: land historical #259 after base drift

Its technical evidence remains valid, but the branch was behind live main. A direct source generation provides a current one-commit four-file landing surface.

### Deferred and later stopped: prompt descendant cancellation

Linux #263 / PR #264 compared caller groups, worker-child ownership, pipeline groups, output capture, and fallback ownership. The source expansion was stopped as disproportionate without measured harmful latency or an explicit supervisor/dependency contract.

## Edge cases covered

| Case | Evidence | Result |
| --- | --- | --- |
| Baseline worker-only TERM | ownership negative control | status 0; later work; cleanup twice; proxy killed |
| Candidate INT/QUIT/TERM | signal matrix | 130/131/143; no later work; each owner cleans once; proxy gone |
| Immediate rerun | retained rerun controls | status 0; no retained state |
| Ordinary failure plus cleanup failure | precedence control | 42 wins over 74 |
| TERM plus cleanup failure | precedence control | 143 wins over 74 |
| Patch and shell syntax | exact-context local application | passed in retained controls |
| Current direct diff | compare/review | one commit, four files, zero behind at generation time |
| Blob transfer | PR #267 | patch/tests identical to #259 |

## Edge cases deferred or outside scope

| Edge case | Reason | Owner or trigger |
| --- | --- | --- |
| Exact current imported-source/repository gate | current clearing gate | CI `30596903218` |
| Prompt foreground-child stop | disproportionate without measured impact | stopped Linux #263/#264 reopening triggers |
| Full mirror and real APT transaction | high-cost integration | before authorized external packet if justified |
| Proxy ignores TERM | parent escalation policy | separate design finding |
| Current public source | pinned import only | refresh before external preparation |

## Exact execution and receipts

| Repository/head | Command or workflow | Result | Evidence class |
| --- | --- | --- | --- |
| historical focused tree | ownership suite | 4/4 passed in 1.562s | `model-executed` |
| historical focused tree | direct signal matrix | INT 130, QUIT 131, TERM 143; clean reruns | `model-executed` |
| `linux-fieldwork#259@d270f558…` | review `4824383270` | no source-visible repair; later stale-base | `source-read` |
| `linux-fieldwork#267@c066db40…` | review `4824709149` | exact four-file direct diff; no repair | `source-read` |
| same head | Linux Fieldwork CI `30596903218` / 772 | queued | `target-test-prepared` |

## Complete-diff and compatibility review

- Changed-file fence: retained patch, investigation README, ownership regression, signal matrix.
- Base relationship: PR #267 is directly ahead of `da52cbfd…` by one commit and four files.
- Blob identity: patch `f09f666a…`, ownership test `c3fa92f4…`, matrix `bbff77d4…` match #259.
- Historical carriers: #238 and #259 retain development/evidence history and should close after transfer.
- Compatibility surfaces: ordinary success/failure, INT/QUIT/TERM status, cleanup precedence, parent propagation, proxy reaping, no later work, rerun, patch application, shell syntax.
- Current disposition: `EXECUTE`; exact hosted execution is the only current clearing gate.

## Current disposition and desk routing

- Finding state: `delivery-gate-ready`
- Review disposition: `EXECUTE`
- Review Queue entry: exact review retained on PR #267
- Delivery lane: `D2`
- Exact next transition: classify CI `30596903218`; if green and unchanged, set `land-ready` and merge internally
- Clearing condition: complete imported-source patch, shell syntax, both focused matrices, and repository discovery pass on `c066db40…`
- Required subgates: intended job executed; head unchanged; base still current enough; historical carriers retired after transfer
- User decision requested: none

## Changes to the canonical conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-30 | Linux #231 | source boundary, negative control, ownership direction |
| 2026-07-30 | PR #238 | patch and focused matrices |
| 2026-07-31 | PR #259 | first clean current-main restack; later base drift |
| 2026-07-31 | PR #267 `c066db40…` | exact technical blobs regenerated directly on live main; exact CI remains |
| 2026-07-31 | Linux #263/#264 | broader prompt-cancellation expansion stopped with reopening triggers |

## References

- https://github.com/teamleaderleo/linux-fieldwork/issues/231
- https://github.com/teamleaderleo/linux-fieldwork/issues/263
- https://github.com/teamleaderleo/linux-fieldwork/pull/224
- https://github.com/teamleaderleo/linux-fieldwork/pull/238
- https://github.com/teamleaderleo/linux-fieldwork/pull/259
- https://github.com/teamleaderleo/linux-fieldwork/pull/264
- https://github.com/teamleaderleo/linux-fieldwork/pull/267
- https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30596903218
- https://github.com/teamleaderleo/fieldwork/issues/254
