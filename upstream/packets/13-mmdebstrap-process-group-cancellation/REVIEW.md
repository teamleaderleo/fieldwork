# Unit 13 review and final inspection guide

## Current disposition

`REPAIR`

The source unit is technically complete for its bounded TERM-responsive claim. The clean one-file target diff, focused target execution, project-native ordinary source slice, source-only submission decision, and complete same-account self-review are present.

The remaining #435 blocker is eligible independent complete-diff acceptance on `teamleaderleo/mmdebstrap#4`. Public authority remains absent.

## Exact review target

- controlled repository: `teamleaderleo/mmdebstrap`
- internal clean review PR: `#4`
- base: `linux-fieldwork/upstream-main-snapshot@77ec9be5417ee44c96343d2347145585da1b1f94`
- clean source: `linux-fieldwork/unit-11-coverage-backend-cancellation@431614b3af58ba4f70791aa1d42cf5b71c965dd2`
- base `coverage.py` blob: `9a522484aef05deae514a98e4b6adf5feb6c886d`
- candidate `coverage.py` blob: `9e31f21cf37228257b5e0705d9ecb13b7a66e40f`
- complete changed-file list: `coverage.py`
- diff: 8 additions, 3 deletions
- retained patch blob: `f1a2c75adfa009b6f1ac29e5a31bef526400444f`

No packet documents, fixtures, workflows, receipts, tests, or unrelated source are present on the clean branch.

## Complete-diff self-review

No blocking defect was found within the stated claim.

### Launch boundary

`start_new_session=True` executes before backend code and makes the selected wrapper leader of a new session and process group. This gives the caller one backend-independent group identity.

Review question: does any supported backend deliberately require membership in the coverage driver's existing session or process group?

### Signal target

`os.killpg(proc.pid, signal.SIGTERM)` targets the wrapper's process group. The call occurs immediately after parent-only SIGINT while the wrapper is the tracked child.

Review questions:

- can any unrelated process enter this group before the signal?
- is PGID reuse a material practical risk in this sequence?
- should an already-exited wrapper be handled differently?

### Race handling

`ProcessLookupError` accepts the group disappearing between interruption and signal delivery. The driver still waits the wrapper and returns 130.

Review question: does this preserve the desired result if the wrapper completed immediately before SIGINT?

### Reaping and result

The second `proc.wait()` reaps the immediate wrapper. The driver prints `interrupted by SIGINT` and raises `SystemExit(130)`.

This does not prove arbitrary descendant drain. The claim is limited to the executed responsive topologies.

### Compatibility boundary

The candidate changes process-session membership for every selected null, sudo, and QEMU backend. Inherited standard file descriptors remain unchanged. Direct controlling-terminal access remains unexecuted.

Review question: are interactive or debug paths dependent on a controlling terminal rather than inherited descriptors?

## Exact evidence

### Focused target gate

Run `30706007117`:

- patch application with zero fuzz;
- byte equivalence to clean target source;
- target compilation;
- 6/6 baseline/status/group controls twice;
- 14/14 null/QEMU-wrapper/passwordless-sudo controls twice;
- no skips; actual sudo controls;
- cleanup and immediate rerun.

### Ordinary project-native source slice

Run `30706633832`, job `91386769087`:

- native `coverage.sh help man version` path;
- 3/3 first pass;
- 3/3 immediate rerun;
- real `coverage.py` and `run_null.sh` execution;
- changed `coverage.py` checked by real Black 26.5.1;
- artifact `8820528312`, SHA-256 `13986015aebc37cd3624f5114baa2a599f3c3dccb01e838b367287b2585b8f55`.

The exact base has a proven unrelated Black failure on unchanged canonical `tarfilter` blob `ad776167a8473d5d15dbe22e850f4f6db35cf278`. The successful gate isolates only that exact blob.

## Source-only test decision

The clean diff contains no native regression file.

The target suite treats every non-dot `tests/` entry as a `coverage.txt`-indexed shell-template package scenario. Testing the outer coverage orchestrator from inside the same harness requires a recursive miniature coverage tree substantially larger than the product change.

The exact deterministic external reproducer and target receipts are retained. A native recursive test is a reopen item if independent review or upstream policy requires it.

Decision record: [`receipts/2026-08-01-source-only-submission-shape.md`](./receipts/2026-08-01-source-only-submission-shape.md).

## Claim-by-claim result

| Claim | Evidence | Result |
| --- | --- | --- |
| exact base uses wrapper-only termination | canonical commit/blob | accepted |
| wrapper-only termination permits later work | focused negative controls | accepted |
| status 130 alone preserves survivor defect | status-only comparator | accepted |
| caller-owned group reaches tested descendants | source and three topology modules | accepted |
| selected responsive groups settle | target 6/6 and 14/14 twice | accepted |
| ordinary source/interface behavior succeeds | native 3/3 twice | accepted |
| clean target diff is bounded | PR #4, one file | accepted by self-review |
| eligible independent complete-diff acceptance | no eligible review yet | blocked |
| public overlap and policy remain current | prior search only | refresh before send |

## Evidence limits, not current blockers

- full prepared-mirror 283-entry package matrix;
- real QEMU/debvm package execution;
- direct `/dev/tty` behavior;
- TERM-resistant or group-escaping descendants;
- repeated-SIGINT and escalation policy;
- non-Linux behavior;
- public upstream CI and maintainer review.

These limits must remain visible in any submission. They do not contradict the narrow responsive-topology result.

## Independent reviewer checklist

1. verify base and head identities;
2. inspect the complete one-file diff, not only the latest hunk;
3. assess session/process-group compatibility for every selected backend;
4. assess `killpg` ownership and race boundaries;
5. inspect `ProcessLookupError`, wrapper-exit-before-SIGINT, and final status behavior;
6. verify claims remain limited to responsive in-group work;
7. decide whether the source-only submission shape is acceptable;
8. decide whether broader prepared-mirror execution is required before authorization;
9. approve, request changes, or state a concrete hold condition.

Same-account self-review is recorded on PR #4 but is not eligible final acceptance.

## After independent acceptance

- refresh overlap, contribution policy, and AI-disclosure requirements;
- update public draft links and exact packet/source heads;
- request explicit authority for the exact canonical-upstream action;
- do not merge or contact upstream before that authority.
