# Upstream unit 13 — mmdebstrap process-group cancellation

## In simple words

`coverage.py` launches backend wrappers that can own nested work. On parent-only SIGINT, terminating only the wrapper can leave descendants running. The selected patch starts each backend in its own session/process group, sends TERM to that group, waits for the wrapper, and exits 130. Exact null, QEMU-wrapper, and sudo controls support this bounded repair. A clean current-upstream source branch and target-native gate remain to be created.

## Current disposition

`REPAIR`

The bounded mechanism is technically coherent and heavily exercised. Delivery remains incomplete because the canonical source is a retained patch inside Linux Fieldwork rather than a clean mmdebstrap branch based on current upstream.

## Assignment

- unit: `13`
- proposed contribution: `fix: cancel backend process groups during interruption`
- assigned packet: `upstream/packets/13-mmdebstrap-process-group-cancellation/`
- packet branch: `p0/435-unit-13-mmdebstrap-process-group`
- packet branch base at claim: `920f87cb25dd0cc7901d59ea2019cd4b4a193b94`
- exact packet head: recorded in the latest unit-13 handoff on `teamleaderleo/fieldwork#435`
- public upstream contact: `false`

## Target identity

- target: mmdebstrap
- canonical upstream repository: `https://salsa.debian.org/debian/mmdebstrap.git`
- upstream default branch: `main`
- imported release/tag: `debian/1.5.7-3`
- imported upstream commit: `6fde999741f4fe1e7bf38079acf29432ef87a35e`
- Linux Fieldwork import commit: `782774b01002abf37878d834a54d0bbf8b226397`
- imported `coverage.py` blob: `9a522484aef05deae514a98e4b6adf5feb6c886d`
- current upstream main inspected 2026-08-01: `77ec9be5417ee44c96343d2347145585da1b1f94`
- relevant lifecycle on current main: unchanged from the imported blob in the inspected public mirror

## Canonical source and packaging

### Current retained source

