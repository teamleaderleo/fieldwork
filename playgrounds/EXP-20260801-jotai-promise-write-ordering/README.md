# Jotai promised storage write ordering

## In simple words

Jotai's `atomWithStorage` accepts a value that may itself be a promise. When that promise resolves, the current implementation updates the atom and writes storage at that later time.

This experiment asks whether an older promised update can finish after a newer direct update, reset, or promised update and become the final in-memory and persisted value. The pinned source follows promise resolution order for this crossing.

A one-counter candidate successfully fences those stale callbacks in ordinary one-store tests, but complete-diff review found that the counter is attached to the atom definition and is therefore shared by every Jotai store using that atom. The candidate is retained for issue-first design and repair, not accepted as a source proposal.

The question remains narrow. It does not cover two ordinary asynchronous `storage.setItem()` calls completing out of order, read ordering, subscription ordering, or general persistence serialization.

## State

`issue-first / repair`

Last updated: `2026-08-02`  
Owner: `chatgpt:gpt-5.6-thinking`  
Claim scope: `mechanism`  
Upstream contact authorized: `no`

## Exact subject

- Target: `pmndrs/jotai`
- Pinned source: `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- Characterization branch: `teamleaderleo/jotai:scout/atom-with-storage-promise-write-ordering`
- Exact characterization head: `09e7964e5da9423920eedb736feb30a347eaec89`
- Characterization draft PR: `teamleaderleo/jotai#4`
- Candidate branch: `teamleaderleo/jotai:fix/utils-promise-write-generation`
- Exact candidate head: `348156c8ae9636c9ad0b43d1c0fb7343dc13a976`
- Candidate draft PR: `teamleaderleo/jotai#5`
- Product source path: `src/vanilla/utils/atomWithStorage.ts`
- Characterization test: `tests/react/vanilla-utils/atomWithStoragePromiseWriteOrdering.test.ts`
- Candidate test: `tests/react/vanilla-utils/atomWithStoragePromiseWriteGeneration.test.ts`

## Project instructions read

At the pinned source, `CONTRIBUTING.md` requires a focused conventional-commit change, failing tests, `pnpm run fix:format`, `pnpm run build`, and `pnpm run test`. It also directs bug reports to a public discussion before a normal upstream proposal.

The owned-fork target workflows cover the declared format, type, lint, spec, build, version, build-variant, old-TypeScript, and size gates. Public discussion remains unauthorized.

## Source model

The `atomWithStorage` write function computes `nextValue` and then has three paths:

1. `RESET` immediately sets the initial value and calls `removeItem`.
2. A promised value waits for resolution, then calls `set(baseAtom, resolvedValue)` and `storage.setItem`.
3. A direct value immediately calls `set(baseAtom, nextValue)` and `storage.setItem`.

No write invocation generation is recorded in the pinned source. Therefore an earlier promised update retains a later callback that can still set state and persist data after a newer operation.

## Characterization cases

1. Older promised update, then newer direct value.
2. Older promised update, then reset.
3. Older promised update, then newer promised update that resolves first.

The characterization tests assert the exact source behavior predicted by the current code path: the older promise resolves last and becomes final atom state and the final recorded storage write.

## Candidate

The candidate adds one `writeGeneration` counter inside each `atomWithStorage` definition.

- Direct updates, promised updates, and reset advance the counter after `nextValue` is computed.
- A promised value captures that generation.
- When the promise resolves, it updates atom state and calls `storage.setItem` only while its generation remains current.
- Promise rejection remains caller-visible because the candidate does not add a rejection handler.
- Direct values and reset keep their existing immediate behavior.

Candidate controls cover:

- newer direct value remains authoritative;
- reset remains authoritative;
- overlapping promises are ordered by invocation in an ordinary one-store sequence;
- stale rejection remains caller-visible without changing newer state.

The candidate intentionally does not serialize ordinary asynchronous storage writes. If `storage.setItem(1)` and `storage.setItem(2)` themselves settle out of order, that is a separate backend-operation question.

## Exact execution

### Characterization head `09e7964...`

Successful:

- Test `30691421788`;
- Test Multiple Builds `30691421748`;
- Test Multiple Versions `30691421760`;
- Test Old TypeScript `30691421765`;
- Compressed Size `30691421781`.

