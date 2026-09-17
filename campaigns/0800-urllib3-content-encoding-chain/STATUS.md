# urllib3 mixed Content-Encoding chain experiment

Issue: #800

State: `candidate-generation-2 — exact baseline RED proven; generation-7 exact GREEN carrier queued`

Target: `urllib3/urllib3@824d97bb1e36f8ac9d3445d9ca1726f0a48b4b78`

Parent exact reproduction: run `31423421919`, Python 3.12 and 3.14 success on the preserved scout discriminator.

## In simple words

Current urllib3 can turn an unsupported coding inside a mixed `Content-Encoding` chain into an implicit deflate decoder. The selected candidate keeps the whole chain opaque whenever any real coding token is unsupported, while preserving all-supported multi-decoding and HTTP empty-list handling.

The exact pinned source has already produced the intended baseline failure on Python 3.12 and 3.14. Two later carrier attempts stopped on reviewer-patch packaging before candidate execution. Generation 7 regenerates that reviewer artifact in Git's ordinary exact-source diff window; the candidate algorithm is unchanged.

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

That run then stopped before candidate code executed because the hand-written reviewer patch had a malformed hunk header:

```text
error: corrupt patch ... candidate.patch:20
```

Run `31428442539` again reached baseline RED on both lanes, then stopped at `git apply --check` because the hand-shaped reviewer hunk did not apply. Direct source inspection showed its visible edit matched the pinned target; the failure remained evidence-carrier packaging.

## Evidence packaging repair

Generation 7 uses the ordinary Git diff window for the exact production edit (`@@ -614,10 +614,12 @@`) with trailing context. The carrier now requires:

1. target working-tree status and any pre-existing `response.py` diff are printed before candidate materialization;
2. `response.py` must remain unchanged from the exact checkout;
3. `git apply --verbose --check candidate.patch` succeeds;
4. deterministic `apply-candidate.py` transforms the exact source;
5. `git diff --check` succeeds;
6. the generated production-only diff matches `candidate.patch` byte-for-byte after Git `index` metadata is removed;
7. only then reinstall and execute candidate controls.

Current exact carrier: #804 run `31557906841`, queued for Python 3.12 and 3.14 at this checkpoint.

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

RFC 9110 also reserves `identity` for its special role in Accept-Encoding and says it should not be included in Content-Encoding, so this candidate does not add an identity/no-op decoder.

## Owner boundary and history

Focused current-source search finds `_get_decoder()` only inside `src/urllib3/response.py`. The deflate fallback cannot be removed because ordinary `deflate` reaches `DeflateDecoder` through that fallback today.

Generation 2 therefore tightens authorization before `MultiDecoder` construction and leaves `_get_decoder()` untouched. It does not invent a new `DecodeError` policy for unsupported chains.

The asymmetry traces back to the original multi-decoder implementation in public urllib3 PR [1442](https://redirect.github.com/urllib3/urllib3/pull/1442), merged in 2018. That patch used recognized tokens only to decide whether multi-decoding should activate, then passed the complete original header into `MultiDecoder`. Its added regressions covered `deflate, deflate`, `deflate, gzip`, and `gzip, gzip`, with no mixed supported/unsupported control. This supports a latent boundary-defect classification rather than a recent regression.

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
