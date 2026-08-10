# Candidate: preserve client TLS setup errors on WebSocket connections

Fieldwork #709 follow-up. Deepened 2026-08-09.

Automated upstream contact: **none**.

## Proposed title

`websocket: surface client TLS setup errors instead of generic connection failure`

## Parent breadcrumb

https://redirect.github.com/oven-sh/bun/pull/36149

Current source pin for this packet: parent head `96c737581f4d6faeded91ee254c59ed3d680b692`.

That active PR fixes bad client cert/key/passphrase diagnostics for `fetch()` and explicitly names two sibling WebSocket SSL-context construction sites as deferred follow-up work:

- `WebSocketProxyTunnel::start`
- `WebSocketUpgradeClient::connect`

RoboBun explicitly agreed in the parent discussion that this is a separate change because WebSocket routes through `bun_http_jsc` and uses an event-based error surface.

Ownership searches found no separate open PR/issue for this exact follow-up.

## Root cause: two captures, one transport problem

### 1. CONNECT-tunnel TLS: `WebSocketProxyTunnel::start`

The tunnel builds an `SslWrapper` from the request TLS config and currently collapses failure to `InvalidOptions`:

```rust
SslWrapperType::init_from_options(...)
    .map_err(|_| crate::Error::InvalidOptions)?;
```

For a mismatched cert/key, BoringSSL has already pushed `X509_R_KEY_VALUES_MISMATCH` onto the calling thread's error queue. The parent fetch PR proves that `bun_http::error::take_boringssl_error()` can consume and preserve that packed code at exactly this kind of failure site.

This half can capture the error locally after the proxy has returned 200 and before TLS tunnel traffic starts.

### 2. Direct `wss://`: `WebSocketUpgradeClient::connect`

The direct path builds/retrieves the client `SSL_CTX` during `WebSocketUpgradeClient::connect`. If `ssl_ctx_cache_get_or_create` returns null, the Rust function returns `None` / a null pointer to C++.

That loses more than a reason string: the **FFI result itself has no error payload**.

`WebSocket.cpp` receives the null `m_upgradeClient` and unconditionally posts:

```cpp
auto eventInit = createErrorEventInit(protectedThis, "Failed to connect"_s, globalObject);
protectedThis->dispatchEvent(ErrorEvent::create(...));
protectedThis->dispatchEvent(CloseEvent::create(false, 1006, ...));
```

`createErrorEventInit` creates a fresh generic JavaScript `Error` from that fixed message. There is currently nowhere for an `ERR_OSSL_*` code captured in Rust to survive this boundary.

## Consequence for implementation size

A new numeric `WebSocketErrorCode` alone is insufficient. That enum transports only a fixed failure category, and C++ maps it back to hard-coded reason strings.

The follow-up needs a richer setup-error carrier across Rust -> C++.

Two viable designs:

### A. Result/out-parameter on the connect ABI — preferred for direct setup failure

Change the HTTPS WebSocket connect FFI so a null client can also return a small failure payload, for example:

- error kind: generic vs client-TLS-setup;
- packed BoringSSL `u32` for `ClientTLSSetup`.

C++ can then keep the existing null-client lifecycle path while constructing an Error whose `.code` / message come from the same `err_code_and_message` helper used by #36149.

This directly fits the synchronous direct-`wss://` failure, where no live upgrade client exists to deliver a later callback.

### B. Dedicated richer failure callback

Introduce a C ABI callback such as a WebSocket client TLS-setup failure carrying the packed code. The proxy-tunnel path can use this naturally because a live WebSocket/upgrade-client object exists when tunnel TLS setup runs.

For the direct path, a callback during `Bun__WebSocketHTTPSClient__connect` would also require suppressing the generic `m_upgradeClient == nullptr` fallback to avoid double error/close dispatch. That makes the ABI-result approach cleaner there.

A practical implementation may use A for initial construction plus the same packed-error formatting helper at the shared C++ event-construction boundary, while the tunnel stores/forwards the same payload through its existing termination path.

## Event semantics to preserve

This candidate is diagnostic-only:

- one `error` event;
- `ErrorEvent.error` remains an `Error` object, now with the expected `.code`;
- direct setup failure keeps abnormal close code `1006` / `wasClean === false`;
- proxy setup failure keeps its existing error-before-close ordering;
- successful/handshake certificate-verification behavior is unchanged (the existing `1015 "TLS handshake failed"` path is a different phase).

The distinction is important: **client TLS material failing to build an SSL_CTX is setup-time**, while an untrusted/self-signed remote certificate is handshake-time. This follow-up should not merge those paths.

## Prepared regression

Fieldwork now carries:

`../candidate-tests/websocket-client-tls-error-fidelity.test.ts`

It has two focused cases using the same harness certificates as Bun's fetch TLS tests:

1. direct `wss://` with `validTls.cert` + `expiredTls.key`;
2. the same mismatched client material after an HTTP CONNECT proxy returns 200.

Both require:

- exactly one error event;
- `event.error instanceof Error`;
- `event.error.code === "ERR_OSSL_X509_KEY_VALUES_MISMATCH"`;
- abnormal close `1006`, `wasClean === false`.

The current direct path should fail the `.code` assertion because C++ creates a fresh generic `Error("... Failed to connect")`. The tunnel path should likewise fail until the packed BoringSSL reason is captured and transported.

## Reuse from #36149

Do this on top of the parent after it settles. Reuse:

- `bun_http::error::take_boringssl_error()` for immediate queue capture;
- `ClientTLSSetup(u32)` as the conceptual error variant;
- the shared BoringSSL `err_code_and_message` formatting so fetch and WebSocket cannot drift in code naming.

Do not duplicate OpenSSL/BoringSSL reason tables in `http_jsc`.

## Size/risk

**Medium.** The native queue capture is trivial and already proven. The work is the cross-language error transport and ensuring the existing one-error/one-close lifecycle remains single-shot.

That makes this a good follow-up, but it is no longer in the same tiny-patch tier as the JSX scan candidate.

## Evidence

- parent explicit deferral + RoboBun acknowledgement: `source-read`
- both SSL-context failure sites: `source-read`
- direct C++ null-client generic-error fallback: `source-read`
- current fixed-string `WebSocketErrorCode` mapping: `source-read`
- prepared two-path regression: `target-test-prepared`
- exact Bun execution: unavailable in current scout environment

## Disposition

**Presentable design/test candidate; implementation not yet prepared.** The bug and both failure sites are pinned, and the transport constraint is now understood. Wait for #36149 to settle, then implement the richer error carrier on top of its shared BoringSSL helpers.