Preview Release `30691421778` failed only at fork-hosted preview publication because the required GitHub App is not installed. This does not invalidate the successful target build.

### Candidate head `348156c...`

Successful:

- Test `30691537697`, job `91347025242`:
  - format passed;
  - types passed;
  - lint passed;
  - 50 test files and 447 tests passed;
  - `atomWithStoragePromiseWriteGeneration.test.ts` passed all four cases;
  - complete build passed.
- Test Multiple Versions `30691537706`;
- Test Multiple Builds `30691537710`;
- Test Old TypeScript `30691537723`;
- Compressed Size `30691537704`.

Preview Release `30691537696` failed only at fork-hosted preview publication after a successful build because the required GitHub App is not installed.

The characterization and candidate are target-executed at their exact heads. Green execution does not settle the broader ownership defect found during review.

## Complete-diff review findings

### 1. The generation is shared across stores

`writeGeneration` is a closure variable on the atom definition. Jotai atoms can be used by more than one store or Provider. Consequently:

1. Store A starts a promised update and captures generation 1.
2. Store B writes the same atom and advances the shared counter to 2.
3. Store A's promise resolves and is classified stale.
4. The candidate skips both Store A's state update and its storage operation.

The atom state itself is store-local, while the candidate authority is atom-global. In server or multi-Provider use, unrelated stores or requests can therefore cancel each other's promised state publication. The current four tests all use one store and do not exercise this boundary.

The shared underlying storage key makes cross-store persistence policy a real design question: storage authority may be global while in-memory atom authority is store-local. One closure counter cannot express both without an explicit policy.

### 2. Authority is assigned after updater evaluation

The candidate computes a functional updater before incrementing `writeGeneration`. If an updater callback performs a reentrant write to the same atom, that nested later invocation advances the counter first; the outer earlier invocation then increments again and regains authority.

This contradicts the candidate description that every update invocation establishes authority in call order. Either the generation must advance before updater evaluation, or reentrant updater behavior must be explicitly excluded and defended by target contract.

### 3. Newer rejection policy is untested

A newer promised update advances authority immediately. If it later rejects, an older promise that could otherwise resolve successfully remains stale and cannot publish. This is a plausible last-invocation-wins rule, but the existing test covers only rejection of the stale older promise. The reverse case needs an explicit test and policy statement.

## Next discriminating probes

### Multi-store characterization

Use one atom and two independent stores:

1. start an older promised update in Store A;
2. invoke a newer direct or promised update in Store B;
3. resolve the older Store A promise;
4. record Store A state, Store B state, storage calls, and caller-visible promise settlement.

Compare at least these policies:

- global invocation authority for storage and state;
- per-store state authority with global storage authority;
- fully per-store authority, which may conflict with the shared storage key.

Do not select an implementation before this policy is named.

### Reentrant updater characterization

Run a functional updater that triggers a nested write before returning an older promise. Verify whether public invocation order or callback completion order owns the final state and storage operation.

### Rejection control

Start an older promise, invoke a newer promise, reject the newer promise, then resolve the older promise. Record whether the older promise remains suppressed and whether that matches the intended API contract.

## Prior-art check

Searches on `2026-08-01` for Jotai `atomWithStorage` promised update ordering, stale promise writes, and related pull requests did not surface an equivalent current repair. Historical issue `pmndrs/jotai#263` discusses timing concerns around asynchronous state and external storage, but it does not establish or repair this exact built-in promised-update sequence.

This search can miss differently worded or unindexed discussions and must be repeated before promotion.

## Risks and reversing controls

- Maintainers may define promised updates as independent async actions whose resolution order intentionally controls state. That would reject the entire invocation-generation direction.
- Maintainers may define one atom's storage authority globally across stores while retaining store-local state, requiring a split authority model rather than one counter.
- A caller may rely on an older promised update eventually applying after a newer direct update. The inspected API does not document this ordering.
- The candidate must not be described as solving general persistence ordering.

## Disposition

Current disposition: `ISSUE FIRST / REPAIR`.

The source behavior and one-store candidate are target-executed. The candidate is not ready because its authority scope crosses Jotai stores and its updater/rejection edge semantics remain unnamed.

## Stop condition

Stop after the multi-store, reentrant-updater, and newer-rejection probes produce one explicit authority policy. Do not widen into general backend write serialization, read ordering, subscription ordering, or public upstream contact.
