# F254-make-mirror-update-cache-subshell: a subshell must not cancel its parent-owned proxy and continue

Finding state: `delivery-gate-ready`

Workstream: `G`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-make-mirror-update-cache-subshell/finding.md`  
Canonical implementation: `teamleaderleo/linux-fieldwork#259` — clean current-main carrier  
Exact implementation head: `d270f558fa7c32569ea380fd614c34edaf60b3b3`  
Exact base or source revision: Linux Fieldwork main `386f5c8dbb01e5de1af45ac0eb325ee8567722e3`; imported `make_mirror.sh` blob `6c4be092edcf23b56b63a3befe238c099c45f590`  
Strongest evidence class: lifecycle claims `model-executed`; exact imported-source gate `target-test-prepared`  
Reviewed input generation: Fieldwork #254 current protocol; Linux issue #231; merged PR #224 boundary; historical PR #238; PR #259 exact review `4824383270`  
Current review disposition: `EXECUTE`  
Desk routing: Delivery Desk #160 D2 after canonical finding reconciliation  
Upstream contact authorized: `no`

## In simple words

`make_mirror.sh` runs `update_cache()` in a separate shell process at the end of a pipeline. That worker owns a temporary APT directory, but it uses a caching proxy owned by the top-level mirror process.

The old worker trap handled normal exit and signals with the same cleanup action. A TERM delivered only to the worker could kill the parent's proxy, clean the worker directory, return to later commands, clean a second time on exit, and report status 0.

Historical PR #238 retained a focused patch and two real-shell matrices. After parent PR #224 merged, #238's branch ancestry became obsolete. Canonical PR #259 is a clean four-file restack directly on merged main. The patch and both tests are byte-identical to #238; only the investigation README was refreshed for current carrier and parent state.

## Why we care

A handled cancellation can become success, later package/cache commands can run after the signal, cleanup can execute twice, and a process can kill a child it does not own. The parent may then continue or fail later for an unrelated proxy error.

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

Because a shell signal trap returns unless it exits or re-raises, a worker-only signal can:

1. be deferred while the worker waits for a foreground command;
2. kill the inherited proxy owned by the parent;
3. remove the worker-owned APT root;
4. return and execute later work;
5. run the same cleanup again on EXIT;
6. return 0 to the parent pipeline.

## Current finding

The `update_cache` worker should own only its APT root and result. The top-level shell should remain the sole owner of proxy shutdown and reaping.

The retained contract is:

- ordinary EXIT cleanup captures `$?`, disables traps, contains cleanup errors, and exits with the primary status;
- INT/QUIT/TERM disable traps, clean the worker-owned APT root once, and exit 130/131/143;
- no worker path signals `$PROXYPID`;
- ordinary success still calls `cleanupapt` explicitly and clears all worker traps;
- the nonzero last-command pipeline result remains fatal under top-level `set -e`;
- top-level owner cleanup stops and waits for the proxy.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| The imported source assigns one cleanup-only action to EXIT, INT, and TERM inside `update_cache()`. | `source-read` | blob `6c4be092…`; exact baseline assertion | Pinned source only |
| Worker-only TERM can return 0, run later work, clean twice, and kill the proxy. | `model-executed` | baseline in `test_make_mirror_update_cache_signal_ownership.py` | Reduced harness, no actual APT |
| Candidate INT/QUIT/TERM return 130/131/143 through the parent pipeline, clean once, omit later work, and leave proxy shutdown to the parent. | `model-executed` | ownership suite and direct signal matrix | Real `/bin/sh`, disposable processes/files |
| Ordinary failure 42 and TERM 143 survive cleanup failure 74. | `model-executed` | precedence control | Reduced cleanup function |
| Immediate unsignaled reruns succeed with no retained APT marker or proxy. | `model-executed` | same-runtime and per-signal reruns | Disposable runtime paths |
| PR #259 is a clean four-file branch directly ahead of merged main. | `source-read` | compare `386f5c8d…` to `d270f558…`; review `4824383270` | Repository relation at this head |
| The complete imported source accepts the patch and passes the named repository gate. | `target-test-prepared` | CI `30593942296` / 740 | Queued at this finding revision |

