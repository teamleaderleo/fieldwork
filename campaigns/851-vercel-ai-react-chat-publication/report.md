## In simple words

Vercel AI SDK's React chat state deep-clones the complete assistant message on every streamed replacement. Public upstream reproduction now establishes the resulting copy amplification on both AI SDK 7/main and the v6 release line. The tempting fix is to copy only the message, parts array, part shells, and metadata shell.

That stream mutation boundary is real, but a blanket shallow replacement is broader than the performance problem. `ReactChatState.replaceMessage` is also used for imperative user/tool updates. In particular, `addToolOutput()` accepts a caller-owned nested `output`, publishes it through `replaceMessage`, and may also write it into the active mutable response. Current React deep cloning detaches that external object. Replacing every `replaceMessage` clone with a shallow part-shell copy can expose caller-owned values by reference.

The useful target is therefore narrower:

> acquire ownership of mutable/external nested values once, then make repeated stream publication cheap and immutable.

This report records the source boundary, the first target execution result, the adjacent first-publication alias, and the design gates a credible fix needs to pass.

## Assignment

- Programme: `sdk-integration-lifecycle` / #13
- Target: `vercel-ai` / #2
- Campaign: #851
- Source scout: #841
- Adjacent ownership lead: #852
- Worker: `chatgpt:gpt-5.6-sol`
- Public source pin: `vercel/ai@7d40fafc394a2c9033f931eb85c895e3817f4b58`
- Owned source candidate: `teamleaderleo/ai#91`
- Focused execution carriers: `teamleaderleo/ai#92`, `teamleaderleo/ai#96`
- Upstream mutation: prohibited and not performed

## Public upstream state

At the source pin, `packages/react/src/chat.react.ts` still implements `ReactChatState.snapshot` with `structuredClone` and calls it from `replaceMessage`.

The current performance report is:

- https://github.com/vercel/ai/issues/18624
- AI SDK 7 reproduction: https://github.com/vercel/ai/pull/18625
- AI SDK 6 reproduction: https://github.com/vercel/ai/pull/18633

Upstream reproduction streams 40 tool outputs of 65,536 bytes. The final assistant message contains 2,621,440 bytes of tool output while 79 snapshots cumulatively clone 104,857,600 bytes: 40x payload-copy amplification.

The historical correctness reason is:

- https://github.com/vercel/ai/issues/6466
- https://github.com/vercel/ai/pull/6762

PR #6762 added the deep clone because React Compiler memoization could miss nested part changes. Its description explicitly retained a custom cloning approach as future work if the performance impact became significant. Issue #18624 is now that performance trigger.

Evidence class: `upstream-documented`, `source-read`.

## Current stream mutation contract

Source inspection at the pin shows the mutable streaming message is updated mainly at the message/part shell boundary:

- text and reasoning deltas mutate top-level `text`, `state`, and provider-metadata fields on their part;
- tool transitions assign top-level `state`, `input`, `output`, approval, error, title, tool metadata, and provider metadata;
- partial tool JSON is reparsed into a fresh value for each update;
- same-id data chunks replace the top-level `data` field;
- message metadata merge creates a fresh merged object along changed paths.

This supports the original scout result: fresh message + fresh part identities can preserve the sampled current mutation visibility without recursively copying unchanged large outputs every time.

The explicit invalidation boundary remains nested in-place mutation. If a supported stream path starts mutating inside a retained payload object without replacing the part's top-level field, a simple part-shell publication fence is insufficient.

Evidence class: `source-read`, with a reduced model retained by scout #841.

## First target execution

The first focused owned-fork compiler carrier executed far enough to establish:

- repository dependency install: passed;
- React dependency-closure build: passed;
- `@ai-sdk/react` type-check: passed;
- bounded replacement target test: failed before React Compiler;
- compiler install/discriminator: skipped after the prior failure.

The failing assertion expected an earlier tool part and a later tool part to have different identities.

That failure was diagnostic rather than evidence against the replacement fence. The test selected retained publications by inspecting their objects after the stream completed. The first assistant publication had been appended by reference and continued mutating, so that earlier object later contained the final tool output/text and was selected for multiple checkpoints.

The canonical target test was corrected to record text/output values at subscription callback time, then inspect the retained replacement publications corresponding to those observations.

Evidence class: `target-executed` for the failure mechanism; compiler result remains unclaimed.

## Adjacent finding: first assistant publication aliases mutable response state

Core stream publication currently does this on each write:

1. mutate `response.state.message`;
2. compare its id with the current last message;
3. replace when ids match;
4. otherwise call `state.pushMessage(response.state.message)`.

For the first new assistant publication after a user message, ids differ. React `pushMessage` concatenates the exact object reference. Later chunks continue mutating that same `response.state.message`.

So an earlier `chat.messages` publication can acquire later parts/text underneath a holder before replacement publication takes over. This is tracked separately as #852 because a replacement-only performance fix can leave it untouched.

A dedicated owned-fork target characterization now retains the first assistant publication at callback time, records its initial part count/text, completes a later text delta, then checks whether the earlier object gained those later values.

Evidence class: `source-read`, `model-executed`; target characterization prepared. The first #851 target failure also independently exhibited the alias mechanism in the real package path.