- carrier: [`teamleaderleo/linux-fieldwork#313`](https://github.com/teamleaderleo/linux-fieldwork/pull/313)
- branch: `fix/coverage-backend-process-group`
- exact carrier head: `dfc6d0503fb844f4c428ce16a567a9fdcd35280a`
- exact executed mechanism head: `e90fc438f530f7bd78ffd6fd1ba24c665bd96913`
- candidate patch blob: `4f2a749e50d42655ebb6519ca6550d2f666985bc`
- packet copy: [`patches/0001-own-backend-process-group.patch`](./patches/0001-own-backend-process-group.patch)

### Clean target-source branch

- owned fork: absent from the accessible repositories
- preferred fork name: `teamleaderleo/mmdebstrap`
- intended branch: `fix/coverage-backend-process-group-current-main`
- intended exact base: refresh current upstream `main`; presently `77ec9be5417ee44c96343d2347145585da1b1f94`
- materialization state: blocked on fork/repository admission

No branch is claimed where repository access is absent.

## Proposed upstream title

`coverage.py: terminate the selected backend process group on SIGINT`

## Contribution synopsis

Current behavior starts a backend with `subprocess.Popen(argv)`. On `KeyboardInterrupt`, the driver terminates and waits for only the immediate wrapper. Nested shells, pipelines, output followers, foreground operations, or privileged workers can continue.

The selected patch:

- imports `signal`;
- starts the backend with `start_new_session=True`;
- sends `SIGTERM` to `os.killpg(proc.pid, ...)`;
- tolerates an already-exited group;
- waits for the wrapper;
- prints an interruption diagnostic;
- exits 130;
- preserves ordinary result handling.

## Intended clean changed-file inventory

Known product file:

- `coverage.py`

Required target-native test:

- path pending inspection of the current upstream test convention and direct materialization.

The clean target branch must exclude Linux Fieldwork investigations, notes, receipts, publishers, and temporary workflows.

## Exact tests and receipts

### Mechanism gate

- head: `e90fc438f530f7bd78ffd6fd1ba24c665bd96913`
- CI: [run 30632491641](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30632491641)
- job: [91161937871](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30632491641/job/91161937871)
- result: success
- recorded result: all 359 Linux Fieldwork tests passed; exact null, QEMU-wrapper, actual-sudo, foreground-group, source-shape, and unsignaled controls passed; compilation, shell syntax, and command-help checks passed.

### Current carrier gate

- head: `dfc6d0503fb844f4c428ce16a567a9fdcd35280a`
- CI: [run 30633602052](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30633602052)
- job: [91165600654](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30633602052/job/91165600654)
- result: success
- recorded result: 340 uniquely discovered tests plus patch validation, compilation, shell syntax, and command-help checks.

### QEMU evidence refinement

- PR: [`teamleaderleo/linux-fieldwork#339`](https://github.com/teamleaderleo/linux-fieldwork/pull/339)
- head: `8253ab2ef6fed22b34fc5f5d6d20cda75c25e2c7`
- CI: [run 30633578396](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30633578396)
- job: [91165522248](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30633578396/job/91165522248)
- result: success; 269 tests recorded
- independent evidence review: comment `5143736054`

### Fresh packet-time model

- environment: Linux 6.12.13 x86_64, Python 3.13.5
- result: baseline 0 with later work; status-only 130 with later work; group candidate 130 without later work
- receipt: [`receipts/2026-08-01-local-process-model.md`](./receipts/2026-08-01-local-process-model.md)

Full details: [`TESTS.md`](./TESTS.md).

## Evidence limits and compatibility risk

Established:

- caller-owned group exists before backend execution;
- parent-only SIGINT sends TERM to that group;
- tested TERM-responsive null, QEMU-wrapper, and sudo groups settle without later work;
- ordinary unsignaled controls succeed.

Limits:

- `proc.wait()` waits for the wrapper rather than arbitrary descendant drain;
- TERM-resistant or TERM-deferring descendants can survive;
- repeated SIGINT can interrupt cleanup;
- descendants can escape by creating another group/session;
- direct `/dev/tty`, real QEMU/debvm, mounts, network, package operations, and non-Linux semantics remain unexecuted;
- upstream target-native and ordinary gates remain pending.

The stronger synthetic policy comparison is retained in [issue #341](https://github.com/teamleaderleo/linux-fieldwork/issues/341) and [PR #347](https://github.com/teamleaderleo/linux-fieldwork/pull/347). Escalation remains unselected.

## Duplicate and prior-art result

A bounded search on 2026-08-01 across the current public upstream source, issue, and merge-request surfaces found the old lifecycle still present and no matching public `SIGINT`/`KeyboardInterrupt`/`killpg`/process-group repair. Refresh this search immediately before any public action.

Internal prior art:

- status-only finding: [issue #141](https://github.com/teamleaderleo/linux-fieldwork/issues/141)
- historical status-only candidate: [PR #143](https://github.com/teamleaderleo/linux-fieldwork/pull/143)
- merged Fieldwork restack: [PR #204](https://github.com/teamleaderleo/linux-fieldwork/pull/204)
- canonical process-group investigation: [issue #306](https://github.com/teamleaderleo/linux-fieldwork/issues/306) / [PR #313](https://github.com/teamleaderleo/linux-fieldwork/pull/313)
- superseded context repair: [PR #332](https://github.com/teamleaderleo/linux-fieldwork/pull/332)
- superseded QEMU refinement: [PR #336](https://github.com/teamleaderleo/linux-fieldwork/pull/336)
- current QEMU refinement: [PR #339](https://github.com/teamleaderleo/linux-fieldwork/pull/339)
- deferred cleanup comparison: [issue #341](https://github.com/teamleaderleo/linux-fieldwork/issues/341), [PR #347](https://github.com/teamleaderleo/linux-fieldwork/pull/347), [PR #353](https://github.com/teamleaderleo/linux-fieldwork/pull/353)

## Packet navigation

- [`DEEP_DIVE.md`](./DEEP_DIVE.md) — source map, invariant, design, compatibility, and current answer
- [`APPROACHES.md`](./APPROACHES.md) — selected, losing, rejected, superseded, and deferred directions
- [`TESTS.md`](./TESTS.md) — exact commands, runs, jobs, evidence classes, limits, and next execution
- [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md) — optional polished issue draft
- [`UPSTREAM_PR.md`](./UPSTREAM_PR.md) — polished PR draft and publication checklist
- [`REVIEW.md`](./REVIEW.md) — exact-head review and final human inspection guide
- [`patches/`](./patches/) — retained source patch
- [`receipts/`](./receipts/) — compact packet-time execution receipt

## Remaining work in strict order

1. obtain or create an owned mmdebstrap fork through the authorized repository-admission path;
2. refresh current upstream main and record the exact base SHA;
3. create `fix/coverage-backend-process-group-current-main` directly from that base;
4. apply or recreate the one-file source patch;
5. select and add a target-native deterministic regression;
6. decide whether the refined QEMU causal control from #339 should be adapted into the target regression evidence;
7. run focused baseline/candidate execution;
8. run project-declared ordinary gates;
9. refresh duplicate, contribution-policy, and AI-disclosure checks;
10. review the complete clean diff independently;
11. update this packet and drafts with the exact target head and receipts;
12. request explicit authority for the exact public interaction.

## Current blockers

- no accessible owned mmdebstrap repository or target branch;
- no clean current-upstream source head carrying the patch;
- no target-native focused regression;
- no upstream ordinary-gate receipt;
- independent final clean-diff acceptance remains pending;
- public contact authority remains `false`.

## Continuation-ready handoff

Resume from this packet and the latest unit-13 comment on `teamleaderleo/fieldwork#435`. Preserve the `REPAIR` disposition until a clean current-upstream target branch and target-native execution exist. Treat `linux-fieldwork#313@dfc6d050…` as the canonical retained technical carrier, `e90fc438…` as the exact executed mechanism generation, and `linux-fieldwork#339@8253ab2e…` as the accepted QEMU evidence successor. Keep escalation research separate unless a real backend supplies the reopening evidence. Perform no public upstream interaction without explicit authority.