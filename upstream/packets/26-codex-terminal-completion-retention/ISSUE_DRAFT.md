# Upstream issue draft — first Codex issue candidate

> Do not post without explicit public-contact authorization. Repeat the public issue and PR search immediately before use.

## Title

Completed unified-exec commands can lose output received before or outside the live output subscriber

## Body

### Problem

Unified exec receives stdout and stderr at the process owner, while live output is delivered through a best-effort broadcast subscriber. The completed command transcript can be assembled from that subscriber’s partial view.

A subscriber can attach after output has already arrived or fall behind the broadcast channel and receive `Lagged`. In both cases, the process owner received bytes that can be absent from the final completed command item.

Best-effort delivery is reasonable for live progress. Final command output should not inherit the same loss model.

### Deterministic reproduction shape

Two cases expose the boundary:

1. emit output before the streaming subscriber is attached, then complete the process;
2. emit enough output to lag the subscriber, then complete the process.

The completed item can omit producer-received bytes. The same loss can affect invalid UTF-8 because the bytes are lost at the delivery boundary before text rendering.

### Proposed invariant

A bounded producer-owned transcript should be authoritative for completed command output:

- retain accepted stdout/stderr bytes before best-effort broadcast;
- continue emitting bounded live deltas to observers;
- on normal close, build the completed transcript from producer-owned state;
- preserve the existing head/tail output bound and cancellation grace.

### Implementation evidence

A focused four-file implementation and tests are available in the owned fork: `teamleaderleo/codex#144`.

At the exact implementation pin:

- 12 focused terminal-retention controls passed;
- the complete source `codex-core` library passed, alongside a green paired baseline;
- integration targets compiled;
- formatting and the exact four-file fence passed.

Public source was refreshed through `78f00743f92cf4fb875ddadcd30293c5201b48ac`, 95 commits after the implementation base. All four source-base files remained byte-identical, and refreshed issue/PR searches found no active proposal for this specific subscriber-timing loss.

The implementation link is evidence for the failure and one bounded repair, not a request to accept the exact commit without discussion.

### Question

Is producer-owned bounded retention the intended authority boundary for final unified-exec output, with broadcast remaining best effort only for live observation?

### Limits

This proposal does not attempt to:

- guarantee bytes produced after the existing hard-termination grace boundary;
- retain unbounded output;
- solve process-tree cleanup or remote reattachment;
- change conversation-history persistence;
- introduce a general execution-receipt framework.

No public upstream interaction has occurred.