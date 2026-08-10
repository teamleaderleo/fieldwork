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

Run `31426131410` already established baseline RED on both Python lanes, then stopped before candidate execution because the reviewer patch artifact had a bad hunk header (`corrupt patch ... candidate.patch:20`). Classification: carrier packaging only.

Carrier generation 5 now requires:

- `git apply --check` accepts the repaired reviewer patch;
- deterministic `apply-candidate.py` transforms the exact source;
- the generated production-only `response.py` diff matches `candidate.patch` byte-for-byte after removing Git `index` metadata;
- candidate tests run only after that identity gate.

Generation 1 remains superseded for protocol semantics. Production generation 2 is unchanged; this rerun repairs evidence packaging only.

Transfer terminal receipts to #800 / `STATUS.md`, then retire this marker and temporary workflow.
