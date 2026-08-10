# urllib3 Retry-After zero experiment

Issue: #806

State: `candidate-prepared — live-overlap hold; exact RED/GREEN pending`

Target: `urllib3/urllib3@824d97bb1e36f8ac9d3445d9ca1726f0a48b4b78`

Parent exact reproduction: run `31423421919`, Python 3.12 and 3.14 success.

## Selected candidate

Preserve the existing `None` versus numeric-zero distinction from `get_retry_after()` through `sleep_for_retry()`:

- absent header returns `False` and permits exponential backoff;
- valid zero delay returns `True` without calling `time.sleep`;
- positive delay sleeps that exact amount and returns `True`.

Production fence: `src/urllib3/util/retry.py` only.

Prepared artifacts:

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
- `respect_retry_after_header=False` retains backoff behavior;
- full `test/test_retry.py` remains green;
- installed `retry.py` byte-matches patched exact source;
- `git diff --check` passes.

## Live overlap hold

Public urllib3 PR 5010 remains open and edits `src/urllib3/util/retry.py` and `test/test_retry.py` for maximum Retry-After handling. Its semantic change is independent, but its file overlap means this Fieldwork candidate is preparation-only until that public branch moves, lands, or closes.

## Historical note

Public PR 955 introduced Retry-After support with the same truthiness check. Its tests covered positive waits and past dates without a positive exponential backoff, leaving explicit/past zero indistinguishable from absence under backoff.

Upstream contact authorized: `false`.
