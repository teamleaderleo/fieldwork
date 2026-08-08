# Tauri authority, IPC, and lifecycle scout

Date: 2026-08-09

Fieldwork lane: #118  
Programme: #114  
Target: `tauri-apps/tauri`  
Pinned source: `34ec18ba5e1acabebd66ae79d6fc746f63d8eb96` (`dev`)  
Upstream contact authorized: `false`

## In simple words

Two candidates survived the first deep pass.

1. Tauri's Rust event manager runs user callbacks while its handler mutex is held. A caught callback panic can poison that mutex. Later `listen`, `unlisten`, and `emit` operations treat the poison result like ordinary lock contention, queue themselves, and can leave the manager silently unable to deliver future events. A focused regression and narrow panic-preserving repair are prepared against the pinned Tauri source.
2. Tauri's IPC fallback decides to switch transports after a side-effecting custom-protocol request may already have reached Rust. Navigation can make the frontend `fetch()` reject after dispatch, causing the same logical invoke to be resent over `postMessage`. A cleaner candidate is to select the transport with a side-effect-free probe before any command runs, then execute each command through one transport only.

The first candidate is compact Rust correctness work. The second is the stronger answer to the long-running reload/duplicate-invoke problem, but it needs WebView2 and WKWebView execution before implementation is promoted.

## Evidence class

- Tauri implementation, tests, history, current issues and pull requests: `source-read`.
- IPC transport-selection state-machine probe: `model-executed`; retained in `ipc-model-receipt-20260809.json`.
- Listener-panic regression and candidate patch: `target-test-prepared`.
- Listener-panic execution carrier run `31283181973`: queued on exact execution head `3427e21a6400314f662539cc0c15851cb3f15c49` at this handoff; no target-executed claim yet.
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

The Rust custom-protocol handler already has an `OPTIONS` branch that returns without calling `Webview::on_message`. That creates an existing side-effect-free probe boundary.

Candidate document-local state machine:

```text
first invoke(s)
  -> await one shared custom-protocol capability probe
  -> probe succeeds: choose custom protocol for this document
  -> probe fails: choose postMessage for this document
  -> dispatch command once through the selected transport
  -> command-level transport rejection never triggers cross-transport replay
```

This directly addresses the known fallback use case: CSP can block custom-protocol `fetch`, especially on externally loaded pages. It also removes dependence on `pagehide` / `beforeunload` ordering, which differs across Chromium and WebKit.

A bare `OPTIONS` request may fail to predict every platform's `POST` behavior. If platform testing disproves equivalence, the same design can use an internal side-effect-free probe request that traverses the exact custom-protocol POST path and is intercepted before command dispatch.

Android regular command IPC already uses `postMessage` because request bodies are unavailable through that custom-protocol path. Preserve its special channel-data behavior when testing this candidate.

## IPC model probe

Retained path: `probe/ipc_transport_model.mjs`  
Receipt: `ipc-model-receipt-20260809.json`  
Runtime: Node `v22.16.0`

The model compares current retry-after-failure semantics with transport selection before dispatch.

Observed:

```text
PASS normal: one custom-protocol dispatch
PASS CSP block: probe selects postMessage before command dispatch
PASS reload after dispatch: no cross-transport retry; Rust sees one command
PASS late transport break: invoke rejects instead of risking duplicate side effect
```

This proves only the state-machine property. It does not prove that WebView2 or WKWebView will treat the proposed probe exactly like the command POST.

## Rust event path

```text
emit_filter
  -> handlers.try_lock()
  -> lock held while filter and callback run
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

### Callback panic path

The handler map uses `std::sync::Mutex`. Both filter evaluation and user callbacks run under its guard.

```text
callback/filter panic
  -> MutexGuard drops during unwind
  -> handler mutex becomes poisoned
  -> later handlers.try_lock() returns Poisoned
  -> current code matches Err(_) as if lock were busy
  -> listen/unlisten/emit are appended to pending
  -> no successful handler-lock path remains to make normal progress
```

This appears absent from the current Tauri issue search.

A closely related filesystem scope manager uses an `emitting` flag plus a pending queue. That code was introduced to repair reentrant scope-event deadlocks. Its callback loop still runs under `event_listeners`, and a user panic skips the `emitting = false` transition while poisoning the listener mutex. Existing predecessor issue: `https://redirect.github.com/tauri-apps/tauri/issues/15468`.

## Listener panic probe

Question: after one Rust event callback panics and the caller catches the unwind, can the same event manager still register and deliver a different event?

Prepared regression:

1. register a callback that panics;
2. call `emit` inside `catch_unwind` and verify the panic propagated;
3. register a second event callback;
4. emit the second event;
5. require the second callback to run.

Prepared candidate:

- catch an unwind from filter/callback execution while the handler mutex guard remains owned outside the catch boundary;
- let the guard drop normally, avoiding mutex poisoning;
- flush pending reentrant actions, including `once` self-removal;
- resume the original panic with `resume_unwind`.

Retained artifacts:

- `probe/listener_panic_test.rs`
- `probe/candidate.patch`

The exact target workflow was created and then removed from the current branch after dispatch. Run `31283181973` remains queued against the execution head. Treat this candidate as prepared until an exact receipt exists.

## Ranked branch candidates

1. **IPC transport negotiation before side-effecting dispatch** — highest leverage. It removes the ambiguous retry boundary instead of guessing why a command-level fetch rejected. Next evidence: one WebView2 and one WKWebView fixture covering normal local page, CSP-blocked custom protocol, reload during a long-running command, and a command after successful negotiation.
2. **Core event callback panic recovery** — compact correctness candidate. Promote only after the prepared baseline fails for the intended assertion and the candidate passes while preserving the caller-visible panic.
3. **Filtered nested emit without public bound widening** — confirmed source defect with an awkward API constraint. Revisit callback ownership / lock lifetime after the panic candidate; avoid storing arbitrary public filter closures in the pending queue.
4. **Filesystem scope panic recovery** — likely sibling failure after the reentrant-deadlock repair. Give it its own regression after core event behavior is established.
5. **Runtime-wry native window/webview listener reentrancy and panic audit** — issue #15468 identified the same callback-under-lock family there. Map current dispatch sites before opening another candidate.

## Negative results and stops

- `pagehide` / `beforeunload` alone cannot serve as the cross-platform reload fix; observed ordering differs between WebView2 and WKWebView.
- Remembering that the custom protocol succeeded once leaves a later transport-failure ambiguity and can pin a document to a broken transport.
- Command-level retry after an ambiguous rejection cannot promise at-most-once side effects.
- Adding `Send + 'static` to `emit_filter` solely so the pending queue can own the closure widens an existing public contract.
- Existing asset multi-range and immediate JS-unlisten fixes are occupied work and stay outside this scout.
- No automated third-party upstream mutation was attempted or performed.

## Next transition

The best next execution is the IPC transport-selection fixture on Windows/WebView2 and macOS/WKWebView. It should make the current implementation and candidate lose on exact, predeclared cases: CSP failure before dispatch, reload after dispatch, and a later transport failure.

In parallel, consume run `31283181973` only when GitHub produces an exact receipt. If the listener baseline and candidate behave as predicted, add `once`-panic and filesystem-scope controls before preparing a human-facing patch packet.
