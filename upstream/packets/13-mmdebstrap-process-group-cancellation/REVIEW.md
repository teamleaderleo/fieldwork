# Unit 13 review and final inspection guide

## In simple words

The process-group mechanism has strong bounded evidence. The original Linux Fieldwork delivery receipt expired after `main` changed governing workflow and test-discovery inputs. A byte-identical nine-file current-main restack now exists on PR #406 and is awaiting its gate and renewed review.

Final upstream delivery still requires a clean mmdebstrap branch, target-native regression, ordinary gates, and precise wording around TERM-responsive versus resistant descendants.

## Current self-review disposition

`REPAIR`

Technical content: accepted for group-wide TERM delivery and settlement in the tested responsive topologies.

Linux Fieldwork delivery identity: reconciliation active on PR #406.

Upstream delivery identity: incomplete; no owned mmdebstrap source branch or target-native current-`master` execution exists.

## Exact reviewed inputs

- Fieldwork backlog issue: `teamleaderleo/fieldwork#435`
- unit: 13
- canonical retained carrier: `teamleaderleo/linux-fieldwork#313`
- retained carrier branch/head: `fix/coverage-backend-process-group@dfc6d0503fb844f4c428ce16a567a9fdcd35280a`
- executed mechanism head: `e90fc438f530f7bd78ffd6fd1ba24c665bd96913`
- current-main reconciliation: `teamleaderleo/linux-fieldwork#406`
- reconciliation base: `6cc74d846c50b9bbb88247e8a128b67e8c174c1e`
- reconciliation branch/head: `repair/313-current-main-reconciliation@e82b9b059850fce1efcf8daadef89049495a8b27`
- reconciliation CI: `30690801852` / run 1151, queued at packet update
- imported target source: `debian/1.5.7-3@6fde999741f4fe1e7bf38079acf29432ef87a35e`
- canonical upstream selected/default branch: `master`
- previously inspected upstream revision: `77ec9be5417ee44c96343d2347145585da1b1f94`; refresh required
- QEMU evidence successor: `8253ab2ef6fed22b34fc5f5d6d20cda75c25e2c7`
- escalation comparison: `615bd4f5256d9851f682e48e037169ceeb7bb98c`

## Current candidate fences

### Clean product intent

- `coverage.py`
- one target-native focused regression, path pending current upstream convention

### Linux Fieldwork research carrier

1. `investigations/mmdebstrap-coverage-process-group/0000-materialize-status-only.patch`
2. `investigations/mmdebstrap-coverage-process-group/0001-own-backend-process-group.patch`
3. `investigations/mmdebstrap-coverage-process-group/README.md`
4. `investigations/mmdebstrap-coverage-process-group/QEMU_WRAPPER.md`
5. `investigations/mmdebstrap-coverage-process-group/SUDO_WRAPPER.md`
6. `notes/processes/callers-must-own-complete-backend-process-groups.md`
7. `tests/test_mmdebstrap_coverage_process_group.py`
8. `tests/test_mmdebstrap_coverage_qemu_process_group.py`
9. `tests/test_mmdebstrap_coverage_sudo_process_group.py`

PR #406 uses the exact nine blob SHAs from PR #313. Only the product hunk and a target-native regression belong in a future mmdebstrap source branch.

## Review finding: expired current-base identity

The latest complete review of PR #313 accepted the bounded mechanism and changed the delivery disposition to `REPAIR CURRENT-BASE DELIVERY IDENTITY`.

Reason: after CI 943, Linux Fieldwork `main` changed material governing inputs, including:

- `.github/workflows/linux-fieldwork-ci.yml`;
- unittest discovery and duplicate handling;
- retained-patch validation;
- process-group kill and zero-status controls;
- signal/result-precedence suites.

Historical CI 931/943 remains evidence for its exact source/base pair. It is no longer a current-main integration receipt.

The review mentioned PR #358 as a routing surface. Live inspection shows #358 is a closed, unrelated mmdebstrap broad-fixture contract repair. Unit 13 does not edit or depend on it. PR #406 is the explicit current-base reconciliation carrier for this unit.

## Claim-by-claim review

