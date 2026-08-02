# Current-head receipt — async iterator read-error cleanup

Date: `2026-08-02`

## Exact identities

- Public target base: `vercel/ai@3bc0d4f40df7a77af4b181bc97dc1c54843545ab`
- Owned target branch: `teamleaderleo/ai:fix/async-iterable-stream-read-error-cleanup`
- Exact candidate head: `147e4066f69451e69aab26cbf47a7d273bbc6427`
- Owned review PR: `teamleaderleo/ai#14`
- Current CI run: `30754133958`
- Fieldwork evidence PR: `teamleaderleo/fieldwork#532`
- Upstream contact authorized: `false`

## Complete candidate fence

1. `.changeset/quiet-stream-errors-release.md`
2. `packages/ai/src/util/async-iterable-stream-read-error.test.ts`
3. `packages/ai/src/util/async-iterable-stream.ts`

Production change: wrap the existing `reader.read()` path in `try/catch`; on rejection call `cleanup(false)` and rethrow the exact reason.

Prepared target-native assertions: six tests total across two helper variants:

- exact non-`Error` reason identity;
- reader lock release;
- no cancellation of the already-errored source;
- terminal repeated `next()` and `return()` behavior;
- reader reacquisition with the same stored error;
- `undefined` error reason preservation;
- two concurrent pending reads preserve the original error and release ownership.

## Executed model receipts

### Unfixed baseline

Environment: Linux, Node `v22.16.0`.

Command:

```sh
node campaigns/477-async-iterator-read-error-cleanup/lanes/mechanism/artifacts/read-error-baseline-model.mjs
```

Both helper variants:

- preserved the source reason;
- remained locked after the error;
- rejected reader reacquisition with `TypeError: Invalid state: ReadableStream is locked`;
- kept rejecting later `next()` calls with the same source error.

Evidence class: `model-executed`.

### Selected candidate

Environment: Linux, Node `v22.16.0`.

Command:

```sh
node campaigns/477-async-iterator-read-error-cleanup/lanes/mechanism/artifacts/read-error-model.mjs
```

Both helper variants:

- preserved exact object error identity;
- released the reader lock;
- made zero source-cancellation calls;
- made later iterator calls terminal;
- allowed reader reacquisition, which observed the same stored source reason;
- settled two concurrent pending reads with the original error.

A direct Node control also confirmed `controller.error(undefined)` rejects `reader.read()` with the exact `undefined` reason and permits lock release.

Evidence class: `model-executed`.

### Changeset verifier model

The official target workflow is filtered to pull requests whose base branch is `main`. PR #14 intentionally targets a current-public-base mirror because the fork's shared `main` is stale and used by unrelated work. Therefore the official Verify Changesets workflow does not trigger on this clean comparison PR.

The retained standalone model mirrors the official action's relevant rules for this exact fence:

```sh
node campaigns/477-async-iterator-read-error-cleanup/lanes/mechanism/artifacts/verify-changeset-model.mjs
```

Result:

```json
{
  "status": "passed",
  "codeFiles": ["packages/ai/src/util/async-iterable-stream.ts"],
  "changedPackageNames": ["ai"],
  "coveredPackages": ["ai"]
}
```

Evidence class: `model-executed`. This is not an official workflow receipt.

## Prior target execution

Previous candidate head `1d7941fc689c8378dc0352ae49517e422af75622`:

- ordinary CI run `30693740097`: passed;
- AI shards passed on Node 22, 24, and 26;
- TypeScript, package and example builds, lint/format, consistency, and codemods passed;
- Verify Changesets `30693740104`, job `91352903452`: failed only because that previous head had no changeset.

The previous head had the same production catch and a narrower test modification, against an older public base. It is supporting evidence rather than exact-head proof.

## Current target execution

Run `30754133958` was queued with the full ordinary repository matrix at receipt creation. Its jobs include Node 22, 24, and 26 AI shards, TypeScript, build, lint/format, consistency, codemods, docs, and examples.

The package Vitest configuration includes every `**/*.test.ts` file for both `node` and `edge-runtime`, so the new focused test file is in the package's Node and Edge collection. Exact shard logs are still required to prove execution.

Evidence class: `target-test-prepared` plus current `execution queued`.

## Review result

Complete-diff self-review removed two accidental JSDoc wording changes. The current production diff contains only the lifecycle repair. No temporary workflow files or dependency changes are present.

Current disposition: `EXECUTE`.

Clearing conditions:

1. current-head CI completes and the relevant AI shard logs show the new test file passed;
2. official changeset validation is obtained later on a `main`-based submission surface, or equivalent exact target execution is retained without widening the diff;
3. commit signatures are verified or the patch is rebuilt as signed commits;
4. independent complete-diff review records a disposition.
