# Unit 10 — workerd receiver-aware TypeScript declarations

## Current disposition

**EXECUTE. Hold public pull-request publication.**

The repaired source is preserved on a clean owned-fork branch rebased onto current public `workerd/main`. Source review found and repaired three concrete defects during the research sequence: stale static-global expectations, ambiguous lexical heritage lookup, and generic full-replacement receivers that could retain an undeclared type parameter. The clean branch excludes the fork-only workflow and contains one source/test commit.

Exact source:

- repository: `teamleaderleo/workerd`
- clean branch: `unit-10/receiver-aware-types`
- clean PR: https://github.com/teamleaderleo/workerd/pull/5
- source head: `f167a283fc9f792c427eeded306c38602e60261d`
- public upstream base: `7cdc8c0e089287c8f3643f3a6f668ecdc221722a` (`Release 2026-07-31`)
- compare: https://github.com/teamleaderleo/workerd/compare/7cdc8c0e089287c8f3643f3a6f668ecdc221722a...f167a283fc9f792c427eeded306c38602e60261d
- source fence: one commit, ten files, no workflow files

Packet:

- branch: `p0/435-unit-10-workerd-receiver-types`
- directory: `upstream/packets/10-workerd-receiver-types/`
- parent: https://github.com/teamleaderleo/fieldwork/issues/435
- campaign record: https://github.com/teamleaderleo/fieldwork/issues/230

## In simple words

`workerd` already rejects ordinary native methods called through the wrong JavaScript object. Its generated TypeScript declarations omit that receiver rule, so incorrect rebinding can compile and fail only in the runtime. The candidate adds explicit TypeScript `this` parameters, carries their generated origin through handwritten overrides, and widens Worker-global operations to the exact nullish/global receiver set used by the runtime.

## What is established

- Native `workerd` and Chromium reject unrelated receivers for Worker `fetch`; Bun and Node deliberately accept them.
- TypeScript 5.8.3 can represent bare, detached, nullish, correct-global, and unrelated-holder behavior while the receiver-aware type remains precise.
- The owned Stensibly production wrapper and native-workerd regression are merged at `f19c2c7aa09fc4d4fdb7e7ae2d4d727d0eedd091`.
- The current source includes generator, override, global-extraction, generic-replacement, static, lexical-heritage, and call-matrix tests.
- Public upstream main advanced only through three release commits touching release-date files; the clean branch is rebased onto that current head.
- Search on 2026-08-01 found no second open `workerd` issue or pull request implementing receiver-aware generated declarations. Existing issue `cloudflare/workerd#6904` remains the public discussion record.

## Current test state

Executed and retained:

- Stensibly exact-head commands at `2c42d8041b0cbe5fbccbe87202381361da2bc6ef`: `bun install`, `bun run typecheck`, `bun run test`, `bun run test:convex`, `bun run worker:check`, `bun run test:runtime-parity` — all passed in run `30449733862`; ordinary `test` and `runtime-parity` also passed in run `30449840120`.
- workerd carrier lint at `0ecc0a6632747031a6650c49a401760e511c9f36`: run `30625540316` — passed.
- TypeScript model commands and diagnostics are retained in Stensibly issue #474 and summarized in `TESTS.md`.

Requested for clean head `f167a283fc9f792c427eeded306c38602e60261d` through owned draft PR #5:

- Lint `30674453451` — queued at packet creation.
- New PR Review `30674453474` — queued.
- CodSpeed `30674453493` — queued.
- Tests `30674453627` — queued.
- Coverage `30674453672` — queued.

Queued jobs provide no pass or failure evidence.

## Remaining blockers

1. The clean exact head needs completed focused generator/override/global/type fixtures and ordinary target gates.
2. The final source head needs independent complete-diff acceptance; review `4827890474` covered the semantically identical product/test blobs on carrier head `0ecc0a…`, while the clean rebase itself has only coordinator verification.
3. A representative generated-output compatibility review should confirm intentional detachable operations and source-break scope across real APIs.
4. Contribution guidance requires tested code and favors discussion before a non-trivial change. Public issue #6904 satisfies the discussion-first history, yet it has no maintainer response.
5. Any public issue follow-up or pull request requires explicit human authorization.

## Continuation-ready next action

Wait for or inspect the clean-head workflow conclusions. If target execution completes, record exact jobs and logs, compare generated output, obtain independent review of `f167a283…`, update this packet, and choose `ACCEPT` or a concrete repair. If the jobs remain queued because the fork cannot obtain runner execution, retain that platform limit and arrange an authorized target-native run before publication.

## Reading order

1. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
2. [`APPROACHES.md`](./APPROACHES.md)
3. [`TESTS.md`](./TESTS.md)
4. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
5. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)
6. [`REVIEW.md`](./REVIEW.md)
