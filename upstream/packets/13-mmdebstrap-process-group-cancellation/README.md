# Upstream unit 13 — mmdebstrap process-group cancellation

## In simple words

`coverage.py` launches backend wrappers that can own nested work. On parent-only SIGINT, terminating only the wrapper can leave descendants running. The selected patch starts each backend in its own session/process group, sends TERM to that group, waits for the wrapper, and exits 130.

Exact null, QEMU-wrapper, and sudo controls support this bounded repair. The old Linux Fieldwork delivery receipt expired after `main` changed. A byte-identical current-main restack now exists on PR #406 and is awaiting its gate. A clean mmdebstrap source branch and target-native gate remain absent.

## Current disposition

`REPAIR`

The bounded mechanism is technically coherent and historically exercised. Current Linux Fieldwork integration is active. Upstream delivery remains incomplete.

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
- canonical selected/default branch: `master`
- imported release/tag: `debian/1.5.7-3`
- imported upstream commit: `6fde999741f4fe1e7bf38079acf29432ef87a35e`
- Linux Fieldwork import commit: `782774b01002abf37878d834a54d0bbf8b226397`
- imported `coverage.py` blob: `9a522484aef05deae514a98e4b6adf5feb6c886d`
- previously inspected upstream revision: `77ec9be5417ee44c96343d2347145585da1b1f94`
- relevant lifecycle on that revision: unchanged from the imported blob
- refresh requirement: resolve the live canonical `master` head before target materialization or public action

## Canonical source and packaging

### Retained technical carrier

