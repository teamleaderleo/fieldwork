## In simple words

I found two concrete urllib3 boundaries worth promoting and one retry idea worth parking.

1. **Mixed `Content-Encoding` lists can silently treat an unknown coding as `deflate`.** A lone unknown coding is passed through as raw bytes, while `gzip, x-fieldwork` constructs a multi-decoder and maps `x-fieldwork` to the default deflate decoder. A synthetic discriminator on urllib3 2.7.0 turns deliberately double-compressed bytes all the way back into plaintext under the made-up `x-fieldwork` label.
2. **`Retry-After: 0` loses its explicit-zero meaning when exponential backoff exists.** urllib3 parses the header to integer zero, then a truthiness check treats zero like an absent value and falls through to backoff. With two retry-history entries and `backoff_factor=1`, both an absent header and `Retry-After: 0` sleep for 2 seconds; `Retry-After: 1` sleeps for 1 second.
3. **`Retry(total=None, status=...)` plus implicit Retry-After status handling is an interesting ambiguity, but the project contract needs more evidence.** The model shows the implicit 429 path returns false while a status-forcelist path returns true. I would keep this parked until docs/history establish the intended relationship between `total=None` and implicit Retry-After retries.

The first item has the cleanest promotion path. The second is also strong, with an open upstream PR touching adjacent Retry-After code, so any future implementation should coordinate around that live work.

## Scout identity

- Programme: `open-source-ecosystems`
- Parent lane: Fieldwork #211, OE-05 foundational systems
- Target: `urllib3/urllib3`
- Upstream branch read: `main`
- Upstream revision: `824d97bb1e36f8ac9d3445d9ca1726f0a48b4b78`
- Upstream revision subject: `Declare support for Python 3.15 (#5145)`
- Upstream write access: absent; upstream stayed read-only
- Upstream-contact authorization: `false`
- Fieldwork claim comment: parent #211
- Owned Fieldwork path: `programmes/open-source-ecosystems/scouts/foundational-systems/urllib3-20260811/`

## Evidence level

- **source-read**: exact upstream revision `824d97bb1e36f8ac9d3445d9ca1726f0a48b4b78` was read through the GitHub connector.
- **model-executed**: `probe.py` was executed against installed urllib3 `2.7.0`; the relevant source mechanisms match the pinned revision read.
- **target-executed**: pending. I did not execute an exact checkout of the pinned upstream revision, so this report deliberately stops below that evidence level.

## Contribution and test map

At the pinned revision, `docs/contributing.rst` gives the normal development path:

```text
nox -rs format
nox -rs lint
nox --reuse-existing-virtualenvs --sessions test-3.12 test-pypy3.11
nox --reuse-existing-virtualenvs --sessions test-3.13 -- <pytest args>
```

For these candidates the focused upstream test owners are:

- `test/test_response.py` for decoder behavior.
- `test/test_retry.py` for Retry-After/backoff behavior.

## Compact code map

### Response decoding

Pinned file: `src/urllib3/response.py`

Relevant path:

```text
HTTPResponse.read()
  -> BaseHTTPResponse._init_decoder()
  -> _get_decoder(content_encoding)
  -> MultiDecoder(mode) for comma-separated values
  -> _get_decoder(token) for each token
```

The key asymmetry is split across two helpers:

- `_init_decoder()` scans comma-separated values and asks whether **at least one** token appears in `CONTENT_DECODERS`.
- When that condition is true, it passes the **whole original header value** to `_get_decoder()`.
- `_get_decoder()` sends comma-separated values to `MultiDecoder`.
- `MultiDecoder` runs `_get_decoder()` on every token.
- `_get_decoder()` falls through to `DeflateDecoder()` for any token that misses gzip, Brotli, and zstd branches.

A lone unknown encoding never enters this multi-decoder path, so the response remains raw. A mixed known/unknown list can therefore reinterpret the unknown token as deflate.

### Connection-pool context

Pinned file: `src/urllib3/connectionpool.py`

`HTTPConnectionPool.urlopen()` tracks socket ownership with a local `release_this_conn` flag. Redirect and status-retry paths drain the response before recursion. I reviewed this path because response decoding and draining can affect connection reuse. The ownership logic and existing drain handling looked deliberate; I did not isolate a separate pool-release defect during this scout.

### Retry timing

Pinned file: `src/urllib3/util/retry.py`

Relevant path:

```text
Retry.sleep(response)
  -> Retry.sleep_for_retry(response)
  -> Retry.get_retry_after(response)
  -> Retry.parse_retry_after(value)
  -> fallback Retry._sleep_backoff()
```

`parse_retry_after("0")` returns numeric `0`. `sleep_for_retry()` uses a truthiness check on that result. Zero therefore returns the same false branch as an absent header, and `sleep()` proceeds to exponential backoff.

## Experiment A — mixed unknown Content-Encoding

### Question

Can an unrecognized content-coding token be treated as a supported decoder when it appears beside a recognized token?

### Model

Use payload:

```text
fieldwork-urllib3-mixed-encoding
```

Build bytes as:

```python
wire = zlib.compress(gzip.compress(payload))
```

This is valid synthetic data for the known control `Content-Encoding: gzip, deflate` because decoders run in reverse application order.

Read the same wire under three headers:

```text
x-fieldwork
gzip, x-fieldwork
gzip, deflate
```

### Observed on urllib3 2.7.0

```text
x-fieldwork          -> raw bytes preserved
gzip, x-fieldwork    -> plaintext payload
gzip, deflate        -> plaintext payload
```

### Discriminator

