# Bun follow-up shortlist: small explicit leftovers

Fieldwork #709, Thread C follow-up pass. Rechecked 2026-08-09.

Automated upstream contact: **none**. All upstream repositories remain read-only.

## Selection rule

Keep candidates that are:

- explicitly left out of nearby active work;
- user-visible or independently testable;
- narrow enough to explain with one mechanism and one regression surface;
- not already owned by another open PR/issue found in the first ownership search.

## 1. Literal-IP `Bun.connect` synchronous failure loses errno

**Source breadcrumb:** https://redirect.github.com/oven-sh/bun/pull/37093

The active connect-error-fidelity PR explicitly leaves one gap: a literal-IP connect that fails synchronously reaches the Rust boundary with the errno intact, then surfaces to JavaScript as generic `FailedToOpenSocket`.

First ownership search for `FailedToOpenSocket` + connect-error terms found no separate open PR owning this literal-IP case; the only direct match was the parent PR itself (plus unrelated `FailedToOpenSocket` work in other subsystems).

Why retain:

- direct user-visible diagnostic loss;
- parent PR already did the hard errno-preservation work around it;
- expected implementation is likely at the Rust/JS error conversion boundary;
- should admit an exact literal-IP regression test.

**Disposition:** highest-priority independent survivor. Prepare after https://redirect.github.com/oven-sh/bun/pull/37093 stabilizes or lands.

## 2. WebSocket client TLS setup errors discard BoringSSL reason

**Source breadcrumb:** https://redirect.github.com/oven-sh/bun/pull/36149

The fetch TLS-error PR fixes bad client cert/key/passphrase reporting for direct fetch and proxy-tunnel fetch, then explicitly defers the two WebSocket SSL-context construction sites. Those sites currently have an event-based error surface, so the follow-up needs an `http_jsc` error variant / mapping instead of reusing the fetch promise path unchanged.

Ownership searches for WebSocket + `ERR_OSSL` + client-cert terms found no separate open PR or issue.

Why retain:

- same proven root bug as an active fix, on two named sibling call sites;
- real user-facing configuration errors currently collapse into generic connection behavior;
- bounded implementation map is already supplied by the parent PR.

**Disposition:** strong second candidate. Wait for https://redirect.github.com/oven-sh/bun/pull/36149 to settle, then source-read the two WebSocket sites and prepare a small error-fidelity regression.

## 3. `Bun.Transpiler.scanImports()` misreports the key-after-spread JSX fallback

**Source breadcrumb:** https://redirect.github.com/oven-sh/bun/pull/35557

The active `autoImportJSX` PR aligns `.scan()` / `.scanImports()` for normal automatic-runtime JSX, while explicitly leaving one known inaccuracy: the deprecated key-after-spread `createElement` fallback imports from the bare package, but the scan pass has no per-symbol use counts and can still report the runtime subpath.

Searches for `scanImports` + `createElement` found no separate open issue and only the parent PR among open PRs.

Why retain:

- observable API mismatch in dependency scanning;
- precise triggering syntax and expected import source are already known;
- likely parser/test-local if a cheap fallback signal can be retained during scan.

Risk:

- the parent PR says the missing information is per-symbol use counts; a naive fix could broaden parser bookkeeping for a niche deprecated fallback.

**Disposition:** scout next, do not assume it is tiny until the scan/full-parse state boundary is mapped. Wait for https://redirect.github.com/oven-sh/bun/pull/35557 to settle.

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

**Disposition:** keep both as scout candidates; prefer the 28-byte leak only with exact ASAN/LSAN access, prefer the atomic-rename fd case if the watcher re-registration seam is already reusable after the parent PR lands.

## Parked / lower value

### macOS `Bun.file(fifo).text()` late-writer hang

https://redirect.github.com/oven-sh/bun/pull/37090 explicitly leaves the Blob `ReadFile` path unfixed for `.text()` / `.bytes()` / `.json()`. It is a real independent bug, but current proof and implementation depend on Darwin/kqueue behavior. Keep parked until a macOS execution lane is available.

### FFI `cc.test.ts` ASAN cleanup

https://redirect.github.com/oven-sh/bun/pull/37116 says the new `leak:bun_ffi_cc` suppression may allow `test/js/bun/ffi/cc.test.ts` to drop old ASAN gates and whole-file leak-validation exclusion. This is test-quality work, and the PR also notes a separate open effort around FFI wrapper finalization. Keep below runtime/user-visible candidates.

## Current order

1. literal-IP `Bun.connect` errno fidelity;
2. WebSocket client TLS setup error fidelity;
3. `.scanImports()` key-after-spread JSX fallback;
4. watcher 28-byte leak / atomic-rename fd leak;
5. macOS FIFO Blob consumer;
6. FFI ASAN cleanup.

The first two fit the same successful pattern as the Request candidate: an active PR identifies and proves the surrounding bug class, names one adjacent case it deliberately leaves alone, and no separate owner is visible yet.