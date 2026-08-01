# Upstream unit 13 — mmdebstrap process-group cancellation

## In simple words

`coverage.py` launches backend wrappers that can own nested work. On parent-only SIGINT, terminating only the immediate wrapper can leave descendants running. The selected patch starts each backend in its own session/process group, sends TERM to that group, waits for the wrapper, prints an interruption diagnostic, and exits 130.

The exact patch now exists on a clean controlled mmdebstrap branch and passed a controlled target-repository gate. The clean branch contains only the one-file product change. Exact baseline/status/group controls passed twice, and the refined null/QEMU-wrapper/passwordless-sudo matrix passed twice with no skips.

Under the strict `teamleaderleo/fieldwork#435` completion contract, the unit remains `REPAIR`: the project-declared mirror-backed ordinary gate, a real target-native regression integration or deliberate source-only decision, workflow retirement, and eligible independent final target-diff acceptance remain unresolved.

## Current disposition

`REPAIR`

The bounded mechanism, clean target identity, patch equivalence, compilation, and focused target execution are accepted. No public upstream interaction is authorized or performed.

## Assignment

- outer unit: `13`
- contribution: `fix: cancel backend process groups during interruption`
- packet: `upstream/packets/13-mmdebstrap-process-group-cancellation/`
- packet branch: `p0/435-unit-13-mmdebstrap-process-group`
- packet base: `920f87cb25dd0cc7901d59ea2019cd4b4a193b94`
- packet review surface: `teamleaderleo/fieldwork#439`
- canonical Linux Fieldwork unit: issue `#397`, unit `11`
- public upstream contact: `false`

## Canonical target identity

- project: mmdebstrap
- canonical repository: `https://gitlab.mister-muffin.de/josch/mmdebstrap`
- canonical branch: `main`
- exact canonical base: `77ec9be5417ee44c96343d2347145585da1b1f94`
- canonical/imported `coverage.py` blob: `9a522484aef05deae514a98e4b6adf5feb6c886d`
- canonical `run_null.sh` blob: `e0a8c106f9d3d636baea286d2ab33834748dffc9`
- canonical `run_qemu.sh` blob: `426aeeb854173569b24e64d6eb85019f45bdf0b6`
- Debian packaging VCS: `https://salsa.debian.org/debian/mmdebstrap.git`

Forgejo `josch/mmdebstrap` is the contribution destination. Salsa is packaging context.

## Clean controlled target branch

- controlled repository: `teamleaderleo/mmdebstrap`
- canonical snapshot branch: `linux-fieldwork/upstream-main-snapshot`
- snapshot/base commit: `77ec9be5417ee44c96343d2347145585da1b1f94`
- clean source branch: `linux-fieldwork/unit-11-coverage-backend-cancellation`
- clean source head: `431614b3af58ba4f70791aa1d42cf5b71c965dd2`
- candidate `coverage.py` blob: `9e31f21cf37228257b5e0705d9ecb13b7a66e40f`
- ancestry: one commit ahead, zero behind
- changed-file fence: `coverage.py` only
- diff: 8 additions, 3 deletions

The clean source commit contains no Fieldwork notes, test carriers, receipts, workflows, or temporary research files.

## Canonical packet and historical carriers

### Current canonical packet

- PR: `teamleaderleo/linux-fieldwork#401`
- branch: `upstream/unit-11-coverage-backend-cancellation`
- current packet head: `1de1aee093191a828c1a7649c5d27bc5e8c12e45`
- upstream-root patch blob: `f1a2c75adfa009b6f1ac29e5a31bef526400444f`
- internal #397 state: `READY FOR AUTHORIZATION`
- outer #435 state: `REPAIR`

The two states use different completion contracts. Issue #397 treats the packet as send/hold ready. Issue #435 additionally requires the unresolved target integration and final-review boundaries listed below.

### Historical carriers

- selected mechanism/evidence carrier: closed `linux-fieldwork#313`, head `dfc6d0503fb844f4c428ce16a567a9fdcd35280a`
- executed mechanism generation: `e90fc438f530f7bd78ffd6fd1ba24c665bd96913`
- refined QEMU evidence: closed `linux-fieldwork#339`, head `8253ab2ef6fed22b34fc5f5d6d20cda75c25e2c7`
- superseded ancestry-only restack: closed `linux-fieldwork#406`, head `e82b9b059850fce1efcf8daadef89049495a8b27`

Unique evidence from the closed carriers is retained in PR #401.

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

Proposed upstream title:

`coverage: cancel the selected backend process group on SIGINT`

## Exact current target execution

Internal controlled-fork execution surface:

- PR: `teamleaderleo/mmdebstrap#2`
- PR base: `linux-fieldwork/upstream-main-snapshot@77ec9be5417ee44c96343d2347145585da1b1f94`
- runner branch/head: `linux-fieldwork/unit-11-coverage-backend-cancellation-runner@f0319d53f515174c3794237f34f76699182ac509`
- generated merge tested: `bf1f0cfde0ec6e0691c0dfb7d4656aafe3deab48`
- workflow run: `30706007117`
- result: success

### Candidate equivalence and null job

- job: `91385135488`
- exact base/source/blob/packet identities: success
- packet patch applied with zero fuzz
- patch-materialized candidate byte-equal to clean target `coverage.py`
- target candidate compilation: success
- first packet pass: 6/6 in 1.421 seconds
- immediate rerun: 6/6 in 1.420 seconds
- artifact: `8820336271`, `unit-11-target-null-gate`
- SHA-256: `97eba28273b50dfcf51c32a2fe4cf49aa50da5634a3aaba6b052ad3728ae1ce8`

