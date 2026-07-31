# F254-run-qemu-result-precedence: preserve authoritative results through cleanup

Finding state: `delivery-gate-ready`

Workstream: `G`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-run-qemu-result-precedence/finding.md`  
Canonical implementation: `teamleaderleo/linux-fieldwork#319`  
Exact implementation head: `2fe3f99364df29de217536dc35a4d03b10f49640`  
Exact base or source revision: Linux Fieldwork main `782774b01002abf37878d834a54d0bbf8b226397`; imported `run_qemu.sh` blob `426aeeb854173569b24e64d6eb85019f45bdf0b6`  
Strongest evidence class: lifecycle and event-order claims `model-executed`; complete composed repository gate `target-test-prepared`  
Reviewed input generation: current Fieldwork/Linux protocols; Linux issues #269/#297; PRs #270/#282/#304; PR #319 review `4828231099`  
Current review disposition: `EXECUTE`  
Desk routing: Delivery Desk #160 D2  
Upstream contact authorized: `no`

## In simple words

`run_qemu.sh` can learn several different results while it exits:

- the host, timeout, debvm, or QEMU command failed;
- the guest completed and reported failure;
- INT or TERM cancelled the wrapper;
- cleanup failed.

The imported wrapper used the same cleanup body for ordinary exit and signals. It could report the wrong owner, return success after cancellation, run cleanup twice, lose the first signal, ignore a signal during ordinary cleanup, or replace an already-completed guest failure with a later cleanup-time signal.

The composed candidate applies one event-ordered rule:

```text
captured host failure
> completed guest failure
> first cleanup-time signal
> first cleanup failure
> success
```

## Why we care

Timeout 124, host failure 42, guest failure 1, cancellation 130/143, and cleanup failure identify different owners and recovery actions. Replacing one with another misclassifies the incident.

A result is not authoritative merely because cleanup observed it last. The final status must preserve the earliest completed failure at the correct ownership layer while still completing bounded cleanup once.

## What happens if we leave it alone

The imported source installs:

```sh
trap cleanup INT TERM EXIT
```

Reproduced consequences include:

- host timeout 124 plus guest failure returns 1;
- missing guest status can replace host failure;
- INT/TERM plus guest success returns 0;
- INT/TERM plus guest failure returns 1;
- signal cleanup exits through the still-installed EXIT trap and runs again;
- an early repair can lose TERM 143 to later INT and stop cleanup after only `rm`;
- a two-patch repair can ignore TERM during ordinary cleanup and return 0;
- a three-patch repair can replace completed guest failure 1 with later TERM 143.

## Exact event order

The guest worker completes before host ordinary EXIT cleanup:

1. it executes the test and captures the status;
2. it writes `/mnt/exitstatus.txt`;
3. it unmounts `/mnt`;
4. it powers off;
5. `debvm-run` returns;
6. host EXIT cleanup begins.

A nonzero guest status is therefore already authoritative before INT or TERM arrives during host cleanup.

## Current finding

Result ownership must be explicit and event ordered.

The retained contract is:

