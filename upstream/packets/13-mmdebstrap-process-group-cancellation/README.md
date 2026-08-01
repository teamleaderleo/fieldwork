# Upstream unit 13 — mmdebstrap process-group cancellation

## Current disposition

`REPAIR`

The technical source unit is complete for its bounded TERM-responsive claim. The exact clean target branch, focused target execution, project-native ordinary source slice, source-only submission-shape decision, and clean one-file review surface now exist.

Under the strict `teamleaderleo/fieldwork#435` contract, the remaining completion blocker is eligible independent complete-diff acceptance. Public contact authority remains `false`. The full prepared-mirror package matrix remains an explicit evidence limit rather than a blocker for this narrow source-only lifecycle change.

## In simple words

`coverage.py` launches backend wrappers that can own nested work. On parent-only SIGINT, terminating only the wrapper can leave descendants running. The selected patch starts each backend in its own session/process group, sends TERM to that group, waits for the wrapper, prints `interrupted by SIGINT`, and exits 130.

Exact target execution distinguishes:

| Variant | Status | Later work |
| --- | ---: | --- |
| imported wrapper-only baseline | 0 after release | yes |
| status-only predecessor | 130 after release | yes |
| selected group candidate | 130 | no |

## Assignment and routing

- outer unit: `13`
- contribution: `fix: cancel backend process groups during interruption`
- packet branch: `p0/435-unit-13-mmdebstrap-process-group`
- packet review surface: `teamleaderleo/fieldwork#439`
- canonical Linux Fieldwork unit: issue `#397`, unit `11`
- canonical packet review: `teamleaderleo/linux-fieldwork#401`
- public upstream contact: unauthorized; none occurred

## Canonical target identity

- canonical repository: `https://gitlab.mister-muffin.de/josch/mmdebstrap`
- canonical branch: `main`
- exact canonical base: `77ec9be5417ee44c96343d2347145585da1b1f94`
- base `coverage.py` blob: `9a522484aef05deae514a98e4b6adf5feb6c886d`
- canonical `run_null.sh` blob: `e0a8c106f9d3d636baea286d2ab33834748dffc9`
- canonical `run_qemu.sh` blob: `426aeeb854173569b24e64d6eb85019f45bdf0b6`
- retained patch blob: `f1a2c75adfa009b6f1ac29e5a31bef526400444f`
- Debian packaging VCS: `https://salsa.debian.org/debian/mmdebstrap.git`

Forgejo is the contribution destination. Salsa is packaging context.

## Clean controlled target source

- controlled repository: `teamleaderleo/mmdebstrap`
- exact snapshot branch: `linux-fieldwork/upstream-main-snapshot`
- clean source branch: `linux-fieldwork/unit-11-coverage-backend-cancellation`
- clean source head: `431614b3af58ba4f70791aa1d42cf5b71c965dd2`
- candidate `coverage.py` blob: `9e31f21cf37228257b5e0705d9ecb13b7a66e40f`
- ancestry: one commit ahead of the exact base, zero behind
- complete diff: `coverage.py` only; 8 additions, 3 deletions
- clean internal review surface: `teamleaderleo/mmdebstrap#4`
- review state: ready for independent review

The clean source branch contains no Fieldwork notes, fixtures, receipts, workflows, or unrelated source.

## Selected product change

```python
proc = subprocess.Popen(argv, start_new_session=True)
try:
    proc.wait()
except KeyboardInterrupt:
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    proc.wait()
    print("interrupted by SIGINT", file=sys.stderr)
    raise SystemExit(130)
```

Proposed title:

`coverage: cancel the selected backend process group on SIGINT`

## Focused target execution

Closed internal execution PR: `teamleaderleo/mmdebstrap#2`.

- workflow run: `30706007117`
- generated merge: `bf1f0cfde0ec6e0691c0dfb7d4656aafe3deab48`
- result: success

Candidate equivalence/null job `91385135488`:

- zero-fuzz patch application;
- byte equality with clean target `coverage.py`;
- target compilation;
- 6/6 in 1.421 seconds;
- immediate rerun 6/6 in 1.420 seconds;
- artifact `8820336271`;
- SHA-256 `97eba28273b50dfcf51c32a2fe4cf49aa50da5634a3aaba6b052ad3728ae1ce8`.

Refined topology job `91385135449`:

