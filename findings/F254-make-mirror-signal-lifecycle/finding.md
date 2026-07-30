# F254-make-mirror-signal-lifecycle: cancellation must own every proxy launch

Finding state: `delivery-gate-ready`

Workstream: `G`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-make-mirror-signal-lifecycle/finding.md`  
Canonical implementation: `teamleaderleo/linux-fieldwork#226`  
Exact implementation head: `3f7c20ca2e97c59930ee3337420277999fc2ca61`  
Exact base or source revision: Linux Fieldwork main `ed49c01a85e9d363626db5d2973a33b67209e13b`; imported `make_mirror.sh` blob `6c4be092edcf23b56b63a3befe238c099c45f590`  
Strongest evidence class: `target-test-prepared` at #226 exact head; predecessor mechanism is `target-executed`  
Reviewed input generation: Fieldwork #254 body as updated 2026-07-30; Linux issues #157 and #221; PR #224 head `dc9222d8d03e51da60b993010c845ec41ea83e61`  
Current review disposition: `EXECUTE`  
Desk routing: `Delivery Desk #160 D2`  
Upstream contact authorized: `no`

## In simple words

`make_mirror.sh` builds a Debian package mirror and starts cache-proxy helper processes while it works. A stop signal should make the script stop, clean up once, wait for its helpers, and report cancellation.

The first retained repair fixed cleanup-only traps that could resume work and return the wrong result. Post-merge review then found that a signal could arrive after a proxy was created but before its PID was stored. PR #224 closed that launch gap for one signal. Complete-diff review found one last timing problem: a later signal could replace the first signal after PID registration but before dispatch.

PR #226 is the canonical repair. It retains the first signal until the proxy PID is owned, then cleans the correct child and exits for that first signal. The exact-head hosted gate is the only routine gate still running.

## Why we care

A mirror build is long-running and mutates package/cache state. Cancellation that resumes work, reports the wrong status, deletes a published cache, or leaves a proxy listener alive is operationally misleading and can interfere with an immediate rerun.

Observed consequences in reduced real-shell controls include false status 0, later work after TERM, duplicate cleanup, and a child-launch interval with no owned proxy PID. The final competing-signal control is prepared to distinguish first-signal retention. Real deployment frequency is unknown.

## What happens if we leave it alone

There are three bounded failure layers:

1. The imported cleanup-only TERM trap kills or cleans resources and then returns, allowing the script to continue.
2. The first repair owns a proxy only after `PROXYPID=$!`; a signal between child creation and PID assignment can clean the owner while missing the child.
3. PR #224 records a signal during launch, but restores ordinary terminating traps before dispatching the recorded status. A later signal in that interval can replace the first cancellation reason.

Leaving the final layer unresolved makes status depend on timing even when cleanup succeeds.

## Current finding

The mirror owner needs one explicit cancellation lifecycle:

- ordinary EXIT cleanup remains separate from signal termination;
- proxy shutdown signals and waits for the child and clears the PID;
- cleanup runs once and preserves a cache already published through the active symlink;
- every top-level proxy launch temporarily retains the first signal while PID ownership is incomplete;
- after PID registration, a pending first signal is dispatched before ordinary terminating traps are restored;
- a later signal cannot overtake the retained first status.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| The imported cleanup-only traps can resume later work and return success after parent-only TERM. | `target-executed` | Linux issue #157; `tests/test_make_mirror_signal_exit.py` baseline | Reduced `/bin/sh` harness, not a full mirror run |
| The merged #205 candidate exits 143, cleans once, waits for the proxy, omits later work, preserves published cache, and supports a clean rerun. | `target-executed` | PR #205 head `ac2680e…`; CI `30579821292`; carrier `30579465025` | Signal after normal PID registration; no launch-window control |
| Both top-level proxy launches have a child-creation/PID-registration interval. | `source-read` | Issue #221 and exact retained patch/source ordering | Static ordering plus deterministic test seam |
| PR #224 closes the one-signal launch window for both launches. | `target-executed` locally; hosted gate pending | PR #224 head `dc9222d…`; six-test local matrix recorded on #221 | First-signal competition was not covered |
| PR #224 can let a later INT overtake an earlier recorded TERM. | `model-executed` / `target-test-prepared` | PR #226 negative-control reconstruction in `tests/test_make_mirror_signal_first_signal.py` | Hosted exact-head execution pending |
| PR #226 preserves the first TERM through PID registration and later INT delivery. | `target-test-prepared` | PR #226 exact patch and competing-signal regression | Becomes `target-executed` only after intended hosted test runs |

## System and ownership map

