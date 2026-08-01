# Approaches — Unit 09 UI-stream SSE keep-alive

## In simple words

The selected technical direction uses optional SSE comments on the client response branch after canonical persistence has split off. It gives the client an immediate byte and later idle bytes without changing UI chunks or stored SSE. A current public pull request independently selected the same approach, so the owned candidate now serves as validation and edge-case prior art.

## Decision criteria

1. preserve canonical UI and persisted SSE bytes;
2. produce a first client body byte and refresh idle liveness;
3. retain one pending source read, bounded comments, and reliable terminal cleanup;
4. preserve disabled behavior and propagate through every public response helper;
5. keep configuration guidance deployment-specific;
6. minimize duplicate upstream review cost.

## Selected approach

### Client-only SSE comments after the persistence tee

- Design: optional immediate comment plus periodic idle comments at the encoded SSE string layer.
- Owning boundary: the UI-message response helper after `consumeSseStream` receives its canonical tee branch.
- Evidence: owned exact-head CI, 100-cycle cancellation soak, real Node first-byte probe, controlled forwarding-proxy probe, and persistence byte controls.
- Advantages: additive API, standards-compatible ignored bytes, canonical storage unchanged, bounded lifecycle work.
- Costs and risks: a timer and manual stream pump when enabled; interval depends on deployment; cancellation and validation ordering need explicit controls.
- Remaining controls: observe whether the public replacement incorporates pre-tee validation and persistence-independent client cancellation.

## Viable alternatives

### Always emit an opening comment, opt in only to periodic comments

- Design: make the first comment unconditional and retain an interval option for later comments.
- Why it remains plausible: immediate comment cost is small and avoids headerless responses by default.
- What it would improve: first-byte behavior without operator configuration.
- What it would widen or complicate: changes wire bytes for every existing response and may surprise byte-sensitive callers.
- Exact discriminator: maintainer compatibility preference and disabled-output tests.
- Reopening trigger: upstream explicitly chooses always-on prelude behavior.

### Separate opening and idle options

- Design: one boolean or mode for the prelude and another interval for idle comments.
- Why it remains plausible: deployments may need first-byte flush without periodic traffic.
- What it would improve: finer control.
- What it would widen or complicate: larger API, more combinations, more tests, and unclear default interaction.
- Exact discriminator: demonstrated caller need for independent controls.
- Reopening trigger: issue discussion shows distinct use cases that one option cannot express.

### Runtime-specific header flush

- Design: call a Node or framework flush primitive before body data.
- Why it remains plausible: can address first-byte behavior in one runtime.
- What it would improve: no synthetic body byte for that adapter.
- What it would widen or complicate: runtime coupling and no portable idle-liveness behavior.
- Exact discriminator: continued connection through an idle deadline.
- Reopening trigger: a portable first-party flush plus heartbeat primitive appears in all supported response paths.

## Executed losing approaches

### Heartbeat UI chunks or pre-tee comments

- Exact branch: earlier design exploration retained in Fieldwork issue #150 and finding F150.
- What ran: persistence comparison and source-path review.
- Result: synthetic bytes would enter application or persistence data.
- Why it lost: violates the governing invariant.
- Useful evidence retained: the persistence tee is the decisive placement boundary.

### Manual formatting guesses

- Exact generations: predecessor heads through `bf3942cd1b615baa43fadcb27388a6911c0c5390`.
- What ran: repository lint/format jobs.
- Result: two helper tests remained rejected until the repository formatter authored the exact spelling.
- Why it lost: manual guesses did not match target formatting.
- Useful evidence retained: formatter carrier produced the bounded two-file correction and removed itself.

### New duplicate upstream pull request

- Exact inputs: public issue `vercel/ai#17805`; public PR `vercel/ai#17921` at `21cd681724103701c3596770d7252a7ef0ad18db`.
- What ran: current issue/PR search, changed-file review, key implementation and all changed test patches.
- Result: same API and core repair already occupy the public lane.
- Why it lost: duplicate submission would increase unsolicited review cost.
- Useful evidence retained: two owned edge controls remain useful review input if future authority permits contact.

## Rejected easy answers

### Documentation only

- Temptation: tell operators to configure proxies or wrap streams themselves.
- Why incomplete: the SDK helper has no portable body-liveness option and every deployment would reimplement cancellation and persistence details.
- Negative control: controlled proxy closes silent traffic while the candidate remains open.

### Fresh read on every interval

- Temptation: race a new `reader.read()` against each timer.
- Why incomplete: long idle periods accumulate pending reads.
- Negative control: single-read-count tests require one outstanding source read across repeated comments.

### Await branch cancellation

- Temptation: return `reader.cancel(reason)` directly from the client wrapper.
- Why incomplete: a branch from `ReadableStream.tee()` can keep its cancellation promise pending until its sibling settles.
- Negative control: owned test keeps `consumeSseStream` active and requires client cancellation to resolve independently.

### Validate inside the wrapper after teeing

- Temptation: keep validation beside timer construction.
- Why incomplete: invalid input can lock/tee the source and invoke persistence callbacks before throwing.
- Negative control: owned response tests require unlocked source and zero callback calls for invalid values.

## Prior upstream approaches

| Link | Approach | Status | Relationship to this unit |
| --- | --- | --- | --- |
| [`vercel/ai#17805`](https://github.com/vercel/ai/issues/17805) | production report, minimal idle reproduction, SSE-comment workaround, `keepAliveMs` ask | open | equivalent public problem statement |
| [`vercel/ai#17921`](https://github.com/vercel/ai/pull/17921) | same optional API and post-tee comment pump, parser test, docs, Node example | open | supersedes submission; owned work supplies lifecycle review controls |
| [`teamleaderleo/ai#4`](https://github.com/teamleaderleo/ai/pull/4) | owned candidate with exact-head CI and cancellation/validation controls | retained historical candidate | independent validation |
| [`teamleaderleo/ai#6`](https://github.com/teamleaderleo/ai/pull/6) | execution-only real Node and controlled proxy probe | closed unmerged | retained integration receipt |

## Deferred adjacent work

- per-proxy interval recommendations — operator documentation, separate from core stream correctness;
- automatic reconnect policy — transport-level follow-up;
- application operation timeouts — separate lifecycle question;
- production deployment access — outside authority and evidence scope.

## Decision history

| Date | Exact inputs | Decision | Reason | Reopening trigger |
| --- | --- | --- | --- | --- |
| 2026-07-30 | base `2b872...`, owned candidate generations | select post-tee optional comments | preserves persistence and proves liveness | reversing persistence/client evidence |
| 2026-07-31 | carrier run `30506032517` | retain transport direction | real Node and controlled proxy passed | representative contradiction |
| 2026-07-31 | head `b4b572...`, CI `30592239115` | candidate gate complete | all named fork jobs passed | head movement |
| 2026-08-01 | upstream main `e84b8bc...`, public PR `21cd6817...` | `SUPERSEDED — validation only` | directly overlapping active public work | public replacement closes or omits required lifecycle controls |
