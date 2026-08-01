# Unit 13 tests and receipts

## In simple words

The selected mechanism passed exact imported-wrapper controls for null, QEMU-style, and sudo process trees. Those receipts remain valid for their exact historical source/base pairs. Linux Fieldwork later changed its workflow and test-discovery inputs, so a byte-identical current-main restack is now executing on PR #406.

A reviewed relocatable local model also repeats the core later-work distinction. The upstream mmdebstrap target suite has yet to run on a clean current-`master` source branch.

## Evidence classes

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| imported `coverage.py` uses wrapper-only termination | `source-read` | imported blob `9a522484…` | imported `debian/1.5.7-3` source |
| previously inspected upstream source carried the same lifecycle | `source-read` | reported revision `77ec9be5…` | refresh canonical Salsa `master` before target materialization |
| wrapper-only variants permit later descendant work | `model-executed` | exact-wrapper controls and packet model | responsive modeled topologies |
| group candidate suppresses later work in null/QEMU-wrapper/sudo controls | `model-executed` | CI 931 and CI 942 | Linux Fieldwork harness; real QEMU omitted |
| historical Linux Fieldwork repository gates passed | `full-gate` | CI 931, 942, 943 | exact historical base pairs only |
| current Linux Fieldwork integration passes | `target-test-prepared` | PR #406 at `e82b9b05…`; CI 1151 queued | result pending |
| upstream target-native regression exists | — | no clean target test exists | preparation pending |
| upstream ordinary gates pass | — | never run | delivery blocker |

## Historical mechanism gate

- source head: `e90fc438f530f7bd78ffd6fd1ba24c665bd96913`
- workflow run: [30632491641](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30632491641)
- job: [91161937871](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30632491641/job/91161937871)
- result: success
- recorded count: 359 passed in 167.224 seconds
- steps: checkout proposed state; validate changed patch carriers; compile Python tools; run unit tests; check shell syntax and command help

Focused controls:

1. imported null baseline — status 0 after release; surviving pipeline; later work;
2. status-only null — status 130 after release; surviving pipeline; later work;
3. group null — status 130; no live in-group work; no later work;
4. imported foreground-group SIGINT — already clean control;
5. group null unsignaled — success;
6. source/patch-shape checks;
7. imported QEMU-wrapper — driver blocked while operation survives, then status 0 after release and later work;
8. status-only QEMU-wrapper — same survivor, status 130 after release and later work;
9. group QEMU-wrapper — status 130, no live group, no later work;
10. group QEMU-wrapper unsignaled — success;
11. imported actual-sudo — privileged worker survives until release;
12. status-only actual-sudo — privileged worker survives until release;
13. group actual-sudo — status 130, no live privileged in-group work;
14. group actual-sudo unsignaled — success.

Specialized `capture-bug-report` and `reproduce-mmdebstrap` jobs were skipped by workflow conditions. The successful `lab-tools` job contains the relevant gate.

## Historical retained-head gate

- source head: `dfc6d0503fb844f4c428ce16a567a9fdcd35280a`
- generated merge: `24c7ba065b4c50fee76a07b0f6d6cb000d4684d8`
- workflow run: [30633602052](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30633602052)
- job: [91165600654](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30633602052/job/91165600654)
- result: success
- recorded count: 340 uniquely discovered repository tests

Candidate patch and executable test bytes remained unchanged after the mechanism head; later commits narrowed evidence wording.

### Staleness classification

A later complete review found that Linux Fieldwork `main` had changed governing inputs after CI 943: workflow behavior, unittest discovery and duplicate handling, retained-patch validation, process-group kill probes, zero-status selection controls, and signal/result-precedence suites. CI 931/943 remain valid at their exact heads and generated merges. They no longer support a current-main delivery claim.

## Current-main reconciliation — active execution

