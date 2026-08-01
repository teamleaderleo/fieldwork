# Upstream unit 13 — mmdebstrap process-group cancellation

## In simple words

`coverage.py` launches backend wrappers that can own nested work. On parent-only SIGINT, terminating only the immediate wrapper can leave descendants running. The selected patch starts each backend in its own session/process group, sends TERM to that group, waits for the wrapper, prints an interruption diagnostic, and exits 130.

Canonical current-source execution now exists in Linux Fieldwork PR #401. The patch applied with zero fuzz to canonical mmdebstrap `main@77ec9be5417ee44c96343d2347145585da1b1f94`; the six-control packet matrix and refined fourteen-control null/QEMU-wrapper/passwordless-sudo matrix each passed twice. Under the stricter #435 packet contract, delivery remains `REPAIR` because no controlled canonical fork branch, complete target-source diff, ordinary mirror-backed source gate, or independent final target-diff acceptance exists.

## Current disposition

`REPAIR`

The bounded mechanism and focused current-source execution are accepted. Clean upstream delivery remains incomplete.

## Assignment

- unit: `13`
- proposed contribution: `fix: cancel backend process groups during interruption`
- assigned packet: `upstream/packets/13-mmdebstrap-process-group-cancellation/`
- packet branch: `p0/435-unit-13-mmdebstrap-process-group`
- packet base: `920f87cb25dd0cc7901d59ea2019cd4b4a193b94`
- packet review surface: [`teamleaderleo/fieldwork#439`](https://github.com/teamleaderleo/fieldwork/pull/439)
- exact packet head: recorded in the latest unit-13 handoff on `teamleaderleo/fieldwork#435`
- public upstream contact: `false`

## Canonical target identity

- project: mmdebstrap
- canonical repository: `https://gitlab.mister-muffin.de/josch/mmdebstrap`
- canonical branch: `main`
- exact canonical base executed: `77ec9be5417ee44c96343d2347145585da1b1f94`
- last canonical commit touching `coverage.py`: `c82fc7e261c7a2fd85e499484108408fd42331d2`
- canonical/imported `coverage.py` blob: `9a522484aef05deae514a98e4b6adf5feb6c886d`
- canonical `run_null.sh` blob: `e0a8c106f9d3d636baea286d2ab33834748dffc9`
- canonical `run_qemu.sh` blob: `426aeeb854173569b24e64d6eb85019f45bdf0b6`
- Debian packaging VCS: `https://salsa.debian.org/debian/mmdebstrap.git`
- controlled canonical fork: `NEEDS FORK`
- intended clean source branch: `fix/coverage-backend-process-group-current-main`

The earlier packet identified Salsa as the canonical source surface. The current project packet and exact execution establish Forgejo `josch/mmdebstrap` as the contribution destination; Salsa remains packaging context.

## Canonical source package

### Current delivery packet

- pull request: [`teamleaderleo/linux-fieldwork#401`](https://github.com/teamleaderleo/linux-fieldwork/pull/401)
- branch: `upstream/unit-11-coverage-backend-cancellation`
- exact head: `d232e4fdd67cf0592e129a60534e984dcbec6bfe`
- Linux Fieldwork base: `6cc74d846c50b9bbb88247e8a128b67e8c174c1e`
- upstream-root patch blob: `f1a2c75adfa009b6f1ac29e5a31bef526400444f`
- packet copy: [`patches/0001-own-backend-process-group.patch`](./patches/0001-own-backend-process-group.patch)
- internal initiative state: `READY FOR AUTHORIZATION`
- outer #435 state: `REPAIR`

The two state labels use different completion contracts. PR #401 has current-source focused execution and a send/hold packet. #435 also requires a clean fork source head, ordinary target gates, and final clean-target review before `READY`.

### Historical carriers

- mechanism/evidence history: closed [`linux-fieldwork#313`](https://github.com/teamleaderleo/linux-fieldwork/pull/313), head `dfc6d0503fb844f4c428ce16a567a9fdcd35280a`
- exact historically executed mechanism: `e90fc438f530f7bd78ffd6fd1ba24c665bd96913`
- refined QEMU evidence: closed [`linux-fieldwork#339`](https://github.com/teamleaderleo/linux-fieldwork/pull/339), head `8253ab2ef6fed22b34fc5f5d6d20cda75c25e2c7`
- superseded ancestry-only restack: closed [`linux-fieldwork#406`](https://github.com/teamleaderleo/linux-fieldwork/pull/406), head `e82b9b059850fce1efcf8daadef89049495a8b27`

PRs #313 and #339 are closed with unique evidence transferred to PR #401. PR #406 is closed as duplicate ancestry evidence.

## Proposed upstream title

`coverage: cancel the selected backend process group on SIGINT`

## Contribution synopsis

Current source starts a backend with `subprocess.Popen(argv)`. On `KeyboardInterrupt`, it terminates and waits for only the immediate wrapper, then breaks into the ordinary epilogue. Nested shells, pipelines, output followers, foreground operations, or privileged workers can continue.

The selected patch:

- imports `signal`;
- starts the backend with `start_new_session=True`;
- sends `SIGTERM` to `os.killpg(proc.pid, ...)`;
- tolerates an already-exited group;
- waits for the wrapper;
- prints `interrupted by SIGINT`;
- exits 130;
- preserves ordinary result handling.

## Intended clean upstream diff

Known product file:

- `coverage.py`

A maintainable upstream-native regression path remains to be selected. Linux Fieldwork fixtures and packet workflows do not belong in the clean target-source branch.

## Exact tests and receipts

### Canonical current-source execution

Linux Fieldwork run [30689911760](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30689911760) executed the selected patch against canonical mmdebstrap commit `77ec9be5417ee44c96343d2347145585da1b1f94`.

Canonical packet-patch job `91342674259`:

- canonical/imported blob equality: success;
- patch application with `--fuzz=0`: success twice;
- Python compilation: success;
- six null/source/status controls: 6/6 twice;
- artifact: `8815289674`;
- SHA-256: `25e62dec929f27e628816568d6264f2bee45474c00b00c3c047f53209608ef1d`.

Canonical refined-topology job `91342674164`:

- exact PR #339 regression carrier materialized: success;
- canonical source and wrappers inserted: success;
- null/QEMU-wrapper/passwordless-sudo controls: 14/14 twice;
- skips: none;
- actual passwordless-sudo root-worker controls: executed;
- first pass: 3.874 seconds;
- immediate rerun: 3.599 seconds;
- artifact: `8815290820`;
- SHA-256: `63634782bfd230129238ee71aa60ad83ae5b43dfcf3291123cfdbd0770bdf63e`.

Final packet head `d232e4fdd67cf0592e129a60534e984dcbec6bfe` passed exact-head run [30690101504](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30690101504); both canonical jobs succeeded.

### Historical repository execution

- mechanism CI `30632491641`, job `91161937871`: 359 tests passed, including fourteen focused lifecycle controls, compilation, shell syntax, and command-help checks;
- retained-head CI `30633602052`, job `91165600654`: 340 uniquely discovered tests passed;
- QEMU evidence CI `30633578396`, job `91165522248`: 269 tests passed.

These remain exact-head historical evidence. Canonical run `30689911760` is the current-source focused receipt.

### Packet model

- Linux 6.12.13 x86_64, Python 3.13.5;
- original run, closeout rerun, and reviewed relocatable replay: success;
- compile check: success for all retained Python files;
- baseline: status 0 with later work;
- status-only: status 130 with later work;
- group candidate: status 130 without later work;
- receipt: [`receipts/2026-08-01-local-process-model.md`](./receipts/2026-08-01-local-process-model.md);
- source: [`fixtures/local-process-model/`](./fixtures/local-process-model/).

Full detail: [`TESTS.md`](./TESTS.md).

## Claim boundary

Established:

- canonical current `coverage.py` matches the imported baseline blob;
- the upstream-root patch applies with zero fuzz and compiles;
- caller-owned group exists before backend execution;
- parent-only SIGINT sends TERM to that group;
- tested TERM-responsive null, QEMU-wrapper, and sudo groups settle without later work;
- ordinary unsignaled controls succeed;
- cleanup and immediate rerun succeed.

Limits:

- `proc.wait()` waits for the wrapper rather than arbitrary descendant drain;
- TERM-resistant or TERM-deferring descendants can survive;
- repeated SIGINT can interrupt cleanup;
- descendants can escape by creating another group/session;
- real QEMU/debvm, prepared-mirror package operations, direct `/dev/tty`, and non-Linux execution remain unexecuted;
- the full mirror-backed/project-declared ordinary source gate was not run;
- no clean controlled-fork candidate branch or target commit exists;
- upstream maintainer review has not occurred.

Issue #341 and closed PR #347 retain stronger cleanup-policy research. Escalation remains unselected.

## Duplicate and prior-art result

The canonical unit-11 packet records a current visible overlap search with no equivalent public repair. Refresh issue, pull-request, commit, and Debian bug searches immediately before any authorized submission.

Internal prior art:

- status-only finding: issue #141; PRs #143 and #204;
- process-group finding and carrier: issue #306 and closed PR #313;
- superseded carrier repairs: PRs #332 and #336;
- refined QEMU evidence: closed PR #339;
- stronger cleanup comparison: issue #341 and closed PRs #347/#353;
- canonical current-source packet: PR #401;
- superseded current-main restack: closed PR #406.

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
- canonical Linux Fieldwork packet: [`PR #401`](https://github.com/teamleaderleo/linux-fieldwork/pull/401)

## Remaining work in strict order

1. obtain an eligible independent complete-diff review of PR #401 and this outer packet;
2. decide whether the unit-specific execution workflow is retained as a permanent reproducible gate or retired after receipt transfer;
3. obtain or create a controlled fork of canonical `josch/mmdebstrap`;
4. refresh canonical `main` and record the exact base;
5. create `fix/coverage-backend-process-group-current-main` from that base;
6. apply the upstream-root patch with zero fuzz;
7. select and add an upstream-native deterministic regression;
8. run the focused regression and project-declared ordinary mirror-backed/source gates;
9. review the complete clean target diff independently;
10. refresh duplicate, contribution-policy, and AI-disclosure checks;
11. synchronize packet and drafts with the exact target head;
12. request explicit authority for the exact public interaction.

## Current blockers

- controlled canonical fork and clean source branch: absent;
- exact clean target candidate head: absent;
- upstream-native regression committed to a target branch: absent;
- project-declared ordinary source gate: unexecuted;
- workflow retention/retirement decision: pending;
- independent final target-diff acceptance: pending;
- public contact authority: `false`.

## Continuation-ready handoff

Resume from this packet, outer packet PR #439, canonical Linux Fieldwork PR #401, and the latest unit-13 handoff on `teamleaderleo/fieldwork#435`.

Use these exact identities:

- canonical upstream base executed: `77ec9be5417ee44c96343d2347145585da1b1f94`;
- canonical delivery packet: `linux-fieldwork#401@d232e4fdd67cf0592e129a60534e984dcbec6bfe`;
- upstream-root patch blob: `f1a2c75adfa009b6f1ac29e5a31bef526400444f`;
- historical mechanism: `e90fc438f530f7bd78ffd6fd1ba24c665bd96913`;
- refined QEMU test head: `8253ab2ef6fed22b34fc5f5d6d20cda75c25e2c7`;
- canonical focused run: `30689911760`;
- final packet run: `30690101504`.

Preserve `REPAIR` under #435 until the clean target branch, ordinary gate, and final target review exist. Keep escalation separate. Perform no public upstream interaction without explicit authority.
