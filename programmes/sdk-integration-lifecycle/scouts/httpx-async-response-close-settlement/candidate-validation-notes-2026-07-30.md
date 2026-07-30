# HTTPX async response close candidate validation notes

Date: `2026-07-30`

Fieldwork issue: #171

Fieldwork scout PR: #173

Owned fork PR: `teamleaderleo/httpx#1`

Exact executed fork head: `04e2da580eea759e712df1656323ae0dd7d26bff`

Pinned fork base: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`

Upstream contact authorized: `false`

## Candidate form

The fork remains a staged exact-anchor experiment, not a direct production-source branch.

Its candidate transformer:

- requires every pinned source snippet exactly once;
- moves elapsed-time publication after underlying close succeeds;
- adds one AnyIO event per authoritative close attempt;
- separates body-read closure from cleanup completion;
- excludes transient attempt state from pickling;
- applies the same candidate on Python 3.9 and 3.13.

The fork also contains focused response-state, control-flow, pickle, client-context, and default-pool regressions plus a read-only workflow.

## Exact-head execution receipts

Focused workflow run: `30507411692`

Jobs:

- Python 3.9 — passed;
- Python 3.13.14 — passed.

Exact runtime dependencies included:

- HTTPX `0.28.1`;
- HTTPCore `1.0.9`;
- AnyIO `4.12.1`;
- Trio `0.31.0`;
- Trustme `1.2.1`;
- Cryptography `45.0.7`;
- Uvicorn `0.35.0`;
- the remaining repository-declared requirements.

Each focused job passed:

```text
28 candidate close-settlement, control-flow, pickle, and pool tests
24 adjacent response/client tests
Ruff on changed source and focused tests
Mypy on httpx
```

The adjacent selector deselected 134 unrelated cases. This is a focused target result, not by itself the complete repository gate.

Ordinary repository Test Suite run: `30507411721` — passed on the same exact head.

Together, the focused and ordinary runs establish exact-head candidate execution and repository compatibility for the staged transformer branch. They do not turn the transformer into a clean source-ready diff.

## Candidate behavior established

### Completion state

Only successful underlying stream cleanup sets `response.is_closed = True`.

Cancellation, non-cancellation control-flow interruption, and ordinary close errors leave public cleanup completion false and allow a later explicit close attempt.

### Attempt ownership

One caller owns one underlying close attempt. Concurrent callers wait for the same attempt rather than returning early or invoking the stream concurrently.

Ordinary `Exception` failures are shared with callers already waiting. A later call may create a new retry attempt.

Cancellation and other direct `BaseException` control-flow signals remain owned by the interrupted caller. Waiting callers wake and may take retry ownership rather than receiving a duplicated control-flow signal.

### Two-axis response state

Once close starts, body iteration remains prohibited even when cleanup completion is false.

The accepted candidate therefore distinguishes:

- body consumption closed;
- cleanup attempt incomplete and retryable;
- cleanup completed.

This is not a contract that reopens response content after a failed close.

### Elapsed time and serialization

`response.elapsed` becomes available only after underlying close succeeds. It stays unavailable after failed cleanup.

Pickling an in-progress response does not serialize the AnyIO event or attempt state. The restored response is terminally closed with an unattached stream, while the original live response retains its own retry ownership.

### Default-pool control

The local-server integration uses HTTPX's default transport with:

```python
httpx.Limits(max_connections=1, max_keepalive_connections=1)
httpx.Timeout(5.0, pool=0.2)
```

The first streaming response wraps its real bound transport stream with a deterministic blocker.

1. First close enters the blocker.
2. Caller cancellation occurs before delegation to HTTPCore.
3. Public cleanup completion remains false.
4. Retry delegates to the real bound stream and succeeds.
5. A follow-up request succeeds through the one-slot pool.

This proves pool-slot recovery for the tested interruption point with HTTPCore 1.0.9. It does not prove same-socket reuse or every close failure inside HTTPCore.

## Harness history

The path to target execution produced several useful non-product findings:

1. The first workflow checked out GitHub's synthetic merge commit, whose moving base did not match the pinned candidate source.
2. The original unified-diff artifact contained malformed hunk metadata and was retired.
3. The exact-anchor transformer first reached pytest without the repository's declared test dependencies and stopped during collection.
4. The next run passed all behavior and adjacent tests but Ruff found one overlong test signature.

None of those failures disproved the candidate behavior. The exact-head runs above fix the harness and pass every focused and ordinary repository stage.

## Claim-scoped evidence

- released response-state mismatch: retained released-package execution in the scout report;
- candidate response close ownership and state semantics: `target-executed` through run `30507411692`;
- one deterministic default-pool recovery path: `integration-executed` through the same run;
- selected adjacent response/client compatibility: `target-executed`;
- ordinary repository Test Suite on the exact candidate head: passed through run `30507411721`;
- direct source integration: absent;
- same-socket reuse, arbitrary transport behavior, every HTTPCore failure point, sync response close, and client multi-transport shutdown: unproven or owned by adjacent lanes.

## Matrix and adjacent lanes

The durable cross-surface inventory is `correctness-matrix-2026-07-30.md`.

Fieldwork #185 records synchronous response close failure separately.

Fieldwork #177 records client-level shutdown separately. Client shutdown publishes terminal client state before all transport owners settle and requires its own policy.

## Current disposition

Accept the candidate behavior, focused compatibility result, deterministic pool-slot result, and ordinary repository receipt at exact head `04e2da580eea759e712df1656323ae0dd7d26bff`.

Do not treat the transformer branch as a source-ready merge candidate. The next transition is:

1. apply the selected implementation directly to a clean source branch;
2. commit the tests in normal target locations;
3. run the complete repository gate at that exact source head;
4. perform complete-diff and independent technical review;
5. keep upstream contact unauthorized unless separately approved.

No upstream interaction occurred.
