# Tauri authority, IPC, and lifecycle scout

Date: 2026-08-09

Fieldwork lane: #118  
Programme: #114  
Target: `tauri-apps/tauri`  
Pinned source: `34ec18ba5e1acabebd66ae79d6fc746f63d8eb96` (`dev`)  
Upstream contact authorized: `false`

## In simple words

Two strong candidates and two adjacent event-lifecycle gaps survived the deep pass.

1. Tauri's Rust event manager runs user callbacks while its handler mutex is held. A callback panic poisons that mutex. If the caller catches the panic, later `listen`, `unlisten`, and `emit` operations mistake the poisoned result for ordinary contention, queue themselves, and stop making progress. This now reproduces on the pinned Tauri source. A narrow catch/flush/resume candidate preserves the original panic and passes the same later-dispatch regression in two corrected Linux executions.
2. Tauri's IPC fallback decides to switch transports after a side-effecting custom-protocol request may already have reached Rust. Navigation can make the frontend `fetch()` reject after dispatch, causing the same logical invoke to be resent over `postMessage`. A cleaner candidate is to negotiate the transport with a side-effect-free `HEAD` request before any command runs, then execute each command through one transport only.
3. Public `emit_filter` has a second panic/reentrancy boundary before the Rust handler map: the JS-listener filter path holds `js_event_listeners` while running the user-supplied filter. A filter panic can poison that mutex, so the verified callback-panic patch must not be described as general filter-panic recovery.
4. Filesystem `Scope` uses a related callback-under-lock plus `emitting` flag design. A callback panic can skip `emitting = false` and poison `event_listeners`. This looks like a sibling invariant gap after the merged reentrant-deadlock repair and deserves its own regression.

The verified Rust callback candidate is compact correctness work. The IPC candidate is the higher-leverage answer to the long-running reload/duplicate-invoke problem, but it still needs WebView2 and WKWebView execution before implementation is promoted.

## Evidence class

- Tauri implementation, tests, history, current issues and pull requests: `source-read`.
- IPC transport-selection state-machine probe: `model-executed`; retained in `ipc-model-receipt-20260809.json`.
- IPC `HEAD` negotiation candidate patch: `target-test-prepared`.
- Core Rust listener callback-panic baseline and candidate: `target-executed` on a focused Linux regression; retained in `listener-execution-receipt-20260809.json`.
- First listener execution attempt, run `31283181973`: invalid harness evidence; retained in `listener-execution-invalid-20260809.json` and excluded from the target claim.
- Public `emit_filter` JS-filter panic/reentrancy seam: `source-read` only.
- Filesystem `Scope` callback-panic seam: `source-read` only.
- Owned application / WebView2 / WKWebView execution: absent.

## Code map

### IPC reload path

```text
frontend invoke
  -> random success/error callback ids
  -> custom-protocol fetch
  -> Rust parses request
  -> Webview::on_message dispatches command
  -> navigation may abort frontend fetch
  -> rejection handler marks custom protocol failed
  -> same message is resent over postMessage
  -> Rust dispatches again
```

Relevant target files:

- `crates/tauri/scripts/core.js`
- `crates/tauri/scripts/ipc-protocol.js`
- `crates/tauri/src/ipc/protocol.rs`
- `crates/tauri/src/webview/mod.rs`

Current issue context: `https://redirect.github.com/tauri-apps/tauri/issues/14154`.

The callback and error ids are generated as random `u32` values per document. The fallback reuses the same message and therefore the same pair. Backend deduplication is possible in principle, but it would need response handoff, expiry, document identity, and collision handling. It is heavier than preventing ambiguous cross-transport retry in the first place.

### Side-effect-free transport selection

Tauri's Rust IPC custom-protocol handler dispatches a command only for `POST`. `OPTIONS` handles preflight without calling `Webview::on_message`; every other method returns `405 Method Not Allowed` through the normal response wrapper, which adds the CORS origin/exposed-header response fields.

That makes `HEAD` useful as a probe:

- `HEAD` is a CORS-safelisted method, like the real `POST`;
- the probe can carry the same Tauri IPC headers and content type, exercising the relevant unsafe-header preflight path;
- Tauri returns `405` without command dispatch, and `fetch()` still receives a normal response rather than a network error when the custom protocol/CSP/CORS path is usable;
- CSP `connect-src` applies to the probe just as it applies to the command fetch.

Candidate document-local state machine:

```text
first invoke(s)
  -> await one shared HEAD capability probe carrying the IPC headers
  -> probe resolves: choose custom protocol for this document
  -> probe rejects: choose postMessage for this document
  -> dispatch command once through the selected transport
  -> if a later custom-protocol command rejects:
       reject that invoke; mark custom protocol blocked for future invokes
  -> future invokes use postMessage
```

