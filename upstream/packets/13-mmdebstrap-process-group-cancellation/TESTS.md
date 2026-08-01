# Unit 13 tests and receipts

## In simple words

The selected patch has exact current-source focused execution against canonical mmdebstrap `main@77ec9be5417ee44c96343d2347145585da1b1f94`. It applied with zero fuzz and compiled twice. The packet six-control matrix and refined null/QEMU-wrapper/passwordless-sudo fourteen-control matrix each passed twice, with no skips in the refined topology run.

Historical Linux Fieldwork repository gates and the packet-local model remain supporting evidence. A clean controlled-fork target branch and the project-declared ordinary mirror-backed/source gate remain absent.

## Evidence classes

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| canonical `coverage.py` matches imported wrapper-only baseline | `source-read` | canonical commit `77ec9be…`, blob `9a522484…` | exact executed base |
| upstream-root patch applies and compiles | `target-executed` | run `30689911760`, job `91342674259` | focused source application |
| wrapper-only variants permit later descendant work | `target-executed` | six-control canonical matrix and fourteen-control refined matrix | responsive modeled topologies |
| group candidate suppresses later work in null/QEMU-wrapper/sudo controls | `target-executed` | run `30689911760`, both jobs | real QEMU omitted |
| cleanup and immediate rerun succeed | `target-executed` | both matrices ran twice | hosted Ubuntu 24.04 Linux runner |
| historical Linux Fieldwork repository gates passed | `full-gate` | CI 931, 942, 943 | exact historical source/base pairs |
| project-declared ordinary mirror-backed/source gate passes | — | unexecuted | outer #435 blocker |
| clean target candidate branch passes | — | no controlled canonical fork branch | outer #435 blocker |

## Exact canonical source identity

| Field | Value |
| --- | --- |
| Canonical repository | `https://gitlab.mister-muffin.de/josch/mmdebstrap` |
| Canonical branch | `main` |
| Exact base executed | `77ec9be5417ee44c96343d2347145585da1b1f94` |
| Last commit touching `coverage.py` | `c82fc7e261c7a2fd85e499484108408fd42331d2` |
| Canonical/imported `coverage.py` blob | `9a522484aef05deae514a98e4b6adf5feb6c886d` |
| Canonical `run_null.sh` blob | `e0a8c106f9d3d636baea286d2ab33834748dffc9` |
| Canonical `run_qemu.sh` blob | `426aeeb854173569b24e64d6eb85019f45bdf0b6` |
| Upstream-root patch blob | `f1a2c75adfa009b6f1ac29e5a31bef526400444f` |
| Historical prefixed patch blob | `4f2a749e50d42655ebb6519ca6550d2f666985bc` |
| Canonical packet head | `d232e4fdd67cf0592e129a60534e984dcbec6bfe` |
| Canonical packet PR | `teamleaderleo/linux-fieldwork#401` |

## Canonical current-source gate

### Run and jobs

- workflow run: [30689911760](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30689911760)
- canonical packet-patch job: `91342674259`
- canonical refined-topology job: `91342674164`
- result: success

### Canonical packet-patch job

The job cloned the canonical repository read-only, checked out exact commit `77ec9be…`, verified the canonical/imported source blob equality, copied canonical source into the verifier checkout, and ran the packet verifier twice.

Verifier operations:

```sh
patch --batch --forward --fuzz=0 -p1 \
  -i patches/0001-coverage-own-selected-backend-group.patch
python3 -m py_compile baseline-coverage.py status-only-coverage.py group-owned/coverage.py
```

Results on both passes:

- zero-fuzz patch application: success;
- Python compilation: success;
- six tests: 6/6;
- imported baseline: status 0 after deliberate release, surviving nested work, later work;
- status-only comparator: status 130 after release, surviving nested work, later work;
- group candidate: status 130, no live responsive in-group process, no later work;
- imported foreground-group SIGINT: already clean;
- group candidate unsignaled: success;
- source-shape distinctions: success.

Artifact:

- ID: `8815289674`
- name: `unit-11-canonical-upstream-gate`
- SHA-256: `25e62dec929f27e628816568d6264f2bee45474c00b00c3c047f53209608ef1d`

### Canonical refined-topology job

The job materialized exact PR #339 commit `8253ab2ef6fed22b34fc5f5d6d20cda75c25e2c7`, verified exact test blobs, copied canonical `coverage.py`, `run_null.sh`, and `run_qemu.sh` into that carrier, compiled source and tests, and ran:

```sh
python3 -m unittest -v \
  tests.test_mmdebstrap_coverage_process_group \
  tests.test_mmdebstrap_coverage_qemu_process_group \
  tests.test_mmdebstrap_coverage_sudo_process_group
```

