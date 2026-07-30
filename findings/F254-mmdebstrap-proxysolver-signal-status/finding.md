# F254-mmdebstrap-proxysolver-signal-status: preserve child signal identity

Finding state: `review-ready`

Workstream: `G`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-mmdebstrap-proxysolver-signal-status/finding.md`  
Canonical implementation: `teamleaderleo/linux-fieldwork#207` — merged internal evidence unit  
Exact implementation head: `e4b16f5180e8bf67bf58621cac4447f4a4a55f44`  
Exact base or source revision: imported `proxysolver` blob `5cd51fab89104d30b8b12bff18a49d38d9be0003`; ordinary-status prerequisite patch blob `0c29e916fa33f41bb5bea0b4ee863d7a0eee5519`  
Strongest evidence class: `target-executed`  
Reviewed input generation: Fieldwork #254 body as updated 2026-07-30; Linux issue #165 narrow contract  
Current review disposition: `ACCEPT`  
Desk routing: `Review Queue #213`  
Upstream contact authorized: `no`

## In simple words

`proxysolver` sits between APT and its real dependency solver. It copies the solver's output and should report how the solver ended.

Python uses a negative subprocess return code to mean that a child died from a signal. The earlier ordinary-status repair passed that negative number to `SystemExit`, turning a child killed by TERM into unrelated ordinary exit code 241. The retained candidate closes output files, flushes stdout, restores and unblocks the child signal, and terminates the wrapper with that same signal.

The internal evidence unit is accepted for this narrow Linux/POSIX signal-identity behavior. It has not been submitted upstream.

## Why we care

Callers distinguish ordinary application failure from cancellation or resource-pressure termination. A wrapper that changes SIGTERM into exit 241 can make logs, retry policy, cancellation reporting, and supervisors choose the wrong interpretation.

The observed result is exact: the predecessor returns 241 for a solver killed by SIGTERM; the candidate is itself observed as terminated by SIGTERM. Real-world occurrence frequency is unknown.

## What happens if we leave it alone

When the solver dies from SIGTERM, `subprocess.Popen.returncode` is `-15`. `SystemExit(-15)` exits normally with the low eight bits, 241. A parent cannot tell that the wrapper's child was signal-terminated, and conventional shell status 143 is also lost.

Ordinary solver exit 7 was already repaired separately. Leaving this follow-up out preserves ordinary status but still misclassifies signal termination.

## Current finding

Negative subprocess return codes are signal identities, not ordinary exit codes. After required output is closed and flushed, the wrapper should restore the default disposition, unblock a catchable inherited signal, and signal itself with the same signum. This preserves true `WIFSIGNALED` behavior and a Python parent observes `-SIGTERM`.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| The ordinary-status predecessor maps child SIGTERM to ordinary exit 241. | `target-executed` | `linux-fieldwork/tests/test_mmdebstrap_proxysolver_signal_status.py`; issue #165 negative control | SIGTERM and one imported source stack |
| The candidate wrapper is observed as terminated by SIGTERM. | `target-executed` | PR #207 head `e4b16f5…`; CI run `30579889333`; carrier run `30579465025` | Linux/POSIX process and signal APIs |
| Complete stdout and dump bytes survive before the wrapper re-signals itself. | `target-executed` | Focused fake-solver matrix | One complete flushed line, not arbitrary output failure |
| Ordinary exit 0 and 7 remain unchanged. | `target-executed` | Same four-test matrix | Depends on the separate ordinary-status patch from PR #134 |
| An inherited blocked SIGTERM mask is cleared before self-signaling. | `target-executed` | Blocked-mask launcher control | Catchable SIGTERM; not every signal or supervisor environment |
| The retained files remain unchanged on current Linux Fieldwork main. | `source-read` | Merge commit `72f4d27…` is an ancestor of current main `ed49c01…`; later compare contains no modification to the four #207 files | Does not refresh against public mmdebstrap current head |

## System and ownership map

- Entrypoint: imported `upstream/mmdebstrap/proxysolver`.
- State owner: the wrapper owns the real solver process, copied stdout, optional dump file, and wrapper result.
- Control flow: start solver, copy each output line to stdout and dump, wait, interpret the return code.
- Side effects: stdout bytes, dump-file bytes, child lifetime, and process termination status.
- Cleanup: subprocess and dump context managers close before exact self-signaling; stdout is explicitly flushed.
- Contract: ordinary positive statuses remain ordinary; negative statuses represent child signal termination and must be deliberately preserved or translated.
- Test boundary: exact imported source plus ordinary-status prerequisite and follow-up patch, with a disposable fake solver.

## Historical precedent

### Ordinary solver-status propagation

- Source: https://github.com/teamleaderleo/linux-fieldwork/pull/134
- Revision or date: merged 2026-07-30 as `ebb11fc382ce6b42597e9130e7abb741c3684ca2`
- Principle supported: a wrapper must propagate the owned child's real result rather than returning success after copying output.
- Important difference: #134 handles ordinary positive exit codes; it exposed rather than solved negative signal return codes.

### Negative subprocess return codes are signals

- Source: https://github.com/teamleaderleo/linux-fieldwork/blob/ed49c01a85e9d363626db5d2973a33b67209e13b/notes/processes/negative-subprocess-returncodes-are-signals.md
- Revision or date: Linux Fieldwork current main on 2026-07-30
- Principle supported: choose exact re-signaling or explicit `128 + signum` mapping; never rely on modulo-256 truncation.
- Important difference: the note is the general rule; this finding proves exact re-signaling for one wrapper and signal.

