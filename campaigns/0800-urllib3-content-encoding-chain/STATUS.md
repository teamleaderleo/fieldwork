# urllib3 mixed Content-Encoding chain experiment

Issue: #800

State: `candidate-prepared — exact RED/GREEN pending`

Target: `urllib3/urllib3@824d97bb1e36f8ac9d3445d9ca1726f0a48b4b78`

Parent exact reproduction: run `31423421919`, Python 3.12 and 3.14 green on the preserved scout discriminator.

## Selected candidate

Only create `MultiDecoder` when every declared coding token is supported. Unknown or empty tokens keep the response chain opaque, matching lone-unknown behavior.

Production fence: `src/urllib3/response.py` only.

Prepared artifacts:

- `candidate.patch`
- `add-regressions.py`

## Required exact gate

Baseline RED:

- `test_fieldwork_unknown_content_encoding_chain_stays_opaque` must fail on exact public source;
- failure covers lone unknown, unknown after known, unknown before known, and trailing empty coding.

Candidate GREEN:

- the same unknown-chain test passes;
- `test_fieldwork_supported_content_encoding_chains_still_decode` passes;
- existing `test_multi_decoding_deflate_deflate`, `test_multi_decoding_deflate_gzip`, and `test_multi_decoding_gzip_gzip` pass;
- installed candidate `response.py` byte-matches the patched target source;
- `git diff --check` passes.

## Boundary

This experiment preserves whole-chain opacity when any coding is unsupported. It does not introduce a new DecodeError policy and does not change `_get_decoder()` fallback behavior for already-authorized callers.

Upstream contact authorized: `false`.
