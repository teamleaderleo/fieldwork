# Exact RED to GREEN request

Execution carrier only.

Target: `urllib3/urllib3@824d97bb1e36f8ac9d3445d9ca1726f0a48b4b78`.

Run candidate generation 2 from baseline RED. The current candidate must keep real unknown codings opaque while honoring RFC 9110 recipient list parsing by ignoring leading, trailing, and interior empty list elements for otherwise supported chains.

Required matrix: Python 3.12 and 3.14; unknown-before/after-known; supported chains; HTTP empty-list controls; installed-source identity; diff hygiene.

Carrier generation 3 installs the target repository's declared test dependencies plus `trustme` before pytest collection, avoiding harness-only missing-dependency failures.

Generation 1 is superseded before execution because adversarial protocol review found its empty-token policy incompatible with RFC 9110 section 5.6.1.2.

Transfer terminal receipts to #800 / `STATUS.md`, then retire this marker and temporary workflow.