1. ordinary EXIT captures the incoming host status;
2. explicit INT and TERM select 130 and 143;
3. EXIT is cleared before final exit, preventing cleanup re-entry;
4. already-handled INT/TERM remain ignored while bounded explicit-signal cleanup finishes;
5. ordinary EXIT cleanup records its first INT/TERM instead of ignoring it;
6. a captured host failure remains authoritative;
7. otherwise a completed guest nonzero, malformed, unreadable, or missing result becomes generic 1;
8. otherwise the first cleanup-time INT/TERM becomes 130/143;
9. otherwise the first cleanup failure becomes final;
10. later cleanup actions still run but cannot replace that first cleanup failure;
11. otherwise status is 0.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Imported host 124 plus guest failure returns 1. | `model-executed` | primary negative control | Reduced exact cleanup shape |
| Imported INT/TERM can become guest-dependent 0/1 and cleanup runs twice. | `model-executed` | explicit signal matrix and cleanup log | Disposable shell model |
| A later handled signal can replace the first and interrupt cleanup. | `model-executed` | TERM→INT predecessor barrier | INT/TERM only |
| A signal during ordinary EXIT cleanup can disappear as status 0. | `model-executed` | two-patch predecessor barrier | Bounded cleanup |
| Guest failure completes before host cleanup. | `source-read` | guest write/unmount/poweroff and host wait order | Pinned import |
| Three-patch signal-over-guest policy returns 143 after completed guest failure. | `model-executed` | PR #304 negative control | Reduced exact source shape |
| Final policy retains host, guest, cleanup-time signal, and cleanup order. | `model-executed` | patches 1–4 and five focused modules | No real QEMU/debvm |
| Composed current-main packet is one commit and seventeen files. | `source-read` | PR #319 compare and review `4828231099` | Exact generation |
| Complete repository gate is prepared on the composed head. | `target-test-prepared` | CI `30628645668` / 889 | Queued at this revision |

## Patch and ownership map

### Patch 1 — primary result and once-only cleanup

- introduces `finish STATUS`;
- reads guest status without allowing `set -e` to replace an existing host failure;
- retains the first cleanup failure;
- separates ordinary EXIT and explicit INT/TERM cleanup;
- prevents EXIT cleanup re-entry.

### Patch 2 — first handled signal stability

- ignores already-handled INT/TERM through bounded cleanup;
- prevents a second handled signal from replacing the first or interrupting cleanup.

### Patch 3 — first signal during ordinary EXIT cleanup

- adds a first-writer cleanup signal slot;
- records INT/TERM during ordinary EXIT cleanup;
- retains cancellation after otherwise successful work.

### Patch 4 — completed guest before later cleanup signal

- changes only final selection;
- places completed guest failure before later cleanup-time cancellation;
- preserves host precedence, signal capture, cleanup, and first-writer behavior.

## System and ownership map

- Wrapper owner: `run_qemu.sh`.
- Primary host result owner: timeout/debvm/QEMU command.
- Explicit cancellation owner: INT/TERM handler.
- Completed subordinate result: guest-written `shared/exitstatus.txt` after guest completion.
- Cleanup-time cancellation owner: first INT/TERM received after ordinary cleanup starts.
- Cleanup owner: temporary log and directory.
- Background log follower: existing `setpriv --pdeathsig TERM tail -f`; unchanged.
- Final flow: host, completed guest, cleanup-time signal, first cleanup failure, success.

## Alternatives and what made them lose

### Imported shared trap — rejected

It loses host and signal identity and runs cleanup twice.

### Host-only guard — rejected

It preserves some host failures but still leaves signal status guest-dependent and cleanup duplicated.

### Restore default INT/TERM before cleanup — rejected

A second signal can replace the first and stop cleanup halfway.

### Ignore INT/TERM for all cleanup — rejected

During ordinary EXIT cleanup no signal has yet been retained; cancellation can disappear as success.

### Cleanup-time signal before completed guest — rejected

It reports later cancellation instead of a guest failure that was already written and durable before cleanup began.

### Last cleanup failure wins — rejected

It hides the first cleanup operation that failed.

## Edge cases covered

| Case | Evidence | Selected result |
| --- | --- | ---: |
| Host 0/42/124/signal-like 143 | primary matrices | incoming host result when nonzero |
| Guest 0/nonzero/malformed/missing | primary/event-order matrices | 1 only after host success |
| Explicit INT/TERM | signal matrices | 130/143 |
| TERM then INT during cleanup | deterministic barrier | first signal retained |
| Ordinary EXIT then INT/TERM | deterministic barrier | 130/143 after guest success |
| Completed guest failure then TERM | event-order matrix | 1 |
| Cleanup rm 74 then rmdir 75 | cleanup regression | 74 |
| Signal over cleanup failure after success | event-order matrix | 130/143 |
| Once-only cleanup | cleanup logs | exactly `rm, rmdir` |
| Immediate rerun | focused modules | clean success |
| Patch composition | patches 1–4 | zero fuzz and `/bin/sh -n` |
| Discovery | repository test suite | no duplicate imported cases |

