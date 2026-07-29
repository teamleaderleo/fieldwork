# Verification notes: Vercel AI lifecycle candidates

## Scope and status

- Scout: #17
- Scout PR: #34
- Pinned target base: [`teamleaderleo/ai@2b872b0db3769decf69945830c66a897c1e37347`](https://github.com/teamleaderleo/ai/commit/2b872b0db3769decf69945830c66a897c1e37347)
- Explicit-abort campaign: #76
- Explicit-abort draft candidate: [`teamleaderleo/ai#1`](https://github.com/teamleaderleo/ai/pull/1)
- Resumable Stop campaign: #95
- Sequential stale-state draft mitigation: [`teamleaderleo/ai#3`](https://github.com/teamleaderleo/ai/pull/3)
- Upstream contact: none

These notes record static review and test construction. The fork has no Actions runs or commit statuses, and the available execution environment could not resolve GitHub for a checkout. The listed tests have not been executed here.

## Explicit-abort candidate review

### Branch-history correction

The maintainer-authored implementation staged from the [external candidate](https://redirect.github.com/vercel/ai/pull/16852) initially retained a divergent commit history. A compare against the claimed pin showed the branch six commits ahead and 262 commits behind.

GitHub had already computed a conflict-free merge commit for the pull request. The owned branch was fast-forwarded to that computed merge commit, preserving the reviewed file tree while making the pinned base an ancestor.

Current explicit-abort branch head:

`cb5eb2582ab22d870b3be4749addd014a90af53a`

Current comparison against the pin:

- ahead: 7 commits;
- behind: 0 commits;
- changed files: 5;
- changed production file: `packages/ai/src/generate-text/stream-text.ts`;
- remaining changes: changeset and focused tests.

This correction matters because a mergeable pull request is not by itself proof that its branch actually descends from the claimed evaluation base.

### Ordinary regression tests

The candidate now has target-native tests for:

- explicit abort after partial output while the provider's next read remains pending;
- rejection of the five root settlement promises;
- rejection of representative derived getters;
- provider-reader cancellation;
- a signal already aborted before `streamText` begins;
- explicit abort during delayed local-tool execution;
- suppression of normal completion and later tool results;
- two active stream consumers receiving one abort part each while `onAbort` and provider cancellation occur once.

The five directly rejected roots are:

1. finish reason;
2. raw finish reason;
3. usage;
4. steps;
5. initial response messages.

Other public getters derive from those roots.

### Expected-failure tests

`packages/ai/src/generate-text/stream-text-explicit-abort-races.test.ts` contains two `it.fails` cases:

1. a pending `onAbort` callback currently delays provider-reader cancellation and outward stream closure;
2. a provider error arriving immediately after the abort signal can compete with the outward abort result.

These are executable defect records, not completed fixes. A green run while they remain `it.fails` means Vitest reproduced the expected defects. When the implementation is corrected, each case must be converted to an ordinary `it` test.

### Focused commands

```bash
pnpm --dir packages/ai test:node -- \
  src/generate-text/stream-text-explicit-abort.test.ts \
  src/generate-text/stream-text-explicit-abort-races.test.ts

pnpm --dir packages/ai test:edge -- \
  src/generate-text/stream-text-explicit-abort.test.ts \
  src/generate-text/stream-text-explicit-abort-races.test.ts

pnpm --dir packages/ai type-check
```

The package Node and Edge Vitest configurations include `**/*.test.ts` files and enable typechecking.

### Remaining implementation gate

The candidate rejects result promises before invoking abort callbacks, but it awaits `notify()` before emitting the outward abort part, closing the outward stream, and cancelling the provider reader. Because `notify()` waits for callback promises, observability can block terminal mechanics.

The implementation must select and test an explicit ordering contract. The recommended invariant is:

1. mark abort as the winning terminal state;
2. reject public result roots;
3. close or terminate outward delivery with one abort part;
4. request provider cancellation;
5. notify callbacks without allowing them to reopen, replace, or indefinitely delay the terminal outcome.

The abort/provider-error race must use the same winner rule.

## Resumable Stop mitigation review

### Refactoring for a testable state transition

The example route now calls an exported `prepareChatForNewRun()` helper. The helper performs the exact awaited sequential transition used before constructing the next provider request:

- save the new message list;
- clear `activeStreamId`;
- clear `canceledAt`.

The helper documentation explicitly says that it is not a run-scoped compare-and-set primitive.

### Ordinary regression test

`examples/next/util/chat-store.test.ts` uses the real file-backed chat store in a temporary directory. It records a stopped run, calls `prepareChatForNewRun()`, and verifies that the next immediate read sees cleared cancellation and active-stream state while preserving chat creation metadata.

### Expected-failure ownership test

The same file contains an `it.fails` case representing a delayed Stop for run A that arrives after run B has started. Because the current record identifies only the chat, it cannot reject the old intent. The test remains expected to fail until cancellation carries a run identity.

### Focused command

```bash
pnpm exec vitest --run \
  examples/next/util/chat-store.test.ts \
  --environment node
```

### Remaining ownership gate

A complete solution requires a run identity and conditional ownership for:

- Stop requests;
- active resumable stream registration;
- finish and abort cleanup;
- message persistence;
- duplicate and delayed requests;
- older-run completion after a newer run starts.

Awaiting file writes fixes local sequential ordering but does not serialize concurrent requests or prevent read-modify-write lost updates.

## Final review disposition

- PR #1 remains a draft candidate. It has clean ancestry and substantially stronger tests, but two lifecycle races are deliberately recorded as expected failures and the suite is unexecuted.
- PR #3 remains a draft sequential mitigation. It now has a passing narrow regression and an expected-failure test proving that run ownership is still missing.
- Neither pull request should be described as validated, release-ready, or a complete fix.
- Reader cancellation remains consumer-scoped and is not changed by either candidate.
