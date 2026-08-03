# Campaign 477 mechanism lane — current handoff

## In simple words

When an AI SDK async iterator receives a source-stream error, the error reaches the consumer but the iterator keeps its reader attached and the stream remains locked. The selected repair releases that reader without cancelling the already-errored stream and preserves the exact error reason. A clean three-file candidate, six target-native tests, baseline and candidate models, and a changeset are ready. Hosted execution is queued.

## Current disposition

`EXECUTE`

## Exact identities

- Public source base: `vercel/ai@3bc0d4f40df7a77af4b181bc97dc1c54843545ab`
- Canonical owned candidate: `teamleaderleo/ai#14`
- Canonical source branch: `fix/async-iterable-stream-read-error-cleanup`
- Canonical source head: `147e4066f69451e69aab26cbf47a7d273bbc6427`
- Focused execution carrier: `teamleaderleo/ai#17`
- Focused run: `30754259605`
- Ordinary current-head CI: `30754133958`
- Previous narrower-head full CI: `30693740097`, passed
- Fieldwork evidence PR: `teamleaderleo/fieldwork#532`
- Upstream contact authorized: `false`

## Candidate fence

- `.changeset/quiet-stream-errors-release.md`
- `packages/ai/src/util/async-iterable-stream-read-error.test.ts`
- `packages/ai/src/util/async-iterable-stream.ts`

Production diff: catch rejected `reader.read()`, call `cleanup(false)`, rethrow the exact reason.

Tests cover both helper variants, object and `undefined` reasons, lock release, no source cancellation, terminal repeated calls, reader reacquisition, and concurrent pending reads.

## Durable evidence

- [Mechanism report](./report.md)
- [Current-head receipt](./receipts/2026-08-02-current-head.md)
- [Unfixed baseline model](./artifacts/read-error-baseline-model.mjs)
- [Unfixed baseline result](./artifacts/read-error-baseline-model-result.json)
- [Candidate model](./artifacts/read-error-model.mjs)
- [Candidate result](./artifacts/read-error-model-result.json)
- [Changeset verifier model](./artifacts/verify-changeset-model.mjs)
- [Changeset verifier result](./artifacts/verify-changeset-model-result.json)

## Current evidence

- Public main still contains the rejected-read cleanup gap at the pinned base.
- The unfixed Node 22 model reproduces a locked stream and failed reader reacquisition for both construction paths.
- The selected Node 22 model releases ownership, preserves exact reasons, skips cancellation, and remains terminal under repeated and concurrent calls.
- The previous narrower candidate passed the ordinary repository CI matrix on Node 22, 24, and 26.
- The official changeset workflow is filtered to `main`-base PRs; a standalone execution of its relevant exact rules passed for this fence.
- Current focused and ordinary hosted runs are queued and have produced no current-head product conclusion.

## Continuation

1. Inspect focused run `30754259605` and transfer its exact job receipt here.
2. Inspect ordinary run `30754133958`, especially the AI shards and Node-version matrix.
3. Confirm the focused test file appears in Node and Edge logs.
4. Verify commit signatures or rebuild the patch as signed commits.
5. Obtain independent complete-diff review on `teamleaderleo/ai#14`.
6. Close execution carrier #17 after its receipt is transferred.
7. Keep public upstream contact disabled until explicitly authorized.
