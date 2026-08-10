# Exact RED to GREEN request

Execution carrier only.

Target: `urllib3/urllib3@824d97bb1e36f8ac9d3445d9ca1726f0a48b4b78`.

Run candidate generation 2 from exact baseline RED on Python 3.12 and 3.14.

Required controls:

- absent Retry-After uses the 2-second backoff;
- explicit zero causes no sleep through `Retry.sleep()`;
- direct `sleep_for_retry()` with zero still returns `False` and does not sleep;
- positive delay sleeps exactly that delay;
- past HTTP-date consumes the header path with no backoff;
- positive delay capped to zero with `retry_after_max=0` consumes the header path with no backoff;
- `respect_retry_after_header=False` retains local backoff;
- complete `test/test_retry.py`, installed-source identity, and diff hygiene pass.

Production candidate generation 1 is superseded because it changed the public helper's zero return from `False` to `True`. Generation 2 leaves `sleep_for_retry()` unchanged and repairs only `Retry.sleep()`'s absence-versus-zero decision.

Carrier generation 4 installs the target repository's declared test dependencies plus `trustme` before collection and uses stable baseline failure markers.

Public urllib3 PR 5010 remains live overlap. This carrier proves the candidate only; it grants no public packaging authority.

Transfer terminal receipts to #806 / `STATUS.md`, then retire this marker and temporary workflow.
