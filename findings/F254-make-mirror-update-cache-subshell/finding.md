# F254-make-mirror-update-cache-subshell: a subshell must not cancel its parent-owned proxy and continue

Finding state: `delivery-gate-ready`

Workstream: `G`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-make-mirror-update-cache-subshell/finding.md`  
Canonical implementation: `teamleaderleo/linux-fieldwork#238` — focused stacked evidence carrier  
Exact implementation head: `14771ccbfc0bd0f378bb3ee1ab0c6fe7c76895d4`  
Exact base or source revision: PR #224 head `13b3c529e983b3ad967725f99f4e31d867fa4742`; imported `make_mirror.sh` blob `6c4be092edcf23b56b63a3befe238c099c45f590`  
Strongest evidence class: `model-executed`; exact imported-source gate `target-test-prepared`  
Reviewed input generation: current Fieldwork #254 protocol; Linux Fieldwork issue #231; PR #224 ownership boundary; PR #238 complete three-file diff  
Current review disposition: `EXECUTE`  
Desk routing: Review Queue #213 update pending  
Upstream contact authorized: `no`

## In simple words

`make_mirror.sh` runs `update_cache()` in a separate shell process at the end of a pipeline. That worker owns a temporary APT directory, but it uses a caching proxy owned by the top-level mirror process.

The worker currently installs the same cleanup action for normal exit and for INT/TERM. When only the worker receives TERM, it can kill the parent's proxy, clean its own directory, return from the trap, continue later work, clean a second time on exit, and report success.

PR #238 now retains a focused patch, investigation, and executable regression. The candidate makes the worker clean only its APT root and exit with an explicit signal-derived status. The parent receives the nonzero pipeline result and its own cleanup stops and waits for the proxy.

The local real-shell model is green. Exact patch application to the complete imported source and repository CI remain pending.

## Why we care

A handled cancellation can become status 0, later APT/cache commands can run after the signal, cleanup can execute twice, and a child process can be killed by a process that does not own its lifecycle. The parent may then continue or fail later for an unrelated proxy error.

The exact occurrence frequency is unknown. The observed path requires signal delivery to the `update_cache` subshell rather than only to the top-level owner or whole process group.

## What happens if we leave it alone

The imported function contains:

```sh
update_cache() (
  ...
  trap 'kill "$PROXYPID" || :;cleanupapt' EXIT INT TERM
  ...
)
```

A shell signal trap returns to interrupted control flow unless it exits or re-raises. Because the same action is also installed for EXIT:

1. TERM can be deferred while the worker waits for a foreground command;
2. the trap kills the inherited parent-owned proxy;
3. `cleanupapt` removes the worker-owned root;
4. the trap returns and later work runs;
5. normal EXIT invokes the same cleanup again;
6. the worker can return 0 to the pipeline parent.

This is the same cleanup-versus-termination class as the top-level defect, with a different resource owner.

## Current finding

The `update_cache` subshell should own only its APT root and result. The top-level shell should remain the sole owner of proxy shutdown and reaping.

PR #238 retains this candidate contract:

- ordinary EXIT cleanup captures `$?`, disables traps, contains cleanup errors, and exits with the primary status;
- INT/QUIT/TERM disable traps, clean the APT root once, and exit 130/131/143;
- no subshell path signals `$PROXYPID`;
- ordinary success still cleans explicitly and clears all worker traps;
- the nonzero last-command pipeline result remains fatal under top-level `set -e`;
- top-level owner cleanup stops and waits for the proxy.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| The imported source assigns one cleanup-only action to EXIT, INT, and TERM inside `update_cache()`. | `source-read` | imported blob `6c4be092…` and PR #238 baseline assertion | Static source plus retained exact-context check |
| A subshell-only TERM can return 0, execute later work, clean twice, and kill the proxy. | `model-executed` | PR #238 baseline real-`/bin/sh` test; Linux issue #231 negative control | Reduced harness, not actual APT |
| The candidate worker returns 143 through the parent pipeline, cleans once, omits later work, and leaves proxy shutdown to the parent. | `model-executed` | PR #238 four-test matrix, local 4/4 | Exact candidate functions extracted after patching an exact-context fixture |
| Ordinary failure 42 and TERM 143 survive cleanup failure 74. | `model-executed` | PR #238 precedence test | Reduced disposable cleanup function |
| Immediate unsignaled rerun succeeds with no retained APT marker or proxy. | `model-executed` | PR #238 same-runtime rerun | Small files and `sleep` proxy |
| The complete imported source accepts the patch, passes `/bin/sh -n`, and preserves repository compatibility. | `target-test-prepared` | Linux Fieldwork CI `30589823763` / 695 | Queued at this finding revision |

## System and ownership map

- Parent entrypoint: top-level `make_mirror.sh`.
- Worker entrypoint: parenthesized `update_cache()` used as the final command in a pipeline.
- Worker-owned state: `$rootdir` and its APT configuration, lists, cache, and lock files.
- Parent-owned state: caching proxy PID, private/published cache lifecycle, top-level result.
- Current cross-owner action: the worker trap kills inherited `$PROXYPID`.
- Candidate propagation: worker exits nonzero; pipeline status is nonzero; top-level `set -e` exits; parent EXIT cleanup stops and waits for proxy.
- Foreground-child boundary: a signal to the worker shell can remain deferred while an unowned foreground APT process runs.

## Historical precedent

### Top-level mirror-owner repair

- Source: https://github.com/teamleaderleo/linux-fieldwork/pull/224
- Revision or date: exact stacked base `13b3c529e983b3ad967725f99f4e31d867fa4742`
- Principle supported: child shutdown, cache deletion, and signal result need explicit owners; cleanup-only signal handlers must terminate.
- Important difference: #224 owns top-level proxy launches. This finding owns a pipeline subshell and prevents that subshell from directly managing the proxy.

