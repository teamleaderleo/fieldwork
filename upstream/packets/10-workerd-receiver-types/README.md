# Unit 10 — workerd receiver-aware TypeScript declarations

## In simple words

`workerd` already rejects ordinary native methods called through the wrong JavaScript object. Its generated TypeScript declarations omit that receiver rule, so incorrect rebinding can compile and fail only at runtime. The candidate adds explicit TypeScript `this` parameters, preserves their generated origin through handwritten overrides and Worker-global extraction, and keeps legal global/nullish calls accepted.

## Current disposition

**HOLD — clean source candidate complete; exact-head execution and final human review remain.**

The source is one commit on the current public `workerd/main` release head. It contains ten product/test files and no workflow or Fieldwork-only files. Public upstream contact remains unauthorized.

## Exact source

- repository: `teamleaderleo/workerd`
- clean branch: `unit-10/receiver-aware-types`
- clean PR: https://github.com/teamleaderleo/workerd/pull/5
- source head: `8f41da276852ad48735c1d817b7c1a3699ac8beb`
- public upstream base: `d82c2a45a8695aac30d4d24828ce1ee7fb11909b` (`Release 2026-08-01`)
- compare: https://github.com/teamleaderleo/workerd/compare/d82c2a45a8695aac30d4d24828ce1ee7fb11909b...8f41da276852ad48735c1d817b7c1a3699ac8beb
- source fence: one commit, ten files, no workflow files
- AI assistance: disclosed in the commit message and owned PR description, as required by current workerd submission guidance

The August 1 upstream release differs from the prior July 31 base only in:

- `src/workerd/io/maximum-compatibility-date.txt`
- `src/workerd/io/release-version.txt`

All implementation blobs other than the new callback-erasure control are identical to the repaired source reviewed on the prior base.

## What is established

- Ordinary JSG methods are installed with an owning V8 signature and reject unrelated receivers before the C++ callback executes.
- Native `workerd` and Chromium reject unrelated receivers for Worker `fetch`; Bun and Node intentionally accept them.
- TypeScript can represent the legal bare, detached, nullish, actual-global, and unrelated-holder call matrix while the receiver-aware type is retained.
- Assignment to a receiver-free callback type intentionally erases the explicit `this` parameter; the current type fixture now preserves that compatibility boundary as an accepted case.
- The candidate covers generator insertion, provenance cleanup, partial and full overrides, overloads, replacement generics, inherited globals, same-name lexical declarations, transformed heritage, static exclusion, and the Worker-global call matrix.
- Public issue `cloudflare/workerd#6904` remains the discussion record. A current search found no competing public implementation PR.
- Closed unmerged PR `cloudflare/workerd#2352` proposed a distinct detached-method registration macro. Its design supports the candidate's default: ordinary `JSG_METHOD` is receiver-owning, while receiver-independent instance operations require separate runtime registration and RTTI support.

## Commit organization result

Retain one source commit.

The generator marker, override preservation, global widening, cleanup, and tests form one semantic change:

- generator-only code loses receivers through handwritten overrides;
- generator plus overrides makes bare Worker-global calls type-invalid until global widening lands;
- source without matching fixture updates does not satisfy the project's per-commit test discipline.

A three-commit split would create knowingly incomplete intermediate behavior and repeated snapshot churn. The current one-commit presentation is larger, yet atomic and easier to defend.

## Test state

Executed on the repaired semantic source:

- workerd lint passed;
- `//types:test/index.spec` passed after the transformed-heritage repair;
- `//types:test/transforms/globals.spec` passed;
- `//types:test/transforms/overrides/index.spec` passed;
- `//types:test/transforms/overrides/replacement-receiver-generics.spec` passed;
- the earlier end-to-end failure reproduced stale pre-transform heritage lookup and directly motivated the current repair.

Executed downstream/runtime evidence:

- Stensibly exact-head typecheck, unit, integration, Worker check, and native runtime-parity commands passed;
- the native matrix accepted legal receiver forms and rejected unrelated holder, `call`, `apply`, and `bind` forms;
- the production OAuth fetch wrapper completed through a local outbound Worker.

Prepared on the final source head and still requiring exact execution:

- callback-erasure compatibility control in `types/test/types/fetch-receiver.ts`;
- full `//types/...` package;
- generated declaration build and representative output diff.

See [`TESTS.md`](./TESTS.md) for exact commands and evidence classes.

## Remaining work in strict order

1. Run the focused receiver targets and the complete `//types/...` package at `8f41da2…`.
2. Build representative ambient and importable declaration output and review method count, global unions, marker leakage, recursive growth, and intentional detachability.
3. Obtain independent complete-diff review of the final exact head.
4. Synchronize the final generated-output findings into `DEEP_DIVE.md`, `TESTS.md`, `UPSTREAM_PR.md`, and `REVIEW.md`.
5. Human decides whether to authorize a public follow-up on issue #6904 and an upstream pull request.

Execution status should remain background evidence collection. Source review, prior-art analysis, contribution guidance, packet drafting, and compatibility analysis continue independently.

## Packet

- branch: `p0/435-unit-10-workerd-receiver-types`
- directory: `upstream/packets/10-workerd-receiver-types/`
- routing board: https://github.com/teamleaderleo/fieldwork/issues/435
- campaign record: https://github.com/teamleaderleo/fieldwork/issues/230

## Reading order

1. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
2. [`APPROACHES.md`](./APPROACHES.md)
3. [`TESTS.md`](./TESTS.md)
4. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
5. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)
6. [`REVIEW.md`](./REVIEW.md)
