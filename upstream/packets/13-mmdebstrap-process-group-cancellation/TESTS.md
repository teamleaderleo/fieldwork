# Unit 13 tests and receipts

## In simple words

The selected mechanism passed exact imported-wrapper controls for null, QEMU-style, and sudo process trees plus the full Linux Fieldwork gate. A fresh local model repeated the core later-work distinction, and its exact source now lives in this packet. The upstream mmdebstrap target suite has yet to run on a clean current-`master` source branch.

## Evidence classes

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| imported and current inspected `coverage.py` use wrapper-only termination | `source-read` | imported blob `9a522484…`; inspected upstream `master` revision `77ec9be5…` | current revision inspected through public source surfaces |
| wrapper-only variants permit later descendant work | `model-executed` | Linux Fieldwork exact-wrapper controls and local 2026-08-01 model | responsive modeled topologies |
| group candidate suppresses later work in null/QEMU-wrapper/sudo controls | `model-executed` | CI 931 and CI 942 | Fieldwork harness, Linux runner; real QEMU omitted |
| Linux Fieldwork repository gates pass | `full-gate` | CI 931, 942, 943 | gate belongs to Linux Fieldwork, not upstream mmdebstrap |
| upstream target-native regression exists | — | no clean target test exists yet | preparation pending |
| upstream ordinary gates pass | — | never run | delivery blocker |

## Retained Linux Fieldwork gate — mechanism generation

- source head: `e90fc438f530f7bd78ffd6fd1ba24c665bd96913`
- workflow run: [30632491641](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30632491641)
- job: [91161937871](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30632491641/job/91161937871)
- result: success
- steps: checkout proposed state; validate changed patch carriers; compile Python tools; run unit tests; check shell syntax and command help
- recorded test count: 359 passed in 167.224 seconds

Focused controls recorded by the canonical carrier:

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

## Retained Linux Fieldwork gate — current carrier generation

- source head: `dfc6d0503fb844f4c428ce16a567a9fdcd35280a`
- generated merge: `24c7ba065b4c50fee76a07b0f6d6cb000d4684d8`
- workflow run: [30633602052](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30633602052)
- job: [91165600654](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30633602052/job/91165600654)
- result: success
- recorded unique discovery count in final review: 340 repository tests
- candidate patch and executable test bytes remained unchanged after the mechanism head; later commits narrowed evidence wording.

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

The fixture records entry into Python's SIGINT handler before the losing controls release the deliberately surviving QEMU-like worker. Candidate product bytes remain unchanged.

## Fresh local process model

- date: 2026-08-01
- kernel: Linux 6.12.13 x86_64
- Python: 3.13.5
- command: `cd /tmp/unit13-probe && python3 harness.py`
- initial result: success
- closeout rerun: success with identical output

```text
variant=baseline rc=0 later_work=true child_live=false
variant=status rc=130 later_work=true child_live=false
variant=group rc=130 later_work=false child_live=false
```

- receipt: [`receipts/2026-08-01-local-process-model.md`](./receipts/2026-08-01-local-process-model.md)
- exact retained source: [`fixtures/local-process-model/`](./fixtures/local-process-model/)

## Setup/network result

Attempted read-only `git ls-remote` against the canonical upstream host from the local execution container. DNS resolution failed with `Could not resolve host`. Classification: setup/network limitation. Public source inspection through available repository interfaces supplied the inspected upstream revision and relevant file comparison.

The canonical Salsa project advertises `master` as its selected/default branch. Any future target materialization must refresh the branch head directly before applying the patch.

## Tests prepared or retained but outside the canonical carrier

- PR #339 refined QEMU losing-control test remains separate from #313.
- PR #347/#353 retained repeated-SIGINT, TERM-resistance, final-publication, and containment comparisons; no product patch selected.
- packet patch matches the inspected source hunk by textual identity, while `git apply --check` against a fresh current-upstream checkout remains pending.

## Required next execution

After an owned target fork exists:

1. create `fix/coverage-backend-process-group-current-master` from the refreshed exact upstream `master` head;
2. apply the retained one-file patch;
3. run `python3 -m py_compile coverage.py`;
4. adapt the discriminating parent-only SIGINT regression into the target's accepted test surface;
5. run that focused test on baseline and candidate;
6. run the project-declared source checks and ordinary suite appropriate to the change;
7. record exact commands, environment, counts, skips, and receipts;
8. review the complete clean target diff.

Until those steps run, the packet carries no target-native or upstream ordinary-gate claim.
