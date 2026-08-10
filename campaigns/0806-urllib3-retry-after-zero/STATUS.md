# urllib3 Retry-After zero experiment

Issue: #806

State: `candidate-generation-3 — protocol-backed; helper return + delegation preserved; live-overlap hold; exact RED/GREEN pending`

Target: `urllib3/urllib3@824d97bb1e36f8ac9d3445d9ca1726f0a48b4b78`

Parent exact reproduction: run `31423421919`, Python 3.12 and 3.14 success.

## Selected candidate

Keep urllib3's existing `sleep_for_retry()` hook and boolean behavior, then distinguish a valid parsed zero from header absence only after the hook returns `False`:

```python
if self.respect_retry_after_header and response:
    slept = self.sleep_for_retry(response)
    if slept:
        return
    if self.get_retry_after(response) == 0:
        return

self._sleep_backoff()
```

Production fence: `src/urllib3/util/retry.py` only.

This changes one high-level case: a present valid Retry-After value that resolves to zero no longer falls through to exponential backoff.

## Candidate evolution

### Generation 1 — superseded

Changed `sleep_for_retry()` so zero returned `True` without sleeping. This repaired the high-level branch but changed an observable public helper return.

### Generation 2 — superseded

Moved Retry-After parsing directly into `Retry.sleep()`. This preserved the helper's direct return but bypassed `self.sleep_for_retry()`, weakening subclass/override compatibility.

### Generation 3 — current

Retains the original helper call exactly. Positive delays and custom hooks keep their existing first chance to own behavior. Only after a false hook result does the candidate check whether urllib3's parser resolved the header to exactly zero; if so, it returns instead of running local backoff.

## Protocol authority

RFC 9110 section 10.2.3 defines Retry-After `delay-seconds` as a non-negative decimal integer. Zero is a valid explicit delay value.

The same ownership rule applies when urllib3's parser produces zero from:

- literal `Retry-After: 0`;
- a valid HTTP-date in the past;
- a positive delay capped to zero by `retry_after_max=0`.

## Call-site and public-surface boundary

- redirect handling calls `sleep_for_retry()` and ignores the return value;
- status retry handling calls `Retry.sleep()`, which owns the reproduced backoff fallthrough;
- current urllib3 API documentation emphasizes `Retry.sleep()`, while older published reference docs also exposed `sleep_for_retry()`;
- generation 3 preserves both the direct helper's zero return (`False`) and the delegation from `Retry.sleep()` to `self.sleep_for_retry()`.

Status retry detection already treats literal header string `"0"` as present, so the candidate changes delay selection only.

## Required exact gate

Baseline RED:

- `test_fieldwork_retry_after_zero_consumes_header` fails because exact source performs the 2-second backoff.

Candidate GREEN:

- explicit zero causes no sleep through `Retry.sleep()`;
- direct `sleep_for_retry()` zero return remains `False` with no sleep;
- `Retry.sleep()` still invokes the `sleep_for_retry()` hook exactly once;
- header absence still uses the 2-second backoff;
- positive `Retry-After: 1` sleeps exactly one second;
- a valid past HTTP-date causes no backoff;
- a positive delay capped to zero with `retry_after_max=0` causes no backoff;
- `respect_retry_after_header=False` retains local backoff;
- full `test/test_retry.py` remains green;
- installed `retry.py` byte-matches patched exact source;
- `git diff --check` passes.

## Live overlap hold

Public urllib3 PR 5010 remains open and edits `retry.py` / `test_retry.py` for maximum Retry-After handling. Direct inspection of head `7cbea353b2dd10dce020467547442994036aab30` shows that it leaves this timing branch available for a trivial mechanical reconciliation.

The semantic questions are independent; this Fieldwork candidate stays preparation-only while that public branch is live.

## Historical note

Public PR 955 introduced Retry-After support with the same truthiness-driven helper path. Its tests covered positive waits and past dates with no positive exponential backoff, leaving zero indistinguishable from absence under backoff.

## Candidate sanity

Earlier candidate generations passed model timing controls on installed urllib3 2.7.0. Generation 3 retains the same target timing invariant while preserving both direct helper return and hook delegation. Exact pinned-source execution remains the acceptance gate.

Upstream contact authorized: `false`.