### Parent repair and published-cache preservation

- Source: https://github.com/teamleaderleo/linux-fieldwork/pull/205
- Revision or date: merged 2026-07-30
- Principle supported: ordinary EXIT cleanup and signal termination are different; killing without waiting is incomplete ownership.
- Important difference: the earlier repair deliberately deferred the `update_cache()` trap because it has separate process scope.

### Composed wrapper ownership

- Source: https://github.com/teamleaderleo/linux-fieldwork/pull/196
- Revision or date: merged 2026-07-30
- Principle supported: every child and cleanup resource should have one owner, and nonzero child results should reach the parent through an explicit precedence path.
- Important difference: the current worker communicates through pipeline status rather than direct child-wait status.

## Approaches considered

### Retained: worker cleans worker state; parent cleans proxy

This follows the actual ownership split and uses the existing top-level `set -e`/EXIT path to retire the proxy. It avoids two processes independently signaling the same child.

### Declined: keep killing the proxy from the worker and only add `exit 143`

This fixes false success while preserving cross-owner child management. Parent and worker cleanup can then race or duplicate proxy signaling and waiting.

### Deferred: make the worker own foreground APT children

Prompt cancellation while the shell waits would require asynchronous launch, child PID tracking, forwarding, waiting, and possibly escalation for several commands. That is a broader lifecycle composition.

### Deferred: process-group cancellation

Group delivery may stop worker, foreground command, parent, and proxy together, but it changes caller-group policy and can hide the parent-only/subshell-only ownership defect.

## Executed edge cases

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Baseline worker-only TERM during foreground wait | PR #238 local real-shell negative control | status 0; proxy gone; cleanup twice; worker and parent later markers present |
| Candidate worker-only TERM under parent `set -e` | PR #238 local composed model | parent status 143; worker cleanup once; parent cleanup once; no later markers; proxy gone |
| Candidate immediate unsignaled rerun | same disposable runtime path | status 0; explicit worker cleanup once; parent cleanup once; no APT marker or proxy |
| Ordinary failure plus cleanup failure | precedence control | status 42 wins over cleanup 74 |
| TERM plus cleanup failure | precedence control | status 143 wins over cleanup 74 |
| Patch fixture and shell syntax | exact-context patch application and `/bin/sh -n` | passed locally |
| Network, APT, mount, and privilege negative control | disposable harness design | none used |

## Remaining gates and deferred edges

| Edge case or gate | State or reason |
| --- | --- |
| Exact complete imported-source patch and `/bin/sh -n` | queued in CI `30589823763` |
| Complete repository suite | queued on exact PR #238 head |
| Complete three-file review | required after hosted result |
| Prompt stop of foreground APT child | separate child-ownership design |
| Process-group delivery | different topology and policy |
| Full mirror and real APT transaction | high-cost integration gate after focused acceptance |
| Proxy ignores TERM | parent escalation policy |
| Current public upstream source | refresh before any authorized upstream packet |

## Exact execution and receipts

| Repository/head | Command or workflow | Result | Evidence class |
| --- | --- | --- | --- |
| local PR #238 fixture | `python3 -m unittest -v tests/test_make_mirror_update_cache_signal_ownership.py` | 4/4 passed in 1.562s | `model-executed` |
| `linux-fieldwork#238@14771ccbfc0bd0f378bb3ee1ab0c6fe7c76895d4` | Linux Fieldwork CI `30589823763` / 695 | queued | `target-test-prepared` |

The first published PR #238 head omitted context lines declared by the first patch hunk. The current head repairs that carrier defect without changing the source mechanism or test contract.

## Complete-diff and compatibility status

- Changed-file fence: retained source patch, focused investigation README, executable regression.
- Stacking base: PR #224 exact head `13b3c529e983b3ad967725f99f4e31d867fa4742`.
- Mechanical overlap: separate source region inside `update_cache()`; PR #224 remains independently reviewable.
- Compatibility surfaces: top-level first-signal handling, launch ownership, cache ownership, published-cache preservation, worker ordinary success/failure, parent pipeline status, cleanup counts, process disappearance, and rerun cleanliness.
- Current disposition: `EXECUTE`; exact hosted target execution and fresh complete-diff review remain.

## Current routing

- Finding state: `delivery-gate-ready`
- Review disposition: `EXECUTE`
- Review Queue: #213 update pending this finding PR
- Delivery lane: not entered
- Exact next transition: classify PR #238 CI, review its unchanged exact head, then promote or issue one bounded repair list.
- Clearing condition: exact imported-source execution of worker status, parent propagation, ownership split, ordinary paths, and rerun.
- User decision requested: none for this internal evidence step.

## Changes to the canonical conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-30 | Linux Fieldwork #231 | Recorded exact source boundary, executed negative control, and candidate ownership model |
| 2026-07-30 | Initial finding PR | Materialized the follow-up as `research-active` |
| 2026-07-30 | Linux Fieldwork PR #238 | Added a focused retained patch, regression, local 4/4 model gate, and queued exact-source CI; state advanced to `delivery-gate-ready` / `EXECUTE` |

## References

- https://github.com/teamleaderleo/linux-fieldwork/issues/231
- https://github.com/teamleaderleo/linux-fieldwork/pull/224
- https://github.com/teamleaderleo/linux-fieldwork/pull/238
- https://github.com/teamleaderleo/linux-fieldwork/pull/205
- https://github.com/teamleaderleo/linux-fieldwork/pull/196
- https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30589823763
- https://github.com/teamleaderleo/fieldwork/issues/254