- canonical current Linux Fieldwork base: `6cc74d846c50b9bbb88247e8a128b67e8c174c1e`
- branch: `repair/313-current-main-reconciliation`
- exact source head: `e82b9b059850fce1efcf8daadef89049495a8b27`
- pull request: [#406](https://github.com/teamleaderleo/linux-fieldwork/pull/406)
- changed-file fence: nine files
- source relation: exact blob-for-blob restack of PR #313 head `dfc6d050…`
- workflow run: [30690801852](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30690801852)
- run number: 1151
- state at packet update: queued

Required receipt from this gate:

- generated merge identity;
- patch validation result;
- compilation result;
- exact discovery count;
- confirmation that all three process-group modules execute once;
- null/QEMU-wrapper/sudo lifecycle results;
- shell syntax and command-help result;
- skips and environment limits.

## QEMU causal-evidence successor

- branch: `repair/313-qemu-negative-release-order-v2`
- exact head: `8253ab2ef6fed22b34fc5f5d6d20cda75c25e2c7`
- changed file: `tests/test_mmdebstrap_coverage_qemu_process_group.py`
- blob: `0c2a050faf8e98320fc0c4fe4634d46bdf7f0dfa`
- workflow run: [30633578396](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30633578396)
- job: [91165522248](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30633578396/job/91165522248)
- result: success
- recorded count: 269 tests passed
- independent exact-head review comment: `5143736054`

The fixture records entry into Python's SIGINT handler before the losing controls release the deliberately surviving QEMU-like worker. Candidate product bytes remain unchanged. This refinement remains separate from #313 and #406.

## Local process model

- date: 2026-08-01
- kernel: Linux 6.12.13 x86_64
- Python: 3.13.5
- evidence class: `model-executed`

Original run:

```sh
cd /tmp/unit13-probe
python3 harness.py
```

Reviewed relocatable replay:

```sh
cd upstream/packets/13-mmdebstrap-process-group-cancellation/fixtures/local-process-model
python3 -m py_compile child.py driver.py harness.py harness_original.py wrapper.py
python3 harness.py
```

Results:

```text
variant=baseline rc=0 later_work=true child_live=false
variant=status rc=130 later_work=true child_live=false
variant=group rc=130 later_work=false child_live=false
```

- compilation: success
- original run: success
- closeout rerun: success
- reviewed relocatable replay: success
- receipt: [`receipts/2026-08-01-local-process-model.md`](./receipts/2026-08-01-local-process-model.md)
- retained source: [`fixtures/local-process-model/`](./fixtures/local-process-model/)

The reviewed replay repairs only portability, readiness ordering, early-exit diagnosis, and cleanup. It changes no expected outcome or mechanism.

## Setup and retrieval limits

A read-only `git ls-remote` attempt against the canonical upstream host failed with `Could not resolve host`. Classification: setup/network limitation.

The Salsa project advertises `master` as its selected/default branch. Revision `77ec9be5417ee44c96343d2347145585da1b1f94` is retained as the previously inspected source identity, not asserted as the current head. Refresh `master` directly before target materialization.

## Tests retained outside the canonical carrier

- PR #339 — refined QEMU losing-control causal proof;
- PR #347/#353 — repeated-SIGINT, TERM-resistance, final-publication, and containment comparisons; no product patch selected;
- packet patch — matches the retained imported source hunk; `git apply --check` against a fresh canonical checkout remains pending.

## Required next execution

1. finish PR #406 current-main CI and complete-diff review;
2. record its exact generated merge, counts, skips, and conclusions;
3. obtain or create an owned mmdebstrap fork;
4. refresh canonical Salsa `master` and record the exact base;
5. create `fix/coverage-backend-process-group-current-master`;
6. apply the retained one-file patch;
7. run `python3 -m py_compile coverage.py`;
8. adapt the discriminating parent-only SIGINT regression into the target's accepted test surface;
9. run focused baseline/candidate execution and project-declared ordinary gates;
10. record exact commands, environment, counts, skips, cleanup, and rerun.

Until those steps run, the packet carries no upstream target-native or upstream ordinary-gate claim.