The negative control is the lone unknown coding. It preserves raw bytes. Adding a recognized coding flips the unknown token into a working deflate decoder and fully transforms the same wire bytes.

### Why it is worth promotion

The unknown token's meaning depends on whether another token in the same header is recognized. That creates silent decoding under a made-up label and diverges from urllib3's own lone-unknown behavior.

### Narrow fix direction

Keep multi-decoder creation behind an all-tokens-supported check, or make unknown-token handling explicit inside `MultiDecoder`. The lowest-change candidate is to instantiate `MultiDecoder` only when every non-empty coding token is supported; this preserves the current lone-unknown pass-through behavior.

### Focused regression test

Add a `test/test_response.py` case with one supported and one made-up coding. Assert the chosen project behavior explicitly. The existing lone-unknown pass-through behavior makes raw preservation the smallest compatibility move; an explicit decode error is a separate interface decision.

### Confidence

**High mechanism confidence.** Exact pinned source read plus deterministic model discriminator and negative control.

## Experiment B — Retry-After zero versus backoff

### Question

Does an explicit `Retry-After: 0` override an already-computed exponential backoff delay?

### Model

Create:

```python
retry = Retry(total=5, backoff_factor=1)
retry = retry.increment(method="GET")
retry = retry.increment(method="GET")
```

The resulting backoff time is `2.0` seconds.

Call `retry.sleep(response)` with three cases while mocking `time.sleep`:

```text
no Retry-After header
Retry-After: 0
Retry-After: 1
```

### Observed on urllib3 2.7.0

```text
absent -> time.sleep(2.0)
zero   -> time.sleep(2.0)
one    -> time.sleep(1)
```

### Discriminator

The positive control `Retry-After: 1` takes precedence over backoff. The absent control uses backoff. Explicit zero collapses onto the absent case.

### Narrow fix direction

Teach `sleep_for_retry()` to distinguish `None` from numeric zero:

```python
retry_after = self.get_retry_after(response)
if retry_after is None:
    return False
if retry_after > 0:
    time.sleep(retry_after)
return True
```

That lets explicit zero consume the Retry-After path without sleeping and prevents the later backoff fallback.

### Focused regression test

In `test/test_retry.py`, build retry history with a positive backoff and assert:

```text
absent header -> backoff sleep
Retry-After: 0 -> no sleep
Retry-After: 1 -> one-second sleep
```

### Upstream overlap

An open upstream PR, `urllib3/urllib3` PR 5010, adds `retry_after_max_strict` and touches `src/urllib3/util/retry.py` plus `test/test_retry.py`. Its diff includes a test that `parse_retry_after("0") == 0`, while leaving the `sleep_for_retry()` truthiness behavior unchanged. This is adjacent ownership, so a future upstream patch should check that PR's live state before editing the same area.

Direct reference in this repository file: https://github.com/urllib3/urllib3/pull/5010

### Confidence

**High mechanism confidence; medium promotion confidence while adjacent upstream work is live.**

## Parked branch — `total=None` and implicit Retry-After statuses

Model:

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

The source uses `bool(self.total and ...)` for the implicit Retry-After status path. Since `total=None` is falsy, that path is disabled even though the class documentation describes `total=None` as removing the total cap and falling back on category counts.

I am parking this branch because the `status` counter documentation is tied closely to `status_forcelist`, while implicit Retry-After status handling may intentionally depend on `total`. A promotion would need history or maintainer-facing contract evidence beyond the current model.

## Negative results and challenged theories

- **Connection release/drain:** source-read the response drain and `HTTPConnectionPool.urlopen()` ownership path. I found explicit ownership tracking, error cleanup, response draining before recursive redirect/status retries, and existing lifecycle tests. No isolated promotion candidate survived this pass.
- **Mixed-decoder false lead check:** supported multiple-coding tests already exist for combinations such as deflate/deflate and gzip/deflate. The missing boundary is the known-plus-unknown list, which exercises a different branch in `_init_decoder()`.
- **Retry-After zero overlap:** focused issue/PR searches found no dedicated zero-versus-backoff report. Upstream PR 5010 is adjacent and currently open.
- **Fieldwork duplication:** focused Fieldwork searches found no open PR, closed issue, or dedicated active scout for urllib3 beyond the parent OE-05 target matrix.

## Runnable reproduction

From a Python environment with urllib3 installed:

```text
python programmes/open-source-ecosystems/scouts/foundational-systems/urllib3-20260811/probe.py
```

Expected output on urllib3 2.7.0 includes:

```text
urllib3=2.7.0
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

## Ranked follow-up branches

1. **Promote: mixed known/unknown Content-Encoding decoder alias.** Small source surface, clear local inconsistency, deterministic model, clean negative control, no matching open upstream PR found.
2. **Promote with overlap check: `Retry-After: 0` falls through to backoff.** Small patch/test surface and crisp discriminator; coordinate with live urllib3 PR 5010 before any upstream implementation.
3. **Park: `total=None` disables implicit Retry-After status retries.** Mechanism confirmed, contract evidence incomplete.
4. **Stop: generic connection-pool release/drain hunt from this pass.** Existing code and tests cover the initial ownership theories well enough to move research time elsewhere.

## Recommendation

Split the first two findings into dedicated Fieldwork carriers if the programme wants patch preparation. Keep upstream read-only until a separate authorization explicitly permits contact or contribution. For immediate follow-up, the decoder candidate gives the cleanest next experiment: reproduce against an exact checkout at `824d97bb1e36f8ac9d3445d9ca1726f0a48b4b78`, add one targeted regression test, and verify the smallest all-codings-supported guard.