## System and ownership map

- Parent entrypoint: top-level `make_mirror.sh`.
- Worker entrypoint: parenthesized `update_cache()` as the last pipeline command.
- Worker-owned state: `$rootdir` and temporary APT configuration, lists, cache, status, and locks.
- Parent-owned state: caching proxy PID, top-level cache publication, top-level result.
- Current cross-owner action: worker trap signals inherited `$PROXYPID`.
- Candidate propagation: worker exits nonzero; pipeline status is nonzero; top-level `set -e` exits; parent EXIT cleanup stops and waits for proxy.
- Foreground-child boundary: a signal to the worker shell can remain deferred while an unowned foreground APT command runs.

## Historical precedent

### Merged top-level mirror-owner repair

- Source: https://github.com/teamleaderleo/linux-fieldwork/pull/224
- Revision or date: merge commit `386f5c8dbb01e5de1af45ac0eb325ee8567722e3`, 2026-07-31
- Principle supported: every child and cleanup resource needs one owner; cleanup-only signal handlers must terminate.
- Important difference: #224 owns top-level proxy launches. This finding owns the pipeline worker's APT state and result.

### Parent repair and published-cache preservation

- Source: https://github.com/teamleaderleo/linux-fieldwork/pull/205
- Revision or date: merged 2026-07-30
- Principle supported: ordinary EXIT cleanup and signal termination are different; killing without waiting is incomplete ownership.
- Important difference: the earlier repair deliberately left the worker-local trap for separate analysis.

### Historical focused carrier

- Source: https://github.com/teamleaderleo/linux-fieldwork/pull/238
- Revision or date: exact head `f6966f0ccd6c3ea91ae39c260f23e6e416b5c601`
- Principle supported: focused patch and real-shell matrices establish the worker ownership contract.
- Important difference: its branch was stacked on the pre-merge #224 head and became a noncanonical delivery surface after #224 landed.

## Approaches considered

### Retained: worker cleans worker state; parent cleans proxy

This matches the actual process and state ownership split and uses the existing top-level `set -e`/EXIT path to retire the proxy.

### Declined: keep killing the proxy from the worker and only add `exit 143`

That fixes false success while preserving cross-owner child management. Parent and worker cleanup can race or duplicate child actions.

### Declined: retarget historical PR #238 to main

Because #224 was merged as a new main commit rather than preserving the stacked ancestry, retargeting #238 would reintroduce the five parent files. A clean restack is the smallest honest diff.

### Deferred: worker owns foreground APT children

Prompt cancellation during a foreground wait would require child PID tracking, forwarding, waiting, and possibly escalation for several commands.

### Deferred: process-group cancellation

Group delivery changes caller policy and can hide the worker-only ownership defect.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Baseline worker-only TERM during foreground wait | historical #238 negative control | status 0; proxy gone; cleanup twice; worker and parent later markers present |
| Candidate worker-only INT/QUIT/TERM under parent `set -e` | retained matrices | parent statuses 130/131/143; worker cleanup once; parent cleanup once; no later markers; proxy gone |
| Immediate unsignaled reruns | same-runtime and per-signal controls | status 0; explicit cleanup once; no APT marker or proxy |
| Ordinary failure plus cleanup failure | precedence control | status 42 wins over cleanup 74 |
| TERM plus cleanup failure | precedence control | status 143 wins over cleanup 74 |
| Patch fixture and `/bin/sh -n` | exact-context local application | passed |
| Current-main diff | compare and exact review | four files only; no duplicated #224 history |
| Blob transfer | PR #259 source identity check | retained patch and both tests byte-identical to #238 |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning record or trigger |
| --- | --- | --- |
| Exact complete imported-source and repository gate | Current clearing gate | CI `30593942296` |
| Prompt stop of foreground APT child | Separate child-ownership design | New finding after exact process map |
| Process-group delivery | Different topology and policy | Reopen on contradictory behavior |
| Full mirror and real APT transaction | High-cost integration | Before any authorized external packet if justified |
| Proxy ignores TERM | Parent escalation policy | Separate top-level design finding |
| Current public source | Pinned import only | Refresh before external preparation |