- pull request: [`teamleaderleo/linux-fieldwork#313`](https://github.com/teamleaderleo/linux-fieldwork/pull/313)
- live state/title: `[REPAIR] coverage: deliver cancellation to the selected backend group`
- branch: `fix/coverage-backend-process-group`
- exact retained head: `dfc6d0503fb844f4c428ce16a567a9fdcd35280a`
- exact executed mechanism head: `e90fc438f530f7bd78ffd6fd1ba24c665bd96913`
- candidate patch blob: `4f2a749e50d42655ebb6519ca6550d2f666985bc`
- packet patch: [`patches/0001-own-backend-process-group.patch`](./patches/0001-own-backend-process-group.patch)

### Current Linux Fieldwork delivery reconciliation

- pull request: [`teamleaderleo/linux-fieldwork#406`](https://github.com/teamleaderleo/linux-fieldwork/pull/406)
- base: `main@6cc74d846c50b9bbb88247e8a128b67e8c174c1e`
- branch: `repair/313-current-main-reconciliation`
- exact source head: `e82b9b059850fce1efcf8daadef89049495a8b27`
- changed-file fence: nine files
- relation to #313: exact blob-for-blob restack
- workflow: `30690801852` / run 1151
- workflow state at packet update: queued

This branch repairs ancestry and current-gate identity. It changes no accepted mechanism, test, or evidence byte.

### Clean mmdebstrap target-source branch

- owned fork: absent from accessible repositories
- preferred fork name: `teamleaderleo/mmdebstrap`
- intended branch: `fix/coverage-backend-process-group-current-master`
- intended base: refreshed exact canonical upstream `master` head
- materialization state: blocked on fork/repository admission

No target branch is claimed where repository access is absent.

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

## Intended clean upstream changed-file inventory

Known product file:

- `coverage.py`

Required target-native test:

- path pending inspection of current upstream test convention and direct materialization.

The clean target branch must exclude Linux Fieldwork investigations, notes, receipts, publishers, and temporary workflows.

## Exact tests and receipts

### Historical mechanism gate

- source head: `e90fc438f530f7bd78ffd6fd1ba24c665bd96913`
- CI: [30632491641](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30632491641)
- job: [91161937871](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30632491641/job/91161937871)
- result: success
- recorded result: 359 tests passed; null, QEMU-wrapper, actual-sudo, foreground-group, source-shape, and unsignaled controls passed; compilation, shell syntax, and command-help checks passed.

### Historical retained-head gate

- source head: `dfc6d0503fb844f4c428ce16a567a9fdcd35280a`
- generated merge: `24c7ba065b4c50fee76a07b0f6d6cb000d4684d8`
- CI: [30633602052](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30633602052)
- job: [91165600654](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30633602052/job/91165600654)
- result: success
- recorded result: 340 uniquely discovered tests plus patch validation, compilation, shell syntax, and command-help checks.

These receipts remain valid for their exact source/base pairs. They no longer prove current-main compatibility.

### Current-main gate

- source head: `e82b9b059850fce1efcf8daadef89049495a8b27`
- pull request: [#406](https://github.com/teamleaderleo/linux-fieldwork/pull/406)
- CI: [30690801852](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30690801852)
- run: 1151
- current result: queued at packet update

### QEMU evidence refinement

- pull request: [`teamleaderleo/linux-fieldwork#339`](https://github.com/teamleaderleo/linux-fieldwork/pull/339)
- head: `8253ab2ef6fed22b34fc5f5d6d20cda75c25e2c7`
- CI: [30633578396](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30633578396)
- job: [91165522248](https://github.com/teamleaderleo/linux-fieldwork/actions/runs/30633578396/job/91165522248)
- result: success; 269 tests recorded
- independent evidence review: comment `5143736054`

### Packet model

- environment: Linux 6.12.13 x86_64, Python 3.13.5
- original run, closeout rerun, and reviewed relocatable replay: success
- result: baseline 0 with later work; status-only 130 with later work; group candidate 130 without later work
- compile check: success for all five retained Python files
- receipt: [`receipts/2026-08-01-local-process-model.md`](./receipts/2026-08-01-local-process-model.md)
- source: [`fixtures/local-process-model/`](./fixtures/local-process-model/)

The exact original harness is preserved as `harness_original.py`. The reviewed `harness.py` repairs path portability, readiness ordering, early-exit diagnosis, and cleanup only.

Full details: [`TESTS.md`](./TESTS.md).

## Evidence limits and compatibility risk

Established at exact historical heads:

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
- current Linux Fieldwork gate remains pending;
- upstream target-native and ordinary gates remain pending.

The stronger synthetic policy comparison is retained in [issue #341](https://github.com/teamleaderleo/linux-fieldwork/issues/341) and [PR #347](https://github.com/teamleaderleo/linux-fieldwork/pull/347). Escalation remains unselected.

## Duplicate and prior-art result

A bounded search on 2026-08-01 across upstream source, issue, merge-request, recent-commit, and Debian bug surfaces found no matching public `SIGINT`/`KeyboardInterrupt`/`killpg`/process-group repair. Refresh this search immediately before public action.

Internal prior art:

- status-only finding: [issue #141](https://github.com/teamleaderleo/linux-fieldwork/issues/141)
- historical status-only candidate: [PR #143](https://github.com/teamleaderleo/linux-fieldwork/pull/143)
- merged Fieldwork restack: [PR #204](https://github.com/teamleaderleo/linux-fieldwork/pull/204)
- canonical process-group investigation: [issue #306](https://github.com/teamleaderleo/linux-fieldwork/issues/306) / [PR #313](https://github.com/teamleaderleo/linux-fieldwork/pull/313)
- superseded context repair: [PR #332](https://github.com/teamleaderleo/linux-fieldwork/pull/332)
- superseded QEMU refinement: [PR #336](https://github.com/teamleaderleo/linux-fieldwork/pull/336)
- refined QEMU evidence: [PR #339](https://github.com/teamleaderleo/linux-fieldwork/pull/339)
- deferred cleanup comparison: [issue #341](https://github.com/teamleaderleo/linux-fieldwork/issues/341), [PR #347](https://github.com/teamleaderleo/linux-fieldwork/pull/347), [PR #353](https://github.com/teamleaderleo/linux-fieldwork/pull/353)
- current-main reconciliation: [PR #406](https://github.com/teamleaderleo/linux-fieldwork/pull/406)

A later review mentioned PR #358. Live inspection shows #358 is a closed, unrelated broad mmdebstrap fixture contract repair. Unit 13 excludes it.

## Packet navigation

- [`DEEP_DIVE.md`](./DEEP_DIVE.md) — source map, invariant, design, compatibility, and current answer
- [`APPROACHES.md`](./APPROACHES.md) — selected, losing, rejected, superseded, and deferred directions
- [`TESTS.md`](./TESTS.md) — exact commands, runs, jobs, evidence classes, limits, and next execution
- [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md) — optional polished issue draft
- [`UPSTREAM_PR.md`](./UPSTREAM_PR.md) — polished PR draft and publication checklist
- [`REVIEW.md`](./REVIEW.md) — exact-head review and final human inspection guide
- [`patches/`](./patches/) — retained source patch
- [`receipts/`](./receipts/) — compact execution receipts
- [`fixtures/local-process-model/`](./fixtures/local-process-model/) — original and reviewed packet model source

## Remaining work in strict order

1. finish PR #406 current-main CI;
2. record literal source head, generated merge, counts, skips, and lifecycle results;
3. renew complete-diff review of PR #406;
4. obtain or create an owned mmdebstrap fork through the authorized repository-admission path;
5. refresh canonical upstream `master` and record the exact base SHA;
6. create `fix/coverage-backend-process-group-current-master` directly from that base;
7. apply or recreate the one-file source patch;
8. select and add a target-native deterministic regression;
9. decide whether the refined QEMU causal control from #339 should be adapted;
10. run focused baseline/candidate execution and project-declared ordinary gates;
11. refresh duplicate, contribution-policy, and AI-disclosure checks;
12. review the complete clean target diff independently;
13. update packet and drafts with exact target head and receipts;
14. request explicit authority for the exact public interaction.

## Current blockers

- PR #406 current-main gate and renewed review remain pending;
- no accessible owned mmdebstrap repository or target branch;
- no clean upstream source head carrying the patch;
- no target-native focused regression;
- no upstream ordinary-gate receipt;
- independent final clean-target-diff acceptance remains pending;
- public contact authority remains `false`.

## Continuation-ready handoff

Resume from this packet, Linux Fieldwork PR #406, and the latest unit-13 comment on `teamleaderleo/fieldwork#435`.

Preserve `REPAIR` until PR #406 is green and reviewed, then continue to clean mmdebstrap materialization. Treat:

- `linux-fieldwork#313@dfc6d050…` as retained technical history;
- `linux-fieldwork#406@e82b9b05…` as active current-main delivery reconciliation;
- `e90fc438…` as the exact historically executed mechanism generation;
- `linux-fieldwork#339@8253ab2e…` as the refined QEMU evidence successor.

Keep escalation research separate unless a real backend supplies reopening evidence. Perform no public upstream interaction without explicit authority.
