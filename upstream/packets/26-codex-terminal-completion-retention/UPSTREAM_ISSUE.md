# Upstream issue draft

## Status

**Draft only. Do not submit without a public-upstream invitation.**

Target: `openai/codex`

Proposed title:

> Unified exec completion can omit stdout/stderr emitted before or beyond broadcast delivery

## Draft body

Unified exec currently uses best-effort broadcast delivery for live process output. A completion watcher can attach after early bytes were emitted, lag behind the broadcast ring, or observe receiver closure. In those cases, the completed process item can omit stdout/stderr bytes that the producer already read.

### Reproduction

A focused regression can start a local process, allow it to emit stdout or stderr, delay the completion subscription, and then await completion. The process finishes, while the completion transcript can miss the early bytes.

The same contract appears when a receiver lags: live streaming can lose chunks by design, yet final completion still needs an authoritative transcript.

### Expected behavior

The completed process item should include the producer-observed terminal output within an explicit bounded-retention policy, independent of subscriber timing.

### Proposed direction

Retain raw stdout/stderr bytes in bounded producer-owned deques before each best-effort broadcast attempt. On normal EOF, return those retained bytes to completion. Reconcile the streamed and retained views by suffix/prefix overlap so completion neither duplicates shared bytes nor discards useful streamed prefix data.

Hard termination should remain prompt when a receiver closes.

### Focused cases

- stdout emitted before completion subscription;
- stderr emitted before completion subscription;
- receiver lag beyond broadcast capacity;
- partial streamed transcript plus authoritative retained suffix;
- invalid UTF-8;
- bounded-retention eviction;
- receiver closure during hard termination.

### Current private evidence

A four-file source patch exists and has passed the exact focused controls on a retained source revision. An earlier revision also passed the full `codex-core` library gate and integration-target compilation. The current-main restack still requires current-head execution and independent review before any upstream submission.

## Prior-art search

Searches of public Codex code, issues, and pull requests for:

- the exact proposed fix title;
- unified-exec terminal output broadcast lag;
- completion transcript retention;
- producer-owned terminal output;

found no direct duplicate issue or pull request. One broad Windows desktop polling issue appeared and concerns a separate path.

Record the exact search date and public main revision again before any submission.

## Submission gate

Submit only after all of these hold:

- invitation from public upstream;
- current source head and base pinned;
- current-head exact tests complete;
- full library and integration evidence preserved;
- independent review complete;
- issue text refreshed against current public behavior;
- no private repository links or internal-only terminology in the public body.

## Private continuation references

- Fieldwork issue #23
- Fieldwork issue #239
- Fieldwork PR #268
- Codex PR #125
- Codex PR #126
- unit source `a020d7bd3e7f6886c3fbc21d75b3110586df08f5`

These private references support continuation and should be removed or replaced with public reproductions before submission.