- Entrypoint: imported `upstream/mmdebstrap/make_mirror.sh`.
- State owner: the shell owner controls two sequential caching-proxy children, a private/new cache, optional QEMU temporary state, and final status.
- Control flow: launch first proxy, update mirror/cache, stop proxy, optionally launch a read-only proxy for QEMU work, stop proxy, publish cache symlink.
- Side effects: child processes/listeners, package cache directories, symlinks, QEMU temporary files, and final exit status.
- Cleanup: `stop_proxy()` signals, waits, and clears PID; `cleanup_owner()` removes only state still privately owned; `signal_exit()` disables traps, cleans once, and exits with a conventional signal-derived status.
- Launch recovery: temporary handlers retain the first INT/QUIT/TERM until a new child PID is owned.
- Contract: cancellation must terminate the owner, preserve its first cause, avoid later work, reap children, clean once, and not delete an already published cache.
- Test boundary: exact retained patch applied to imported source plus reduced real `/bin/sh` lifecycle harnesses.

## Historical precedent

### Composed gpgv wrapper lifecycle

- Source: https://github.com/teamleaderleo/linux-fieldwork/pull/196
- Revision or date: merged 2026-07-30 as `65d4213393cf2b2d84c71a8b6a05fdad15396b9b`
- Principle supported: a wrapper launching a child must close the child-launch/PID-registration signal interval with temporary recording traps and explicit ownership.
- Important difference: the gpgv wrapper owns verifier/filter children and buffered status bytes; this finding owns shell cache proxies, cache publication, and relaunch after a cleared PID.

### Signal traps must terminate after cleanup

- Source: https://github.com/teamleaderleo/linux-fieldwork/blob/ed49c01a85e9d363626db5d2973a33b67209e13b/notes/processes/signal-traps-must-terminate-after-cleanup.md
- Revision or date: Linux Fieldwork current main on 2026-07-30
- Principle supported: cleanup-only traps can resume work; killing is not reaping; parent-only and process-group delivery differ.
- Important difference: the reusable note predates the exact competing-signal repair now proposed by #226.

### First-event retention in Fieldwork classifiers

- Source: https://github.com/teamleaderleo/linux-fieldwork/blob/ed49c01a85e9d363626db5d2973a33b67209e13b/FIELD_GUIDE.md
- Revision or date: `d1793c43d81b209a363744cf629807910b6b62da`
- Principle supported: preserve the first meaningful failure or signal rather than choosing a later event by timing or fixed precedence.
- Important difference: the field-guide rule is general; #226 applies it inside one shell launch seam.

## Approaches considered

### Retained approach: temporary first-signal handler through PID ownership

The launch handler records the first signal while the PID is empty. Once PID ownership exists, it immediately dispatches the retained first status. Pending dispatch occurs before ordinary terminating traps are restored, so a later signal cannot overtake it.

This preserves the existing cleanup path and avoids introducing a second child-shutdown implementation.

### Declined: restore ordinary traps before pending dispatch

That is PR #224's ordering. It closes the orphan interval for a single signal but leaves a smaller competing-signal race where a later signal can replace the first.

### Declined: block signals around launch

Shell-portable signal-mask control is not available in the `/bin/sh` implementation. External helpers or a language rewrite would substantially broaden the candidate.

### Deferred: force-kill escalation

A proxy that ignores TERM can leave `wait` blocked. Timeout and SIGKILL policy changes grace periods and failure semantics and belongs to a separate design decision.

### Deferred: subshell-local `update_cache()` trap

