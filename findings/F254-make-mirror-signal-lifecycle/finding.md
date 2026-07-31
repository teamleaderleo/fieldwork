# F254-make-mirror-signal-lifecycle: cancellation must own every proxy launch

Finding state: `closed`

Workstream: `G`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-make-mirror-signal-lifecycle/finding.md`  
Canonical implementation: merged `teamleaderleo/linux-fieldwork#224`  
Exact implementation head: `13b3c529e983b3ad967725f99f4e31d867fa4742`  
Merge commit: `386f5c8dbb01e5de1af45ac0eb325ee8567722e3`  
Exact base or source revision: Linux Fieldwork `ed49c01a85e9d363626db5d2973a33b67209e13b`; imported `make_mirror.sh` blob `6c4be092edcf23b56b63a3befe238c099c45f590`  
Strongest evidence class: lifecycle claims `target-executed`; named Linux Fieldwork CI gate `full-gate` within the repository paths described below  
Reviewed input generation: Fieldwork #254 current protocol; Linux issues #157/#221; PR #224 complete five-file diff; reviews `4823593228`, `4823717630`  
Current review disposition: `ACCEPT`  
Desk routing: durable closeout; no active delivery lane  
Upstream contact authorized: `no`

## In simple words

`make_mirror.sh` starts two caching-proxy helpers while building a Debian mirror. Cancellation must stop the correct helper, preserve the first stop reason, clean only state currently owned, and avoid damaging a cache that has already been published.

The original internal candidate fixed cleanup-only traps but still had a window between child creation and PID registration. Review also found two proof defects: the first launch was granted cache-deletion authority too early, and a later signal could overtake the first signal during trap handoff.

PR #224 combined the parent repair, both launch-window repairs, first-signal retention, launch-specific cleanup authority, published-cache preservation, and exact regression controls. The exact head passed Linux Fieldwork CI and was merged into the internal evidence repository as `386f5c8d…`. No public upstream interaction occurred.

## Why we care

Without an explicit owner lifecycle, cancellation can report success, leak a proxy, kill or wait for the wrong PID, delete state before ownership begins, damage a published cache, or report a later signal instead of the first cancellation request. Those are correctness and recovery defects even when the full mirror workload is not executed.

Observed frequency remains unknown. The retained proof uses reduced real-shell process and filesystem controls rather than a complete networked mirror build.

## What happens if we leave it alone

The original top-level source used the same cleanup-only traps for normal exit and signals and launched each proxy in separate child-creation and `$!` assignment commands. A signal could therefore:

1. run cleanup and return to later work;
2. arrive after child creation but before PID ownership;
3. let a second signal replace the first during trap restoration;
4. invoke cache deletion at a lifecycle point that did not own it;
5. leave an owned child unreaped or act on a stale PID.

The merged internal candidate closes those bounded paths.

## Current finding

The top-level mirror process must remain the sole owner of proxy launch, PID registration, stopping, waiting, and cache/QEMU cleanup state.

The accepted contract is:

- ordinary EXIT cleanup is separate from signal termination;
- `stop_proxy()` signals a live owned child, waits even if it already exited, and clears the PID;
- `cleanup_owner()` is one idempotent owner cleanup;
- private-cache deletion is enabled only after first readiness and disabled after publication;
- a published cache survives late cleanup;
- each asynchronous launch keeps a first-signal handler active until the new PID is stored;
- pending cancellation is dispatched before ordinary terminating traps are restored;
- the first signal remains authoritative;
- an interrupted pre-readiness cache is handled by the next startup preflight.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Cleanup-only parent TERM can resume later work and return 0. | `target-executed` | baseline in `tests/test_make_mirror_signal_exit.py` | Reduced `/bin/sh` harness |
| The candidate exits 143, omits later work, cleans once, stops and waits for the proxy, and preserves a published cache. | `target-executed` | merged PR #205 and PR #224 regressions | Pinned imported source, no real mirror |
| Both proxy launches close child-creation/PID-registration windows. | `target-executed` | stopped-owner controls in PR #224 | Top-level launches only |
| Launch one does not own cache deletion; launch two does. | `target-executed` | `tests/test_make_mirror_proxy_launch_ownership.py` | Reduced cache-state model |
| TERM before registration remains authoritative over later INT. | `target-executed` | first-signal competing control | Two-signal case, not arbitrary storms |
| The exact five-file head passed the repository-declared Linux Fieldwork CI gate. | `full-gate` | run `30586490855` | Gate ran compile, unit tests, shell syntax, and help; no APT/QEMU/network mirror integration |
| The accepted exact head is retained on current main. | `source-read` | merge commit `386f5c8d…` | Internal evidence repository only |

## System and ownership map

- Entrypoint: imported `upstream/mmdebstrap/make_mirror.sh`.
- Process owner: top-level shell owns two sequential caching-proxy children.
- Result owner: handled INT/QUIT/TERM map to 130/131/143 after owner cleanup.
- Filesystem owner: private cache only after first readiness; published cache protected by `shared/cache`; QEMU temporary state only while active.
- Recovery: pre-readiness partial state is retained for the next run's existing preflight; published state remains.
- Separate boundary: `update_cache()` is a pipeline subshell and is owned by finding `F254-make-mirror-update-cache-subshell`.

## Historical precedent

### Composed gpgv wrapper lifecycle

