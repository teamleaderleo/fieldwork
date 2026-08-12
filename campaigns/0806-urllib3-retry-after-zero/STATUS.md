# urllib3 Retry-After zero experiment

Issue: #806

State: `candidate-generation-3 — exact baseline RED proven; generation-7 exact GREEN carrier queued; live-overlap hold`

Target: `urllib3/urllib3@824d97bb1e36f8ac9d3445d9ca1726f0a48b4b78`

Parent exact reproduction: run `31423421919`, Python 3.12 and 3.14 success.

## In simple words

Current urllib3 parses an explicit `Retry-After: 0` as zero, yet its high-level sleep path treats that result like an absent header and can apply exponential backoff. The selected candidate preserves the existing helper hook and return contract, then prevents local backoff only when urllib3's own parser says a present Retry-After value resolves to exactly zero.

The exact pinned source has already produced the intended baseline failure on Python 3.12 and 3.14. The latest carrier failure occurred after the deterministic transformer produced the intended edit; only reviewer-patch byte-equivalence failed. Generation 7 regenerates that reviewer artifact in Git's ordinary exact-source diff window. Candidate behavior is unchanged.

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

## Exact baseline RED and carrier repair

Carrier #808 run `31428627770` executed the baseline discriminator on exact source for Python 3.12 and 3.14. Both lanes reached the intended failure: with positive local backoff available, explicit `Retry-After: 0` selected the backoff path.

Evidence class: `target-executed` RED.

That run then passed patch applicability and reached the deterministic production transformer. The remaining failure was reviewer-patch byte-equivalence: the hand-shaped reviewer hunk used a different context window from Git's generated production diff.

Generation 7 regenerates `candidate.patch` with the ordinary exact-source Git window (`@@ -384,6 +384,8 @@`) and trailing context. The transformer and production algorithm are unchanged.

Current exact carrier: #808 run `31558054435`, queued for Python 3.12 and 3.14 plus the complete Retry unit suite at this checkpoint.

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

## Historical owner check

Public urllib3 PR [955](https://redirect.github.com/urllib3/urllib3/pull/955) introduced Retry-After support with the same semantic split that survives today. At merge commit `29b9ddadc7664a329e4c4978baa53d3025face24`:

- `parse_retry_after()` normalized elapsed/past values to numeric zero;
- `get_retry_after()` used `None` for header absence;
- `sleep_for_retry()` used `if retry_after:`;
- `Retry.sleep()` fell through to exponential backoff when that helper returned `False`.

The pinned current tests explicitly assert `parse_retry_after("0") == 0`. Their Retry-After sleep matrix covers positive delays and zero-duration date cases under the default zero backoff, leaving the absent-header versus explicit-zero distinction untested when positive backoff exists.

This supports a latent selector-defect classification in the original Retry-After path rather than a parse-layer ambiguity.

## Required exact GREEN gate

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
- reviewer patch matches transformed production diff exactly;
- `git diff --check` passes.

## Live overlap hold

Public urllib3 PR [5010](https://redirect.github.com/urllib3/urllib3/pull/5010) remains open and edits `retry.py` / `test_retry.py` for maximum Retry-After handling. Direct inspection of head `7cbea353b2dd10dce020467547442994036aab30` shows that it leaves this zero-delay timing branch available for a small mechanical reconciliation.

The semantic questions are independent; this Fieldwork candidate stays preparation-only while that public branch is live.

## Candidate sanity

Earlier candidate generations passed model timing controls on installed urllib3 2.7.0. Generation 3 retains the same target timing invariant while preserving both direct helper return and hook delegation. Exact pinned-source candidate execution remains the acceptance gate.

Upstream contact authorized: `false`.
