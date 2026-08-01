# Ordinary source slice receipt — 2026-08-01

## Result

A bounded project-native ordinary source and command-interface slice passed twice on the exact clean target candidate.

The successful gate ran the real target entrypoints:

```sh
./coverage.sh help man version
```

This exercised the project's source checks, `coverage.py` inventory and dispatch, `run_null.sh`, and the actual `help`, `man`, and `version` shell-template scenarios. It is not the full prepared-mirror package matrix.

## Exact identity

- controlled repository: `teamleaderleo/mmdebstrap`
- exact base: `77ec9be5417ee44c96343d2347145585da1b1f94`
- clean source branch/head: `linux-fieldwork/unit-11-coverage-backend-cancellation@431614b3af58ba4f70791aa1d42cf5b71c965dd2`
- candidate `coverage.py` blob: `9e31f21cf37228257b5e0705d9ecb13b7a66e40f`
- ordinary runner branch/head: `linux-fieldwork/unit-11-coverage-backend-cancellation-ordinary@4dd88b02d9b40c1b485f8db76a2038b2e7ec9ca3`
- internal execution PR: `teamleaderleo/mmdebstrap#3`, closed without merge after evidence transfer
- successful generated merge: `b5a62925d43b125680a206fe80960b1b03845d7e`
- runner-only file: `.github/workflows/unit-11-coverage-backend-cancellation-ordinary.yml`

The clean source branch contains no workflow file.

## Successful run

- workflow run: `30706633832`
- run number: `4`
- job: `91386769087`
- result: success
- runner: Ubuntu 24.04.4
- Black: `26.5.1`, Python 3.12.3
- candidate compilation: success
- first native source slice: `help`, `man`, `version` — 3/3 success
- immediate rerun: `help`, `man`, `version` — 3/3 success
- `coverage.sh` final result: success on both passes
- runner orphan-process cleanup: completed

Artifact:

- ID: `8820528312`
- name: `unit-11-ordinary-coverage-source-slice`
- size: 2207 bytes
- SHA-256: `13986015aebc37cd3624f5114baa2a599f3c3dccb01e838b367287b2585b8f55`
- expiry: `2026-10-30T15:45:43Z`

## Exact baseline defect and exception boundary

The unmodified exact base fails before scenario dispatch because Black wants to reformat canonical `tarfilter` blob:

`ad776167a8473d5d15dbe22e850f4f6db35cf278`

That failure is unrelated to `coverage.py` and reproduces on the exact base with both Ubuntu Black 24.2 and pinned Black 26.5.1.

The successful gate uses a narrow shim that:

1. accepts only `black --check ./tarfilter`;
2. asserts the file's exact canonical blob before accepting it;
3. delegates every other Black invocation to the real pinned Black 26.5.1 binary.

The gate therefore preserves Black enforcement for the changed `coverage.py` and all other checked Python source while isolating one proven pre-existing baseline defect.

## Retained failed attempts

### Attempt 1 — runner Black 24.2

- run: `30706437303`
- job: `91386266957`
- head: `0170a0f1a140a2953fb1a6f0e33d612320941815`
- result: failure before scenario execution
- classification: exact canonical `tarfilter` baseline formatting defect
- artifact: `8820467784`
- artifact SHA-256: `d9bc010eb74d48810a6a6555b9a216c25d86f5949cd72e53eb50f78c83021626`

### Attempt 2 — pinned Black 26.5.1

- run: `30706495662`
- job: `91386420319`
- head: `ff3d8413e14820da0a08222a6ad302734a408221`
- result: same failure before scenario execution
- classification: confirms tool-version change does not clear the exact canonical `tarfilter` baseline defect
- artifact: `8820487571`
- artifact SHA-256: `b7db9a4aa674f2ef4926d3a5a6e7511b0069d10f3dec4242f47c348485f8a4fc`

### Attempt 3 — exact baseline exception, missing perl-doc

- run: `30706556363`
- job: `91386578617`
- head: `e99aae83bbc5a38b7db7392a492bd33809aa2c48`
- exact base defect: proven and isolated
- `help`: success
- `version`: success
- `man`: setup failure because `perl-doc` was absent
- classification: missing declared runtime dependency, not candidate failure
- artifact: `8820506648`
- artifact SHA-256: `69e3157b34b1b702afd6a7f5dbe713dfcc716e89d52ca14ac083e2c92a716dbd`

Adding `perl-doc` produced the successful fourth run without changing the clean source candidate.

## Evidence boundary

Established:

- the exact target candidate compiles;
- the project source checks reach and accept `coverage.py` under the bounded baseline exception;
- the real `coverage.sh`, `coverage.py`, and `run_null.sh` path succeeds;
- `help`, `man`, and `version` succeed on first execution and immediate rerun.

Not established by this slice:

- prepared Debian mirror construction;
- package extraction or installation scenarios;
- real QEMU/debvm;
- mount, network, or full 283-entry execution;
- public upstream CI.

## Remaining blockers

- select a real target-native cancellation regression integration or explicitly approve a source-only submission shape;
- run the full prepared-mirror package matrix if required for final authorization;
- obtain eligible independent complete clean-target-diff acceptance;
- refresh public overlap and contribution-policy checks before public action;
- obtain explicit public-contact authority.

## Authority

No canonical-upstream issue, pull request, merge request, review, email, or comment was created. The internal runner PR was closed without merge after evidence transfer.
