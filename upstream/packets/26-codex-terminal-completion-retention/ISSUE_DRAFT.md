# Upstream issue draft — first Codex issue candidate

> Hold for explicit public-contact authorization. Refresh the public source and overlap search immediately before posting.

## Title

Unified exec can drop command output when the live listener starts late or falls behind

## Body

I started looking at this while trying to understand why some tool calls time out or otherwise finish without a useful result. The timeout itself can come from several parts of the process lifecycle, but I found a narrower problem that makes those failures much harder to understand: Codex can receive command output and still leave some of it out of the completed command record.

### What seems to be happening

Unified exec receives stdout and stderr at the process owner. Live output is then sent through a best-effort broadcast channel so the UI and other listeners can show progress.

That live listener can:

- attach after the command has already printed something;
- fall behind a noisy command and receive `Lagged`;
- close while the process owner still has valid output.

The surprising part is that the listener's partial view can become the completed command transcript. That gives a best-effort delivery path authority over the final result.

### Why this matters in ordinary Codex use

A few examples:

- A test command prints the actual failure early, then continues for a while. Codex can finish with a transcript that misses the useful failure line.
- A build or search produces enough output to lag the live listener. The completed item can contain an arbitrary partial view rather than the bounded head/tail view of everything Codex received.
- A command prints progress or an explanation and then times out. The timeout may be real, while the final record loses the output that would explain whether it was compiling, waiting on the network, prompting for input, or stuck during cleanup.
- A command succeeds, but the model sees an incomplete or empty result and decides to retry, change approach, or report that the command produced nothing.

So this appears related to timeout investigations mainly through **lost context around the terminal event**. It also affects commands that complete normally.

### A small reproduction

Two deterministic cases expose the boundary:

1. Send output before the streaming listener is attached, then finish the command.
2. Send enough output to lag the listener, then finish the command.

In both cases, the process owner received the bytes, while the completed item can omit them. Invalid UTF-8 has the same basic risk because the loss happens before text rendering.

### Possible direction

The process owner could keep one bounded completion transcript before sending live updates:

1. receive stdout or stderr;
2. add it to the bounded completion buffer;
3. send the live update on a best-effort basis;
4. build the completed command item from the producer-owned buffer.

Live streaming would stay best effort. The final command output would come from the component that actually received the bytes.

### Implementation and tests

I put together a focused four-file implementation here: `teamleaderleo/codex#144`.

At that exact source revision:

- 12 focused terminal-output controls passed;
- the complete source `codex-core` library passed alongside a green paired baseline;
- integration targets compiled;
- formatting and the four-file source fence passed.

The relevant public files were still byte-identical at the latest source refresh, and the current issue/PR search found no active proposal for this specific late-or-lagged-listener case.

The implementation link is mainly there to make the behavior concrete. The ownership boundary is the important part; the exact shape can follow maintainer preference.

### Question

Does producer-owned bounded retention sound like the right source of truth for completed unified-exec output, while the broadcast channel stays focused on live progress?

### Scope and follow-ups

This issue focuses on output Codex has already received by the normal completion or existing cancellation-grace boundary.

Closely related follow-ups include the causes of long-running or timed-out tool calls, output that arrives after forced termination, process-tree cleanup, and remote execution settlement. Those have different owners and can be discussed separately without making this first issue carry the entire execution lifecycle.

No public upstream interaction has occurred.
