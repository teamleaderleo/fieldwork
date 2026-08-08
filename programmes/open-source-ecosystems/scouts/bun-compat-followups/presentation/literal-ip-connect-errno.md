# Candidate: preserve synchronous literal-IP `Bun.connect` errno

Fieldwork #709 follow-up. Prepared 2026-08-09.

Automated upstream contact: **none**.

## Proposed title

`net: preserve errno when Bun.connect fails synchronously`

## Parent breadcrumb

https://redirect.github.com/oven-sh/bun/pull/37093

That PR fixes several connect-error fidelity paths and explicitly leaves one gap: a literal-IP connect that fails synchronously still surfaces as generic `FailedToOpenSocket`, even though the native failure has a real errno.

## Current-main mechanism

Revalidated against Bun main `9d519e8ca9f63a19f94790c47019bd7b6752c27a`.

`src/uws_sys/SocketGroup.rs` currently defines:

```rust
pub enum ConnectResult {
    Socket(*mut us_socket_t),
    Connecting(*mut ConnectingSocket),
    Failed,
}
```

`SocketGroup::connect()` calls `us_socket_group_connect(...)`; when the returned pointer is null it immediately returns payload-less `ConnectResult::Failed`.

The caller in `src/runtime/socket/socket_body.rs` then maps that branch to:

```rust
uws::ConnectResult::Failed => {
    return Err(crate::Error::FailedToOpenSocket);
}
```

So the diagnostic loss occurs at the C/Rust boundary: the native call fails on the calling thread, but the Rust enum carries no errno payload.

The later asynchronous `handle_connect_error()` path already knows how to turn real connect errnos such as `EADDRNOTAVAIL` into a `SystemError { code, errno, syscall: "connect", message: "Failed to connect" }`. The follow-up should reuse that vocabulary instead of inventing another error surface.

## Small implementation seam

Likely narrow repair:

1. Change the synchronous failure variant to carry an errno, e.g. `Failed(c_int)`.
2. Capture the platform's last socket error immediately after `us_socket_group_connect(...)` returns null, before any Rust/C helper can disturb it.
3. At the `socket_body.rs` match, convert that errno through the same connect-error mapping used by `handle_connect_error()`.
4. Keep a generic fallback only when the captured error is zero/unknown.

Windows needs the socket error source corresponding to uSockets' `LIBUS_ERR` / WSA error convention, not CRT `errno`.

A small helper extracting `SystemError` construction from `handle_connect_error()` would avoid duplicating its Windows normalization and errno-code table. If #37093 lands first, build directly on its expanded table for `ETIMEDOUT` / `EHOSTUNREACH` / `ENETUNREACH`.

## Deterministic regression candidate

Use a valid literal destination plus an invalid local bind address. Node's vendored `test-http-localaddress-bind-error.js` uses `1.2.3.4` as `invalidLocalAddress`; binding that address should fail synchronously with `EADDRNOTAVAIL` on a normal host.

For Bun's direct socket API:

```ts
await Bun.connect({
  hostname: "127.0.0.1",
  port,
  localAddress: "1.2.3.4",
  socket: { data() {} },
});
```

Expected rejection after the fix:

- `code === "EADDRNOTAVAIL"`
- `syscall === "connect"`
- message uses the normal connect-error shape (`"Failed to connect"`)
- must not be `FailedToOpenSocket`

A loopback server can hold `port` open so the only failure is the local bind.

## Scope

Keep this to the synchronous `SocketGroup::connect` null-return path. Do not reopen the asynchronous multi-address behavior owned by #37093.

## Evidence

- Bun implementation: `source-read`
- Node invalid-local-address fixture: `source-read`
- Bun regression: `target-test-prepared` once the candidate test is added
- Exact Bun execution: not available in the current scout environment

## Disposition

**High-confidence small follow-up.** This is currently the strongest independent candidate after the Request precedence work. Prepare internally; wait for #37093 to stabilize/land before considering human upstream submission.