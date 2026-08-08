# Candidate: preserve client TLS setup errors on WebSocket connections

Fieldwork #709 follow-up. Prepared 2026-08-09.

Automated upstream contact: **none**.

## Proposed title

`websocket: surface client TLS setup errors instead of generic connection failure`

## Parent breadcrumb

https://redirect.github.com/oven-sh/bun/pull/36149

That active PR fixes bad client cert/key/passphrase diagnostics for `fetch()` and explicitly names two sibling WebSocket SSL-context construction sites as deferred follow-up work:

- `WebSocketProxyTunnel::start`
- `WebSocketUpgradeClient::connect`

The parent explains why it stopped there: WebSockets have an event-based error surface, while fetch rejects a promise with a `SystemError`; carrying `ERR_OSSL_*` through WebSockets therefore needs a separate `http_jsc` error mapping.

Ownership searches found no separate open PR/issue for this WebSocket follow-up.

## Current-main source read

Revalidated against Bun main `9d519e8ca9f63a19f94790c47019bd7b6752c27a`.

### 1. CONNECT-tunnel TLS: `WebSocketProxyTunnel::start`

`src/http_jsc/websocket_client/WebSocketProxyTunnel.rs` builds an `SslWrapper` from the request's TLS config:

```rust
let wrapper = SslWrapperType::init_from_options(
    &options.as_usockets(),
    true,
    handlers,
)
.map_err(|_| crate::Error::InvalidOptions)?;
```

So any SSL-context setup failure that reaches this point is immediately collapsed to `InvalidOptions`. The BoringSSL reason queue is not consumed and transported.

This is especially direct because #36149 already added the sibling fetch-side pattern: immediately take the thread-local BoringSSL error after the failed SSL-context build, carry the packed code through an error enum, then format it at the JS boundary.

### 2. Direct/upgrade client TLS: `WebSocketUpgradeClient::connect`

`src/http_jsc/websocket_client/WebSocketUpgradeClient.rs` owns the other TLS construction path. It obtains a per-config client `SSL_CTX` through the VM's `ssl_ctx_cache_get_or_create` hook and threads a low-level `create_bun_socket_error_t` alongside it.

The function's external contract is currently `Option<*mut Self>`: returning `None` means the connection setup failed. That contract has no room for a BoringSSL reason, so a cert/key/passphrase parse failure can only collapse into the WebSocket client's generic failure handling.

This means the two sites probably want one shared WebSocket-specific error carrier instead of independent fixes.

## Expected user-facing behavior

For client TLS material failures, WebSocket's `error` event should expose an Error whose diagnostics preserve the same BoringSSL reason as the equivalent fetch/node:tls operation, e.g.:

- cert/key mismatch → `ERR_OSSL_X509_KEY_VALUES_MISMATCH`
- encrypted key with bad passphrase → `ERR_OSSL_*_BAD_DECRYPT` (library prefix follows Bun/BoringSSL mapping)
- non-PEM cert/key → `ERR_OSSL_PEM_NO_START_LINE`

The WebSocket close/error event ordering should stay unchanged; this candidate is about the diagnostic payload, not handshake lifecycle policy.

## Suggested implementation seam

Do this after #36149 settles so the BoringSSL formatting helper/error-code representation can be reused.

Likely split:

1. Add a WebSocket/http_jsc error variant carrying the packed BoringSSL code.
2. At both SSL-context construction sites, consume the BoringSSL thread-local error immediately after failure.
3. Thread that variant to the existing WebSocket termination/error-event boundary.
4. Materialize a JS Error/SystemError there with `code` and the BoringSSL message.
5. Preserve the old generic error only when there is no queued BoringSSL reason.

Avoid doing eager validation on the JS thread merely to produce an error if the HTTP-thread/site-local queue can be carried correctly; #36149's current approach is the better sibling pattern.

## Regression matrix

Prepare two families because the two source sites are distinct:

### Direct `wss://`

- bad cert/key mismatch
- bad passphrase
- non-PEM cert or key
- matching valid material control

### `wss://` through HTTP CONNECT proxy

Repeat at least cert/key mismatch and non-PEM input to pin `WebSocketProxyTunnel::start` separately.

Assertions should check:

- one WebSocket error event;
- error `.code` is the expected `ERR_OSSL_*`, not a generic connection/invalid-options label;
- process remains healthy and close behavior is unchanged.

## Size/risk

**Medium-small, not tiny.** The native failure capture is straightforward and already proven by #36149. The real design question is the WebSocket JS error-event carrier. That makes it a good prepared follow-up, but lower priority than the literal-IP connect errno fix.

## Evidence

- #36149 breadcrumb and sibling mechanism: `source-read`
- current WebSocketProxyTunnel collapse: `source-read`
- current upgrade-client TLS construction ownership: `source-read`
- regression matrix: `target-test-prepared` only after concrete fixture code exists
- exact Bun execution: unavailable in current scout environment

## Disposition

**Retain.** Wait for #36149 to stabilize, then prepare code/tests on top of its error helper rather than duplicating the BoringSSL mapping.