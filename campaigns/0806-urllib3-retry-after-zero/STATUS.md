# urllib3 Retry-After zero experiment

Issue: #806

State: `candidate-prepared — protocol-backed; live-overlap hold; exact RED/GREEN pending`

Target: `urllib3/urllib3@824d97bb1e36f8ac9d3445d9ca1726f0a48b4b78`

Parent exact reproduction: run `31423421919`, Python 3.12 and 3.14 success.

## Selected candidate

Preserve the existing `None` versus numeric-zero distinction from `get_retry_after()` through `sleep_for_retry()`:

- absent header returns `False` and permits exponential backoff;
- valid zero delay returns `True` without calling `time.sleep`;
- positive delay sleeps that exact amount and returns `True`.

Production fence: `src/urllib3/util/retry.py` only.

## Protocol authority

RFC 9110 section 10.2.3 defines Retry-After `delay-seconds` as a non-negative decimal integer. Zero is therefore a valid explicit delay value rather than header absence.

The same ownership rule applies when urllib3's existing parser produces zero from:

- a valid past HTTP-date;
- a positive delay capped to zero by `retry_after_max=0`.

## Call-site boundary

Current source has two relevant uses:

- redirect handling invokes `sleep_for_retry()` and ignores its boolean result, so candidate zero behavior remains immediate and does not alter redirect control flow;
- `Retry.sleep()` consumes the boolean solely to decide whether exponential backoff should run. This is the reproduced owner.

Status retry detection already treats literal header value `"0"` as present, so the candidate changes delay selection only.

## Prepared artifacts

- `candidate.patch`
- `add-regressions.py`

## Required exact gate

Baseline RED:

- `test_fieldwork_retry_after_zero_consumes_header` must fail on exact public source because a 2-second backoff occurs.

Candidate GREEN:

- explicit zero causes no sleep;
- header absence still uses the 2-second backoff;
- positive `Retry-After: 1` sleeps exactly one second;
- a valid past HTTP-date consumes the Retry-After path with no sleep;
- a positive delay capped to zero with `retry_after_max=0` consumes the Retry-After path with no sleep;
- `respect_retry_after_header=False` retains backoff behavior;
- full `test/test_retry.py` remains green;
- installed `retry.py` byte-matches patched exact source;
- `git diff --check` passes.

## Live overlap hold

Public urllib3 PR 5010 remains open and edits `src/urllib3/util/retry.py` and `test/test_retry.py` for maximum Retry-After handling. Direct inspection of its current head `7cbea353b2dd10dce020467547442994036aab30` shows that it leaves `sleep_for_retry()` unchanged, so the semantic changes remain independent and mechanically easy to reconcile.

This Fieldwork candidate stays preparation-only while that public branch is live.

## Historical note

Public PR 955 introduced Retry-After support with the same truthiness check. Its tests covered positive waits and past dates without a positive exponential backoff, leaving explicit/past zero indistinguishable from absence under backoff.

## Candidate sanity

A model-executed monkeypatch on installed urllib3 2.7.0 produced the intended matrix for absent, zero, positive, past-date, and opt-out cases. Exact pinned-source execution remains the promotion gate.

Upstream contact authorized: `false`.
