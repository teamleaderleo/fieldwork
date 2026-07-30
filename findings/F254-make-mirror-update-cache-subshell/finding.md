# F254-make-mirror-update-cache-subshell: a subshell must not cancel its parent-owned proxy and continue

Finding state: `research-active`

Workstream: `G`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-make-mirror-update-cache-subshell/finding.md`  
Canonical implementation: `none`; Linux Fieldwork issue `#231` owns the retained follow-up  
Exact base or source revision: imported `make_mirror.sh` blob `6c4be092edcf23b56b63a3befe238c099c45f590`  
Strongest evidence class: `model-executed` plus `source-read`  
Reviewed input generation: current Fieldwork #254 protocol; Linux Fieldwork issue #231; PR #224 ownership boundary  
Current review disposition: `RESEARCH`  
Desk routing: not entered  
Upstream contact authorized: `no`

## In simple words

`make_mirror.sh` runs `update_cache()` in a separate shell process at the end of a pipeline. That worker owns a temporary APT directory, but it uses a caching proxy owned by the top-level mirror process.

The worker currently installs the same cleanup action for normal exit and for INT/TERM. When only the worker receives TERM, it can kill the parent's proxy, clean its own directory, return from the trap, continue later work, clean a second time on exit, and report success.

A reduced real `/bin/sh` control reproduced that exact result. A candidate ownership model also showed the intended split: the worker cleans its APT directory and exits 143; the parent sees the nonzero pipeline result under `set -e`, exits 143, and its owner cleanup stops the proxy.

No repository patch has been retained yet. This finding remains `research-active` and must not be confused with PR #224's review-ready top-level proxy-launch scope.

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

This is the same cleanup-versus-termination class as the top-level defect, but the resource ownership is different.

## Current finding

The `update_cache` subshell should own only its APT root and result. The top-level shell should remain the sole owner of proxy shutdown and reaping.

A focused candidate direction is:

- ordinary EXIT cleanup calls `cleanupapt`;
- INT/QUIT/TERM handlers disable traps, clean the APT root once, and exit 130/131/143;
- signal cleanup does not kill `$PROXYPID` from the subshell;
- the nonzero last-command pipeline result remains fatal under top-level `set -e`;
- top-level owner cleanup stops and waits for the proxy.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| The imported source assigns one cleanup-only action to EXIT, INT, and TERM inside `update_cache()`. | `source-read` | imported blob lines around the parenthesized function and trap | Static source only |
| A subshell-only TERM can return 0, execute later work, clean twice, and kill the proxy. | `model-executed` | local disposable `/bin/sh` harness recorded in Linux issue #231 | Reduced exact-shape harness, not actual APT |
| Separating subshell cleanup from parent proxy ownership can produce parent status 143, one cleanup per owner, no later work, and no proxy survivor. | `model-executed` | composed parent/worker `/bin/sh` model recorded in #231 | Candidate design model, not retained source patch |
| The actual target pipeline under the complete candidate preserves the same composition. | `not-yet-proved` | required retained regression | Must execute exact patched source/harness |

## System and ownership map

- Parent entrypoint: top-level `make_mirror.sh`.
- Worker entrypoint: parenthesized `update_cache()` used as the final command in a pipeline.
- Worker-owned state: `$rootdir` and its APT configuration, lists, cache, and lock files.
- Parent-owned state: caching proxy PID, private/published cache lifecycle, top-level result.
- Current cross-owner action: the worker trap kills inherited `$PROXYPID`.
- Expected propagation: worker exits nonzero; pipeline status is nonzero; top-level `set -e` exits; parent EXIT cleanup stops and waits for proxy.
- Foreground-child boundary: a signal to the worker shell can remain deferred while an unowned foreground APT process runs.

## Historical precedent

### Top-level mirror-owner repair

- Source: https://github.com/teamleaderleo/linux-fieldwork/pull/224
- Revision or date: exact reviewed head `13b3c529e983b3ad967725f99f4e31d867fa4742`
- Principle supported: child shutdown, cache deletion, and signal result need explicit owners; cleanup-only signal handlers must terminate.
- Important difference: #224 owns top-level proxy launches. This finding owns a pipeline subshell and must not let that subshell directly manage the proxy.

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

### Preferred direction: worker cleans worker state; parent cleans proxy

This follows the actual ownership split and uses the existing top-level `set -e`/EXIT path to retire the proxy. It avoids two processes independently signaling the same child.

### Declined: keep killing the proxy from the worker and only add `exit 143`

This fixes false success but preserves cross-owner child management. Parent and worker cleanup can then race or duplicate proxy signaling and waiting.

