# Adjacent Vercel AI SDK review

## Purpose

This note records the broader read-only scan requested after the original stream/tool lifecycle scout. It distinguishes:

- useful precedent that strengthens the current campaigns;
- nearby defects already owned by external work, where duplicate implementation should stop;
- subsystems reviewed and judged not to reproduce the suspected failure shape;
- one newly promoted Fieldwork candidate.

Pinned owned target: [`teamleaderleo/ai@2b872b0db3769decf69945830c66a897c1e37347`](https://github.com/teamleaderleo/ai/commit/2b872b0db3769decf69945830c66a897c1e37347).

No upstream contact was made.

## Precedent 1: terminal outcome must be classified once

A later HarnessAgent fix established the same outcome rule used by campaign #76: a caller-triggered abort should surface as an abort part, not as an error part. The fix moved failure settlement ahead of forwarding so an aborted turn could not emit both an error and an abort outcome.

Evidence: [HarnessAgent abort-semantics commit](https://redirect.github.com/vercel/ai/commit/86a84c90c05a2dbbf828505b2809a0350b13c7e8).

### Relevance

- supports explicit abort winning the terminal race;
- supports no competing outward provider-error outcome after abort wins;
- supports UI `onError` remaining silent for a clean user Stop;
- supports `onEnd({ isAborted: true })` agreeing with the stream.

This is direct precedent for the expected-failure abort/provider-error test in owned draft `teamleaderleo/ai#1`.

## Precedent 2: public result promises must own stream progress

Streaming transcription previously allowed `await result.text` to deadlock unless `fullStream` was consumed. The accepted repair made result getters claim and drain the stream, with an explicit single-consumer ownership contract for unbounded audio.

Evidence: [streaming transcription ownership commit](https://redirect.github.com/vercel/ai/commit/2696562b90b6f181df8696c40b2f6dfbe89a0386).

### Relevance

- confirms that public result accessors must settle without hidden extra consumption requirements;
- shows that stream ownership should be explicit where replay buffering is unsafe;
- provides a model for distinguishing replayable `streamText` results from unbounded live streams.

## Precedent 3: lazy stream lifetimes own timer cleanup

A later `streamText` step-timeout fix found that a timer was cleared when a lazy stream was merely registered, not when the step actually ended. The repair moved timer ownership into the stream lifecycle and added stall and leak tests.

Evidence: [step-timeout lifecycle commit](https://redirect.github.com/vercel/ai/commit/eeefc3f64920fc4f576263f1272194e004edae4d).

A later first-content timeout change expanded the same standard: semantic activity definitions, abort-listener cleanup, provider error, cancellation, multi-step re-arming, Node and Edge coverage, and documentation.

Evidence: [first-content timeout commit](https://redirect.github.com/vercel/ai/commit/106ea59106671b9e782d32c1fa2acdbce2ab5057).

### Relevance

- timer and listener cleanup are correctness requirements, not polish;
- tests must cover idle streams, cancellation, provider error, and normal completion;
- the UI keep-alive candidate must clear timers and preserve backpressure on every terminal path.

## Reviewed subsystem: streaming translation

Current streaming translation was checked for the old transcription deadlock and cancellation shape.

The implementation:

- gives the live stream one explicit owner;
- lets the first result getter claim and drain the stream;
- rejects late or duplicate `fullStream` access clearly;
- propagates `fullStream` cancellation to pending setup and the model stream;
- cancels unowned input audio after setup failure;
- rejects pending result promises on stream failure.

Its tests cover promise-only access, full-stream-first access, concurrent result access, cancellation, setup failure, provider error, and ownership errors.

### Disposition

**No new Fieldwork issue.** The reviewed current implementation already embodies the relevant ownership contract and does not reproduce the earlier deadlock shape.

## Stopped duplicate: UI end-outcome ambiguity

The finding that UI end callbacks can persist fatal failures as completed overlaps campaign #94 and is independently reproduced externally.

Active external work already includes:

- a full outcome-model candidate with completed, failed, aborted, and unknown states;
- execution and merged-stream failure coverage;
- explicit composer outcome declarations;
- version-specific reproductions.

Evidence: [outcome candidate](https://redirect.github.com/vercel/ai/pull/17578) and [underlying issue](https://redirect.github.com/vercel/ai/issues/17500).

### Disposition

**Stop duplicate implementation.** Use the external proposal as precedent and compatibility input for campaign #94. Continue only if the Fieldwork truncation matrix demonstrates a missing incomplete/protocol-close state not represented by that proposal.

## Stopped duplicate: large-output tee retention

`streamText().textStream` can retain large outputs because the public path tees the stream and materializes final text/reasoning. The reported constrained-memory failure is concrete.

External work already contains:

- constrained-heap reproductions;
- a proposed opt-in single-consumer mode;
- result-first and stream-first ownership rules;
- duplicate-consumer rejection;
- versions for current and release branches.

Evidence: [current candidate](https://redirect.github.com/vercel/ai/pull/17980), [release-branch candidate](https://redirect.github.com/vercel/ai/pull/18034), and [issue](https://redirect.github.com/vercel/ai/issues/16753).

### Disposition

**Stop duplicate implementation.** The work is real but already has a stronger reproduction and candidate than a new Fieldwork branch would add.

## Promoted candidate: idle UI response liveness

The current UI response helper writes no body byte until the first UI chunk and exposes no keep-alive interval. A self-hosted idle stream can therefore fail to flush its response head and can later be closed by a reverse proxy after prolonged silence.

The external report provides:

- a minimal idle `ReadableStream` reproduction;
- direct-origin and reverse-proxy observations;
- a working SSE-comment workaround;
- a maintainer high-confidence bug classification.

Evidence: [idle UI stream bug](https://redirect.github.com/vercel/ai/issues/17805).

No matching external fix PR was found.

### Owned candidate

- Fieldwork campaign: #150
- owned draft: [`teamleaderleo/ai#4`](https://github.com/teamleaderleo/ai/pull/4)
- branch: `teamleaderleo/ai:fieldwork/ui-message-stream-keepalive`

The candidate adds opt-in `keepAliveMs` with:

- immediate `: stream-open` SSE comment;
- periodic idle comments;
- client-branch-only injection after the persistence tee;
- demand-aware bounded buffering;
- timer cleanup on close, error, and cancel;
- client cancellation independent of a persistence branch;
- propagation through Fetch, Node, `streamText`, and agent response helpers;
- documentation and focused tests.

### Review corrections made before opening

1. guarded a pending source read that resolves after cancellation;
2. moved interval validation before source locking, tee creation, and callback side effects;
3. changed client cancellation so it does not await a tee branch shared with persistence;
4. found and fixed silent option dropping in both agent helpers;
5. kept synthetic comments out of `consumeSseStream`;
6. added runtime smoke tests for every advertised helper path.

### Remaining gates

- focused Node and Edge execution;
- package typecheck, formatting, lint, and docs validation;
- repeated open/cancel leak checks;
- real self-hosted first-byte verification;
- reverse-proxy or configurable idle-timeout verification;
- supported-client confirmation that SSE comments remain invisible to the UI protocol.

## Ranked next work

1. Execute and correct draft `teamleaderleo/ai#1`; convert its callback-stall and abort/error expected failures into normal tests.
2. Execute and validate draft `teamleaderleo/ai#4`, then run a real HTTP/proxy reproduction.
3. Replace chat-scoped Stop state with run identity under campaign #95; convert its delayed-Stop expected failure.
4. Build campaign #94's truncation matrix and compare its needed terminal status with the existing external UI outcome proposal.
5. Monitor, but do not duplicate, the large-output single-consumer work.

## Boundary

This review used public source, history, issues, and proposals only. It made no upstream comment, review, issue, or pull request and made no acceptance claim for external work.