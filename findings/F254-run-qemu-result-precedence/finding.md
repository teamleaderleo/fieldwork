# F254-run-qemu-result-precedence: cleanup must not replace the primary result

Finding state: `delivery-gate-ready`

Workstream: `G`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-run-qemu-result-precedence/finding.md`  
Canonical implementation: `teamleaderleo/linux-fieldwork#270`  
Exact implementation head: `14cb0e16014d0e4abe29ea5d2302abfb7ff7c299`  
Exact base or source revision: Linux Fieldwork main `c35f877b4fd4d70f487852973d2bc47bd97ac2d0`; imported `run_qemu.sh` blob `426aeeb854173569b24e64d6eb85019f45bdf0b6`  
Strongest evidence class: lifecycle claims `model-executed`; complete imported-source gate `target-test-prepared`  
Reviewed input generation: current Fieldwork/Linux protocols; Linux #269; PR #270 exact review `4824831881`  
Current review disposition: `EXECUTE`  
Desk routing: Delivery Desk #160 D2  
Upstream contact authorized: `no`

## In simple words

`run_qemu.sh` owns several possible results: the host/QEMU command can fail, the guest can report a test failure, a signal can cancel the wrapper, and cleanup can fail.

The imported cleanup function ran for normal exit and signals. It could let the guest or cleanup cover up a more specific host result, report a stop signal as success, and run cleanup twice.

PR #270 separates normal exit from explicit signal handling and applies one order:

```text
host or signal failure > guest failure > first cleanup failure > success
```

## Why we care

Timeout 124, host failure 42, cancellation 130/143, guest test failure 1, and cleanup failure identify different owners and recovery actions. Replacing one with another misclassifies the failure and makes debugging harder.

False success after INT/TERM is a direct correctness defect. Duplicate cleanup and last-cleanup-failure precedence also hide resource ownership.

## What happens if we leave it alone

The imported source installs:

```sh
trap cleanup INT TERM EXIT
```

The cleanup function captures `$?`, removes temporary state, reads the guest status, and sets the final result to 1 when the guest status is nonzero.

Consequences reproduced in the exact reduced model:

- host timeout 124 plus guest failure returns 1;
- missing guest status can replace host failure;
- parent-only INT/TERM plus guest success returns 0;
- parent-only INT/TERM plus guest failure returns 1;
- signal cleanup exits through the still-installed EXIT trap and runs again.

## Current finding

Result ownership must be explicit before cleanup starts.

The retained contract is:

1. ordinary EXIT captures its incoming status;
2. INT and TERM use explicit 130 and 143;
3. every converging trap is cleared before cleanup;
4. an existing host or signal nonzero status wins;
5. otherwise guest nonzero, missing, unreadable, or malformed status becomes generic 1;
6. otherwise the first cleanup failure becomes final;
7. later cleanup actions are attempted but cannot replace that first cleanup failure;
8. otherwise status is 0.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Host 124 plus guest failure becomes 1 in the baseline. | `model-executed` | primary regression negative control | Reduced exact cleanup shape |
| Parent-only INT/TERM can become guest-dependent 0/1. | `model-executed` | signal matrix | Target `/bin/sh`, held foreground command |
| Baseline signal cleanup runs twice. | `model-executed` | cleanup log `rm, rmdir, rm` | Disposable wrappers |
| Candidate preserves host/signal result over guest and cleanup. | `model-executed` | precedence matrix | No actual QEMU/debvm |
| Candidate retains first cleanup failure 74 over later 75. | `model-executed` | additive cleanup regression | Simulated cleanup functions |
| Candidate applies to complete imported source and passes syntax/repository gate. | `target-test-prepared` | CI `30597908319` / 787 | Queued at this revision |
| PR #270 is one commit and five files over live base. | `source-read` | PR metadata and review `4824831881` | Exact relation at generation time |

## System and ownership map

- Wrapper owner: `run_qemu.sh`.
- Primary result owner: timeout/debvm/QEMU command or explicit signal handler.
- Subordinate result channel: guest-written `shared/exitstatus.txt` when `shared/output.txt` exists.
- Cleanup owner: temporary log and directory.
- Background log follower: existing `setpriv --pdeathsig TERM tail -f`; unchanged by this candidate.
- Result flow: primary status, then guest classification only after primary success, then first cleanup failure only after both succeed.

## Historical precedent

### Shell signal and cleanup ownership

- Source: https://github.com/teamleaderleo/linux-fieldwork/pull/224
- Revision: merged 2026-07-31
- Principle supported: signal cleanup must terminate with explicit identity and clear converging traps.
- Important difference: #224 owns child/cache lifecycle; #270 owns result-channel precedence.

### Worker result precedence

- Source: https://github.com/teamleaderleo/linux-fieldwork/pull/267
- Revision: `c066db4046626cbed0b1c186cb52b9dffa72554a`
- Principle supported: primary failure and cancellation must survive cleanup.
- Important difference: #267 owns pipeline worker and parent proxy; #270 combines host, guest, signal, and cleanup results.