| Claim | Current evidence | Review question |
| --- | --- | --- |
| wrapper-only termination can leave nested work | exact imported-wrapper controls and packet model | Do the negative controls prove later work after parent SIGINT? |
| status 130 alone leaves the cancellation defect | exact status-only controls | Are result status and operation settlement kept separate? |
| caller-owned group sends TERM to nested in-group work | code review and null/QEMU/sudo controls | Is the group created before every backend launch? |
| tested responsive groups settle without later work | CI 931/942 | Are claims limited to executed topologies? |
| current Linux Fieldwork integration is compatible | PR #406 / CI 1151 | Did the exact nine-file restack pass current discovery and controls? |
| ordinary execution remains successful | unsignaled controls | Do all current-base unsignaled controls pass? |
| previously inspected upstream revision carried old lifecycle | source read at `77ec9be5…` | Refresh canonical `master` before materialization. |
| no duplicate public repair found | bounded search on 2026-08-01 | Refresh issue/MR, Debian bug, and recent commit search before publication. |

## Required PR #406 review

1. confirm base `6cc74d846c50b9bbb88247e8a128b67e8c174c1e` is the current Linux Fieldwork `main` used by the run;
2. confirm all nine file blobs match PR #313 head `dfc6d050…`;
3. record literal source head and generated merge separately;
4. inspect patch validation and Python compilation;
5. record exact unittest discovery count;
6. prove the null, QEMU, and sudo modules execute once each;
7. inspect all lifecycle control results and skips;
8. inspect shell syntax and command-help checks;
9. review the complete current diff;
10. preserve same-account review as self-review only.

## Packet fixture review

The original local model harness used an absolute `/tmp/unit13-probe` path and waited only for `child-ready` before reading `wrapper-ready`.

The packet now preserves that exact source as `harness_original.py` and provides a relocatable `harness.py` that:

- resolves sibling files from `__file__`;
- waits for both readiness markers;
- diagnoses early driver exit;
- cleans all modeled processes in `finally`.

Compilation and replay passed with unchanged output. This repair affects packet reproducibility only.

## Required clean-upstream review

After target materialization:

1. verify branch ancestry begins at the refreshed canonical upstream `master` SHA;
2. compare the complete branch diff against upstream;
3. confirm Fieldwork vocabulary, receipts, temporary workflows, and research files are absent;
4. confirm the source patch touches only the owning lifecycle path;
5. inspect `start_new_session=True` portability against supported Python/platform policy;
6. confirm `killpg(proc.pid, SIGTERM)` targets only the dedicated backend group;
7. confirm `ProcessLookupError` preserves exit 130;
8. inspect behavior when the wrapper exits before SIGINT;
9. ensure the regression proves handler entry or equivalent causal ordering;
10. keep fixture escalation inside teardown;
11. run focused and ordinary gates at the exact target head;
12. refresh drafts and pinned links.

## Human inspection focus

- Is a new session acceptable for all supported backends, especially interactive debug paths?
- Which upstream-native test location gives a maintainable deterministic regression?
- Should exit-130 correction and group delivery be one coherent upstream patch?
- Does the project prefer an issue first or direct merge request for coverage-harness lifecycle fixes?
- What current contribution and AI-disclosure policy applies?

## Known limits requiring visible wording

- `proc.wait()` proves wrapper exit, not arbitrary process-group drain.
- TERM-resistant descendants and repeated SIGINT remain outside the selected patch.
- group/session escape remains outside a group-local policy.
- real QEMU/debvm and direct `/dev/tty` behavior remain unexecuted.
- Linux Fieldwork CI is supporting research evidence, not the upstream ordinary gate.

## Clearing conditions for `READY`

- PR #406 current-main gate and complete-diff review pass;
- owned target repository/fork exists;
- clean current-`master` target branch exists with exact base and head;
- changed-file list is product-native;
- retained patch applies cleanly or is recreated directly;
- target-native focused regression passes;
- project-declared ordinary gates pass;
- duplicate/prior-art search is refreshed;
- complete exact target diff receives independent review;
- packet and drafts match the clean target head;
- exact public action awaits explicit authority.

Upstream contact remains unauthorized.
