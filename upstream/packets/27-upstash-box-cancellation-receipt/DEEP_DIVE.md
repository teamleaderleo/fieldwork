# Deep dive — Unit 27 cancellation-request receipt

## In simple words

The target currently combines three facts: stopping local observation, sending a remote cancellation request, and publishing terminal run state. Those facts can diverge. A request can fail, a local reader can stop while the remote run continues, and a later server event can report natural completion.

The retained design separates request delivery from remote outcome through an immutable receipt and one shared request per in-memory run object. The Python implementation composes cleanly with its current source. The TypeScript implementation still uses the same abort signal for timeout and cancellation-request observer shutdown, and the stream catch translates both to terminal `cancelled`. That composition needs one bounded repair.

## Governing invariant

> Local cancellation intent and local observer shutdown must never publish a remote terminal run outcome; only authoritative server/event data may do that.

## Current behavior

- entrypoint: TypeScript `Run.cancel()`; Python async/sync `Run.cancel()`
- state owner: each `Run` object owns cached status; TypeScript stream iterators update it through `Run._update`
- caller-visible result: legacy void/`None`; errors from the cancel endpoint are swallowed
- side effects: TypeScript aborts the attached observer, every caller sends a POST, and local status becomes `cancelled`; Python every caller sends a POST and local status becomes `cancelled`
- cleanup owner: stream iterator/fetch body reader in TypeScript; request coroutine/client in Python
- publication boundary: cached `Run.status`
- ordering: local observer abort can happen before remote cancellation request settlement; server events can arrive before or after that request

## Source map

