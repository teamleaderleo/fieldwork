# F254-mmdebstrap-coverage-parent-sigint: cancellation must not report success

Finding state: `review-ready`

Workstream: `G`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-mmdebstrap-coverage-parent-sigint/finding.md`  
Canonical implementation: `teamleaderleo/linux-fieldwork#204` — merged internal evidence unit  
Exact implementation head: `b5efc8faf35c1da725a3b995a344fadc078ad5d2`  
Exact base or source revision: imported `coverage.py` blob `9a522484aef05deae514a98e4b6adf5feb6c886d`  
Strongest evidence class: `target-executed`  
Reviewed input generation: Fieldwork #254 body as updated 2026-07-30; Linux issue #141 narrow contract  
Current review disposition: `ACCEPT`  
Desk routing: `Review Queue #213`  
Upstream contact authorized: `no`

## In simple words

`coverage.py` runs many mmdebstrap tests and reports whether the run succeeded. When its parent process received Ctrl-C, it stopped and reaped the current child, skipped the remaining tests, and then returned success because no ordinary test failure had been recorded.

The retained candidate keeps the existing child cleanup but exits 130 with a focused interruption message. The internal evidence unit is accepted for this narrow behavior. It has not been sent to mmdebstrap or Debian.

## Why we care

A cancelled test matrix must not look complete and green. CI, scripts, or a person can otherwise trust a result that covers only the tests that happened to run before interruption.

The concrete observed consequence is false status 0 after parent-only SIGINT. Frequency in real CI is unknown.

## What happens if we leave it alone

A caller can interrupt the coverage driver after a child starts. The driver terminates and waits for that child, exits the test loop, and reaches the normal success epilogue. Remaining tests do not run, yet the caller receives status 0.

This finding does not claim that ordinary mmdebstrap package execution is wrong. It owns the test-driver cancellation contract.

## Current finding

After handling parent-only SIGINT, the coverage driver must not fall through to normal success. Exiting 130 after child cleanup preserves the conventional shell-visible cancellation result without an unhandled Python traceback.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| The imported driver can skip the rest of the matrix and return 0 after parent-only SIGINT. | `target-executed` | `linux-fieldwork/tests/test_mmdebstrap_coverage_parent_sigint.py`; issue #141 negative control | One imported revision and a reduced disposable suite |
| The candidate returns 130, logs the interruption, terminates and reaps the child, and leaves no success marker. | `target-executed` | PR #204 head `b5efc8f…`; CI run `30579733315`; execution carrier run `30579465025` | Parent-only SIGINT after the child has started |
| An immediate unsignaled candidate rerun still succeeds. | `target-executed` | Same focused matrix and carrier rerun | Not the complete Debian mirror or QEMU matrix |
| The retained files remain unchanged on current Linux Fieldwork main. | `source-read` | Merge commit `23522b7…` is an ancestor of current main `ed49c01…`; later compare contains no modification to the four #204 files | Does not refresh against public mmdebstrap current head |

## System and ownership map

- Entrypoint: `upstream/mmdebstrap/coverage.py`.
- State owner: the coverage parent owns the current test child and the final process status.
- Control flow: start child, wait, catch `KeyboardInterrupt`, terminate and wait for child, then decide final status.
- Side effects: child processes and retained test summary output.
- Cleanup: immediate child termination and `wait()` already existed.
- Contract: status 0 means the selected matrix completed without failure; cancellation is not completion.
- Test boundary: exact imported driver in a minimal disposable suite with synthetic dependencies.

## Historical precedent

### Cleanup is not successful completion

- Source: https://github.com/teamleaderleo/linux-fieldwork/blob/ed49c01a85e9d363626db5d2973a33b67209e13b/notes/processes/cancellation-cleanup-must-not-fall-through-to-success.md
- Revision or date: Linux Fieldwork current main on 2026-07-30
- Principle supported: resource cleanup and operation success are separate results.
- Important difference: the note is a reusable rule; this finding proves one exact Python driver path.

### Shell-owner cancellation in make_mirror

- Source: https://github.com/teamleaderleo/linux-fieldwork/pull/205
- Revision or date: merged 2026-07-30
- Principle supported: a handler that cleans resources must also terminate with an explicit cancellation result.
- Important difference: #205 is POSIX-shell proxy/cache ownership; this finding is a Python test runner and only owns SIGINT.

## Approaches considered

### Retained approach: explicit `SystemExit(130)` after existing cleanup

This is the smallest change that prevents false success, preserves child cleanup, gives callers a conventional result, and avoids a Python traceback.

