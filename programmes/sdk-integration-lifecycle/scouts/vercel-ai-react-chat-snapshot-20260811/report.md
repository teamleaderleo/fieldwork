# Vercel AI SDK React chat snapshot scout

Lane: #841  
Programme: #13  
Target hub: #2  
Worker: `chatgpt:gpt-5.6-sol`  
Pinned target revision: `7d40fafc394a2c9033f931eb85c895e3817f4b58`  
Claim scope: mechanism and interface  
Evidence: `source-read + model-executed`; upstream factory reproduction recorded separately  
Upstream contact authorized: `false`

## In simple words

I am testing whether React chat can publish each streaming update with fresh identities at the boundaries the stream actually mutates, while keeping large tool outputs shared until the stream replaces them.

The performance failure itself is already well established upstream: `ReactChatState.replaceMessage` deep-clones the full accumulated assistant message on every publication, and the current upstream reproduction reports 40x cumulative payload-copy amplification for a 40-tool turn. Fieldwork can add more value by protecting the correctness reason that deep cloning was introduced in the first place: React Compiler must still observe tool, text, data, approval, and metadata updates.

Current source supports a bounded candidate:

```text
stream chunk
   ↓
processUIMessageStream mutates state.message / top-level part fields
   ↓ write()
AbstractChat calls ReactChatState.replaceMessage
   ↓
snapshot for React publication

candidate publication fence
message                 -> new object
├── metadata            -> new root object
└── parts               -> new array
    └── each part       -> new object
        └── payloads    -> shared until their top-level part field is replaced
```

A local model probe preserves every sampled current mutation across that fence and deliberately fails when a nested payload is mutated in place. That failure defines the candidate's boundary. The remaining promotion gate is a React Compiler-enabled integration regression; source reading and a model do not substitute for that execution.

## Source pin and code map

Target: https://github.com/vercel/ai  
Pin: https://github.com/vercel/ai/commit/7d40fafc394a2c9033f931eb85c895e3817f4b58

Primary paths:

- `packages/react/src/chat.react.ts`: React state owner. `replaceMessage` calls `snapshot(message)` and `snapshot` is `structuredClone`.
- `packages/ai/src/ui/chat.ts`: streaming lifecycle owner. `makeRequest` creates the mutable streaming state, then each `write()` publishes that state through `replaceMessage` or `pushMessage`.
- `packages/ai/src/ui/process-ui-message-stream.ts`: mutates the streaming message and parts as chunks arrive.
- `packages/ai/src/util/merge-objects.ts`: produces fresh objects for metadata merges.

Current execution path:

```text
provider/UI chunks
   ↓
processUIMessageStream
   ↓ mutates response.state.message
write()
   ↓
AbstractChat
   ↓
ReactChatState.replaceMessage
   ↓
structuredClone(response.state.message)
   ↓
React subscriber callback
```

## Why the deep clone exists

The original React Compiler report is https://github.com/vercel/ai/issues/6466. Streaming logic mutates parts in place, so recreating only the outer messages array could leave compiler-memoized consumers blind to the changed nested object.

The repair landed in https://github.com/vercel/ai/pull/6762. It chose `structuredClone` because it was the simplest safe publication snapshot. The pull request explicitly named a custom clone as future work if performance became significant. Verification was a React Compiler-enabled demo; the pull request added no automated regression for the compiler behavior.

That history changes the question from “can we make cloning cheaper?” to:

> What is the smallest identity fence that preserves every current in-place mutation React must observe?

## What is already proven upstream

Current public issue: https://github.com/vercel/ai/issues/18624  
Current reproduction: https://github.com/vercel/ai/pull/18625

The upstream factory reproduced the deep-copy amplification through the public React `Chat` implementation on the AI SDK 7 line. Its retained result uses 40 tool outputs of 65,536 bytes each: the final assistant message contains 2,621,440 tool-output bytes, while 79 snapshots cumulatively deep-clone 104,857,600 tool-output bytes, or 40x the final payload size. A corresponding AI SDK 6 reproduction also exists.

Fieldwork therefore does not need another bug reproduction. The useful gap is candidate correctness under the compiler constraint.

## Current mutation contract sampled at the pin

The sampled streaming path changes the following identities or fields:

| Boundary | Current behavior | Candidate requirement |
| --- | --- | --- |
| message id | assigns `state.message.id` | new message object per publication |
| message metadata | assigns a fresh deep-merge result | new message object; metadata root can be copied again for publication |
| parts collection | pushes new part objects | new `parts` array per publication |
| text/reasoning | mutates `text`, `state`, provider metadata fields on existing part | new part object per publication |
| static/dynamic tool | mutates top-level `state`, `input`, `output`, error, title, metadata and provider fields | new part object per publication |
| approval | changes tool state and assigns a new approval object | new part object per publication |
| data part | assigns `existingUIPart.data = dataChunk.data` | new part object per publication |

I found no sampled path here that mutates *inside* an existing tool output, input, data payload, provider metadata payload, or approval object and then expects that same nested object identity to represent two published versions. The model probe treats any future nested in-place mutation as a reopening trigger.

## Competing candidates

### A. Outer message and parts-array copy only

