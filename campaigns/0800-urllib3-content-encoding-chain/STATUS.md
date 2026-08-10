# urllib3 mixed Content-Encoding chain experiment

Issue: #800

State: `candidate-generation-2 — protocol-list control added; exact RED/GREEN pending`

Target: `urllib3/urllib3@824d97bb1e36f8ac9d3445d9ca1726f0a48b4b78`

Parent exact reproduction: run `31423421919`, Python 3.12 and 3.14 success on the preserved scout discriminator.

## Selected candidate

For comma-separated `Content-Encoding`:

1. parse and ignore empty list elements;
2. create `MultiDecoder` only when every remaining coding is supported;
3. pass the normalized supported chain into the decoder.

Unknown codings keep the whole chain opaque, matching lone-unknown behavior. Empty elements alone do not disable valid supported decoding.

Production fence: `src/urllib3/response.py` only.

Prepared artifacts:

- `candidate.patch`
- `add-regressions.py`

## Protocol correction from adversarial review

Candidate generation 1 treated an empty token as unsupported. RFC 9110 section 5.6.1.2 requires HTTP recipients to parse and ignore a reasonable number of empty list elements. Generation 2 therefore strips empty elements before the all-supported check and normalizes the decoder chain without them.

This specifically preserves:

```text
gzip,
, gzip
gzip, , deflate
```

as supported chains while still keeping chains containing a real unknown coding opaque.

## Required exact gate

Baseline RED:

- `test_fieldwork_unknown_content_encoding_chain_stays_opaque` must fail on exact public source because known+unknown chains currently reinterpret the unknown token as deflate.

Candidate GREEN:

- lone unknown remains raw;
- unknown after known remains raw;
- unknown before known remains raw;
- `gzip, deflate` and `deflate, deflate` fully decode;
- leading, trailing, and interior empty list elements are ignored for otherwise supported chains;
- existing `test_multi_decoding_deflate_deflate`, `test_multi_decoding_deflate_gzip`, and `test_multi_decoding_gzip_gzip` pass;
- installed candidate `response.py` byte-matches patched exact source;
- `git diff --check` passes.

## Boundary

This experiment preserves whole-chain opacity when any non-empty coding is unsupported. It does not introduce a new DecodeError policy and does not change `_get_decoder()` fallback behavior for already-authorized callers.

Upstream contact authorized: `false`.
