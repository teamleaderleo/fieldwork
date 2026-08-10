# urllib3 Retry-After zero experiment

Issue: #806

State: `candidate-generation-2 — protocol-backed; public-helper compatibility preserved; live-overlap hold; exact RED/GREEN pending`

Target: `urllib3/urllib3@824d97bb1e36f8ac9d3445d9ca1726f0a48b4b78`

Parent exact reproduction: run `31423421919`, Python 3.12 and 3.14 success.

## Selected candidate

Repair the delay-selection owner inside `Retry.sleep()` while leaving public `sleep_for_retry()` behavior unchanged.

Current `Retry.sleep()` asks `sleep_for_retry()` for a boolean and falls through to exponential backoff when the helper returns `False`. A valid parsed zero returns `False`, making explicit zero indistinguishable from header absence.

Candidate behavior:

```text
respect Retry-After + response
        ↓
get_retry_after(response)
        ↓
None             -> local backoff may apply
0                -> return immediately
positive seconds -> sleep exactly that delay, then return
```

Direct `sleep_for_retry(response)` remains byte-for-byte unchanged, including its existing `False` return for a zero-second delay.

Production fence: `src/urllib3/util/retry.py` only.

## Why generation 1 was superseded

Generation 1 changed `sleep_for_retry()` so a valid zero returned `True` without sleeping. Internal redirect callers ignore the return value, but `sleep_for_retry()` is a public method and an external caller could reasonably observe its boolean as “a positive sleep occurred.”

Generation 2 moves the distinction into `Retry.sleep()` and adds a direct compatibility control requiring:

```python
Retry().sleep_for_retry(response_with_zero) is False
```

with no `time.sleep` call.

## Protocol authority

RFC 9110 section 10.2.3 defines Retry-After `delay-seconds` as a non-negative decimal integer. Zero is therefore a valid explicit delay value rather than header absence.

The same ownership rule applies when urllib3's existing parser produces zero from:

- a valid past HTTP-date;
- a positive delay capped to zero by `retry_after_max=0`.

## Call-site boundary

Current source has two relevant internal paths:

- redirect handling invokes `sleep_for_retry()` and ignores its boolean result; generation 2 leaves this helper untouched;
- status retry handling invokes `Retry.sleep()`, which owns the reproduced fallthrough to `_sleep_backoff()`.

Status retry detection already treats literal header value `"0"` as present, so the candidate changes delay selection only.

## Prepared artifacts

- `candidate.patch`
- `add-regressions.py`

## Required exact gate

Baseline RED:

- `test_fieldwork_retry_after_zero_consumes_header` must fail on exact public source because a 2-second backoff occurs.

Candidate GREEN:

- explicit zero causes no sleep through `Retry.sleep()`;
- direct `sleep_for_retry()` zero return remains `False` with no sleep;
- header absence still uses the 2-second backoff;
- positive `Retry-After: 1` sleeps exactly one second;
- a valid past HTTP-date consumes the Retry-After path with no sleep;
- a positive delay capped to zero with `retry_after_max=0` consumes the Retry-After path with no sleep;
- `respect_retry_after_header=False` retains backoff behavior;
- full `test/test_retry.py` remains green;
- installed `retry.py` byte-matches patched exact source;
- `git diff --check` passes.

## Live overlap hold

Public urllib3 PR 5010 remains open and edits `src/urllib3/util/retry.py` and `test/test_retry.py` for maximum Retry-After handling. Direct inspection of its current head `7cbea353b2dd10dce020467547442994036aab30` shows that it leaves both `sleep_for_retry()` and the surrounding `Retry.sleep()` branch mechanically easy to reconcile.

This Fieldwork candidate stays preparation-only while that public branch is live.

## Historical note

Public PR 955 introduced Retry-After support with the truthiness-driven helper path. Its tests covered positive waits and past dates without a positive exponential backoff, leaving explicit/past zero indistinguishable from absence under backoff.

## Candidate sanity

Generation 1 passed a model-executed timing matrix on installed urllib3 2.7.0. Generation 2 preserves the same high-level timing invariant while narrowing public API impact; exact pinned-source execution remains the promotion gate.

Upstream contact authorized: `false`.
