# Unit 13 tests and receipts

## Current result

The exact clean target candidate exists and has passed:

- zero-fuzz patch equivalence and compilation;
- the six-control baseline/status/group matrix twice;
- the refined fourteen-control null/QEMU-wrapper/passwordless-sudo matrix twice with no skips;
- a bounded project-native ordinary source and command-interface slice twice through the real `coverage.sh`, `coverage.py`, and `run_null.sh` path.

The full prepared-mirror 283-entry package matrix, real QEMU/debvm, and public upstream CI remain unexecuted.

## Exact identities

| Field | Value |
| --- | --- |
| Canonical repository | `https://gitlab.mister-muffin.de/josch/mmdebstrap` |
| Canonical base | `77ec9be5417ee44c96343d2347145585da1b1f94` |
| Base `coverage.py` blob | `9a522484aef05deae514a98e4b6adf5feb6c886d` |
| Canonical `run_null.sh` blob | `e0a8c106f9d3d636baea286d2ab33834748dffc9` |
| Canonical `run_qemu.sh` blob | `426aeeb854173569b24e64d6eb85019f45bdf0b6` |
| Retained patch blob | `f1a2c75adfa009b6f1ac29e5a31bef526400444f` |
| Controlled repository | `teamleaderleo/mmdebstrap` |
| Clean source branch | `linux-fieldwork/unit-11-coverage-backend-cancellation` |
| Clean source head | `431614b3af58ba4f70791aa1d42cf5b71c965dd2` |
| Candidate `coverage.py` blob | `9e31f21cf37228257b5e0705d9ecb13b7a66e40f` |
| Clean diff | one commit; `coverage.py` only; 8 additions, 3 deletions |
| Clean review surface | `teamleaderleo/mmdebstrap#4` |

## Evidence matrix

| Claim | Evidence | Limit |
| --- | --- | --- |
| exact base carries wrapper-only termination | canonical commit and blob above | exact base only |
| retained patch equals clean target candidate | target run `30706007117`, job `91385135488` | exact head/blob pair |
| wrapper-only baseline permits later work | six-control and refined matrices | modeled responsive topologies |
| status-only 130 still permits later work | same matrices | modeled responsive topologies |
| group candidate returns 130 without later work | six-control and refined matrices | in-group TERM-responsive work |
| target candidate compiles | runs `30706007117` and `30706633832` | Python 3.12 hosted runner |
| null/QEMU-wrapper/sudo focused controls pass | run `30706007117` | real QEMU omitted |
| project-native ordinary source slice passes | run `30706633832` | `help`, `man`, `version`; no package build |
| immediate rerun remains clean | both target runs | hosted Ubuntu 24.04 |
| full prepared-mirror matrix passes | not run | explicit remaining evidence limit |
| public upstream CI passes | not run | no public contact authorized |

## Focused controlled-target gate

Internal execution surface: closed `teamleaderleo/mmdebstrap#2`.

- runner branch/head: `linux-fieldwork/unit-11-coverage-backend-cancellation-runner@f0319d53f515174c3794237f34f76699182ac509`
- generated merge: `bf1f0cfde0ec6e0691c0dfb7d4656aafe3deab48`
- workflow run: `30706007117`
- result: success

### Candidate equivalence and null job

- job: `91385135488`
- exact base/source/blob/packet identities: success
- patch application: zero fuzz
- patch-materialized candidate byte-equal to clean target `coverage.py`
- target compilation: success
- first packet pass: 6/6 in 1.421 seconds
- immediate rerun: 6/6 in 1.420 seconds
- artifact: `8820336271`
- SHA-256: `97eba28273b50dfcf51c32a2fe4cf49aa50da5634a3aaba6b052ad3728ae1ce8`

### Refined topology job

- job: `91385135449`
- exact PR #339 carrier and four regression blobs: verified
- compilation: success
- first null/QEMU-wrapper/passwordless-sudo pass: 14/14 in 4.246 seconds
- immediate rerun: 14/14 in 4.367 seconds
- skips: none
- actual passwordless-sudo controls: executed
- artifact: `8820337503`
- SHA-256: `8d72b079fa9e30ee92bdf28cf217e9df3e4ae7a5ffeb7374b76950313bf24614`

Both jobs uploaded receipts and completed runner orphan-process cleanup.

Receipt: [`receipts/2026-08-01-controlled-target-branch.md`](./receipts/2026-08-01-controlled-target-branch.md).

## Project-native ordinary source slice

Internal execution surface: closed `teamleaderleo/mmdebstrap#3`.

