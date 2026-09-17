# Refined Bun compatibility candidate packet

Fieldwork #709. Prepared 2026-08-09.

Automated upstream contact: **none**. All Bun work in this packet is read-only source research plus Fieldwork-owned prepared material.

## What survived refinement

### A. Presentable source patch: `Bun.Transpiler.scanImports()` JSX fallback fidelity

Parent: https://redirect.github.com/oven-sh/bun/pull/35557  
Pinned head: `2f2125e73a65cebef62c32c32acd3d114ac67e09`

Problem:

```tsx
export default <div {...obj} key="after" />;
```

The parent's full transform correctly falls back to `createElement` and imports the bare package (`react` by default), while scan-only reports the automatic runtime subpath (`react/jsx-dev-runtime` in development).

Why the fix is small:

- scan parsing already computes the exact key-after-spread condition;
- the full visitor already uses that same condition to select `createElement`;
- scan only needs to retain two dependency categories: automatic-runtime JSX and classic-fallback JSX.

Prepared material:

- `scanimports-key-after-spread.md`
- `../proposed-patches/scanimports-key-after-spread.patch`
- `../candidate-tests/scanimports-key-after-spread.test.ts`

The proposed patch changes three parser files and adds focused tests to the parent's existing transpiler test block. The broader Fieldwork matrix covers fragments, nested mixed JSX, runtime/import-source pragmas, custom `jsxImportSource`, and opt-out behavior.

Evidence:

- implementation seam: `source-read`
- proposed patch: `source-read`
- regression matrix: `target-test-prepared`
- exact Bun execution: pending

**Assessment:** strongest current independent contribution candidate.

---

### B. Presentable design + regression: WebSocket client TLS setup diagnostics

Parent: https://redirect.github.com/oven-sh/bun/pull/36149  
Pinned head: `96c737581f4d6faeded91ee254c59ed3d680b692`

The parent fixes `ERR_OSSL_*` fidelity for fetch and explicitly defers two WebSocket sibling sites. RoboBun acknowledged the WebSocket work as a separate follow-up.

Two failure sites:

1. `WebSocketProxyTunnel::start`: failed SSL-context creation is collapsed to `InvalidOptions`; the BoringSSL error queue is discarded.
2. Direct `WebSocketUpgradeClient::connect`: failed SSL-context creation returns a null pointer over FFI. `WebSocket.cpp` sees null and manufactures a generic `Error("... Failed to connect")` before closing with 1006.

The second point defines the real implementation work: a numeric WebSocket error enum cannot carry the packed BoringSSL reason. The direct connect ABI needs a richer error payload/out-parameter (or an equivalent single-shot richer failure callback), and tunnel setup needs to carry the same packed code to the C++ error-event boundary.

Prepared material:

- `websocket-client-tls-error-fidelity.md`
- `../candidate-tests/websocket-client-tls-error-fidelity.test.ts`

The test covers direct `wss://` and the HTTP CONNECT tunnel site with mismatched cert/key material. It requires one error event whose `event.error.code` is `ERR_OSSL_X509_KEY_VALUES_MISMATCH`, while preserving abnormal close 1006 / `wasClean === false`.

Evidence:

- root cause / transport boundary: `source-read`
- direct + proxy regression: `target-test-prepared`
- exact Bun execution: pending

**Assessment:** good follow-up, medium-sized because of Rust/C++ error transport. Wait for #36149's helpers to settle before preparing implementation.

---

### C. Retired implementation candidate, retained coverage: synchronous `Bun.connect` errno

Parent: https://redirect.github.com/oven-sh/bun/pull/37093  
Pinned recheck head: `36cb6413a17ad220ae91953f6217eb282c624f6b`

The PR description still calls literal-IP synchronous failure a remaining `FailedToOpenSocket` gap. Current head code now catches synchronous `do_connect()` failure, reads the platform socket error, preserves local-bind errors such as `EADDRNOTAVAIL`, and routes them through the existing `handle_connect_error` path.

So the implementation was absorbed into the parent branch while its description stayed stale.

Prepared material retained only as coverage:

- `literal-ip-connect-errno.md`
- `../candidate-tests/bun-connect-sync-errno.test.ts`

The parent visible test diff covers a different false-`ECONNRESET` peer-close case, so the local-bind test may still add useful coverage if it passes against the eventual landed code.

**Assessment:** do not compete with the parent. This is also a useful demonstration that breadcrumb mining must re-read current head code before turning prose into a new contribution.

---

## Other shelf items

- `Request` GET/HEAD constructor body precedence remains a strong prepared compatibility candidate coordinated with https://redirect.github.com/oven-sh/bun/pull/37033.
- `bun --hot` 28-byte reload leak / atomic-rename fd leak remain interesting but need LSAN or platform-specific proof before promotion.
- macOS FIFO Blob consumer remains parked for Darwin execution.
- worker peak-RSS / MessagePort throughput leftovers are larger performance investigations.

## Recommended internal order

1. Treat the JSX patch as the next exact-target validation candidate once #35557 settles.
2. Keep refining the WebSocket ABI/error-carrier design while #36149 is active; do not code against helpers that may still move.
3. Re-run the `Bun.connect` coverage test after #37093 lands; only reopen implementation work if the landed code differs from its current head.
4. Keep the Request patch/test packet warm behind #37033.

No upstream comment or PR is needed from this packet today.