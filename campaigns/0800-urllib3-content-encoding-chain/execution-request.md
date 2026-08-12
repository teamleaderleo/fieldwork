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

Run `31426131410` established baseline RED on both Python lanes, then stopped before candidate execution because the reviewer patch artifact had a bad hunk header (`corrupt patch ... candidate.patch:20`). Classification: carrier packaging only.

Run `31428442539` again reached baseline RED on both lanes, then stopped at `git apply --check` with `patch does not apply` even though the reviewer patch context matches the pinned source when inspected directly.

Carrier generation 6 adds one diagnostic gate before patch application:

- print target working-tree status;
- print any pre-existing `response.py` diff;
- require `response.py` to remain byte-clean relative to the exact checkout before the reviewer patch gate;
- run `git apply --verbose --check` so any remaining applicability failure is attributable to the patch artifact rather than a mutated target source.

The urllib3 candidate logic is unchanged. Generation 1 remains superseded for protocol semantics. Generation 6 is evidence-carrier diagnosis only.

Transfer terminal receipts to #800 / `STATUS.md`, then retire this marker and temporary workflow.