## Edge cases deferred or outside scope

| Edge case | Why outside scope | Reopening trigger |
| --- | --- | --- |
| Real QEMU/debvm guest execution | high-cost integration | contradictory reduced evidence or delivery need |
| Foreground-child/process-group cancellation | separate topology | surviving descendant evidence |
| HUP/QUIT mapping | no selected contract | explicit policy request |
| TERM-to-KILL escalation | cleanup is bounded in this proof | uncooperative process evidence |
| Background tail lifecycle | existing pdeathsig unchanged | leak evidence |
| Current public source | pinned import only | external preparation authority |
| Unusual filesystem cleanup | reduced failures only | contradictory filesystem evidence |

## Exact execution and receipts

| Repository/head | Gate | Result | Evidence class |
| --- | --- | --- | --- |
| PR #270 `76ffad2e…` | Linux CI `30623610733` / 828 | passed | `model-executed` / repository gate |
| PR #282 `e973546c…` | Linux CI `30624661338` / 844 | passed | mechanism gate |
| PR #304 `0d5864c5…` | Linux CI `30625359304` / 854 | passed | event-order comparison gate |
| PR #319 `2fe3f993…` | complete review `4828231099` | no source-visible repair | `source-read` |
| same head | Linux CI `30628645668` / 889 | queued | `target-test-prepared` |

The component runs validate exact historical generations. They do not replace the composed head's final gate.

## Complete-diff and compatibility review

- Direct relation: one commit ahead of current main, zero behind at generation time.
- File fence: four patches, four investigation records, four reusable notes, five executable modules.
- Sixteen component blobs transferred byte-identically; only the canonical README changed.
- Imported product source is not edited directly; the exact patch stack is retained as candidate material.
- Compatibility surfaces reviewed: host/guest/signal/cleanup ordering, competing signals, missing/malformed guest status, once-only cleanup, rerun, syntax, discovery.
- Unchanged: QEMU/debvm command construction, timeout policy, guest status format, background follower, HUP/QUIT, process-group policy.

## Current disposition and desk routing

- Finding state: `delivery-gate-ready`
- Review disposition: `EXECUTE`
- Delivery lane: `D2`
- Exact next transition: classify CI `30628645668`; if green and unchanged, mark PR #319 `land-ready` and retire #270/#282/#304 without merge
- Clearing condition: all five focused modules, zero-fuzz patches 1–4, complete shell syntax, repository discovery, unchanged seventeen-file fence
- User decision requested: none

## Changes to the canonical conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-31 | Linux #269/#270 | found host overwrite, false signal success, duplicate cleanup, and first cleanup failure rule |
| 2026-07-31 | competing-signal review | found second handled signal could replace first and interrupt cleanup |
| 2026-07-31 | Linux #282 | found first signal during ordinary EXIT cleanup could disappear; mechanism passed CI 844 |
| 2026-07-31 | Linux #297/#304 | proved completed guest failure precedes later cleanup signal; comparison passed CI 854 |
| 2026-07-31 | Linux #319 | materialized one current-main seventeen-file composed carrier |

## References

- https://github.com/teamleaderleo/linux-fieldwork/issues/269
- https://github.com/teamleaderleo/linux-fieldwork/issues/297
- https://github.com/teamleaderleo/linux-fieldwork/pull/270
- https://github.com/teamleaderleo/linux-fieldwork/pull/282
- https://github.com/teamleaderleo/linux-fieldwork/pull/304
- https://github.com/teamleaderleo/linux-fieldwork/pull/319
- https://github.com/teamleaderleo/fieldwork/issues/254
