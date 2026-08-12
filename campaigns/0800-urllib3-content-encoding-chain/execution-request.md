# Exact RED to GREEN request

Execution carrier only.

Target: `urllib3/urllib3@824d97bb1e36f8ac9d3445d9ca1726f0a48b4b78`.

Run production candidate generation 2 from exact baseline RED on Python 3.12 and 3.14.

Required matrix:

- unknown-before/after-known stays opaque;
- supported chains decode;
- leading, trailing, and interior empty HTTP list elements are ignored;
- six real codings still hit `MultiDecoder.max_decode_links`;
- installed candidate `response.py` byte-matches patched exact source;
- existing supported-chain tests and diff hygiene pass.

Run `31426131410` established baseline RED on both Python lanes, then stopped before candidate execution because the reviewer patch artifact had a bad hunk header. Run `31428442539` again reached baseline RED, then stopped at patch applicability.

Carrier generation 8 refreshes this execution head against the current research base after the evidence artifacts advanced. The required research generation is `research/0800-urllib3-content-encoding-chain@0f675ab1fe4789061b50869adf2ddb555231437c`.

The selected production algorithm remains generation 2. The current reviewer patch uses the ordinary Git diff window for the exact source edit:

- hunk starts at line 614 with three lines of leading context;
- trailing `_decode()` context is retained;
- `git apply --verbose --check` must accept the reviewer patch on a byte-clean exact checkout;
- deterministic `apply-candidate.py` must produce a production diff matching the reviewer patch byte-for-byte after Git `index` metadata is removed.

The workflow also records target status and any `response.py` diff before patch materialization, so source mutation and patch-format failure stay distinguishable.

The urllib3 candidate logic is unchanged. Generation 1 remains superseded for protocol semantics.

Transfer terminal receipts to #800 / `STATUS.md`, then retire this marker and temporary workflow.
