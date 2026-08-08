# Bun follow-up shortlist: small explicit leftovers

Fieldwork #709, Thread C follow-up pass. Rechecked and deepened 2026-08-09.

Automated upstream contact: **none**. All upstream repositories remain read-only.

## Selection rule

Keep candidates that are:

- explicitly left out of nearby active work;
- user-visible or independently testable;
- narrow enough to explain with one mechanism and one regression surface;
- not already owned by another open PR/issue found in the ownership search.

## 1. Literal-IP `Bun.connect` synchronous failure loses errno

**Source breadcrumb:** https://redirect.github.com/oven-sh/bun/pull/37093

The active connect-error-fidelity PR explicitly leaves one gap: a literal-IP connect that fails synchronously surfaces as generic `FailedToOpenSocket` even though the native failure has a real errno.

Deep source read sharpened the mechanism: `src/uws_sys/SocketGroup.rs` turns a null `us_socket_group_connect(...)` result into payload-less `ConnectResult::Failed`; `socket_body.rs` then maps that variant directly to `FailedToOpenSocket`. The errno is therefore discarded at the C/Rust wrapper boundary, before the JS error builder has a chance to preserve it.

The later asynchronous connect-error path already has the desired Node-style mapping for errors such as `EADDRNOTAVAIL`, so the likely fix is to make the synchronous failure variant carry the captured platform socket errno and reuse that mapping.

A prepared regression uses a live `127.0.0.1` destination plus `localAddress: "1.2.3.4"`, the invalid local address used by Bun's vendored Node local-bind test, and expects `EADDRNOTAVAIL` / `syscall: "connect"` instead of `FailedToOpenSocket`.

See:

- `literal-ip-connect-errno.md`
- `../candidate-tests/bun-connect-sync-errno.test.ts`

**Disposition:** highest-priority independent survivor. Prepare on top of https://redirect.github.com/oven-sh/bun/pull/37093 after it stabilizes or lands.

## 2. `Bun.Transpiler.scanImports()` misreports the key-after-spread JSX fallback

**Source breadcrumb:** https://redirect.github.com/oven-sh/bun/pull/35557

The active `autoImportJSX` PR aligns `.scan()` / `.scanImports()` for normal automatic-runtime JSX, while explicitly leaving one known inaccuracy: key-after-spread falls back to classic `createElement` from the bare JSX package, but scan-only can report the automatic runtime subpath.

Deep source read makes this look smaller than the parent prose initially suggests. The scan-only JSX parser already computes the exact `is_key_after_spread` condition and sets `JSXElement::IsKeyAfterSpread`; the full visitor later checks that same flag and routes the element through `JSXImport::CreateElement`.

The parent PR's own transform test proves the expected dependency for:

```tsx
<div {...obj} key="after" />
```

is bare `react`, while its scan-finalization logic blindly emits `react/jsx-dev-runtime` for any JSX under the dev automatic runtime.

This likely needs only separate scan bookkeeping for automatic-runtime JSX versus classic-fallback JSX. A mixed file must be able to report both dependencies.

See:

- `scanimports-key-after-spread.md`
- `../candidate-tests/scanimports-key-after-spread.test.ts`

**Disposition:** promoted to strong second candidate. Wait for https://redirect.github.com/oven-sh/bun/pull/35557 to settle, then keep the implementation parser-local; demote if it starts requiring visitor execution or broad symbol-use reconstruction.

## 3. WebSocket client TLS setup errors discard BoringSSL reason

**Source breadcrumb:** https://redirect.github.com/oven-sh/bun/pull/36149

The fetch TLS-error PR fixes bad client cert/key/passphrase reporting for direct fetch and proxy-tunnel fetch, then explicitly defers two WebSocket SSL-context construction sites.

Deep source read confirms one direct collapse:

`WebSocketProxyTunnel::start` maps `SslWrapper::init_from_options(...)` failure immediately to `InvalidOptions`, losing the queued BoringSSL reason. The direct/upgrade client path builds or retrieves its SSL context during `WebSocketUpgradeClient::connect` but its setup contract has no rich error carrier back to the WebSocket event boundary.

The native error capture is already proven by #36149. The extra work here is defining and threading a WebSocket/http_jsc error variant so the `error` event can carry `ERR_OSSL_*` diagnostics without changing handshake/close ordering.

See `websocket-client-tls-error-fidelity.md`.

**Disposition:** retain as a medium-small third candidate. Build on #36149's BoringSSL helper after that PR settles.

## 4. `bun --hot` watcher leftovers

**Source breadcrumb:** https://redirect.github.com/oven-sh/bun/pull/36675

The active hot-reload memory PR explicitly leaves three watcher defects:

1. one 28-byte LSAN direct leak per reload in `Watcher::append_file_assume_capacity::<true>` / `to_vec()`;
2. one fd leaked per atomic rename-save of the entrypoint on Linux due to the `st_nlink` safety gate;
3. macOS/FreeBSD already-watched path drops an incoming fd, with ownership not yet proven.

Exact-search ownership checks for the 28-byte path and `leaks one fd per save` found no separate PR/issue beyond the parent PR.

Why retain:

- unusually concrete measurements and locations;
- the Linux fd leak is operationally more meaningful than the 28-byte allocation;
- the 28-byte leak may be a very small ownership bug if LSAN execution is available.

Risk:

- the atomic-rename fd repair needs watch re-registration ordering, so it may stop being small once followed through;
- the 28-byte leak needs sanitizer execution to avoid guessing about `Cow` ownership.

**Disposition:** keep as scout candidates; do not promote without the needed sanitizer/platform evidence.

## Parked / lower value

### macOS `Bun.file(fifo).text()` late-writer hang

https://redirect.github.com/oven-sh/bun/pull/37090 explicitly leaves the Blob `ReadFile` path unfixed for `.text()` / `.bytes()` / `.json()`. It is a real independent bug, but current proof and implementation depend on Darwin/kqueue behavior. Keep parked until a macOS execution lane is available.

### FFI `cc.test.ts` ASAN cleanup

https://redirect.github.com/oven-sh/bun/pull/37116 says the new `leak:bun_ffi_cc` suppression may allow `test/js/bun/ffi/cc.test.ts` to drop old ASAN gates and whole-file leak-validation exclusion. This is test-quality work, and the PR also notes a separate open effort around FFI wrapper finalization. Keep below runtime/user-visible candidates.

### Worker-overhaul performance leftovers

The just-merged worker overhaul contains several explicit follow-ups. Ownership de-duplication already eliminated UDP starvation (owned by https://redirect.github.com/oven-sh/bun/pull/37103) and found strong overlap for general thread-pool/file fairness (https://redirect.github.com/oven-sh/bun/pull/36479).

The apparently unowned leads are concurrent-worker peak RSS retention and the roughly 0.8x `worker_threads` MessagePort throughput regression. These are research leads, not small correctness candidates yet. See `worker-overhaul-leftovers.md`.

## Current order

1. literal-IP `Bun.connect` synchronous errno fidelity;
2. `.scanImports()` key-after-spread JSX fallback;
3. WebSocket client TLS setup error fidelity;
4. watcher 28-byte leak / atomic-rename fd leak;
5. macOS FIFO Blob consumer;
6. worker RSS / MessagePort performance probes;
7. FFI ASAN cleanup.

The top three now all have a concrete source seam. The first two also have prepared regression tests.