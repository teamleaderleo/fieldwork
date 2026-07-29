# Plain-language explainer: Stop, streams, and resumable runs

## The five-year-old version

Imagine an AI response is a restaurant order.

- the model is the cook;
- a local tool is another worker, such as someone checking the weather or charging a card;
- the stream is a conveyor belt carrying pieces of the answer to the screen;
- the Stop button is the emergency-stop button for the whole order.

Two actions can look similar while meaning different things.

### “I stopped watching”

This is like turning off one television that shows the kitchen.

That television should stop receiving pictures. The kitchen may still have another television, a recorder, a persistence worker, or a resumable client that needs the order to continue.

In the SDK this is consumer or reader cancellation. It should normally affect only that consumer.

### “Stop the whole order”

This is pressing the red emergency button.

The cook should receive the stop signal. Cooperative tool workers should receive it. The conveyor belt should close. Public result promises and callbacks should all agree that the operation was aborted.

In the SDK this is an explicit operation abort through `AbortSignal`.

## The confirmed core problem

At the pinned revision, the resilient stream can be waiting inside `reader.read()`. The implementation checks the abort signal only after that read returns. If the provider keeps the stream open without producing another chunk, the caller can press Stop while public result promises remain pending.

Evidence: [pinned resilient-stream implementation](https://redirect.github.com/vercel/ai/blob/2b872b0db3769decf69945830c66a897c1e37347/packages/ai/src/generate-text/stream-text.ts#L1432-L1493).

The draft candidate adds an abort listener that does not need another provider chunk before reacting. Campaign #76 and owned draft PR [`teamleaderleo/ai#1`](https://github.com/teamleaderleo/ai/pull/1) track that work.

## Why callback ordering matters

The current candidate roughly does this:

1. reject public result promises;
2. wait for `onAbort` and telemetry callbacks;
3. emit the abort part;
4. close the outward stream;
5. cancel the provider reader.

The callback helper waits for callback promises. A callback that never settles can therefore delay provider cancellation and outward stream closure.

Evidence: [`notify()` waits for callback promises](https://github.com/teamleaderleo/ai/blob/fieldwork/explicit-abort-terminal-settlement/packages/ai/src/util/notify.ts#L6-L20) and the [candidate abort path](https://github.com/teamleaderleo/ai/blob/fieldwork/explicit-abort-terminal-settlement/packages/ai/src/generate-text/stream-text.ts#L1443-L1560).

The preferred invariant under review is:

1. abort wins the terminal-state race;
2. root result promises reject;
3. the outward stream emits and closes one abort outcome;
4. provider cancellation is requested;
5. logging and telemetry are notified without being able to reopen, replace, or indefinitely delay the terminal result.

The draft contains an `it.fails` regression that records the current callback-stall defect. It must become a normal passing test before promotion.

## Why abort/error arbitration matters

Suppose the user presses Stop and the provider connection fails almost simultaneously.

Without an explicit winner rule, different layers can disagree:

- public result promises say “aborted”;
- the outward stream throws “provider error”;
- callbacks or persistence record a third interpretation.

That makes recovery, UI state, billing, retries, and debugging unreliable. Campaign #76 therefore requires one terminal winner and includes an `it.fails` abort/provider-error race test.

## The resumable Stop problem

Imagine each AI generation is a package. A chat can contain many packages over time.

The pinned example stores a Stop timestamp on the whole chat instead of one specific run.

A simple stale-state sequence is:

1. run A starts;
2. Stop A stores `canceledAt` on the chat;
3. run B starts later;
4. B reads A’s old Stop marker and aborts.

Owned draft PR [`teamleaderleo/ai#3`](https://github.com/teamleaderleo/ai/pull/3) fixes that ordered case by clearing and awaiting the old state before B starts.

A harder race remains:

1. B starts;
2. a delayed Stop request intended for A arrives;
3. the request names only the chat;
4. the server cannot tell that the Stop belongs to A, so B can be cancelled.

The complete design needs a generation or run ID. Stop, resumable registration, finish, abort cleanup, and message persistence must update state only when that run still owns the operation. Campaign #95 tracks this work and keeps the delayed-Stop case as an `it.fails` test.

## The incomplete-stream problem

A third case is neither reader cancellation nor explicit abort.

A provider can close after producing partial output but before sending a terminal finish chunk. At the pinned revision, partial text can be retained and the finish reason becomes `other`; UI end handling does not classify it as aborted.

Evidence: [pinned partial-close tests](https://redirect.github.com/vercel/ai/blob/2b872b0db3769decf69945830c66a897c1e37347/packages/ai/src/generate-text/stream-text.test.ts#L2644-L2724).

Keeping partial text is useful, but callers need a truthful way to distinguish ordinary completion from protocol truncation. Campaign #94 owns that classification question.

## What happens if this work is skipped

- Stop can appear to work while result promises remain pending forever.
- Provider or cooperative tool work can continue consuming resources after Stop.
- Applications can remain stuck in a generating state.
- One layer can report abort while another reports provider error or ordinary completion.
- Persistence can save partial or aborted output as complete.
- A Stop for an older run can cancel a newer run.
- Users may retry and duplicate model calls or already-committed tool side effects.
- Logging or telemetry callbacks can accidentally control operational cancellation.

## Why the tests are shaped this way

The tests use mock provider streams, local tools, temporary file-backed state, and exact event ordering. They avoid provider credentials and network timing, making the races repeatable.

Ordinary tests protect behavior that should already work. `it.fails` tests are executable records of known defects: a green suite while they remain `it.fails` means the defect was reproduced as expected, not fixed. Promotion requires converting those cases to normal passing tests.

## Current status

- campaign #76: explicit-abort settlement and terminal arbitration;
- campaign #94: truthful classification of truncated provider streams;
- campaign #95: run-scoped resumable Stop ownership;
- owned AI SDK PRs #1 and #3 remain drafts;
- fork tests are written and statically reviewed but have not run in this environment;
- no upstream contact has been made or authorized.