# Exact RED to GREEN request

Execution carrier only.

Target: `urllib3/urllib3@824d97bb1e36f8ac9d3445d9ca1726f0a48b4b78`.

Run the exact baseline failure and one-file candidate acceptance matrix on Python 3.12 and 3.14. Preserve distinct controls for header absence, explicit zero, positive delay, past HTTP-date, and `respect_retry_after_header=False`, then run the complete `test/test_retry.py` suite and source-identity/diff gates.

Public urllib3 PR 5010 remains live overlap. This carrier proves the candidate only; it grants no public packaging authority.

Transfer terminal receipts to #806 / `STATUS.md`, then retire this marker and temporary workflow.
