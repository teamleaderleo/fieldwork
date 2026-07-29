# Verification notes: Vercel AI lifecycle candidates

## Scope and status

- Scout: #17
- Scout PR: #34
- Pinned target base: [`teamleaderleo/ai@2b872b0db3769decf69945830c66a897c1e37347`](https://github.com/teamleaderleo/ai/commit/2b872b0db3769decf69945830c66a897c1e37347)
- Explicit-abort campaign: #76
- Explicit-abort draft candidate: [`teamleaderleo/ai#1`](https://github.com/teamleaderleo/ai/pull/1)
- Resumable Stop campaign: #95
- Sequential stale-state draft mitigation: [`teamleaderleo/ai#3`](https://github.com/teamleaderleo/ai/pull/3)
- Idle UI response campaign: #150
- UI keep-alive draft candidate: [`teamleaderleo/ai#4`](https://github.com/teamleaderleo/ai/pull/4)
- Central review registration: #87 and evaluator dogfood #138
- Upstream contact: none

The local work environment could not resolve GitHub for a checkout. GitHub Actions later became available for owned PRs #1 and #4, so these notes distinguish local non-execution, historical CI from older heads, current-head receipts, and unexecuted integration gates. PR #3 still has no workflow run.

## Explicit-abort candidate review

### Branch-history correction

The maintainer-authored implementation staged from the [external candidate](https://redirect.github.com/vercel/ai/pull/16852) initially retained a divergent commit history. A compare against the claimed pin showed the branch six commits ahead and 262 commits behind.

GitHub had already computed a conflict-free merge commit for the pull request. The owned branch was fast-forwarded to that computed merge commit, preserving the reviewed file tree while making the pinned base an ancestor.

Current explicit-abort branch head:

`e685a4c92a5869aec306718ab5a440b7cb4fa5b1`

The branch remains cleanly based on the pin and contains the intended five-file candidate diff: one production file, the existing target test, two focused Fieldwork tests, and one changeset.

This correction matters because a mergeable pull request is not by itself proof that its branch actually descends from the claimed evaluation base.

### Ordinary regression tests

The candidate has target-native tests for:

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

### CI evidence

An older owned-fork CI run produced useful partial validation:

- TypeScript typecheck passed;
- package build passed;
- code-consistency checks passed;
- changeset verification passed;
- the main workflow failed only because the two new test files did not match the repository formatter.

A temporary owned-branch workflow ran the repository formatter and printed its exact diff. The formatter-produced blob contents were applied byte-for-byte and the temporary workflow was deleted, returning the pull request to its intended five files.

Current-head receipts:

- changeset verification run `30495574982`: passed;
- normal CI run `30495574988`: queued.

No clean current-head main-CI result is claimed yet. Historical success remains bound to the older tested head.

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

### Validation status

Current branch head:

`56453af2c2688d158d4291293a11dfe34db260e7`

No owned-fork workflow run is visible for this branch. Its targeted test remains `target-test-prepared`, statically reviewed, and unexecuted.

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

## Idle UI response candidate review

### Candidate boundary

PR #4 adds optional `keepAliveMs` support to the client response branch of UI message stream helpers. The option is off by default.

The candidate:

- emits one immediate SSE comment;
- emits periodic comments after idle intervals;
- resets the timer after canonical UI data;
- tees canonical SSE before adding comments, so persistence and resumable consumers remain unchanged;
- emits comments only while the client branch has demand;
- clears timers on close, error, and cancel;
- requests source-branch cancellation without waiting for an independent tee consumer;
- ignores a pending source read that resolves after cancellation;
- validates before locking or teeing the source or invoking callbacks;
- forwards the option through Fetch, Node, `streamText`, and agent response helpers.

Current candidate head:

`88849192b0b235ef79cc6d0fb1aaa9b9a17e98b5`

### CI evidence

The first CI run on an older head established that:

- changeset verification passed;
- package builds passed;
- code-consistency checks passed;
- the AI test shard ran 758 tests with no type errors;
- 757 tests passed;
- one new cancellation test failed because it asserted that downstream source cancellation had completed when the deliberately non-blocking client cancellation promise resolved;
- two new helper tests required repository formatting.

The implementation contract is that client cancellation must not wait for an independent persistence tee, while cancellation still propagates eventually. The test now waits for eventual source cancellation instead of requiring it to be complete synchronously. The two formatter-rejected files were corrected on the current head.

Current-head receipts:

- changeset verification run `30494247723`: passed;
- normal CI run `30494247717`: queued.

No clean current-head package-CI result is claimed yet. The 757/758 receipt remains historical evidence for its tested head.

### Remaining validation gate

Even a green package suite cannot prove deployment behavior. Promotion still requires:

- one real self-hosted HTTP reproduction showing that the opening comment flushes the status and headers;
- one reverse-proxy or configurable idle-timeout reproduction showing that periodic comments maintain liveness;
- supported-client confirmation that SSE comments remain invisible to the UI protocol;
- repeated open/cancel leak checks;
- deployment guidance that does not promise one universal interval.

## Central review disposition

The packet is registered as four independent review nodes on coordination issue #87 and evaluator dogfood issue #138. The scout and synthesis PR are evidence parents, not one blanket acceptance decision.

- PR #1: requested disposition `REPAIR` or `EXECUTE`; two lifecycle races remain expected failures.
- Campaign #94: requested contract disposition `ACCEPT`, `HOLD`, or `REJECT`; no implementation branch exists.
- PR #3: requested disposition `EXECUTE`, then `REPAIR` or `HOLD`; run ownership remains absent.
- PR #4: requested disposition `EXECUTE` or `REPAIR`; current package CI and real HTTP/proxy gates remain open.

The author's self-review does not count as independent acceptance.

## Final review disposition

- PR #1 remains a draft candidate with exact formatter output applied and current-head changeset verification passed; normal CI is queued.
- PR #3 remains a draft sequential mitigation with one ordinary regression and one expected-failure ownership test, but no workflow execution.
- PR #4 remains a draft transport candidate with historical 757/758 evidence, current-head changeset verification passed, and normal CI queued. Real HTTP/proxy validation remains mandatory.
- None of the candidates should yet be described as release-ready or complete.
- Reader cancellation remains consumer-scoped and is not changed by these candidates.
