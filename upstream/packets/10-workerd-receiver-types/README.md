# Unit 10 — workerd receiver-aware TypeScript declarations

## In simple words

`workerd` already rejects ordinary native methods called through the wrong JavaScript object. Its generated TypeScript declarations omit that receiver rule, so incorrect rebinding can compile and fail only at runtime. The candidate adds explicit TypeScript `this` parameters, preserves their generated origin through handwritten overrides and Worker-global extraction, and keeps legal global/nullish calls accepted.

## Current disposition

**HOLD — repaired clean source candidate is complete; exact-head execution and independent final review remain.**

The source is one atomic commit on the current public `workerd/main` release head. It contains ten product/test files and no workflow or Fieldwork-only files. Public upstream contact remains unauthorized.

## Exact source

- repository: `teamleaderleo/workerd`
- clean branch: `unit-10/receiver-aware-types`
- clean PR: https://github.com/teamleaderleo/workerd/pull/5
- source head: `18a117c28773cd7aa0ee599e03439c5fbbf06584`
- public upstream base: `813c31394b9909d8f557bba14324db275bc12720` (`Release 2026-08-02`)
- compare: https://github.com/teamleaderleo/workerd/compare/813c31394b9909d8f557bba14324db275bc12720...18a117c28773cd7aa0ee599e03439c5fbbf06584
- source fence: one commit, ten files, no workflow files
- AI assistance: disclosed in the commit message and owned PR description, as required by current workerd submission guidance

The August 2 upstream release differs from the prior August 1 base only in:

- `src/workerd/io/maximum-compatibility-date.txt`
- `src/workerd/io/release-version.txt`

## What is established

- Ordinary JSG methods are installed with an owning V8 signature and reject unrelated receivers before the C++ callback executes.
- `JSG_ITERABLE`, `JSG_ASYNC_ITERABLE`, `JSG_DISPOSE`, and `JSG_ASYNC_DISPOSE` also register callbacks with the same owning signature, so their generated method declarations correctly receive owners.
- Callable resource instances use a separate instance call-handler surface; this patch does not alter callable signatures.
- Native `workerd` and Chromium reject unrelated receivers for Worker `fetch`; Bun and Node intentionally accept them.
- TypeScript can represent the legal bare, detached, nullish, actual-global, and unrelated-holder call matrix while the receiver-aware type is retained.
- Assignment to a receiver-free callback type intentionally erases the explicit `this` parameter; the type fixture preserves that compatibility boundary as an accepted case.
- The candidate covers generator insertion, provenance cleanup, partial and full overrides, overloads, replacement generics, renamed replacements, inherited globals, same-name lexical declarations, transformed heritage, static-method exclusion, static-global constant preservation, and the Worker-global call matrix.
- Public issue `cloudflare/workerd#6904` remains the discussion record. A current search found no competing public implementation PR.
- Closed unmerged PR `cloudflare/workerd#2352` proposed a distinct detached-method registration macro. Its design supports the candidate's default: ordinary `JSG_METHOD` is receiver-owning, while receiver-independent instance operations require separate runtime registration and RTTI support.

## Latest repair

Exact-head review of the prior candidate found that a blanket static-member check removed generated ambient constants along with static methods. JSG constants are represented as `static readonly` properties, so this was an unrelated source regression.

The current head repairs the boundary:

- static methods remain receiver-free and are not extracted as ambient functions;
- static properties/constants retain existing ambient constant extraction;
- `globals.spec.ts` now requires `static readonly CONSTANT: 42` to produce `declare const CONSTANT: 42` while the static method remains unextracted.

A second missing control now proves that a full replacement which both renames the owner and changes its generic parameters emits the receiver as the replacement name, not a dangling original type.

## Commit organization result

Retain one source commit.

The generator marker, override preservation, global widening, cleanup, and tests form one semantic change:

- generator-only code loses receivers through handwritten overrides;
- generator plus overrides makes bare Worker-global calls type-invalid until global widening lands;
- source without matching fixture updates does not satisfy the project's per-commit test discipline.

A three-commit split would create knowingly incomplete intermediate behavior and repeated snapshot churn. The current one-commit presentation is larger, yet atomic and easier to defend.

## Test state

Executed on the prior repaired semantic source:

- workerd lint passed;
- `//types:test/index.spec` passed after the transformed-heritage repair;
- `//types:test/transforms/globals.spec` passed before the later static-constant review finding;
- `//types:test/transforms/overrides/index.spec` passed;
- `//types:test/transforms/overrides/replacement-receiver-generics.spec` passed before the new renamed-replacement control was added;
- the earlier end-to-end failure reproduced stale pre-transform heritage lookup and directly motivated that repair.

Executed downstream/runtime evidence:

- Stensibly exact-head typecheck, unit, integration, Worker check, and native runtime-parity commands passed;
- the native matrix accepted legal receiver forms and rejected unrelated holder, `call`, `apply`, and `bind` forms;
- the production OAuth fetch wrapper completed through a local outbound Worker.

Prepared on final head `18a117c…` and requiring exact execution:

- static-global constant preservation and static-method exclusion in `types/test/transforms/globals.spec.ts`;
- renamed generic replacement receiver ownership in `types/test/transforms/overrides/replacement-receiver-generics.spec.ts`;
- callback-erasure compatibility in `types/test/types/fetch-receiver.ts`;
- focused receiver targets and complete `//types/...` package;
- generated declaration build and representative ambient/importable output diff.

See [`TESTS.md`](./TESTS.md) for exact commands and evidence classes.

## Remaining work in strict order

1. Run the focused receiver targets and complete `//types/...` package at `18a117c…`.
2. Build representative ambient and importable declaration output and review method count, global unions, constant preservation, marker leakage, recursive growth, owner resolution, and intentional detachability.
3. Obtain independent complete-diff review of the final exact head.
4. Synchronize completed output findings into `DEEP_DIVE.md`, `TESTS.md`, `UPSTREAM_PR.md`, and `REVIEW.md`.
5. Human decides whether to authorize a public follow-up on issue #6904 and an upstream pull request.

Execution status is background evidence collection. Source review, prior-art analysis, contribution guidance, packet drafting, and compatibility analysis continue independently.

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