- Source: https://github.com/teamleaderleo/linux-fieldwork/pull/196
- Revision or date: merged 2026-07-30
- Principle supported: temporary signal-recording handlers can close child-launch/PID-registration windows before normal handlers resume.
- Important difference: `make_mirror.sh` owns cache publication and two proxy lifecycles.

### Parent signal cleanup repair

- Source: https://github.com/teamleaderleo/linux-fieldwork/pull/205
- Revision or date: merged 2026-07-30
- Principle supported: signal handlers must terminate after cleanup and owned children must be waited for.
- Important difference: the later #224 work adds launch registration, first-signal, and state-ownership controls.

## Approaches considered

### Retained: first-signal handler through PID registration

This gives cleanup an owned PID before dispatch and prevents a later signal from overtaking the first.

### Declined: restore ordinary traps before pending dispatch

That ordering closes the orphan window but lets a second signal replace the retained first signal.

### Declined: identical cache ownership for both launches

The first launch occurs before private-cache deletion authority begins. Treating both launches alike proves a lifecycle the source does not have.

### Deferred: process groups, escalation, and full mirror timing

Those change cancellation policy or require expensive integration execution and remain separate findings.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Baseline parent-only TERM | combined regression | Later work and false success reproduced |
| Candidate parent-only TERM | combined regression | Status 143, one cleanup, proxy gone |
| First launch registration | ownership controls | Child reaped; no premature cache deletion |
| Second launch registration | ownership controls | Child reaped; private cache deletion once |
| TERM then INT | competing-signal control | First TERM remains status 143 |
| Published-cache cleanup | focused control | Published directory preserved |
| Immediate rerun | focused controls | Status 0 and no surviving proxy |
| Patch and shell syntax | exact candidate tests | Passed |
| Named repository CI | run `30586490855` | Passed on unchanged exact head |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning record or trigger |
| --- | --- | --- |
| `update_cache()` subshell ownership | Different process owner and result path | `F254-make-mirror-update-cache-subshell`, Linux #231 |
| Proxy ignores TERM | Requires timeout/escalation policy | Reopen as separate design finding |
| Full APT/QEMU/network mirror execution | High-cost integration gate | Before any authorized external packet if justified |
| Process-group delivery | Different caller topology | Reopen on contradictory group behavior |
| Current public source | Imported source is pinned | Refresh before external preparation |

## Exact execution and receipts

| Repository/head | Command or workflow | Result | Evidence class |
| --- | --- | --- | --- |
| `linux-fieldwork@ac2680e0dc92b497f6ada5622b50e7f41ebb56af` | CI `30579821292` | Parent repair passed | `target-executed` |
| carrier `#201@da0974a81419d6dc27cb89173bed821ced0e5c53` | four-test matrix twice | 8/8 executions passed | `target-executed` |
| `linux-fieldwork#224@13b3c529e983b3ad967725f99f4e31d867fa4742` | both focused suites twice | 10/10 passed twice locally | `target-executed` |
| same head | Linux Fieldwork CI `30586490855` | passed | `full-gate` within named limits |
| merged main | commit `386f5c8dbb01e5de1af45ac0eb325ee8567722e3` | exact candidate retained | `source-read` |

## Complete-diff and compatibility review

- Complete fence: retained patch, investigation README, reusable process note, combined regression, ownership regression.
- Final source head: `13b3c529…`; merge commit: `386f5c8d…`.
- Supersession: duplicate PR #226 closed without merge; historical PRs #159/#205 retain development history; #224 is the accepted combined unit.
- Compatibility surfaces reviewed: status, first-signal identity, PID ownership, reaping, cleanup count, private/published cache authority, QEMU state, rerun, patch application, shell syntax.
- Exact-head review found no remaining source-visible blocker; exact CI passed before merge.

## Current disposition and desk routing

- Finding state: `closed`
- Review disposition: `ACCEPT`
- Review Queue entry: no active entry; review is retained in the exact PR history
- Delivery lane: closed after internal merge
- Exact next transition: none
- Clearing condition: already satisfied by exact-head review, CI `30586490855`, and merge commit `386f5c8d…`
- Required subgates: none
- User decision requested: none

## Changes to the canonical conclusion

| Date | Record | Change in conclusion |
| --- | --- | --- |
| 2026-07-30 | PR #205 | Parent termination, waiting, and published-cache evidence retained |
| 2026-07-30 | early PR #224 reviews | Found launch ownership, cache-state fidelity, and first-signal handoff defects |
| 2026-07-30 | PR #224 `13b3c529…` | Combined and repaired all top-level proxy lifecycle controls |
| 2026-07-31 | CI `30586490855` and merge `386f5c8d…` | Exact gate passed and accepted internal evidence was merged; state changed to `closed` |

## References

- https://github.com/teamleaderleo/linux-fieldwork/issues/157
- https://github.com/teamleaderleo/linux-fieldwork/issues/221
- https://github.com/teamleaderleo/linux-fieldwork/pull/205
- https://github.com/teamleaderleo/linux-fieldwork/pull/224
- https://github.com/teamleaderleo/linux-fieldwork/pull/226
- https://github.com/teamleaderleo/linux-fieldwork/pull/196
- https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30586490855
- https://github.com/teamleaderleo/linux-fieldwork/commit/386f5c8dbb01e5de1af45ac0eb325ee8567722e3
- https://github.com/teamleaderleo/fieldwork/issues/254