- exact regression carrier and blobs verified;
- null/QEMU-wrapper/passwordless-sudo matrix 14/14 in 4.246 seconds;
- immediate rerun 14/14 in 4.367 seconds;
- no skips; actual sudo controls executed;
- artifact `8820337503`;
- SHA-256 `8d72b079fa9e30ee92bdf28cf217e9df3e4ae7a5ffeb7374b76950313bf24614`.

See [`receipts/2026-08-01-controlled-target-branch.md`](./receipts/2026-08-01-controlled-target-branch.md).

## Project-native ordinary source slice

Closed internal execution PR: `teamleaderleo/mmdebstrap#3`.

- workflow run: `30706633832`
- job: `91386769087`
- generated merge: `b5a62925d43b125680a206fe80960b1b03845d7e`
- result: success
- command path: `./coverage.sh help man version`
- first pass: 3/3
- immediate rerun: 3/3
- artifact `8820528312`
- SHA-256 `13986015aebc37cd3624f5114baa2a599f3c3dccb01e838b367287b2585b8f55`

The exact unmodified base fails before scenario dispatch because Black wants to reformat unchanged canonical `tarfilter` blob `ad776167a8473d5d15dbe22e850f4f6db35cf278`. The successful gate accepts only that exact blob for `black --check ./tarfilter` and delegates all other Black checks to pinned Black 26.5.1. The changed `coverage.py` remains checked normally.

See [`receipts/2026-08-01-ordinary-source-slice.md`](./receipts/2026-08-01-ordinary-source-slice.md).

## Source-only submission shape

The target suite treats every non-dot `tests/` entry as a shell-template package scenario indexed by `coverage.txt`. Testing the outer coverage orchestrator from inside that same harness would require a recursive miniature coverage tree substantially larger than the product fix.

The clean contribution is therefore deliberately source-only. The deterministic baseline/candidate reproducer and exact target receipts remain in the packet. A native recursive regression is a reopen item if an eligible reviewer or upstream maintainer requires it.

See [`receipts/2026-08-01-source-only-submission-shape.md`](./receipts/2026-08-01-source-only-submission-shape.md).

## Supporting canonical and historical evidence

Canonical Linux Fieldwork run `30689911760` passed zero-fuzz application, compilation, 6/6 twice, and 14/14 twice. Packet head `d232e4fdd67cf0592e129a60534e984dcbec6bfe` passed exact-head run `30690101504`.

Historical repository gates:

- `e90fc438f530f7bd78ffd6fd1ba24c665bd96913`: 359 tests passed;
- `dfc6d0503fb844f4c428ce16a567a9fdcd35280a`: 340 unique tests passed;
- `8253ab2ef6fed22b34fc5f5d6d20cda75c25e2c7`: 269 tests passed.

Historical PRs #313 and #339 are closed with evidence transferred. PR #406 is closed superseded.

## Claim boundary

Established:

- exact canonical base and clean target identity;
- zero-fuzz patch and source byte equivalence;
- target compilation;
- group-wide TERM delivery for tested responsive in-group work;
- status 130 and no later work for selected controls;
- unsignaled focused success;
- native ordinary source/interface success twice;
- cleanup and immediate rerun.

Not established:

- arbitrary TERM-resistant descendant drain;
- repeated-SIGINT policy;
- group/session escape handling;
- real QEMU/debvm and prepared-mirror package execution;
- full 283-entry matrix;
- non-Linux behavior;
- public upstream CI or maintainer acceptance.

## Remaining blocker and next safe action

One technical governance blocker remains:

- eligible independent complete review of `teamleaderleo/mmdebstrap#4` at clean head `431614b3af58ba4f70791aa1d42cf5b71c965dd2`.

After acceptance, refresh overlap and contribution-policy checks and request explicit authority for the exact canonical-upstream action. Do not merge or contact upstream without that authority.

## Packet navigation

- [`TESTS.md`](./TESTS.md)
- [`DEEP_DIVE.md`](./DEEP_DIVE.md)
- [`APPROACHES.md`](./APPROACHES.md)
- [`REVIEW.md`](./REVIEW.md)
- [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
- [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)
- [`patches/`](./patches/)
- [`receipts/`](./receipts/)
- [`fixtures/local-process-model/`](./fixtures/local-process-model/)