## Approaches considered

### Retained approach: exact self-signaling after output closure

This preserves actual signal termination to a POSIX parent, retains output bytes, and keeps ordinary statuses unchanged. Restoring `SIG_DFL` and unblocking the signal avoids Python runtime disposition and inherited-mask surprises.

### Declined: `SystemExit(returncode)` for negative values

It creates an unrelated ordinary code such as 241 and loses signal identity.

### Alternative not selected: exit `128 + signum`

Status 143 is conventional and simpler, but the wrapper would have exited normally; a parent using wait-status semantics could not observe signal termination. The retained exact behavior better matches the child result.

### Deferred: output failure during explicit flush

A broken stdout sink can raise before self-signaling. That is a distinct output-path precedence decision and needs its own negative control.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Child self-terminates with SIGTERM | Focused regression | Predecessor returns 241; candidate parent observes `-SIGTERM` |
| Wrapper inherits blocked SIGTERM | Launcher control | Candidate unblocks and still terminates by SIGTERM |
| Child exits 0 | Focused regression | Wrapper returns 0; stdout/dump preserved |
| Child exits 7 | Focused regression | Wrapper returns 7; stdout/dump preserved |
| Final flushed output before signal | Fake solver and byte assertions | Complete stdout and dump line retained |
| Child disappearance | PID checks | Every fake solver PID gone |
| Exact patch composition and compilation | Test setup and CI | Passed |
| Immediate repeated execution | Carrier #201 ran four-test matrix twice | Both runs passed |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Signals other than SIGTERM | Dynamic proof is deliberately narrow | Reopen for a concrete differing disposition or mask behavior |
| SIGKILL and SIGSTOP handler setup | Cannot install handlers; source handles them separately | Add execution only if a safe discriminating control is needed |
| Broken stdout sink during flush | Competing output-error precedence | New finding with exact sink failure |
| Outer supervisor translates signals | Outside wrapper ownership | Integration finding when an actual supervisor path matters |
| Non-POSIX platforms | Candidate uses `pthread_sigmask` | Separate portability design; Linux target currently intentional |
| Current public upstream composition | Imported source and two retained patches only | Refresh before an upstream packet |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `linux-fieldwork@e4b16f5180e8bf67bf58621cac4447f4a4a55f44` | Linux Fieldwork CI `30579889333` | GitHub-hosted Ubuntu | Passed exact-head repository gate | `target-executed` |
| carrier `#201@da0974a81419d6dc27cb89173bed821ced0e5c53` | run `30579465025`, proxysolver four-test matrix twice | Ubuntu 24.04 | 8/8 proxysolver test executions passed; imported source unchanged | `target-executed` |
| historical candidate `#166@50fdbcd25b51842ff2b489a91e36668e0e2340ea` | run `30577348662` | GitHub-hosted Ubuntu | Passed before clean current-main restack | `target-executed` |

## Complete-diff and compatibility review

- Complete changed-file fence: retained signal patch, investigation README, reusable process note, executable regression.
- Current-base relationship: PR #207 merged as `72f4d27aadf1863ee1b534d9751f3061c55b2ba4`; current Linux Fieldwork main `ed49c01a85e9d363626db5d2973a33b67209e13b` is 41 commits ahead and zero behind.
- Temporary carrier: #201 closed without merge after evidence transfer.
- Compatibility surfaces examined: signal identity, inherited signal mask, stdout bytes, dump bytes, ordinary 0/7 statuses, file closure, child disappearance, compilation, immediate rerun.
- Known routine repair remaining: none inside the stated SIGTERM signal-identity scope.
- Reviewer eligibility: the user designated agent review as the operative last-mile review; no separate reviewer is expected for this internal research packet.
- Exact-head disposition: `ACCEPT` for review-ready internal evidence.

## Current disposition and desk routing

- Finding state: `review-ready`
- Review disposition: `ACCEPT`
- Review Queue entry: `#213` update pending this finding PR
- Delivery lane: `not-entered`
- Exact next transition: use this finding as the canonical source when composing a current-upstream proxysolver patch stack.
- Clearing condition: explicit authorization before any public upstream interaction.
- Required subgates: refresh against current upstream; compose with the ordinary-status prerequisite; duplicate/precedent search; retain Linux/POSIX and output-error boundaries.
- User decision requested: none for internal readiness.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-30 | Linux Fieldwork PR #134 | Ordinary positive solver status propagation merged internally |
| 2026-07-30 | Linux Fieldwork PR #207 | Signal-identity follow-up accepted and merged internally |
| 2026-07-30 | Fieldwork #254 clarification | Distinguished internal evidence merge from public publication readiness |
| 2026-07-30 | This finding PR | Records `review-ready` and `ACCEPT` under the user's operative review model |

## References

- https://github.com/teamleaderleo/linux-fieldwork/issues/165
- https://github.com/teamleaderleo/linux-fieldwork/pull/134
- https://github.com/teamleaderleo/linux-fieldwork/pull/207
- https://github.com/teamleaderleo/linux-fieldwork/pull/201
- https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30579889333
- https://github.com/teamleaderleo/linux-fieldwork/blob/ed49c01a85e9d363626db5d2973a33b67209e13b/investigations/mmdebstrap-proxysolver-signal-status/README.md
- https://github.com/teamleaderleo/linux-fieldwork/blob/ed49c01a85e9d363626db5d2973a33b67209e13b/tests/test_mmdebstrap_proxysolver_signal_status.py
- https://github.com/teamleaderleo/fieldwork/issues/254