That trap has a different process and pipeline ownership topology. It remains outside the top-level proxy lifecycle unless a concrete reproducer shows an overlapping repair.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Baseline TERM while owner waits | `test_make_mirror_signal_exit.py` | Cleanup occurs but owner resumes and may return 0 |
| Candidate TERM after proxy readiness | Same focused matrix | Status 143, cleanup once, no later work, proxy reaped |
| Unsignaled rerun | Same matrix | Status 0, normal later marker, proxy reaped |
| Signal before first proxy PID registration | #224 stopped-owner control | Local 6/6 record says status 143, one cleanup, child gone |
| Signal before QEMU proxy PID registration | #224 second-launch control | Local record covers relaunch after first PID is cleared |
| Published cache followed by cleanup | #205/#224 cache control | Active cache preserved and private ownership flag cleared |
| TERM then INT around PID registration | PR #226 negative control | Predecessor expected 130; candidate expected 143 |
| Exact patch application and shell syntax | #226 test setup | Prepared; hosted result pending |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Proxy ignores TERM | Requires escalation policy | New design finding with bounded timeout choice |
| Full multi-hour mirror and QEMU run | Reduced harness proves mechanism only | Integration gate before an external packet when justified |
| `update_cache()` subshell trap | Separate process/pipeline owner | New issue after exact process map and reproducer |
| Process-group delivery | Current tests deliver to owner PID | New finding if group behavior differs materially |
| More than two rapid signals | First two distinguish the overtaking mechanism | Expand only if retained handler shows another reachable state |
| Cleanup failure after cancellation | Existing candidate contains cleanup errors to protect status | Separate retained-state/observability decision |
| Current public mmdebstrap source | Work uses pinned imported blob | Refresh before upstream preparation |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `linux-fieldwork@ac2680e0dc92b497f6ada5622b50e7f41ebb56af` | Linux Fieldwork CI `30579821292` | GitHub-hosted Ubuntu | Passed exact-head #205 gate | `target-executed` |
| carrier `#201@da0974a81419d6dc27cb89173bed821ced0e5c53` | run `30579465025`, make_mirror four-test matrix twice | Ubuntu 24.04 | 8/8 make_mirror test executions passed; imported source unchanged | `target-executed` |
| `linux-fieldwork#224@dc9222d8d03e51da60b993010c845ec41ea83e61` | focused six-test suite locally three times; hosted run `30585323130` | Local Linux plus queued GitHub Actions | Local mechanism green; hosted exact-head receipt not yet final | `target-executed` locally |
| `linux-fieldwork#226@3f7c20ca2e97c59930ee3337420277999fc2ca61` | Linux Fieldwork CI `30586175997` | GitHub-hosted Ubuntu | Queued; intended assertion not yet classified | `target-test-prepared` |

Harness/setup distinctions: #224's earlier local full discovery recorded three ambient failures reproduced unchanged on pristine current main; those are not product failures for this candidate. #226 must still prove that its exact patch applies and its new competing-signal test actually executes in hosted CI.

## Complete-diff and compatibility review

- Canonical changed-file fence at #226: combined retained patch and investigation material from #224 plus first-signal review records, reusable note, and exact competing-signal regression.
- Base relationship: #226 is based on Linux Fieldwork main `ed49c01a85e9d363626db5d2973a33b67209e13b`.
- Temporary/superseded carrier status: #224 remains open while its hosted run finishes, but its review disposition is `REPAIR`; #226 is the canonical successor for first-signal correctness.
- Compatibility surfaces examined: status 130/131/143, first-signal identity, one cleanup, child PID registration, child reaping, later-work absence, immediate rerun, published-cache preservation, shell syntax, exact patch application.
- Known routine repair remaining: none identified after the #226 ordering repair; exact-head hosted execution remains.
- Reviewer eligibility: the user designated agent review as the operative last-mile review. A separate reviewer is not a hard gate.
- Exact-head disposition: `EXECUTE`; promote after intended hosted assertions pass and the final exact diff remains unchanged.

## Current disposition and desk routing

- Finding state: `delivery-gate-ready`
- Review disposition: `EXECUTE`
- Review Queue entry: none until execution result
- Delivery lane: `D2`
- Exact next transition: classify Linux Fieldwork CI `30586175997`; if the exact patch and competing-signal regression pass, update this finding and #226 to `review-ready`/`ACCEPT` and mark the PR ready for review.
- Clearing condition: successful exact-head hosted execution of the intended first-signal assertion with no head movement.
- Required subgates: patch application, shell syntax, competing-signal negative control, cleanup/child assertions, complete-diff recheck.
- User decision requested: none while the gate runs.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-30 | Linux Fieldwork PR #205 | Accepted and merged cleanup/status/published-cache repair |
| 2026-07-30 | Linux issue #221 / PR #224 | Added both proxy launch/PID-registration controls |
| 2026-07-30 | PR #224 review `4823593228` | Found later-signal overtaking interval; disposition `REPAIR` |
| 2026-07-30 | Linux Fieldwork PR #226 | Prepared first-signal-retention repair and exact negative control |
| 2026-07-30 | This finding PR | Reconciles the full lifecycle and routes the remaining hosted gate |

## References

- https://github.com/teamleaderleo/linux-fieldwork/issues/157
- https://github.com/teamleaderleo/linux-fieldwork/issues/221
- https://github.com/teamleaderleo/linux-fieldwork/pull/205
- https://github.com/teamleaderleo/linux-fieldwork/pull/224
- https://github.com/teamleaderleo/linux-fieldwork/pull/226
- https://github.com/teamleaderleo/linux-fieldwork/pull/196
- https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30586175997
- https://github.com/teamleaderleo/linux-fieldwork/blob/ed49c01a85e9d363626db5d2973a33b67209e13b/investigations/make-mirror-signal-exit/README.md
- https://github.com/teamleaderleo/fieldwork/issues/254
