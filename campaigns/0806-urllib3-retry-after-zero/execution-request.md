# Exact RED to GREEN request

Execution carrier only.

Target: `urllib3/urllib3@824d97bb1e36f8ac9d3445d9ca1726f0a48b4b78`.

Run production candidate generation 3 from exact baseline RED on Python 3.12 and 3.14.

Required controls:

- absent Retry-After uses the 2-second backoff;
- explicit zero causes no sleep through `Retry.sleep()`;
- direct `sleep_for_retry()` with zero still returns `False` and does not sleep;
- `Retry.sleep()` still invokes the `sleep_for_retry()` hook exactly once;
- positive delay sleeps exactly that delay;
- past HTTP-date consumes the header path with no backoff;
- positive delay capped to zero with `retry_after_max=0` consumes the header path with no backoff;
- `respect_retry_after_header=False` retains local backoff;
- complete `test/test_retry.py`, installed-source identity, and diff hygiene pass.

Production candidate generations 1 and 2 are superseded. Generation 3 keeps the existing helper hook and adds only an exact-zero stop after a false hook result.

Carrier generation 7 repairs reviewer-patch representation only. Run `31428627770` already proved exact baseline RED on both Python lanes and then showed that the deterministic transformer produced the intended production edit; the remaining failure was byte-equivalence against a hand-shaped reviewer hunk. The regenerated patch now uses the ordinary Git diff window (`@@ -384,6 +384,8 @@`) and retains trailing context.

Public urllib3 PR 5010 remains live mechanical overlap. This carrier proves the candidate only and grants no public packaging authority.

Transfer terminal receipts to #806 / `STATUS.md`, then retire this marker and temporary workflow.