Rejected by the negative control. Existing part objects remain shared, so later top-level mutations rewrite the previously published snapshot.

### B. Deep clone every publication

Correct under the widest mutation model, but it retains the demonstrated repeated copy cost of accumulated tool outputs.

### C. Bounded publication snapshot

Current leading candidate:

```ts
function snapshotMessage(message) {
  return {
    ...message,
    metadata:
      message.metadata != null && typeof message.metadata === 'object'
        ? { ...message.metadata }
        : message.metadata,
    parts: message.parts.map(part => ({ ...part })),
  };
}
```

This gives a fresh identity to every object the sampled stream mutates directly while retaining nested payload references. It reduces publication work from traversing payload bytes to copying the message shell plus part shells.

Boundary: if the stream starts mutating nested payload objects in place, this candidate becomes insufficient. The retained probe demonstrates that failure explicitly.

### D. Publication throttling alone

Frequency controls can reduce how often publication occurs. They leave the cost of each deep clone proportional to the accumulated payload. Treat this as complementary work.

## Model-executed probe

Retained files:

- `probe.mjs`
- `probe-results.json`

Command:

```sh
node probe.mjs
```

Environment used for the retained run:

```text
Node v22.16.0
linux/x64
```

Correctness result:

- `structuredClone`: prior snapshot values stayed stable.
- outer-only negative control: text, tool state/output/approval, and data changed retroactively because old and new snapshots shared part objects.
- bounded snapshot: prior snapshot values stayed stable for every mutation modeled from the sampled source path; message, parts array, every part shell, and metadata root received new identities.
- deliberate nested mutation: changing `output.rows[0]` in place changed the prior bounded snapshot too. This is expected and records the repair boundary.

The synthetic size-scaling loop ran 30 publications over 10, 25, 50, and 100 tool parts, each with 100 unique row objects in its output. Median of five rounds:

| tool parts | deep clone | bounded copy | ratio |
| ---: | ---: | ---: | ---: |
| 10 | 34.534 ms | 0.039 ms | 880.6x |
| 25 | 64.609 ms | 0.069 ms | 930.5x |
| 50 | 67.310 ms | 0.129 ms | 521.6x |
| 100 | 131.087 ms | 0.227 ms | 577.3x |

These timings are mechanism evidence from a synthetic Node model. They show the expected difference between traversing unique nested payloads and copying only shells; they are not browser, React, or product performance measurements.

## Missing proof: React Compiler

This is the consequential remaining gate.

A useful target-native or owned-testbed regression should compile the consuming React component with React Compiler enabled, stream several mutation classes through the public `Chat`/`useChat` path, and assert the rendered UI advances after each change:

1. text delta on an existing text part;
2. tool `input-available` → `output-available`;
3. approval request → approval response;
4. same-id data part replacement;
5. nested metadata merge;
6. a large tool output retained across a later unrelated chunk.

The test should include an outer-only-copy negative control that reproduces at least one stale render. For the bounded candidate, it should also assert that the large nested output reference remains shared across publications while the containing part gets a fresh identity.

If a repository-native compiler test is awkward, a small owned Next.js testbed with React Compiler enabled is justified because the compiler behavior is an application integration property. The trial should stay synthetic and local.

## Recommendation

**Retain this finding and advance only the compiler-enabled characterization/candidate test.** The upstream project already has the performance reproduction and an active factory workflow, so duplicating its issue or reproduction adds review cost.

If the bounded identity fence passes a real compiler-enabled render test, prepare a narrow candidate in the owned `teamleaderleo/ai` fork and run the React package's target-native gates. Before implementation, recheck current upstream activity so Fieldwork does not race an already-landed repair.

If the compiler test requires deeper cloning of a specific nested field, record that exact field and copy only the path needed to preserve the compiler-observed identity transition. Avoid restoring recursive payload cloning by default.

## Negative results and dead ends

- xAI image-generation self-managed-history was sampled first and dropped: Fieldwork scout #783 already retained it as known maintainer prior art.
- The existing upstream factory has already reproduced the React clone amplification on current major lines, so a second Fieldwork reproduction is duplicate evidence.
- Outer-only copying fails the local negative control and should not be promoted.
- Source-level identity reasoning alone cannot close the React Compiler question.

## Adjacent lead worth watching

https://github.com/vercel/ai/issues/18457 reports a separate `resumeStream()` lifecycle failure: a persisted previous assistant message can seed resumed streaming state, then the replay `start` chunk changes the message id and the replace/append check can append a copy of the old answer. Current source at this pin still contains the relevant seed, id reassignment, and replace/append mechanics. Upstream factory work is already active and has reproduction coverage across major lines, so Fieldwork should enter only with a distinct design, compatibility, or regression question.

## Handoff

Strongest supported finding: the current React publication boundary deep-clones substantially more state than the sampled streaming mutation contract requires. A bounded message/parts/part/metadata-root snapshot survives the sampled mutations in a local executable model and exposes a clear invalidation boundary for nested in-place payload mutation.

Strongest unresolved question: does that bounded snapshot preserve every render transition when the consumer is compiled with React Compiler?

Next transition: compiler-enabled characterization; then decide whether an owned-fork candidate is worth target execution.

Automated upstream contact remained prohibited and no upstream mutation was attempted.
