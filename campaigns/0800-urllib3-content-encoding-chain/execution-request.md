# Exact RED to GREEN request

Execution carrier only.

Target: `urllib3/urllib3@824d97bb1e36f8ac9d3445d9ca1726f0a48b4b78`.

Run candidate generation 2 from baseline RED. The current candidate must keep real unknown codings opaque while honoring RFC 9110 recipient list parsing by ignoring leading, trailing, and interior empty list elements for otherwise supported chains.

Required matrix: Python 3.12 and 3.14; unknown-before/after-known; supported chains; HTTP empty-list controls; six-real-coding `MultiDecoder.max_decode_links` negative control; installed-source identity; diff hygiene.

Carrier generation 4 installs the target repository's declared test dependencies plus `trustme` before pytest collection and explicitly proves the existing five-coding chain-depth cap still applies to real coding elements. Empty elements do not contribute to that count under RFC 9110.

Generation 1 is superseded because its empty-token policy conflicted with RFC 9110 section 5.6.1.2. The current production candidate remains generation 2; later carrier generations only harden evidence.

Transfer terminal receipts to #800 / `STATUS.md`, then retire this marker and temporary workflow.
