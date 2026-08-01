# Upstream pull-request draft — fix: share cancellation request receipts without publishing terminal run state

Draft status: `not ready — selected TypeScript agent-stream repair and renewed execution required`  
Proposed head: `owned fork / fix/shared-cancellation-request-receipt`  
Proposed base: `upstash/box main at a renewed exact head`  
Public interaction authorized: `no`

---

## Summary

- Preserve existing `cancel()` return contracts while adding an explicit immutable cancellation-request receipt.
- Share one cancellation request and result within each in-memory `Run` object.
- Keep remote run status authoritative.
- Distinguish caller-requested agent-stream shutdown from timeout while preserving iterator rejection.

## Problem

The current SDK treats a cancellation request attempt as confirmed terminal cancellation. Request errors are suppressed, yet local status becomes `cancelled`. Multiple callers can send duplicate requests.

In the TypeScript agent stream, cancellation and timeout also abort the same controller. The iterator maps every resulting `AbortError` to terminal `cancelled` and `Stream timed out`, even when the caller requested cancellation.

The governing rule is: local request delivery and observer shutdown cannot prove a remote terminal run result.

## Change

### TypeScript

- Add `RunCancellationReceipt`.
- Add `requestCancel(): Promise<RunCancellationReceipt>`.
- Keep `cancel(): Promise<void>` and delegate to the shared operation.
- Store one shared Promise per `Run`.
- Return frozen request receipts with outcome `unknown`.
- Omit raw provider error detail.
- Record the first owner of each attached agent-stream controller in a private weak map.
- Route timeout and cancellation-request aborts through one first-owner helper.
- On cancellation-request abort, keep iterator rejection with cancellation-specific prose and let cleanup publish partial output plus `detached`.
- Preserve the existing timeout branch separately.
- Keep single-flight claims scoped to one in-memory `Run`.
- Keep local observer-shutdown claims scoped to agent streams unless command/code streams deliberately gain equivalent controllers and tests.

### Python

- Add frozen `RunCancellationReceipt`.
- Add `request_cancel()`.
- Keep async/sync `cancel() -> None`.
- Use a shielded Task in async Python.
- Generate a lock-protected Future coordinator for sync Python.
- Preserve async source-of-truth and parity.

## Receipt vocabulary

The retained candidate uses `requestState: "accepted"`. Before submission, confirm what a successful cancellation endpoint response establishes. If it only acknowledges receipt or transport completion, use a narrower value such as `acknowledged` or `sent`. Remote outcome remains `unknown` in every case until authoritative run data arrives.

## Tests

Historical exact-source candidate passed:

- focused TypeScript: 21/21;
- complete TypeScript package: 385/385;
- TypeScript build and Prettier;
- focused Python: 7/7;
- complete Python: 185 passed, 12 deselected;
- deterministic sync generation;
- JS/Python parity;
- Ruff and MyPy.

Before submission, renew on the proposed head with:

- real agent-stream pending-read cancellation while the cancellation POST remains pending;
- cancellation-specific iterator rejection, partial output, and `detached` status;
- timeout-only behavior;
- cancellation-first and timeout-first races;
- cancellation after receipt settlement with a fresh attached controller;
- two wrappers with the same run ID;
- later authoritative completion/cancellation updates;
- agent versus command/code stream boundary;
- catch-based CLI cancellation compatibility;
- complete target package and declared matrix gates.

## Compatibility

- public API: additive receipt methods;
- existing behavior retained: `cancel()` return values, endpoint, and cancellation-triggered iterator rejection;
- behavior corrected: cancellation-request rejection no longer reports timeout or asserts remote terminal state;
- status: local agent-stream shutdown becomes `detached` until authoritative data arrives;
- stream scope: command/code local observer shutdown is unchanged unless explicitly included;
- platform notes: historical evidence covers Ubuntu, Node 22, Python 3.12; package currently declares Node `>=18`;
- performance: one coordinator object per run plus one weak controller ownership entry while live;
- migration: none;
- rollback: remove additive API/coordinator and abort-owner helper.

## Alternatives considered

- Changing `cancel()` to return the receipt directly risks static source compatibility.
- Silently ending the iterator can make catch-based CLI consumers publish ordinary completion.
- Using only `AbortSignal.reason` needs cross-runtime body-stream proof.
- Separate controller families plus `AbortSignal.any()` add a wider signal-composition surface.
- Adding `cancelling` plus mandatory polling introduces a wider network lifecycle.
- A box/run-ID registry introduces cross-object lifetime and retry policy.
- Automatic retry can duplicate an operation whose remote delivery is uncertain.

## Limits

- Single-flight scope is one in-memory `Run`.
- Local controller shutdown is currently an agent-stream capability.
- Hosted endpoint behavior, provider idempotency, billing, and actual remote termination remain untested.
- Request-state vocabulary and command/code stream parity remain maintainers' choices.

## Related work

- Existing run/stream status model: `upstash/box#68`.
- Existing cancellation integration path: `upstash/box#51`.
- Open CLI Ctrl+C consumer: `upstash/box#82`.

---

## Submission checklist

- [ ] Create an owned fork and clean branch from current `main`.
- [ ] Materialize the first-owner weak-map repair.
- [ ] Settle receipt request-state vocabulary.
- [ ] Decide and document agent-only versus all-stream local shutdown scope.
- [ ] Integrate tests under target-native names; remove Fieldwork-only files.
- [ ] Add any required changeset.
- [ ] Run current focused and ordinary gates.
- [ ] Review complete exact diff.
- [ ] Repeat duplicate search.
- [ ] Check contribution and AI disclosure policy.
- [ ] Obtain exact user authorization to open the pull request.
