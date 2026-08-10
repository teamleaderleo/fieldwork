# urllib3 mixed Content-Encoding chain experiment

Issue: #800

State: `candidate-generation-2 — protocol-correct controls hardened; exact RED/GREEN pending`

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

## Why generation 1 was superseded

Generation 1 treated an empty list element as unsupported. RFC 9110 section 5.6.1.2 requires recipients to parse and ignore a reasonable number of empty list elements, and empty elements do not contribute to the list element count.

Generation 2 therefore strips empty elements before the all-supported check and normalizes the supported decoder chain without them.

## Protocol and decoder controls

Supported-chain controls include:

```text
gzip, deflate
deflate, deflate
gzip,
, gzip
gzip, , deflate
```

Unknown-chain controls include:

```text
x-fieldwork
gzip, x-fieldwork
x-fieldwork, gzip
```

A six-real-coding control requires the existing `MultiDecoder.max_decode_links = 5` protection to keep raising `DecodeError`. Empty list elements are excluded from this count in line with HTTP list parsing.

RFC 9110 also reserves `identity` for its special role in Accept-Encoding and says it should not be included in Content-Encoding, so this candidate does not need a new identity/no-op decoder.

## Owner boundary

Focused current-source search finds `_get_decoder()` only inside `src/urllib3/response.py`. The deflate fallback cannot simply be removed because ordinary `deflate` reaches `DeflateDecoder` through that fallback today.

Generation 2 therefore tightens authorization before `MultiDecoder` construction and leaves `_get_decoder()` untouched. It does not invent a new DecodeError policy for unsupported chains.

## Candidate sanity

A model-executed monkeypatch on installed urllib3 2.7.0 passed unknown-chain opacity, supported-chain decoding, and leading/trailing/interior empty-element controls. Exact pinned-source candidate execution remains the authority gate.

## Required exact gate

Baseline RED:

- `test_fieldwork_unknown_content_encoding_chain_stays_opaque` fails on exact public source because known+unknown chains currently reinterpret the unknown token as deflate.

Candidate GREEN:

- lone unknown remains raw;
- unknown after known remains raw;
- unknown before known remains raw;
- supported chains fully decode;
- leading, trailing, and interior empty list elements are ignored for otherwise supported chains;
- six real supported codings still hit the existing link-count limit;
- existing multi-decoding controls pass;
- installed candidate `response.py` byte-matches patched exact source;
- `git diff --check` passes.

Current exact carrier: #804, run `31426131410` queued at the latest checkpoint.

Upstream contact authorized: `false`.