- runner branch/head: `linux-fieldwork/unit-11-coverage-backend-cancellation-ordinary@4dd88b02d9b40c1b485f8db76a2038b2e7ec9ca3`
- generated merge: `b5a62925d43b125680a206fe80960b1b03845d7e`
- workflow run: `30706633832`
- job: `91386769087`
- result: success
- runner: Ubuntu 24.04.4
- Black: 26.5.1, Python 3.12.3

Command path:

```sh
./coverage.sh help man version
```

The gate used the real project source checks, `coverage.py` inventory and dispatch, `run_null.sh`, and the native `help`, `man`, and `version` shell-template scenarios.

Results:

- exact candidate compilation: success;
- first pass: 3/3;
- immediate rerun: 3/3;
- `coverage.sh`: success twice;
- orphan-process cleanup: completed.

Artifact:

- ID: `8820528312`
- name: `unit-11-ordinary-coverage-source-slice`
- size: 2207 bytes
- SHA-256: `13986015aebc37cd3624f5114baa2a599f3c3dccb01e838b367287b2585b8f55`
- expiry: `2026-10-30T15:45:43Z`

### Exact baseline exception

The unmodified exact base fails before scenario dispatch because Black wants to reformat unchanged canonical `tarfilter` blob `ad776167a8473d5d15dbe22e850f4f6db35cf278`.

The successful gate accepts only `black --check ./tarfilter` after asserting that exact blob. Every other Black invocation is delegated to the real pinned Black 26.5.1 binary. The changed `coverage.py` remains checked normally.

### Retained setup negatives

| Run/job | Result | Artifact |
| --- | --- | --- |
| `30706437303` / `91386266957` | Ubuntu Black 24.2 rejected exact canonical `tarfilter` before scenarios | `8820467784`, SHA-256 `d9bc010eb74d48810a6a6555b9a216c25d86f5949cd72e53eb50f78c83021626` |
| `30706495662` / `91386420319` | Black 26.5.1 confirmed the same base defect | `8820487571`, SHA-256 `b7db9a4aa674f2ef4926d3a5a6e7511b0069d10f3dec4242f47c348485f8a4fc` |
| `30706556363` / `91386578617` | base defect isolated; `help` and `version` passed; `man` exposed missing `perl-doc` | `8820506648`, SHA-256 `69e3157b34b1b702afd6a7f5dbe713dfcc716e89d52ca14ac083e2c92a716dbd` |

Adding `perl-doc` produced the successful fourth run without changing the clean source candidate.

Receipt: [`receipts/2026-08-01-ordinary-source-slice.md`](./receipts/2026-08-01-ordinary-source-slice.md).

## Canonical packet gate

Linux Fieldwork run `30689911760` against exact canonical source:

- packet-patch job `91342674259`: zero-fuzz application, compilation, and 6/6 twice;
- refined topology job `91342674164`: 14/14 twice, no skips;
- artifacts `8815289674` and `8815290820` with retained digests;
- cleanup and immediate rerun: success.

Packet head `d232e4fdd67cf0592e129a60534e984dcbec6bfe` passed run `30690101504`. Later packet heads carry the controlled-target receipts and have their own exact-head runs recorded on PR #401.

## Historical repository gates

- mechanism head `e90fc438f530f7bd78ffd6fd1ba24c665bd96913`: run `30632491641`, job `91161937871`, 359 tests passed;
- retained evidence head `dfc6d0503fb844f4c428ce16a567a9fdcd35280a`: run `30633602052`, job `91165600654`, 340 uniquely discovered tests passed;
- refined QEMU head `8253ab2ef6fed22b34fc5f5d6d20cda75c25e2c7`: run `30633578396`, job `91165522248`, 269 tests passed.

PRs #313 and #339 are closed with evidence transferred. PR #406 is closed superseded.

## Packet-local model

```text
variant=baseline rc=0 later_work=true child_live=false
variant=status rc=130 later_work=true child_live=false
variant=group rc=130 later_work=false child_live=false
```

The original run, closeout rerun, and reviewed relocatable replay passed. See [`receipts/2026-08-01-local-process-model.md`](./receipts/2026-08-01-local-process-model.md).

## Submission-shape decision

The clean target diff is deliberately source-only.

The native suite treats every non-dot `tests/` entry as a shell-template package scenario indexed by `coverage.txt`. Testing this outer orchestrator from inside that same harness would require a recursive mini-coverage fixture substantially larger than the product fix. The exact deterministic reproducer and target-run receipts remain in the packet. A native recursive regression can be added later if an eligible reviewer or upstream maintainer requires it.

Clean review surface: open draft `teamleaderleo/mmdebstrap#4`.

## Remaining evidence limits

- full prepared-mirror 283-entry package matrix;
- real QEMU/debvm and package operations;
- non-Linux behavior;
- eligible independent complete clean-diff acceptance;
- public upstream CI and maintainer review.

No public upstream interaction is authorized or performed.
