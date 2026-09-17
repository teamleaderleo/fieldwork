# Cloudflare Access cache credential lifetime

Current public source: `cloudflare/workers-sdk@20470fa8b09761c50b5c2c1d6a5f2652b61bd271`.

Relevant file: `packages/workers-auth/src/access.ts`.

## Source finding

The Access helper owns two process-wide caches:

- `headersCache`, keyed only by domain;
- `usesAccessCache`, keyed only by domain.

When a complete Access service-token pair is present, `getAccessHeaders()` constructs the two secret headers and stores them under the domain. On a later call where the credentials are absent or only one variable remains set, the helper can return the old complete cached pair after Access detection.

An interactive `CF_Authorization` cookie is stored in the same domain-only cache. The cache records no credential owner, creation time, expiry, auth mode, or operation generation.

`domainUsesAccess()` also caches `false` when its probe throws or times out. The negative result has no expiry or distinction between a conclusive non-Access response and a transient detection failure.

## Executed model

```sh
node fieldwork-experiments/workers-sdk-authority-scan/access-cache-credential-lifetime.mjs
```

Output:

```text
PASS: removed Access service credentials still reuse the cached prior headers
PASS: a partial current Access credential pair can fall back to the complete cached prior pair
PASS: a transient Access detection failure becomes a process-lifetime negative result
PASS: per-call service headers cannot outlive the current credential pair
```

The model uses sentinel values only. No real credential, Access application, domain, network request, browser login, or public upstream interaction was used.

## Required target controls

1. Complete pair A followed by no current pair must not reuse A.
2. Complete pair A followed by only the ID or only the secret must not reuse A.
3. Pair A followed by pair B must return B and leave no path back to A.
4. Concurrent same-domain operations with distinct pairs remain owner-correct.
5. Interactive cookie reuse is bounded by explicit expiry and credential owner.
6. A service-token request cannot inherit an interactive cookie or vice versa.
7. A transient Access probe failure is retried after a bounded interval or on the next operation.
8. A conclusive non-Access result may be cached only with an explicit lifetime.
9. Non-interactive requests without current credentials fail clearly.
10. Secret header values are never logged or retained in durable evidence.

## Candidate repair direction

### Service-token credentials

Construct service-token headers directly from the current environment on every call. Do not retain those secret headers in a process-global domain cache.

### Interactive authorization

Store interactive cookies in an entry that records auth mode, domain, expiry, and owner generation. Reuse only while every field remains valid. An operation-scoped cache is preferable when callers can overlap.

### Access detection

Do not convert probe errors into permanent negative knowledge. Either:

- avoid caching error-derived `false` results; or
- attach a short retry deadline and preserve the difference between a conclusive response and a failed probe.

## Rejected directions

- Clear the cache only when both environment variables are absent: partial pairs and pair rotation remain unsafe.
- Key the cache by raw credential values: this retains secret-derived identity and still leaves rotation/expiry ambiguity.
- Keep indefinite negative detection cache entries: network and Access policy state can change during a long-lived process.

## Boundary

- #496 owns Wrangler profile and temporary-account operation state.
- #471 owns cached Cloudflare account selection.
- This finding owns Access service headers, interactive Access cookies, and Access-detection cache lifetime.

Public upstream issue and PR searches found no direct matching open work. That search is not exhaustive.