### Declined: keep `break` and mark a failure flag later

A flag can work, but it broadens the state path and makes interruption depend on the final epilogue. Immediate explicit termination is easier to review and cannot be accidentally cleared.

### Deferred: restore and re-raise SIGINT

Exact kernel-level signal identity is a viable CLI policy, but the focused contract only requires that cancellation cannot become status 0. Re-raising changes diagnostic and shutdown behavior and belongs to a separate policy decision.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Parent-only SIGINT against baseline | Focused regression | Child gone; completion marker absent; driver incorrectly returns 0 |
| Parent-only SIGINT against candidate | Focused regression | Child gone; marker absent; status 130 and interruption diagnostic |
| Unsignaled candidate run | Focused regression | Matrix item completes and driver returns 0 |
| Exact patch application and Python compilation | Test setup and Linux Fieldwork CI | Passed |
| Immediate repeated execution | Carrier #201 ran the four-test matrix twice | Both runs passed |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| SIGTERM and SIGHUP | Different signal/handler contract | Reopen when a concrete parent-only path is selected |
| Process-group delivery | Different ownership topology | LF-23 process-lifecycle work or a new finding |
| Grandchildren | Current driver directly owns one child | New reproducer showing descendant survival |
| Child that ignores TERM | Requires timeout/escalation policy | Separate design decision |
| Signal before child registration | Not exercised by this matrix | Reopen on a deterministic launch-window reproducer |
| Full QEMU backend execution | Multi-hour/integration boundary | Separate integration gate |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `linux-fieldwork@b5efc8faf35c1da725a3b995a344fadc078ad5d2` | Linux Fieldwork CI `30579733315` | GitHub-hosted Ubuntu | Passed exact-head repository gate | `target-executed` |
| carrier `#201@da0974a81419d6dc27cb89173bed821ced0e5c53` | run `30579465025`, coverage four-test matrix twice | Ubuntu 24.04 | 8/8 coverage test executions passed; imported source unchanged | `target-executed` |
| historical candidate `#143@96ddac76ab9dead7875937a6edfa37137bc52eb9` | run `30577412842` | GitHub-hosted Ubuntu | Passed before clean current-main restack | `target-executed` |

## Complete-diff and compatibility review

- Complete changed-file fence: retained patch, investigation README, reusable process note, executable regression.
- Current-base relationship: PR #204 merged as `23522b7f7d39ee3a237820e46168720edafb4d0a`; current Linux Fieldwork main `ed49c01a85e9d363626db5d2973a33b67209e13b` is 43 commits ahead and zero behind.
- Temporary carrier: #201 closed without merge after evidence transfer.
- Compatibility surfaces examined: status, stderr diagnostic, child disappearance, completion marker, unsignaled success, patch application, Python compilation, immediate rerun.
- Known routine repair remaining: none inside the stated parent-only SIGINT scope.
- Reviewer eligibility: the user designated agent review as the operative last-mile review; no separate reviewer is expected for this internal research packet.
- Exact-head disposition: `ACCEPT` for review-ready internal evidence.

## Current disposition and desk routing

- Finding state: `review-ready`
- Review disposition: `ACCEPT`
- Review Queue entry: `#213` update pending this finding PR
- Delivery lane: `not-entered`
- Exact next transition: use this finding as the canonical source for any internally prepared current-upstream patch packet.
- Clearing condition: explicit authorization before any public upstream interaction.
- Required subgates: refresh against current upstream revision; duplicate/precedent search; preserve the narrow evidence limits.
- User decision requested: none for internal readiness.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-30 | Linux Fieldwork PR #204 | Clean current-main evidence unit accepted and merged internally |
| 2026-07-30 | Fieldwork #254 clarification | Distinguished internal evidence merge from public publication readiness |
| 2026-07-30 | This finding PR | Records `review-ready` and `ACCEPT` without treating a second human reviewer as a hard gate |

## References

- https://github.com/teamleaderleo/linux-fieldwork/issues/141
- https://github.com/teamleaderleo/linux-fieldwork/pull/204
- https://github.com/teamleaderleo/linux-fieldwork/pull/201
- https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30579733315
- https://github.com/teamleaderleo/linux-fieldwork/blob/ed49c01a85e9d363626db5d2973a33b67209e13b/investigations/mmdebstrap-coverage-parent-sigint/README.md
- https://github.com/teamleaderleo/linux-fieldwork/blob/ed49c01a85e9d363626db5d2973a33b67209e13b/tests/test_mmdebstrap_coverage_parent_sigint.py
- https://github.com/teamleaderleo/fieldwork/issues/254
