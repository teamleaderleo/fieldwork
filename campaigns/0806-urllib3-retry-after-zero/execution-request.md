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

Production candidate generations 1 and 2 are superseded. Generation 1 changed the helper's direct zero return; generation 2 bypassed the helper delegation. Generation 3 keeps the existing hook and adds only an exact-zero stop after a false hook result.

Carrier generation 6 additionally requires `git apply --check` on the reviewer patch, deterministic `apply-candidate.py`, and byte-for-byte production-diff equivalence before candidate tests run. This preempts the patch-hunk packaging failure already observed in the sibling urllib3 and Serde carriers.

Public urllib3 PR 5010 remains live overlap. This carrier proves the candidate only; it grants no public packaging authority.

Transfer terminal receipts to #806 / `STATUS.md`, then retire this marker and temporary workflow.
