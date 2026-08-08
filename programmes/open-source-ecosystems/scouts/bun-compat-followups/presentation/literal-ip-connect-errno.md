# Coverage note: synchronous literal-IP `Bun.connect` errno

Fieldwork #709 follow-up. Reclassified 2026-08-09.

Automated upstream contact: **none**.

## Parent breadcrumb

https://redirect.github.com/oven-sh/bun/pull/37093

The parent PR description still says one gap remains: a literal-IP connect that fails synchronously surfaces as generic `FailedToOpenSocket`.

That description is now stale relative to the PR head.

## Current parent-head behavior

Revalidated against #37093 head `36cb6413a17ad220ae91953f6217eb282c624f6b`.

`src/runtime/socket/socket_body.rs::do_connect()` still has an internal payload-less failure:

```rust
uws::ConnectResult::Failed => {
    return Err(crate::Error::FailedToOpenSocket);
}
```

But the caller in `Listener.rs::connect_finish()` now catches any synchronous `do_connect()` error before it escapes to JS. On that path it:

- reads `WSAGetLastError()` on Windows or `bun_sys::last_errno()` elsewhere;
- handles Unix-socket errors separately;
- for synchronous TCP/local-bind failures preserves `EADDRINUSE`, `EADDRNOTAVAIL`, `EACCES`, and `EINVAL`;
- normalizes other synchronous TCP failures to `ECONNREFUSED`;
- calls the existing `NewSocket::handle_connect_error(...)`, so the promise and `connectError` callback use the normal Node-style connect `SystemError` path.

That is the follow-up implementation we were preparing. It appears to have been incorporated into the parent branch after the PR description was written.

## Why the stale description happened

The parent is still under active review. Its later commits changed the synchronous-error path while its scope paragraph was not updated. The discussion also caught a Windows-specific error-source issue in the same area (`LIBUS_ERR` / Winsock vs CRT `errno`), which confirms this code was still moving after the original “remaining gap” text was authored.

This is useful evidence for our mining method: **PR prose is a breadcrumb, not a durable ownership/status record. Re-read the head before preparing overlapping work.**

## Prepared regression remains useful

Fieldwork still carries:

`../candidate-tests/bun-connect-sync-errno.test.ts`

It uses a live loopback destination plus `localAddress: "1.2.3.4"` (the invalid local address used by Bun's vendored Node local-bind fixture) and expects:

- `code === "EADDRNOTAVAIL"`;
- `syscall === "connect"`;
- message `"Failed to connect"`;
- the same fidelity in `connectError` if that callback fires.

The current #37093 test patch does not add this local-bind regression; its visible new socket test targets a different peer-close/false-`ECONNRESET` case. So our test can remain as an optional coverage suggestion after exact-target execution, even though there is no independent implementation patch to make.

## Evidence

- parent description: `source-read`
- current parent-head implementation: `source-read`
- prepared local-bind regression: `target-test-prepared`
- exact Bun execution: unavailable in the current scout environment

## Disposition

**Retire as an independent fix.** #37093 head appears to have absorbed the behavior. Keep the regression as coverage-only material and re-check after the parent lands.