# Upstream issue draft — first Codex issue candidate

> Do not post without explicit public-contact authorization. Repeat the public issue search and refresh source revisions immediately before use.

## Title

Completed unified-exec commands can lose output received before or outside the live broadcast subscriber

## Body

### Problem

Unified exec receives stdout/stderr at the process owner, but the completed command transcript is assembled through a best-effort broadcast subscriber used for live output events.

That subscriber can attach after output has already arrived or fall behind the channel capacity. In either case, the producer received bytes that can be absent from the final completed command item.

Live events being best effort is reasonable. Final command output should not inherit that loss model.

### Reproduction shape

Two deterministic cases expose the boundary:

1. emit output before the streaming completion subscriber is attached, then complete the process;
2. emit enough output to force a live receiver into `Lagged`, then complete the process.

The current behavior can omit producer-received bytes from the completed transcript. The same mechanism applies to invalid UTF-8 bytes because broadcast lag happens before text rendering.

### Proposed invariant

A bounded producer-owned buffer should be the authority for completed command output:

- record bytes before best-effort broadcast;
- continue emitting bounded live deltas to observers;
- on normal close, reconcile the completed transcript from producer-owned state;
- retain the existing head/tail output bound and cancellation grace.

### Implementation evidence

A focused four-file prototype and tests are available in the owned fork: `teamleaderleo/codex#144`.

At its exact source pin:

- 12 focused terminal-retention controls passed;
- the complete `codex-core` library passed against a paired baseline;
- integration targets compiled;
- all four source-base files remain unchanged on the latest public main inspected.

The link is offered as implementation evidence, not as a request to accept the exact API or commit without discussion.

### Question

Is producer-owned bounded retention the intended authority boundary for final unified-exec output, with broadcast remaining best effort only for live observation?

### Limits

This proposal does not attempt to guarantee bytes produced after the existing hard-termination grace boundary, retain unbounded output, solve process-tree cleanup, or introduce a general execution-receipt system.

No public upstream interaction has occurred.