| Area | Exact path and symbol | Responsibility | Relevant tests |
| --- | --- | --- | --- |
| TypeScript run state | [`client.ts@9f7533c`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/sdk/src/client.ts) `Run`, `Run._update` | cached status, run ID, observer controller, cancellation | [`run.test.ts`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/sdk/src/__tests__/run.test.ts) |
| TypeScript agent stream | same file, agent `_stream` iterator | timeout controller, body read, `AbortError` translation, terminal/detached updates | package stream tests plus required new reversing control |
| Python async source | [`_async/client.py@9f7533c`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/python-sdk/upstash_box/_async/client.py) `AsyncRun` | request and cached status | [`tests/_async/test_run.py`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/python-sdk/tests/_async/test_run.py) |
| Python sync generation | [`generate_sync.py@9f7533c`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/python-sdk/scripts/generate_sync.py) | maps async source into sync client | [`tests/_sync/test_sync_client.py`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/python-sdk/tests/_sync/test_sync_client.py) |
| Retained transformation | [`apply_target_repair.py@ccaa28e`](https://github.com/teamleaderleo/fieldwork/blob/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd/programmes/high-leverage-open-source/scouts/upstash-box-cancel-receipts/target-materialization/apply_target_repair.py) | adds receipt API and coordinators | retained controls beside it |
| Follow-up transformation | [`apply_sync_test_repair.py@ccaa28e`](https://github.com/teamleaderleo/fieldwork/blob/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd/programmes/high-leverage-open-source/scouts/upstash-box-cancel-receipts/target-materialization/apply_sync_test_repair.py) | aborts current TS observer on every call and updates sync test/typing | isolated late-observer test |

## Reproduction or characterization

### Setup

- exact upstream revision: `b55d832d6e3ae0156e32d21ea3863e231dfff9cd`
- environment: Ubuntu 24.04, Node 22, Python 3.12 in GitHub Actions
- fixture: repository-native mocked requests; no hosted Box call
- workflows: baseline `30622339900`; selected candidate `30642924979`

### Baseline result

Both SDK families suppress cancellation HTTP failure and publish `cancelled`. Concurrent callers issue independent POSTs. TypeScript also aborts the attached observer before request settlement. A later internal authoritative update can replace the local status.

### Candidate result

The retained patch shares an immutable accepted/failed receipt per in-memory run object, preserves legacy return contracts, isolates Python waiters, avoids replay, and stops direct status assignment in the new cancellation methods. All named package gates passed at the executed base.

The real TypeScript stream path remained outside the focused test. Existing source catches the request-triggered `AbortError`, assigns terminal `cancelled`, and reports `Stream timed out`. The broad status claim therefore remains unproved and is likely false for that path.

## Failure model

1. `box.agent.stream()` creates a `Run` and one `AbortController`.
2. The same controller backs optional timeout and local stream reading.
3. `requestCancel()` or legacy `cancel()` aborts that controller.
4. The iterator catches `AbortError` without an ownership marker.
5. The catch assigns `status: "cancelled"` and throws `BoxError("Stream timed out")`.
6. Local cancellation intent becomes indistinguishable from timeout and remote terminal cancellation.

Steps 1–5 are source-confirmed. Hosted remote outcome after step 3 remains unknown.

## Consequence and claim boundary

### Established

- Baseline false-terminal and duplicate-request behavior exists in local mocked target execution.
- The additive receipt API, immutable values, fixed diagnostics, legacy return compatibility, Python waiter isolation, deterministic generation, and per-object no-replay behavior passed the executed matrix.
- Current relevant source paths are unchanged from the executed base through `9f7533c...`.
- The candidate stores coordination on a `Run` object, so two wrappers with one remote ID coordinate independently.

### Inferred

- A cancellation-request abort through the real TypeScript stream path will enter the same `AbortError` branch as timeout and publish `cancelled`, because the candidate leaves that catch unchanged.
- Using existing `detached` for cancellation-request observer shutdown may fit current semantics: local consumption stopped while remote execution remains possible. This remains a design candidate until target-native controls pass.

### Unknown or unmeasured

- Hosted endpoint acceptance and idempotency
- Actual remote termination or natural completion after local abort
- Billing and production interruption behavior
- Cross-process or multi-wrapper coordination requirements
- Maintainer naming and receipt-lifetime preference

## Selected implementation

Keep the receipt family and repair TypeScript abort ownership at the stream boundary:

- One per-`Run` Promise/Task/Future owns request execution and settlement.
- `accepted` reports successful local request completion; `failed` reports bounded request failure; remote outcome stays `unknown`.
- Legacy `cancel()` delegates and discards the receipt.
- TypeScript records why the observer controller was aborted before calling `abort()`.
- The stream `AbortError` handler treats cancellation-request observer shutdown as a local detach/nonterminal event and preserves timeout behavior separately.
- A later server `completed` or `cancelled` update remains authoritative.
- Claims explicitly say “per in-memory `Run` instance.”

Exact implementation choice between a private abort-reason field and a distinct cancellation observer controller should follow the reversing test. A box/run-keyed registry stays excluded from this unit.

## Compatibility analysis

- public API: additive receipt method and type; legacy `cancel()` signature retained
- source compatibility: callers ignoring `cancel()` result remain unchanged; new method is additive
- binary or wire compatibility: no wire change; same POST endpoint
- persistence or format compatibility: no persisted state
- platform behavior: executed on Node 22 and Python 3.12; target CI supports wider matrices that require rerun
- performance and allocation: one Promise/Task/Future and one receipt per run object
- cancellation, retry, and recovery: automatic replay is absent; failed receipt remains cached; explicit retry policy deferred
- generated output: Python sync must remain generated and deterministic
- migration or rollback: delete the additive types/coordinator and restore prior methods; no data migration

## Adversarial and edge controls

- concurrent callers on one object share one request and object-identical receipt
- one async Python waiter cancellation leaves the shared request alive
- later caller receives settled receipt without replay
- request failure exposes fixed prose and no provider body
- later authoritative completion/cancellation wins
- request cancellation during a pending real TS stream read
- request cancellation after receipt settlement with a newly attached real observer
- timeout abort remains separately classified
- two wrappers with one box/run ID issue two requests, documenting per-object scope
- distinct run objects remain isolated

## Review risks

- `detached` may surprise callers who expect cancellation intent to remain `running`; the stream reversing test and maintainer direction must settle this.
- A private abort-reason flag can become stale; clear it during iterator cleanup and cover immediate reuse/re-attachment.
- Caching failed receipts removes implicit retry; document that policy and defer explicit retry to a separate unit.
- Open upstream PR #82 expects Ctrl+C cancellation UX; preserve legacy `cancel()` return and allow the CLI to continue tracking user intent separately.

## Reversing evidence

Reopen the selected direction if:

- target maintainers define local `cancelled` as intentional client state independent of remote outcome;
- the cancellation endpoint supplies a durable request ID or confirmed terminal response that supports a richer receipt;
- a real stream-path test shows the abort can be separated without source changes;
- current main gains equivalent receipt or abort-ownership work.

## Adjacent work excluded

- provider-side idempotency keys
- cross-process or account-wide cancellation coordination
- automatic polling/reconciliation to terminal state
- explicit retry APIs after failed/unknown request delivery
- CLI Ctrl+C design beyond preserving `Run.cancel()` compatibility
- hosted billing or cost measurements
