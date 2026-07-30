# F254-make-mirror-signal-lifecycle: cancellation must own every proxy launch

Finding state: `delivery-gate-ready`

Workstream: `G`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-make-mirror-signal-lifecycle/finding.md`  
Canonical implementation: `teamleaderleo/linux-fieldwork#224`  
Exact implementation head: `13b3c529e983b3ad967725f99f4e31d867fa4742`  
Exact base or source revision: Linux Fieldwork main `ed49c01a85e9d363626db5d2973a33b67209e13b`; imported `make_mirror.sh` blob `6c4be092edcf23b56b63a3befe238c099c45f590`  
Strongest evidence class: `target-executed` locally; exact-head hosted gate pending  
Reviewed input generation: Fieldwork #254 body as updated 2026-07-30; Linux issues #157 and #221; PR #224 complete five-file diff  
Current review disposition: `EXECUTE`  
Desk routing: `Delivery Desk #160 D2`  
Upstream contact authorized: `no`

## In simple words

`make_mirror.sh` builds a Debian package mirror and starts two cache-proxy helpers at different stages. A stop signal should make the owner stop, report the first cancellation reason, clean only resources it actually owns, and wait for the correct helper process.

The imported script had cleanup-only signal traps that could return to normal work. The first internal repair fixed termination, child waiting, and published-cache preservation. Review then found a smaller launch interval: a proxy could exist before `$!` was stored. Another review found that the test gave the first launch cache-deletion authority too early. A final review found that a later signal could overtake the first signal during trap handoff.

PR #224 at `13b3c529…` combines all three repairs and the corresponding controls. It is the canonical carrier. PR #226 was a temporary duplicate created from an older #224 head and is closed without merge after its useful review shape was absorbed.

## Why we care

A leaked proxy can retain port 8080 and interfere with an immediate rerun. A cleanup-only trap can make a cancelled mirror build continue and report the wrong result. Deleting a cache before ownership begins can hide retained state. Letting a later signal replace the first makes cancellation reporting depend on a tiny timing interval.

The observed failures are bounded process, status, and state-ownership defects. Real-world frequency is unknown because the proof uses reduced local shell harnesses rather than a complete mirror build.

## What happens if we leave it alone

Three failure layers remain without the combined candidate:

1. Parent-only TERM can run cleanup and then resume later commands, eventually returning success or an unrelated failure.
2. A signal between proxy creation and PID registration can leave cleanup with no owned child PID.
3. Restoring ordinary terminating traps before dispatching a recorded signal can let a later signal replace the first cancellation status.

A test can also provide false confidence when it models both proxy launches with identical cache-cleanup authority. Before first readiness, the script owns the child but not private-cache deletion. During the later QEMU launch, it owns both.

## Current finding

The top-level mirror owner needs one explicit lifecycle:

- ordinary EXIT cleanup is separate from signal termination;
- `stop_proxy()` signals, waits for, and clears an owned PID;
- `cleanup_owner()` cleans once and deletes only state currently owned;
- a cache already published through `shared/cache` survives late cleanup;
- every asynchronous proxy launch keeps a temporary first-signal handler active until the PID is stored;
- a pending first signal is dispatched before ordinary terminating traps are restored;
- a later signal cannot overtake the retained first signal;
- launch-one retained state is handled by the next run's actual startup preflight.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Cleanup-only TERM traps can resume later work and return 0. | `target-executed` | `tests/test_make_mirror_signal_exit.py` baseline; issue #157 | Reduced `/bin/sh` harness |
| The parent repair exits 143, omits later work, waits for the proxy, cleans once, and preserves an active published cache. | `target-executed` | merged PR #205; CI `30579821292`; carrier `30579465025` | Signal after ordinary PID registration |
| Both top-level proxy launches have a child-creation/PID-registration interval. | `source-read` plus executed seam | issue #221; PR #224 source ordering and stopped-owner controls | Top-level proxy launches only |
| Launch one owns child cleanup but not cache deletion before readiness. | `target-executed` locally | `tests/test_make_mirror_proxy_launch_ownership.py`; source-order controls | Simulated retained cache represents actual startup-preflight contract |
| Launch two owns child cleanup and private-cache deletion. | `target-executed` locally | same ownership regression | Reduced QEMU relaunch harness |
| TERM recorded before PID assignment remains authoritative when INT arrives afterward. | `target-executed` locally | `test_first_recorded_signal_wins_during_registration_dispatch` | Two-signal control; not an arbitrary signal storm |
| The exact combined five-file head passes hosted repository CI. | `target-test-prepared` | run `30586490855` | Pending at this revision of the finding |

## System and ownership map