## Approaches considered

### Retained: explicit precedence in one finish function

This keeps one cleanup implementation while supplying the primary status explicitly from ordinary exit or signal handlers.

### Declined: only guard guest overwrite when `$?` is nonzero

That preserves host failures but still leaves signals guest-dependent and cleanup duplicated through EXIT.

### Declined: use one shared trap and infer signal from `$?`

A deferred shell trap can see the foreground command's status rather than the signal identity.

### Declined: last cleanup failure wins

Later cleanup errors can hide the first cleanup operation that failed. The candidate attempts all cleanup while retaining the first failure.

### Deferred: HUP/QUIT policy and full QEMU integration

Those require separate policy or expensive execution and do not overlap the exact repair.

## Edge cases covered

| Case | Evidence | Result |
| --- | --- | --- |
| Host 0/42/124/143 | primary matrix | expected primary precedence |
| Guest 0/nonzero/malformed/missing | primary matrix | generic 1 only after host success |
| INT/TERM with guest 0/nonzero | signal matrix | candidate 130/143; baseline 0/1 |
| Signal cleanup convergence | cleanup logs | candidate once; baseline twice |
| Cleanup rm 74 then rmdir 75 | cleanup regression | 74 retained |
| Host 42 plus cleanup 74/75 | cleanup regression | 42 retained |
| Exact patch application | source test | passed locally |
| Complete shell syntax | `/bin/sh -n` | passed locally |
| Unittest discovery | six unique tests | no duplicate imported cases |

## Edge cases deferred or outside scope

| Edge case | Why outside scope | Owner or trigger |
| --- | --- | --- |
| Complete QEMU/debvm guest execution | high-cost integration | before authorized external packet if justified |
| Timeout behavior in every signal topology | separate execution topology | contradictory exact evidence |
| Background tail lifecycle | existing pdeathsig design unchanged | leak or stale log evidence |
| HUP/QUIT mapping | no current contract selected | separate policy finding |
| Current public source | pinned import only | refresh before external preparation |
| Unusual filesystem cleanup failures | reduced status model only | contradictory filesystem evidence |

## Exact execution and receipts

| Repository/head | Command or workflow | Result | Evidence class |
| --- | --- | --- | --- |
| local retained tree | primary result/signal module | 4 tests passed | `model-executed` |
| local retained tree | first cleanup failure module | 2 tests passed | `model-executed` |
| combined local discovery | `python3 -m unittest discover -v -s tests -p 'test_run_qemu*.py'` | 6 unique tests passed in 2.981s | `model-executed` |
| `linux-fieldwork#270@14cb0e16…` | exact review `4824831881` | no source-visible repair | `source-read` |
| same head | Linux Fieldwork CI `30597908319` / 787 | queued | `target-test-prepared` |

The Python startup spreadsheet-runtime warmup diagnostic was unrelated to these test modules; the unittest process returned 0.

## Complete-diff and compatibility review

- Changed-file fence: retained patch, investigation README, reusable note, primary regression, cleanup regression.
- Base relationship: one commit ahead of `c35f877b…`, zero behind at generation time.
- Imported source file is not changed directly; the patch is retained as evidence/candidate material.
- Compatibility surfaces: host status, guest status, missing/malformed result, INT/TERM identity, cleanup ordering, first cleanup failure, later-work suppression, syntax, discovery.
- Unchanged surfaces: QEMU/debvm command construction, timeout policy, guest status format, background tail ownership, HUP/QUIT.
- Current disposition: `EXECUTE`; exact hosted imported-source execution is the only current gate.

## Current disposition and desk routing

- Finding state: `delivery-gate-ready`
- Review disposition: `EXECUTE`
- Review Queue entry: exact review retained on PR #270
- Delivery lane: `D2`
- Exact next transition: classify CI `30597908319`; if green and unchanged with current-enough base, set `land-ready` and merge internally
- Clearing condition: patch application, shell syntax, both focused modules without duplicate discovery, and repository discovery pass on `14cb0e16…`
- Required subgates: intended job executed; exact head unchanged; base relationship current enough
- User decision requested: none

## Changes to the canonical conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-31 | Linux #269 | recorded host-overwrite question and live checkpoint |
| 2026-07-31 | reduced matrix | found false signal success and duplicate cleanup in addition to host overwrite |
| 2026-07-31 | complete-diff review | found and repaired last-cleanup-failure precedence; added nonduplicating cleanup module |
| 2026-07-31 | PR #270 `14cb0e16…` | published clean current-main five-file candidate with one exact gate |

## References

- https://github.com/teamleaderleo/linux-fieldwork/issues/269
- https://github.com/teamleaderleo/linux-fieldwork/pull/270
- https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30597908319
- https://github.com/teamleaderleo/linux-fieldwork/pull/224
- https://github.com/teamleaderleo/linux-fieldwork/pull/267
- https://github.com/teamleaderleo/fieldwork/issues/254
