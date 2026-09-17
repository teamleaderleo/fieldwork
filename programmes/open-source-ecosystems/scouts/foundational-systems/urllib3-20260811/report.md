# urllib3 foundational-systems scout — 2026-08-11

## In simple words

Two current urllib3 boundaries reproduced on the exact pinned source, and one retry-policy question remains parked.

1. **Mixed `Content-Encoding` lists can silently reinterpret an unknown coding as `deflate`.** A lone unknown coding is passed through raw. Put the same unknown token beside a supported coding and urllib3 can instantiate it as the default deflate decoder.
2. **`Retry-After: 0` loses its explicit-zero meaning when exponential backoff exists.** The header parses successfully to numeric zero, then a truthiness check falls through to backoff.
3. **`Retry(total=None, status=...)` disables the implicit Retry-After status path in the reproduced mechanism.** A status-forcelist path still retries. The intended API contract needs more evidence, so this branch stays parked.

The first finding is the cleanest implementation candidate. The second is also bounded, with adjacent live upstream work in [urllib3 PR 5010](https://redirect.github.com/urllib3/urllib3/pull/5010), so refresh overlap immediately before implementation or public packaging.

## Scout identity

- Programme: `open-source-ecosystems`
- Parent lane: Fieldwork #211 / OE-05 foundational libraries
- Target: `urllib3/urllib3`
- Exact public source: `824d97bb1e36f8ac9d3445d9ca1726f0a48b4b78`
- Source subject: `Declare support for Python 3.15 (#5145)`
- Owned Fieldwork path: `programmes/open-source-ecosystems/scouts/foundational-systems/urllib3-20260811/`
- Research PR: Fieldwork #787
- Exact execution carrier: Fieldwork #792
- Authoritative exact run: `31423421919`
- Upstream contact authorized: `false`
- Third-party target remained read-only

## Evidence state

- `source-read`: exact public source and adjacent tests inspected.
- `model-executed`: preserved probe first reproduced all three mechanisms on installed urllib3 2.7.0.
- `target-executed`: authoritative run `31423421919` executed the same probe against an installed build produced from the exact pinned source on Python 3.12 and 3.14.

Exact jobs:

```text
Python 3.12: 93569358489 — success
Python 3.14: 93569358404 — success
```

Both jobs:

1. checked out exact `824d97bb1e36f8ac9d3445d9ca1726f0a48b4b78`;
2. built and installed that checkout;
3. byte-compared installed `response.py` and `retry.py` with the checked-out source;
4. executed the preserved discriminator.

Python 3.12 recorded matching SHA-256 pairs:

```text
response.py  9a8aed6d04aced6c43ab5d239373d3c8ea77c94fcca6a612f6ad4eb8226c9a9d
retry.py     af28113e0350b332df9b7d83501a9ac4438056c812dc1f910f7b11e3131ab613
```

Full receipt: `exact-execution-20260811.md`.

The predecessor run `31423216020` is harness-only failure evidence. Exact checkout succeeded, then direct source-tree import stopped because generated `urllib3._version` was absent. No discriminator ran in that predecessor.

## Contribution and test map

The pinned contribution guide gives these ordinary development gates:

```text
nox -rs format
nox -rs lint
nox --reuse-existing-virtualenvs --sessions test-3.12 test-pypy3.11
nox --reuse-existing-virtualenvs --sessions test-3.13 -- <pytest args>
```

Focused test owners for promoted candidates:

- `test/test_response.py` — decoder behavior;
- `test/test_retry.py` — Retry-After/backoff behavior.

## Finding A — mixed known/unknown Content-Encoding alias

### Source owner

Pinned file: `src/urllib3/response.py`.

Relevant path:

```text
HTTPResponse.read()
  -> BaseHTTPResponse._init_decoder()
  -> _get_decoder(content_encoding)
  -> MultiDecoder(mode)
  -> _get_decoder(token) for each coding token
```

Current behavior is split across two helpers:

- `_init_decoder()` scans comma-separated values and enters the multi-decoder path when **at least one** token is supported;
- it then passes the **whole original header** into `_get_decoder()`;
- `MultiDecoder` asks `_get_decoder()` to instantiate every token;
- `_get_decoder()` falls through to `DeflateDecoder()` for a token that misses gzip, Brotli, and zstd branches.

A lone unknown coding does not enter this path. A mixed list containing one known token does.

### Exact discriminator

Payload:

```text
fieldwork-urllib3-mixed-encoding
```

Wire bytes:

```python
wire = zlib.compress(gzip.compress(payload))
```

Header matrix:

```text
x-fieldwork
gzip, x-fieldwork
gzip, deflate
```

Exact target result on Python 3.12 and 3.14:

```text
unknown-only preserved raw bytes: True
known+unknown decoded to payload: True
known control decoded to payload: True
```

The same made-up token changes meaning solely because another token in the header is supported.

### Candidate invariant

Unknown content codings should never silently acquire deflate semantics through list composition.

The smallest compatibility-preserving candidate is to create a `MultiDecoder` only when every non-empty coding token is supported. A separate design could raise a decode error for unsupported mixed chains, but that is a wider interface decision.

### Focused target test

Add one `test/test_response.py` matrix covering:

```text
unknown alone -> current raw-preservation behavior
known + unknown -> must not interpret unknown as deflate
known + known -> existing decoding unchanged
```

### Disposition

**PROMOTE.**

Evidence: exact-source `target-executed`, crisp negative control, narrow owner, no matching repair found in the scout overlap search.

## Finding B — Retry-After zero falls through to backoff

### Source owner

Pinned file: `src/urllib3/util/retry.py`.

Relevant path:

```text
Retry.sleep(response)
  -> Retry.sleep_for_retry(response)
  -> Retry.get_retry_after(response)
  -> Retry.parse_retry_after(value)
  -> Retry._sleep_backoff()
```

`parse_retry_after("0")` returns numeric `0`. `sleep_for_retry()` checks the parsed value by truthiness, so zero returns the same branch as header absence. `Retry.sleep()` then invokes exponential backoff.

### Exact discriminator

Build retry history with:

```python
retry = Retry(total=5, backoff_factor=1)
retry = retry.increment(method="GET")
retry = retry.increment(method="GET")
```

Computed backoff: `2.0` seconds.

Exact target result on both Python versions:

```text
absent: [call(2.0)]
zero:   [call(2.0)]
one:    [call(1)]
```

The positive `Retry-After: 1` control overrides backoff. Explicit zero collapses onto the absent-header case.

### Candidate direction

Distinguish `None` from numeric zero:

```python
retry_after = self.get_retry_after(response)
if retry_after is None:
    return False
if retry_after > 0:
    time.sleep(retry_after)
return True
```

This consumes an explicit zero Retry-After value without sleeping and prevents the later backoff fallback.

### Overlap

Open [urllib3 PR 5010](https://redirect.github.com/urllib3/urllib3/pull/5010) touches the same Retry-After implementation/test neighborhood for maximum-wait handling. Its current diff explicitly tests `parse_retry_after("0") == 0` while leaving the sleep truthiness path unchanged.

### Disposition

**PROMOTE WITH LIVE OVERLAP REFRESH.**

Mechanism is exact-target reproduced. Implementation should proceed only after checking the live state of PR 5010 and any newer retry work.

## Parked branch — total=None and implicit Retry-After statuses

Exact target mechanism:

```python
Retry(total=None, status=2, respect_retry_after_header=True).is_retry(
    "GET", 429, has_retry_after=True
)
# False

Retry(
    total=None,
    status=2,
    status_forcelist={429},
    respect_retry_after_header=True,
).is_retry("GET", 429, has_retry_after=True)
# True
```

The implicit Retry-After path uses `bool(self.total and ...)`; `total=None` disables that branch. The class documentation describes `total=None` as removing the total cap and falling back on category counts, while status-counter documentation is closely tied to explicit status-forcelist use.

### Disposition

**PARK.**

The mechanism is target-executed. Promotion still requires contract/history evidence showing that implicit Retry-After statuses are expected to consume `status` when `total=None`.

## Negative results and challenged theories

### Connection release/drain

I source-read response draining and `HTTPConnectionPool.urlopen()` socket ownership. The path explicitly tracks `release_this_conn`, cleans error connections, and drains responses before recursive redirect/status retries. Existing lifecycle tests cover the initial theories well enough to stop this branch.

Disposition: **STOP for this scout.**

### Multi-decoder ordinary controls

Existing tests already cover supported chains such as deflate/deflate and gzip/deflate. The missing boundary is specifically known-plus-unknown composition.

### Fieldwork duplication

Focused Fieldwork search found no dedicated urllib3 investigation before this scout. #211 was the target-list owner.

## Preserved probe

`probe.py` contains all three discriminators.

Exact-target output from run `31423421919`:

```text
[mixed-content-encoding]
unknown-only preserved raw bytes: True
known+unknown decoded to payload: True
known control decoded to payload: True

[retry-after-zero]
configured exponential backoff: 2.0
absent: [call(2.0)]
zero: [call(2.0)]
one: [call(1)]

[retry-total-none]
implicit Retry-After 429 retried: False
status-forcelist 429 retried: True
```

## Ranked next actions

1. Create a dedicated mixed-content-encoding experiment with one narrow candidate and exact target RED/GREEN test.
2. Refresh live urllib3 retry overlap, then create a separate `Retry-After: 0` experiment if the lane remains free.
3. Keep `total=None` parked until contract/history evidence selects an intended behavior.
4. Retire execution carrier #792 after this receipt transfer and keep the parent research PR free of temporary workflows.

No automated upstream issue, pull request, comment, review, reaction, branch, or message was created or changed.