- Entrypoint: imported `upstream/mmdebstrap/make_mirror.sh`.
- Process owner: the top-level shell owns two sequential caching-proxy children.
- Filesystem owner: before first readiness it does not yet own failed-cache deletion; after readiness it owns the private new cache; after publication the active symlink protects the completed cache.
- QEMU state: temporary cleanup is owned only while the QEMU phase is active.
- Result owner: handled INT, QUIT, and TERM map to 130, 131, and 143 after cleanup.
- Recovery: an interrupted pre-readiness cache is retained and the next run's preflight removes the inactive sibling cache before continuing.
- Test boundary: exact patch application to the pinned source with disposable real `/bin/sh` processes, files, symlinks, and stop/continue signal controls.

## Historical precedent

### Composed gpgv wrapper lifecycle

- Source: https://github.com/teamleaderleo/linux-fieldwork/pull/196
- Revision or date: merged 2026-07-30
- Principle supported: temporary signal-recording traps can close child-launch/PID-registration intervals before normal forwarding or termination resumes.
- Important difference: the gpgv wrapper owns verifier/filter children and status bytes; `make_mirror.sh` also owns cache publication and a second proxy launch.

### Signal traps must terminate after cleanup

- Source: https://github.com/teamleaderleo/linux-fieldwork/blob/ed49c01a85e9d363626db5d2973a33b67209e13b/notes/processes/signal-traps-must-terminate-after-cleanup.md
- Revision or date: current Linux Fieldwork main reviewed 2026-07-30
- Principle supported: cleanup-only traps resume work; child termination requires waiting; PID registration and resource ownership are separate boundaries.
- Important difference: PR #224 adds exact first-signal and launch-specific cache-ownership controls.

### First-event retention

- Source: https://github.com/teamleaderleo/linux-fieldwork/blob/ed49c01a85e9d363626db5d2973a33b67209e13b/FIELD_GUIDE.md
- Revision or date: blob `d1793c43d81b209a363744cf629807910b6b62da`
- Principle supported: preserve the first meaningful failure or signal instead of letting a later event decide the result.
- Important difference: the field guide is general; this finding applies it inside one shell launch handoff.

## Approaches considered

### Retained: first-signal handler through PID registration

The launch handler records only the first signal while the PID is empty. Once the PID exists, the handler or the normal launch path dispatches that retained status before restoring ordinary traps. Cleanup therefore has an owned child and a later signal cannot overtake the first.

### Declined: restore ordinary traps before pending dispatch

That ordering closed the one-signal orphan interval but retained a smaller race in which a second signal could replace the first.

### Declined: identical cache ownership for both launches

The source does not own cache deletion before first readiness. A harness that sets ownership to `yes` at both launches proves the wrong lifecycle and can hide retained-state behavior.

### Deferred: signal masking or language rewrite

Portable `/bin/sh` has no direct signal-mask mechanism. Moving launch ownership to another language would enlarge the candidate beyond the demonstrated repair.

### Deferred: TERM-to-KILL escalation

A proxy that ignores TERM can make `wait` block. Timeout and escalation policy require a separate design choice.

### Deferred: `update_cache()` subshell trap

That trap runs in a different pipeline/subshell ownership topology and remains a separate investigation target.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Baseline parent-only TERM | combined regression | Later work occurs; cleanup runs twice; result can be 0 |
| Candidate parent-only TERM after readiness | combined regression | Status 143; no later marker; proxy gone; one owner cleanup |
| Unsignaled rerun | combined regression | Status 0; later marker present; proxy reaped |
| First proxy registration window | two focused regressions | Status 143; one proxy stop; zero signal-time cache deletion; retained state handled by rerun preflight |
| Second proxy registration window | two focused regressions | Status 143; completed first proxy plus signaled second proxy stopped; private cache deleted once |
| TERM then INT across registration | combined regression | Status remains 143; first signal wins |
| Published cache followed by cleanup | combined regression | Published directory remains and private ownership flag clears |
| Exact patch application and `/bin/sh -n` | both suites | Passed locally at exact combined tree |
| Two consecutive focused-suite runs | PR #224 receipt | 10/10 passed twice locally |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Proxy ignores TERM | Requires escalation policy | New design finding with timeout/grace-period options |
| Full mirror, APT, QEMU, and network execution | Reduced harness proves mechanism | Integration gate before any external packet when justified |
| `update_cache()` subshell trap | Different process owner | New issue after exact process map and distinguishing reproducer |
| Process-group delivery | Current controls signal only the owner PID | Reopen if group behavior produces a different result |
| Signal storm beyond two distinct signals | Two signals prove the overtaking class | Expand on evidence of another reachable state |
| Cleanup failure observability | Candidate preserves primary cancellation status | Separate retained-state/reporting decision |
| Current public upstream source | Pinned imported source only | Refresh before upstream preparation |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `linux-fieldwork@ac2680e0dc92b497f6ada5622b50e7f41ebb56af` | CI `30579821292` | GitHub-hosted Ubuntu | Parent repair passed | `target-executed` |
| carrier `#201@da0974a81419d6dc27cb89173bed821ced0e5c53` | run `30579465025`, four-test matrix twice | Ubuntu 24.04 | 8/8 parent-repair executions passed | `target-executed` |
| `linux-fieldwork#224@13b3c529e983b3ad967725f99f4e31d867fa4742` | both focused suites twice | local Linux record in PR | 10/10 passed twice; patch dry-run, shell syntax, and diff check passed | `target-executed` locally |
| same exact head | Linux Fieldwork CI `30586490855` | GitHub-hosted Ubuntu | queued/pending | `target-test-prepared` |

