# Upstream pull-request draft — fix: share cancellation request receipts without publishing terminal run state

Draft status: `not ready — TypeScript stream-abort repair and renewed execution required`  
Proposed head: `owned fork / fix/shared-cancellation-request-receipt`  
Proposed base: `upstash/box main at a renewed exact head`  
Public interaction authorized: `no`

---

## Summary

- Preserve existing `cancel()` return contracts while adding an explicit immutable cancellation-request receipt.
- Share one cancellation request and result within each in-memory `Run` object.
- Keep remote run status authoritative and classify local stream shutdown separately from timeout.

## Problem

The current SDK treats a cancellation request attempt as confirmed terminal cancellation. Request errors are suppressed, yet local status becomes `cancelled`. Multiple callers can send duplicate requests. In TypeScript, observer shutdown also shares the timeout abort path, which can publish the same terminal state through the stream iterator.

The governing rule is: local request delivery and observer shutdown cannot prove a remote terminal run result.

## Change

### TypeScript

- Add `RunCancellationReceipt`.
- Add `requestCancel(): Promise<RunCancellationReceipt>`.
- Keep `cancel(): Promise<void>` and delegate to the shared operation.
- Store one shared Promise per `Run`.
- Return frozen accepted/failed receipts with outcome `unknown`.
- Omit raw provider error detail.
- Distinguish cancellation-request observer shutdown from timeout in the real stream iterator.
- Keep single-flight claims scoped to one in-memory `Run`.

### Python

- Add frozen `RunCancellationReceipt`.
- Add `request_cancel()`.
- Keep async/sync `cancel() -> None`.
- Use a shielded Task in async Python.
- Generate a lock-protected Future coordinator for sync Python.
- Preserve async source-of-truth and parity.

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

- real agent-stream pending-read cancellation before and after receipt settlement;
- timeout classification;
- two wrappers with the same run ID;
- complete target package and declared matrix gates.

## Compatibility

- public API: additive receipt methods;
- existing behavior retained: `cancel()` return values and cancellation endpoint;
- behavior corrected: local request/observer events no longer assert remote terminal status;
- platform notes: historical evidence covers Ubuntu, Node 22, Python 3.12;
- performance: one coordinator object per run;
- migration: none;
- rollback: remove additive API/coordinator and restore old methods.

## Alternatives considered

- Changing `cancel()` to return the receipt directly risks static source compatibility.
- Adding `cancelling` plus mandatory polling introduces a wider network lifecycle.
- A box/run-ID registry introduces cross-object lifetime and retry policy.
- Automatic retry can duplicate an operation whose remote delivery is uncertain.

## Limits

- Single-flight scope is one in-memory `Run`.
- Hosted endpoint behavior, provider idempotency, billing, and actual remote termination remain untested.
- Public naming and retry policy remain maintainers' choice.

## Related work

- Existing run/stream status model: `upstash/box#68`.
- Existing cancellation integration path: `upstash/box#51`.
- Open CLI Ctrl+C consumer: `upstash/box#82`.

---

## Submission checklist

- [ ] Create an owned fork and clean branch from current `main`.
- [ ] Integrate tests under target-native names; remove Fieldwork-only files.
- [ ] Add any required changeset.
- [ ] Run current focused and ordinary gates.
- [ ] Review complete exact diff.
- [ ] Repeat duplicate search.
- [ ] Check contribution and AI disclosure policy.
- [ ] Obtain exact user authorization to open the pull request.
