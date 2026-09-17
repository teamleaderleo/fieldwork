# Bun follow-up shortlist: small explicit leftovers

Fieldwork #709, Thread C follow-up pass. Rechecked and deepened 2026-08-09.

Automated upstream contact: **none**. All upstream repositories remain read-only.

## Selection rule

Keep candidates that are:

- explicitly left out of nearby active work;
- user-visible or independently testable;
- narrow enough to explain with one mechanism and one regression surface;
- not already owned or absorbed by another active PR when its **current head** is re-read.

That last rule is now important: one candidate below was present in a PR description and then silently absorbed by later commits on the same branch.

## 1. `Bun.Transpiler.scanImports()` misreports the key-after-spread JSX fallback

**Source breadcrumb:** https://redirect.github.com/oven-sh/bun/pull/35557

The active `autoImportJSX` PR aligns `.scan()` / `.scanImports()` for normal automatic-runtime JSX, while explicitly leaving one known inaccuracy: key-after-spread falls back to classic `createElement` from the bare JSX package, but scan-only can report the automatic runtime subpath.

Deep source read shows the scan parser already computes the exact `is_key_after_spread` condition that the full visitor later uses to select `JSXImport::CreateElement`. The missing piece is only retaining two dependency categories through scan finalization.

Fieldwork now has a proposed source patch pinned to #35557 head `2f2125e73a65cebef62c32c32acd3d114ac67e09`:

- `../proposed-patches/scanimports-key-after-spread.patch`
- `scanimports-key-after-spread.md`
- `../candidate-tests/scanimports-key-after-spread.test.ts`

The regression matrix covers fallback-only, normal JSX, fragments, mixed and nested mixed files, tsconfig/pragma `jsxImportSource`, runtime pragmas, and `autoImportJSX:false`.

**Disposition:** strongest current independent candidate. Source patch + prepared regression are ready for exact-target validation after #35557 settles.

## 2. WebSocket client TLS setup errors discard BoringSSL reason

**Source breadcrumb:** https://redirect.github.com/oven-sh/bun/pull/36149

The fetch TLS-error PR fixes bad client cert/key/passphrase reporting for direct fetch and proxy-tunnel fetch, then explicitly defers two WebSocket SSL-context construction sites. RoboBun acknowledged in the parent discussion that this needs a separate WebSocket/http_jsc change.

Deep source read pins both failures and the real transport constraint:

- `WebSocketProxyTunnel::start` collapses the failed SSL-context build to `InvalidOptions` without consuming the queued BoringSSL reason.
- Direct `WebSocketUpgradeClient::connect` returns only a pointer/null over FFI. When C++ receives null, `WebSocket.cpp` creates a fresh generic `Error("... Failed to connect")` and closes with 1006. A numeric WebSocket error code cannot carry an `ERR_OSSL_*` payload through that boundary.

Fieldwork now has a two-path prepared regression:

- `websocket-client-tls-error-fidelity.md`
- `../candidate-tests/websocket-client-tls-error-fidelity.test.ts`

The likely implementation needs a richer connect result/out-parameter for direct setup failure plus the same packed BoringSSL code transport for tunnel setup, reusing #36149's `take_boringssl_error` / error-formatting helpers.

**Disposition:** presentable medium candidate. Bug and tests are pinned; implementation should wait for #36149 because the remaining work is cross-language error transport, not error discovery.

## 3. `bun --hot` watcher leftovers

**Source breadcrumb:** https://redirect.github.com/oven-sh/bun/pull/36675

The active hot-reload memory PR explicitly leaves three watcher defects:

1. one 28-byte LSAN direct leak per reload in `Watcher::append_file_assume_capacity::<true>` / `to_vec()`;
2. one fd leaked per atomic rename-save of the entrypoint on Linux due to the `st_nlink` safety gate;
3. macOS/FreeBSD already-watched path drops an incoming fd, with ownership not yet proven.

Ownership searches found no separate PR/issue beyond the parent PR.

These remain attractive because the parent supplies concrete measurements and locations. They are not promoted yet: the 28-byte case wants sanitizer execution, and the rename case may require careful watch re-registration ordering.

**Disposition:** scout candidates requiring stronger execution evidence.

## Retired as independent work: synchronous `Bun.connect` errno

**Source breadcrumb:** https://redirect.github.com/oven-sh/bun/pull/37093

The #37093 description still says literal-IP synchronous failure surfaces generic `FailedToOpenSocket`. Its current head `36cb6413a17ad220ae91953f6217eb282c624f6b` now catches synchronous `do_connect()` failure in `connect_finish`, reads the platform socket error, preserves meaningful local-bind errnos such as `EADDRNOTAVAIL`, and routes them through `handle_connect_error`.

So the implementation we were preparing has been absorbed by the parent branch even though the description was not updated.

Fieldwork keeps the local-bind regression as coverage material:

- `literal-ip-connect-errno.md`
- `../candidate-tests/bun-connect-sync-errno.test.ts`

The visible #37093 test diff covers a different peer-close regression, so this test may still be useful after exact-target execution.

**Disposition:** no competing source patch. Re-check after #37093 lands; coverage-only candidate.

## Parked / lower value

### macOS `Bun.file(fifo).text()` late-writer hang

https://redirect.github.com/oven-sh/bun/pull/37090 explicitly leaves the Blob `ReadFile` path unfixed for `.text()` / `.bytes()` / `.json()`. It is real, but current proof and implementation depend on Darwin/kqueue behavior. Keep parked until a macOS execution lane is available.

### Worker-overhaul performance leftovers

The just-merged worker overhaul contains several explicit follow-ups. Ownership de-duplication eliminated UDP starvation (owned by https://redirect.github.com/oven-sh/bun/pull/37103) and found strong overlap for general thread-pool/file fairness (https://redirect.github.com/oven-sh/bun/pull/36479).

The apparently unowned leads are concurrent-worker peak RSS retention and the roughly 0.8x `worker_threads` MessagePort throughput regression. These are research leads, not small correctness candidates yet. See `worker-overhaul-leftovers.md`.

### FFI `cc.test.ts` ASAN cleanup

https://redirect.github.com/oven-sh/bun/pull/37116 says the new `leak:bun_ffi_cc` suppression may allow `test/js/bun/ffi/cc.test.ts` to drop old ASAN gates and whole-file leak-validation exclusion. Useful test-quality work, lower value than user-visible runtime discrepancies.

## Current order

1. `.scanImports()` key-after-spread JSX fallback — **proposed source patch + hardened test**;
2. WebSocket client TLS setup error fidelity — **design mapped + prepared direct/proxy test**;
3. watcher 28-byte leak / atomic-rename fd leak — **needs sanitizer/platform proof**;
4. macOS FIFO Blob consumer — **needs Darwin execution**;
5. worker RSS / MessagePort performance probes — **larger research**;
6. FFI ASAN cleanup — **test-quality follow-up**.

Separate from this Thread C shelf, the Request GET/HEAD constructor-precedence candidate remains a strong prepared compatibility item coordinated with https://redirect.github.com/oven-sh/bun/pull/37033.