The earlier #224 head `dc9222d8…` received two valid `REPAIR` reviews: first-signal trap handoff and launch-one cache-ownership fidelity. The current head addresses both. Closed PR #226 is a superseded duplicate and is not part of the canonical stack.

## Complete-diff and compatibility review

- Complete five-file fence: retained patch, combined investigation README, reusable process note, combined regression, independent ownership regression.
- Base relationship: direct from Linux Fieldwork main `ed49c01a85e9d363626db5d2973a33b67209e13b`; GitHub reports mergeable.
- Temporary carrier status: #226 closed without merge after evidence reconciliation; #224 is the sole canonical carrier.
- Compatibility surfaces examined: status, first-signal identity, child PID ownership, child reaping, owner-cleanup count, state-specific cache deletion, retained-state preflight, published-cache preservation, unsignaled rerun, patch application, shell syntax.
- Known routine repair remaining: none found in the complete current diff; hosted exact-head execution remains.
- Reviewer eligibility: the user designated agent review as the operative last-mile review. No separate reviewer is a hard gate.
- Exact-head disposition: `EXECUTE` until run `30586490855` completes without head movement.

## Current disposition and desk routing

- Finding state: `delivery-gate-ready`
- Review disposition: `EXECUTE`
- Review Queue entry: none until the hosted result is classified
- Delivery lane: `D2`
- Exact next transition: if exact-head CI passes the intended tests, set this finding and PR #224 to `review-ready` / `ACCEPT` and mark #224 ready for review.
- Clearing condition: successful Linux Fieldwork CI `30586490855` on exact head `13b3c529e983b3ad967725f99f4e31d867fa4742` plus final no-head-movement check.
- Required subgates: intended jobs executed; both focused regressions passed; complete five-file diff unchanged; cleanup/rerun receipt retained.
- User decision requested: none while the exact-head gate runs.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-30 | PR #205 | Merged internal parent-repair evidence for termination, proxy waiting, and published-cache preservation |
| 2026-07-30 | issue #221 / early PR #224 | Added deterministic controls for both launch/PID-registration intervals |
| 2026-07-30 | reviews on `dc9222d8…` | Found first-signal handoff race and launch-one ownership overclaim |
| 2026-07-30 | PR #224 head `13b3c529…` | Combined first-signal, ownership-state, retained-preflight, and existing parent repair into one five-file carrier |
| 2026-07-30 | PR #226 | Closed as a superseded duplicate after useful review shape transferred to #224 |
| 2026-07-30 | This finding PR | Records #224 as canonical and routes only its exact hosted gate |

## References

- https://github.com/teamleaderleo/linux-fieldwork/issues/157
- https://github.com/teamleaderleo/linux-fieldwork/issues/221
- https://github.com/teamleaderleo/linux-fieldwork/pull/205
- https://github.com/teamleaderleo/linux-fieldwork/pull/224
- https://github.com/teamleaderleo/linux-fieldwork/pull/226
- https://github.com/teamleaderleo/linux-fieldwork/pull/196
- https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30586490855
- https://github.com/teamleaderleo/linux-fieldwork/blob/13b3c529e983b3ad967725f99f4e31d867fa4742/investigations/make-mirror-signal-exit/README.md
- https://github.com/teamleaderleo/linux-fieldwork/blob/13b3c529e983b3ad967725f99f4e31d867fa4742/tests/test_make_mirror_signal_exit.py
- https://github.com/teamleaderleo/linux-fieldwork/blob/13b3c529e983b3ad967725f99f4e31d867fa4742/tests/test_make_mirror_proxy_launch_ownership.py
- https://github.com/teamleaderleo/fieldwork/issues/254
