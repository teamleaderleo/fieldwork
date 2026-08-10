# urllib3 mixed Content-Encoding chain experiment

Issue: #800

State: `candidate-generation-2 — exact baseline RED proven; deterministic candidate rerun queued`

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

- `candidate.patch` — reviewer-facing production-only diff;
- `apply-candidate.py` — deterministic exact-source transformer;
- `add-regressions.py` — focused target regressions.

## Exact baseline RED

Carrier #804 run `31426131410` executed the baseline discriminator on exact source for Python 3.12 and 3.14.

Both lanes reached the intended failing assertion: a mixed known/unknown chain decoded all the way to `fieldwork-unknown-chain` where the regression required the original wire bytes to remain opaque.

Evidence class: `target-executed` RED.

The same run then stopped before any candidate code executed because the hand-written reviewer patch had a malformed hunk header:

```text
error: corrupt patch ... candidate.patch:20
```

Classification: **carrier packaging only**. The candidate invariant and algorithm did not run in that generation.

## Evidence packaging repair

The reviewer patch hunk count is corrected and carrier generation 5 now requires:

1. `git apply --check candidate.patch` on clean exact source;
2. deterministic `apply-candidate.py` transformation;
3. `git diff --check`;
4. generated production-only `response.py` diff matches `candidate.patch` byte-for-byte after removing Git `index` metadata;
5. only then reinstall and execute candidate controls.

Current rerun: #804 run `31428442539`, queued at this checkpoint.

## Why production generation 1 was superseded

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

## Candidate GREEN gate

- lone unknown remains raw;
- unknown after known remains raw;
- unknown before known remains raw;
- supported chains fully decode;
- leading, trailing, and interior empty list elements are ignored for otherwise supported chains;
- six real supported codings still hit the existing link-count limit;
- existing multi-decoding controls pass;
- installed candidate `response.py` byte-matches transformed exact source;
- reviewer patch matches transformed production diff exactly;
- `git diff --check` passes.

Upstream contact authorized: `false`.