The key rule is that a command-level rejection never triggers replay of the same command over a second transport. Once a side-effecting `POST` may have reached Rust, the caller gets the failure and the next invoke can recover through `postMessage`.

This directly addresses the known fallback use case: CSP can block custom-protocol `fetch`, especially on externally loaded pages. It also removes dependence on `pagehide` / `beforeunload` ordering, which differs across Chromium and WebKit.

The public invoke API permits custom request headers. A later header profile can still make a previously usable custom transport fail. Under this candidate, that one invoke rejects without duplicate side effects and flips subsequent calls to `postMessage`; it does not replay the ambiguous call.

Android regular command IPC already uses `postMessage` because request bodies are unavailable through that custom-protocol path. The candidate keeps the existing special channel-data custom-protocol fallback separate.

Prepared patch: `probe/ipc-head-negotiation.patch`.

## IPC model probe

Retained path: `probe/ipc_transport_model.mjs`  
Receipt: `ipc-model-receipt-20260809.json`  
Runtime: Node `v22.16.0`

The model compares current retry-after-failure semantics with transport selection before dispatch.

Observed:

```text
PASS normal: one custom-protocol dispatch
PASS CSP block: HEAD probe selects postMessage before command dispatch
PASS reload after dispatch: no cross-transport retry; Rust sees one command
PASS late transport break: invoke rejects instead of risking duplicate side effect
```

This proves only the state-machine property. It does not prove that WebView2 or WKWebView will treat the proposed `HEAD` + IPC-header probe as a reliable predictor for the later `POST`.

## Rust event path

```text
emit_filter
  -> handlers.try_lock()
  -> lock held while Rust handler filter and callback run
       -> nested listen/unlisten/emit cannot lock
       -> nested action enters pending queue
  -> callback returns
  -> pending queue flushes
```

Relevant target files:

- `crates/tauri/src/event/listener.rs`
- `crates/tauri/src/manager/mod.rs`
- `crates/tauri/src/lib.rs`

Current `Pending::Emit` stores only `EmitArgs`. If a filtered emit is deferred, replay goes through plain `emit()`, dropping the filter. Existing issue context: `https://redirect.github.com/tauri-apps/tauri/issues/15759`.

The public `Emitter::emit_filter` closure has no `Send` or `'static` bound. A previous repair attempted to store the closure in the pending queue by widening those public bounds. That path is a poor fit for the existing API.

### Rust callback panic path

The Rust handler map uses `std::sync::Mutex`, and user callbacks run under its guard.

```text
callback panic
  -> MutexGuard drops during unwind
  -> handler mutex becomes poisoned
  -> later handlers.try_lock() returns Poisoned
  -> current code matches Err(_) as if lock were busy
  -> listen/unlisten/emit are appended to pending
  -> no successful handler-lock path remains to make normal progress
```

This appears absent from the current Tauri issue search.

### Public filter path is a separate boundary

Public `Emitter::emit_filter` routes through the manager in this order:

```text
manager.emit_filter
  -> listeners.emit_js_filter(..., &filter)
       -> js_event_listeners.lock().unwrap()
       -> user filter runs while JS-listener mutex is held
  -> listeners.emit_filter(..., &filter)
       -> Rust handler mutex path
```

Consequences from source reading:

- a user filter panic can poison `js_event_listeners` before the verified Rust callback-panic candidate is reached;
- later JS listener operations use `.lock().unwrap()` and can panic on that poisoned mutex;
- the same public filter is evaluated across two distinct lock domains;
- a reentrant call from the filter back into JS-event emission may attempt to acquire `js_event_listeners` again while it is already held, so reentrancy deserves its own executable probe.

Do not roll this into the verified callback claim without a separate test and repair boundary.

### Filesystem scope sibling

Filesystem `Scope::emit` has its own `event_listeners` mutex, an atomic `emitting` flag, and a pending-event queue. The current path sets `emitting = true`, invokes user listeners while holding `event_listeners`, then clears `emitting` and drains pending work.

If a listener panics, unwind skips the clear and poisons the listener mutex. A caller that catches the panic can therefore leave the scope permanently in its “already emitting” state while future operations accumulate in the pending queue or encounter the poisoned lock.

The emitting/pending mechanism was added by the merged repair for the reentrant scope-event deadlock tracked at `https://redirect.github.com/tauri-apps/tauri/issues/15468`. Its regression covers reentrancy/deadlock. Panic cleanup is a distinct invariant and currently has no matching open issue in the search performed for this scout.

## Listener panic probe

Question: after one Rust event callback panics and the caller catches the unwind, can the same event manager still register and deliver a different event?

Regression:

1. register a callback that panics;
2. call `emit` inside `catch_unwind` and verify the panic propagated;
3. register a second event callback;
4. emit the second event;
5. require the second callback to run.

Candidate:

- catch the callback unwind while the handler mutex guard remains owned outside the catch boundary;
- let the guard drop normally, avoiding mutex poisoning;
- flush pending reentrant actions, including `once` self-removal;
- resume the original panic with `resume_unwind`.

Retained artifacts:

- `probe/listener_panic_test.rs`
- `probe/candidate.patch`
- `listener-execution-receipt-20260809.json`
- `listener-execution-invalid-20260809.json`

### Corrected target execution

Pinned target: `34ec18ba5e1acabebd66ae79d6fc746f63d8eb96`  
Runner: Ubuntu 24.04.4 x86_64  
Rust: `rustc 1.97.1 (8bab26f4f 2026-07-14)`  
Cargo: `cargo 1.97.1 (c980f4866 2026-06-30)`  
Command: `cargo test -p tauri --lib --no-default-features listener_panic_does_not_stall_future_events -- --nocapture`

Primary corrected run `31284095629`:

- baseline exited `101` and matched the intended assertion `event manager stopped dispatching after callback panic`;
- candidate patch applied successfully;
- candidate test exited `0`.

Independent confirmation run `31284174704` repeated the comparison:

- baseline printed the intentional callback panic, then failed on the exact post-panic stall assertion;
- candidate printed the same intentional panic, showing the unwind still reached the test's `catch_unwind`, then delivered the later event and passed `1/1` focused tests (`57` filtered out).

Evidence class for this exact callback-panic/later-delivery claim is now `target-executed`. It is a focused Linux result, not a full Tauri gate and not proof of public filter-panic recovery.

The first execution attempt `31283181973` is retained only as invalid harness evidence. Its baseline ran Cargo from the Fieldwork root rather than the Tauri checkout; its candidate stopped at a malformed retained-patch hunk. Neither old job contributes to the target claim.

## Ranked branch candidates

1. **IPC `HEAD` transport negotiation before side-effecting dispatch** — highest leverage. It removes the ambiguous retry boundary instead of guessing why a command-level fetch rejected. Next evidence: one WebView2 and one WKWebView fixture covering local page, CSP-blocked custom protocol, external page, custom invoke headers, reload during a long-running command, binary channel traffic, and recovery after a post-negotiation transport failure.
2. **Core Rust event callback panic recovery** — reproduced and candidate-validated on the focused Linux regression. Next controls: a panicking `once` callback, ordinary reentrant `listen`/`unlisten`, and the crate's broader relevant test set before any human-facing patch packet is called ready.
3. **Public `emit_filter` JS-listener panic/reentrancy** — source-supported separate lock boundary. Add a focused executable probe before choosing a repair; do not widen the verified callback patch by assumption.
4. **Filtered nested emit without public bound widening** — confirmed source defect with an awkward API constraint. Revisit callback ownership / lock lifetime after the panic candidate; avoid storing arbitrary public filter closures in the pending queue.
5. **Filesystem `Scope` callback panic recovery** — likely sibling failure after the reentrant-deadlock repair. Give it its own baseline/candidate regression rather than bundling it into the core event patch.
6. **Runtime-wry native window/webview listener reentrancy and panic audit** — the same callback-under-lock family has appeared in adjacent runtime paths. Map current dispatch sites before opening another candidate.

## Negative results and stops

- `pagehide` / `beforeunload` alone cannot serve as the cross-platform reload fix; observed ordering differs between WebView2 and WKWebView.
- Remembering that the custom protocol succeeded once leaves a later transport-failure ambiguity and can pin a document to a broken transport.
- Command-level retry after an ambiguous rejection cannot promise at-most-once side effects.
- A user-issued `OPTIONS` capability probe is less attractive than `HEAD`: `OPTIONS` is not a CORS-safelisted method, while `HEAD` and the real `POST` are.
- Adding `Send + 'static` to `emit_filter` solely so the pending queue can own the closure widens an existing public contract.
- The verified core callback patch does not repair the separate `js_event_listeners` filter-panic boundary.
- Existing asset multi-range and immediate JS-unlisten fixes are occupied work and stay outside this scout.
- No automated third-party upstream mutation was attempted or performed.

## Next transition

The highest-value execution remains the `HEAD` transport-selection fixture on Windows/WebView2 and macOS/WKWebView. It should compare current and candidate behavior on predeclared cases: CSP failure before dispatch, external-page custom protocol, additional invoke headers, reload after dispatch, channel traffic, and a later transport failure.

For the event family, run a `once`-panic control against the now-validated core candidate, then give the public-filter JS mutex seam and filesystem `Scope` panic seam separate regressions. Promote only the exact invariants those probes establish.