## Exact execution and receipts

| Repository/head | Command or workflow | Result | Evidence class |
| --- | --- | --- | --- |
| historical local #238 tree | `python3 -m unittest -v tests/test_make_mirror_update_cache_signal_ownership.py` | 4/4 passed in 1.562s | `model-executed` |
| historical local #238 tree | `python3 -m unittest -v tests/test_make_mirror_update_cache_signal_matrix.py` | INT 130, QUIT 131, TERM 143; clean reruns | `model-executed` |
| `linux-fieldwork#238@f6966f0ccd6c3ea91ae39c260f23e6e416b5c601` | Linux Fieldwork CI `30590250175` / 704 | historical stacked run queued | `target-test-prepared`; noncanonical for landing |
| `linux-fieldwork#259@d270f558fa7c32569ea380fd614c34edaf60b3b3` | complete review `4824383270` | no source-visible repair required | `source-read` |
| same exact head | Linux Fieldwork CI `30593942296` / 740 | queued | `target-test-prepared` |

The first historical #238 patch omitted context lines declared by its first hunk. The final historical head repaired that packaging defect before the exact patch and test blobs were transferred to #259.

## Complete-diff and compatibility review

- Changed-file fence: retained source patch, focused investigation README, ownership regression, direct signal matrix.
- Base relationship: PR #259 is directly ahead of merged main `386f5c8d…` by four files.
- Blob identity: patch `f09f666a…`, ownership test `c3fa92f4…`, signal matrix `bbff77d4…` match #238.
- README change: carrier/base state only; technical mechanism and evidence limits preserved.
- Historical carrier: PR #238 remains evidence history and should retire after exact-head evidence transfer.
- Compatibility surfaces: worker ordinary success/failure, INT/QUIT/TERM status, cleanup precedence, parent pipeline propagation, proxy reaping, no later work, rerun cleanliness, patch application, shell syntax.
- Current disposition: `EXECUTE`; exact hosted target execution is the only current gate after review `4824383270`.

## Current disposition and desk routing

- Finding state: `delivery-gate-ready`
- Review disposition: `EXECUTE`
- Review Queue entry: no additional technical review gate; exact review retained on PR #259
- Delivery lane: `D2`
- Exact next transition: classify CI `30593942296` on unchanged head, then set `land-ready` and merge or issue one bounded repair
- Clearing condition: exact imported-source patch, shell syntax, both focused matrices, and repository discovery pass on `d270f558…`
- Required subgates: intended job executed; exact head unchanged; historical #238 retired after transfer
- User decision requested: none

## Changes to the canonical conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-30 | Linux #231 | Recorded source boundary, negative control, and ownership direction |
| 2026-07-30 | PR #238 | Added patch, two regressions, direct signal matrix, and focused review |
| 2026-07-31 | PR #224 merge `386f5c8d…` | Parent lifecycle became part of main; #238's stacked ancestry became obsolete |
| 2026-07-31 | PR #259 `d270f558…` | Restacked the exact patch/tests on current main, refreshed carrier prose, and retained one exact CI gate |

## References

- https://github.com/teamleaderleo/linux-fieldwork/issues/231
- https://github.com/teamleaderleo/linux-fieldwork/pull/224
- https://github.com/teamleaderleo/linux-fieldwork/pull/238
- https://github.com/teamleaderleo/linux-fieldwork/pull/259
- https://github.com/teamleaderleo/linux-fieldwork/pull/205
- https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30593942296
- https://github.com/teamleaderleo/fieldwork/issues/254