### Deferred: make the worker own foreground APT children

Prompt cancellation while the shell waits would require asynchronous launch, child PID tracking, forwarding, waiting, and possibly escalation for several commands. That is a broader lifecycle composition.

### Deferred: process-group cancellation

Group delivery may stop worker, foreground command, parent, and proxy together, but it changes caller-group policy and can hide the parent-only/subshell-only ownership defect.

## Edge cases already executed

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Baseline worker-only TERM during foreground wait | local reduced `/bin/sh` negative control | status 0; proxy gone; cleanup twice; later marker present |
| Candidate-model worker-only TERM under parent `set -e` | local composed model | parent status 143; worker cleanup once; parent cleanup once; no later markers; proxy gone |
| No network, APT, mount, or privilege | disposable harness design | confirmed |

## Required retained edge cases

| Edge case | Required result |
| --- | --- |
| Exact imported-source patch and `/bin/sh -n` | pass |
| Baseline worker-only TERM | reproduce status 0, later work, double cleanup, proxy kill |
| Candidate worker-only TERM | worker exits 143, one APT cleanup, no later work |
| Parent pipeline composition | parent exits 143 under `set -e`; parent cleanup stops/waits for proxy once |
| Ordinary worker success | explicit cleanup, traps cleared, status 0 |
| Ordinary worker failure | primary status survives cleanup |
| Immediate unsignaled rerun | no retained process or APT root; status 0 |
| INT/QUIT/TERM mapping | explicit and executed, or narrow supported set documented |
| Cleanup failure | cancellation precedence and retained-state diagnostic decided |

## Deferred or outside scope

| Edge case | Why deferred | Reopening or owning trigger |
| --- | --- | --- |
| Prompt stop of foreground APT child | Current signal may be deferred until child returns | Separate child-ownership design after focused repair |
| Process-group delivery | Different topology and policy | New control if behavior differs materially |
| Full mirror and real APT transaction | High-cost integration boundary | Gate only after exact focused candidate is accepted |
| Proxy ignores TERM | Parent escalation policy | Separate design finding |
| Current public upstream source | Imported pinned blob | Refresh before any authorized upstream packet |

## Exact execution and receipts

| Environment | Command shape | Result | Evidence class |
| --- | --- | --- | --- |
| local Linux `/bin/sh` | baseline owner with exact `trap 'kill "$PROXYPID" || :;cleanupapt' EXIT INT TERM`, foreground wait, worker-only TERM | status 0; proxy killed; cleanup twice; later work present | `model-executed` |
| local Linux `/bin/sh` | candidate worker signal-exit plus parent `set -e` and parent-owned proxy cleanup | parent status 143; one worker cleanup; one parent cleanup; no later work; proxy gone | `model-executed` |

No retained branch, PR, hosted run, or public upstream contact exists yet.

## Complete-diff and compatibility status

- Canonical source overlap: same imported `make_mirror.sh` and investigation area as PR #224.
- Stacking rule: do not modify #224 while its exact hosted gate is pending. Build a focused successor from the stable accepted #224 head.
- Compatibility surfaces to preserve: top-level first-signal handling, launch ownership, cache ownership, published-cache preservation, worker ordinary success/failure, parent pipeline status, cleanup counts, rerun cleanliness.
- Current disposition: `RESEARCH`; the source and model establish a concrete defect and repair direction, but no exact retained patch/test exists.

## Current routing

- Finding state: `research-active`
- Review disposition: `RESEARCH`
- Review Queue: not entered
- Delivery lane: not entered
- Exact next transition: after #224 is stable, create one focused successor branch with an exact patch and retained negative/control matrix.
- Clearing condition: target-executed exact-source proof of worker status, parent propagation, ownership split, ordinary paths, and rerun.
- User decision requested: none; this is a bounded internal follow-up.

## Changes to the canonical conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-30 | Linux Fieldwork #231 | Recorded exact source boundary, executed negative control, and candidate ownership model |
| 2026-07-30 | This finding PR | Materialized the follow-up as `research-active` without expanding #224's canonical scope |

## References

- https://github.com/teamleaderleo/linux-fieldwork/issues/231
- https://github.com/teamleaderleo/linux-fieldwork/pull/224
- https://github.com/teamleaderleo/linux-fieldwork/pull/205
- https://github.com/teamleaderleo/linux-fieldwork/pull/196
- https://github.com/teamleaderleo/linux-fieldwork/blob/ed49c01a85e9d363626db5d2973a33b67209e13b/upstream/mmdebstrap/make_mirror.sh
- https://github.com/teamleaderleo/fieldwork/issues/254
