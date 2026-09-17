# urllib3 exact execution receipt — 2026-08-11

Target: `urllib3/urllib3@824d97bb1e36f8ac9d3445d9ca1726f0a48b4b78`

Carrier: Fieldwork PR #792

Authoritative run: `31423421919`

Jobs:

- Python 3.12: `93569358489` — success
- Python 3.14: `93569358404` — success

Evidence class: `target-executed` for the preserved discriminator against the exact pinned urllib3 source.

## Identity gate

Both jobs checked out the exact target SHA, built the checkout, installed it, and byte-compared the installed `urllib3/response.py` and `urllib3/util/retry.py` against the pinned source before running the probe.

Python 3.12 recorded:

```text
response.py sha256: 9a8aed6d04aced6c43ab5d239373d3c8ea77c94fcca6a612f6ad4eb8226c9a9d
retry.py    sha256: af28113e0350b332df9b7d83501a9ac4438056c812dc1f910f7b11e3131ab613
```

The source and installed digests matched in each identity check.

## Exact discriminator result

Both Python versions passed the same assertions.

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

Therefore:

1. the mixed known/unknown `Content-Encoding` alias is exact-target reproduced;
2. explicit `Retry-After: 0` falling through to exponential backoff is exact-target reproduced;
3. the `total=None` implicit-status asymmetry is exact-target reproduced as a mechanism, while its intended contract remains parked.

## Superseded harness run

Run `31423216020` is harness-only failure evidence. Exact checkout succeeded, but direct source-tree import stopped on generated `urllib3._version` absence before the discriminator ran. The repaired run built the exact checkout and added byte-identity checks before execution.

## Disposition

- Mixed content encoding: **PROMOTE** to a bounded candidate experiment.
- Retry-After zero: **PROMOTE WITH LIVE OVERLAP REFRESH** because upstream PR 5010 touches the same Retry-After file/test neighborhood.
- `total=None`: **PARK** pending contract/history evidence.

Upstream urllib3 remained read-only. Upstream contact authorized: `false`.