## Design review: why blanket shallow `replaceMessage` is too broad

The initial owned candidate #91 changed every React replacement from whole-message `structuredClone` to fresh message/part shells.

Deeper call-site review found `ChatState.replaceMessage` has several owners:

- stream publication from `runUpdateMessageJob`;
- user-message replacement through `sendMessage(...messageId...)`;
- `addToolApprovalResponse()`;
- `addToolOutput()`.

`addToolOutput()` is the important counterexample. It receives a caller-provided `output`, creates a new part containing that exact object, and calls `state.replaceMessage`. If a response is active, it also writes the same output into `activeResponse.state.message.parts`.

Current React replacement deep-clones the message, which detaches the published state from that caller object. A blanket shallow replacement removes that detachment. A later stream publication can also expose the raw active-response output unless ownership is established before bounded publication.

Therefore a React Compiler pass is necessary but no longer sufficient to promote #91.

Evidence class: `source-read`; an owned-fork RED ownership test is prepared that calls `addToolOutput` with a nested object, mutates the caller object afterward, and requires the published output to remain detached.

## Callback escape audit

The stream processor has two additional escape points worth preserving in the design:

### `onToolCall`

For `tool-input-available`, stream state stores `chunk.input`, publishes a write, then invokes `onToolCall` with the tool-call chunk. The current whole-message deep clone protects the already-published React snapshot from a callback that retains or mutates the input object. A shallow publication would share the same nested input unless ownership is acquired separately.

### `onData`

Persistent data parts store `dataChunk.data` (or the data chunk itself), invoke `onData`, then publish. Current deep publication detaches the resulting React snapshot. A bounded publication needs a clear policy for callback-held data objects as well.

There is no evidence that mutating callback arguments is a supported state-update mechanism. The important compatibility question is still explicit: a safe optimization should either preserve the current detached-snapshot effect or intentionally document/tighten the ownership contract.

Evidence class: `source-read`.

## Candidate designs

### A. Blanket part-shell replacement

Mechanism:

- every React `replaceMessage` copies message + parts array + each part shell;
- nested payloads remain shared.

Advantages:

- smallest patch;
- matches the current #18624 proposal;
- removes repeated large-output cloning.

Blockers:

- changes imperative `addToolOutput` ownership;
- leaves #852 first append alias;
- callback-held nested values can alias published snapshots;
- changing the shared `snapshot` method itself would also weaken the request-start ownership boundary.

Disposition: useful compiler characterization, not promotion-ready.

### B. Stream-specific publication mode

Mechanism:

- core distinguishes stream append/replace from ordinary state replacement;
- React keeps current deep clone for ordinary replacement;
- React uses message/part-shell publication only for stream-owned writes;
- stream append uses the same safe publication path, fixing #852.

Advantages:

- directly matches the performance mechanism;
- preserves imperative replacement behavior;
- explicit semantics are easier to test.

Remaining requirement:

- nested values entering active stream state from caller APIs/callback-visible chunks need one-time ownership acquisition before later shallow publications.

Disposition: preferred interface direction if a core/React split is acceptable.

### C. Ownership at stream ingress + bounded publication

Mechanism:

- clone/detach nested external values once when they enter the mutable response state;
- hand callbacks a distinct/original observation value according to a defined contract;
- thereafter publish fresh message/part shells while sharing SDK-owned nested payloads.

Advantages:

- strongest immutable-snapshot model;
- total copying becomes proportional to incoming payload bytes plus publication shells, not accumulated message bytes per chunk;
- resolves imperative active-response output and callback alias questions in one ownership model.

Costs:

- broader core changes;
- callback mutation behavior needs explicit compatibility review;
- more tests required.

Disposition: strongest semantic design; worth prototyping after compiler characterization confirms the part-shell boundary.

### D. Retain whole-message deep clone

Disposition: correctness baseline. Keep if compiler or ownership gates defeat bounded publication.

## Required promotion gates

A contribution candidate should pass all of these before any human upstream packet is prepared:

1. React Compiler negative control demonstrates stale rendering when the same mutated part identity is reused.
2. Bounded stream publication renders text delta changes.
3. Tool state/input/output transitions render.
4. Approval request/response renders.
5. Same-id data replacement renders.
6. Message metadata replacement/merge renders.
7. A large tool output is copied at most once per ownership ingress, then reference-shared across unrelated later stream publications.
8. Earlier published stream snapshots stay immutable, including the first assistant append (#852).
9. Imperative `addToolOutput` preserves detached published ownership for nested caller values, or a deliberate API contract change is documented and accepted.
10. Callback escape tests cover `onToolCall` input and persistent `onData` data ownership.
11. Ordinary `@ai-sdk/react` tests pass.
12. React package type-check passes.
13. Current upstream overlap is refreshed immediately before delivery.

## Current recommendation

Retain campaign #851 and lead #852.

Treat #91 as a useful research carrier for the React Compiler question, not as the final patch. The highest-value next result is the compiler execution receipt plus the imperative-output ownership RED test. If the compiler test passes, prototype design B/C with explicit ownership gates instead of promoting the blanket shallow replacement.

No automated upstream interaction is authorized or performed.