Exact regression blobs:

| Module | Blob |
| --- | --- |
| parent-only status fixture | `9bedaa7cd2368f8679de9948d9fecb3fe75c6bd2` |
| null/process-group fixture | `1649c10f8d6639bd26a42b9ab3587b64d84e072c` |
| refined QEMU fixture | `0c2a050faf8e98320fc0c4fe4634d46bdf7f0dfa` |
| actual sudo fixture | `8cc7cffb129595a5e4b967385616fbeede4814db` |

Results:

- first pass: 14/14 in 3.874 seconds;
- immediate rerun: 14/14 in 3.599 seconds;
- skips: none;
- actual passwordless-sudo root-worker controls: executed;
- QEMU losing controls: exact Python SIGINT-handler receipt observed before deliberate survivor release;
- group candidate: status 130, no live responsive in-group work, no later marker;
- unsignaled controls: success.

Artifact:

- ID: `8815290820`
- name: `unit-11-canonical-refined-topology-gate`
- SHA-256: `63634782bfd230129238ee71aa60ad83ae5b43dfcf3291123cfdbd0770bdf63e`

### Cleanup and rerun

Both jobs completed on Ubuntu 24.04 runners. Temporary directories completed, owned groups settled, deliberate losing-control survivors were released and reaped, and both complete matrices passed an immediate rerun.

## Final packet-head gate

- exact packet head: `d232e4fdd67cf0592e129a60534e984dcbec6bfe`
- workflow run: [30690101504](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30690101504)
- canonical refined-topology job: `91343158161`, success
- canonical packet-patch job: `91343158226`, success

This is the exact-head execution receipt for PR #401.

## Historical repository gates

### Mechanism generation

- source head: `e90fc438f530f7bd78ffd6fd1ba24c665bd96913`
- run: `30632491641`
- job: `91161937871`
- result: 359 tests passed in 167.224 seconds
- included patch validation, compilation, null/QEMU-wrapper/sudo lifecycle controls, shell syntax, and command-help checks.

### Retained evidence generation

- source head: `dfc6d0503fb844f4c428ce16a567a9fdcd35280a`
- generated merge: `24c7ba065b4c50fee76a07b0f6d6cb000d4684d8`
- run: `30633602052`
- job: `91165600654`
- result: 340 uniquely discovered tests passed.

### QEMU refinement generation

- source head: `8253ab2ef6fed22b34fc5f5d6d20cda75c25e2c7`
- run: `30633578396`
- job: `91165522248`
- result: 269 tests passed.

Historical PRs #313 and #339 are now closed with evidence transferred to PR #401. PR #406 is closed as a superseded ancestry-only restack.

## Packet-local process model

Environment:

- date: 2026-08-01
- kernel: Linux 6.12.13 x86_64
- Python: 3.13.5
- evidence class: `model-executed`

Reviewed replay:

```sh
cd upstream/packets/13-mmdebstrap-process-group-cancellation/fixtures/local-process-model
python3 -m py_compile child.py driver.py harness.py harness_original.py wrapper.py
python3 harness.py
```

Output:

```text
variant=baseline rc=0 later_work=true child_live=false
variant=status rc=130 later_work=true child_live=false
variant=group rc=130 later_work=false child_live=false
```

- compilation: success;
- original run: success;
- closeout rerun: success;
- reviewed relocatable replay: success;
- receipt: [`receipts/2026-08-01-local-process-model.md`](./receipts/2026-08-01-local-process-model.md);
- retained source: [`fixtures/local-process-model/`](./fixtures/local-process-model/).

## Unexecuted gates and limits

- no controlled canonical fork candidate branch exists;
- no upstream-native regression has been committed to a clean target branch;
- full mirror-backed `coverage.py` matrix with prepared Debian mirror state was not run;
- real QEMU/debvm and prepared-mirror package operations were not run;
- non-Linux behavior was not run;
- upstream maintainer CI/review has not occurred;
- workflow retirement after receipt transfer remains undecided.

## Required next execution

1. create or select a controlled fork of canonical `josch/mmdebstrap` after internal authority permits it;
2. refresh canonical `main` and record the exact base;
3. create the clean candidate branch;
4. apply the upstream-root patch with zero fuzz;
5. add an upstream-native deterministic regression;
6. rerun focused controls if the base changed;
7. run the project-declared ordinary mirror-backed/source gate;
8. record exact target head, commands, counts, skips, cleanup, rerun, and artifacts;
9. complete independent review of the clean target diff.

Until those steps run, unit 13 carries no clean-target-branch or ordinary-upstream-gate claim.