### Refined topology job

- job: `91385135449`
- exact PR #339 carrier and regression blobs: verified
- compilation: success
- first null/QEMU-wrapper/passwordless-sudo pass: 14/14 in 4.246 seconds
- immediate rerun: 14/14 in 4.367 seconds
- skips: none
- actual passwordless-sudo controls: executed
- artifact: `8820337503`, `unit-11-target-refined-topology-gate`
- SHA-256: `8d72b079fa9e30ee92bdf28cf217e9df3e4ae7a5ffeb7374b76950313bf24614`

Both jobs uploaded receipts and completed runner orphan-process cleanup.

Receipt: [`receipts/2026-08-01-controlled-target-branch.md`](./receipts/2026-08-01-controlled-target-branch.md).

## Canonical and historical execution

Canonical Linux Fieldwork run `30689911760` passed against exact base `77ec9be...`:

- zero-fuzz patch application and compilation twice;
- packet matrix 6/6 twice;
- refined matrix 14/14 twice, no skips;
- cleanup and immediate rerun success;
- artifacts `8815289674` and `8815290820` with recorded digests.

Final canonical packet head `d232e4fdd67cf0592e129a60534e984dcbec6bfe` passed exact-head run `30690101504`. Current packet head `1de1aee093191a828c1a7649c5d27bc5e8c12e45` passed run `30706149498`.

Historical repository receipts remain:

- CI `30632491641`: 359 tests passed at mechanism head `e90fc438...`;
- CI `30633602052`: 340 uniquely discovered tests passed at evidence head `dfc6d050...`;
- CI `30633578396`: 269 tests passed at QEMU refinement `8253ab2e...`.

## Target test-layout decision

The canonical project declares its ordinary suite through `make_mirror.sh`, `coverage.sh`, `coverage.py`, `coverage.txt`, and shell-template entries under `tests/`. `coverage.py` rejects non-dot `tests/` entries that lack matching `coverage.txt` records.

A guessed Python unit-test file under `tests/` would therefore violate the target suite inventory and run through the wrong harness. No fake target-native path is claimed. The focused regression remains in the exact internal carrier until one of these is selected:

1. integrate a deterministic scenario into the real `coverage.txt`/shell-template harness;
2. add a deliberately separate accepted self-test surface;
3. make a documented source-only submission decision while retaining the external reproducer.

## Claim boundary

Established:

- exact canonical base and source blob;
- clean one-file target branch and candidate blob;
- zero-fuzz patch equivalence;
- target candidate compilation;
- caller-owned group before backend execution;
- parent-only SIGINT sends TERM to the group;
- tested responsive null, QEMU-wrapper, and sudo groups settle without later work;
- ordinary unsignaled focused controls succeed;
- cleanup and immediate rerun succeed.

Limits:

- `proc.wait()` waits for the wrapper, not arbitrary descendant drain;
- TERM-resistant or TERM-deferring descendants can survive;
- repeated SIGINT can interrupt cleanup;
- descendants can escape by creating another group/session;
- real QEMU/debvm, prepared-mirror package operations, direct `/dev/tty`, and non-Linux execution remain outside the claim;
- the project-declared full mirror-backed ordinary gate has not run at clean target head `431614b3...`;
- upstream maintainer review has not occurred.

Issue #341 and closed PR #347 retain stronger cleanup-policy research. Escalation remains unselected.

## Remaining work in strict order

1. decide the target-native regression integration or explicitly accept a source-only submission shape;
2. run the project-declared mirror-backed/source ordinary gate at `431614b3af58ba4f70791aa1d42cf5b71c965dd2`;
3. decide whether internal target PR #2 and its workflow are retained or closed after evidence transfer;
4. obtain eligible independent complete-diff acceptance for the clean target branch;
5. refresh public overlap, contribution-policy, and AI-disclosure checks immediately before any public action;
6. synchronize final upstream drafts with the authorized submission shape;
7. obtain explicit authority for the exact public interaction.

## Current blockers

- target-native regression integration or explicit source-only decision: pending;
- project-declared ordinary mirror-backed/source gate: unexecuted at the clean target head;
- runner retention/retirement decision: pending;
- eligible independent final clean-target-diff acceptance: pending;
- public contact authority: `false`.

## Packet navigation

- [`DEEP_DIVE.md`](./DEEP_DIVE.md)
- [`APPROACHES.md`](./APPROACHES.md)
- [`TESTS.md`](./TESTS.md)
- [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
- [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)
- [`REVIEW.md`](./REVIEW.md)
- [`patches/`](./patches/)
- [`receipts/`](./receipts/)
- [`fixtures/local-process-model/`](./fixtures/local-process-model/)

## Continuation-ready handoff

Resume from this packet, outer PR `teamleaderleo/fieldwork#439`, canonical packet `teamleaderleo/linux-fieldwork#401`, clean source `teamleaderleo/mmdebstrap@431614b3...`, and internal target runner PR `teamleaderleo/mmdebstrap#2`.

Preserve `REPAIR` under #435 until the target integration decision, ordinary gate, and eligible final target review are complete. Keep escalation separate. Perform no canonical-upstream public interaction without explicit authority.
