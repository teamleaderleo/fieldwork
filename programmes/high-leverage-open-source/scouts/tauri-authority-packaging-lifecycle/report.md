# Tauri authority, IPC, and lifecycle scout

Date: 2026-08-09

Fieldwork lane: #118  
Programme: #114  
Target: `tauri-apps/tauri`  
Pinned source: `34ec18ba5e1acabebd66ae79d6fc746f63d8eb96` (`dev`)  
Upstream contact authorized: `false`

## In simple words

Two lifecycle boundaries are worth pushing.

First, Tauri's custom-protocol IPC can already have dispatched a Rust command when navigation makes the frontend `fetch()` reject. The frontend then interprets the rejection as transport failure and retries the same logical invoke over `postMessage`. WebView2 and WKWebView order navigation teardown differently, so page-lifecycle flags haven't produced one cross-platform answer.

Second, Tauri's Rust event manager invokes user callbacks while its handler mutex is held. Reentrant event operations are deferred through a pending queue. That design already loses `emit_filter` semantics on the deferred path. A callback panic exposes a second failure mode: unwinding poisons the handler mutex, and later `try_lock()` calls classify poison the same way as ordinary contention and keep queuing work. A closely related filesystem scope event manager keeps an `emitting` flag set across callbacks, so a callback panic can leave that flag set as well.

The first executable probe targets the panic case because it is platform-independent, bounded, and currently appears unreported. The IPC branch remains active research until we can distinguish transport failure from post-dispatch navigation on both Chromium and WebKit.

## Evidence class

- Tauri implementation, tests, history, current issues and pull requests: `source-read`.
- Maintainer-reported WebView2/WKWebView ordering: `Documented` upstream context; no Fieldwork platform execution yet.
- Listener-panic regression: `target-test-prepared`; execution carrier attached to this scout.
- Owned application execution: absent.

## Code map

### IPC reload path

```text
frontend invoke
  -> random callback/error ids
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

The callback and error ids are generated as random `u32` values per document. Both transports carry those same ids for a fallback of the same invoke. This gives the backend a potential logical-request identity, but cross-document collision and stale-response behavior must be handled before treating those ids as a durable deduplication key.

Current issue context: `https://redirect.github.com/tauri-apps/tauri/issues/14154`.

### Rust event path

```text
emit_filter
  -> handlers.try_lock()
  -> lock held while callback runs
       -> nested listen/unlisten/emit can't lock
       -> nested action enters pending queue
  -> callback returns
  -> pending queue flushes
```

Relevant target files:

- `crates/tauri/src/event/listener.rs`
- `crates/tauri/src/manager/mod.rs`
- `crates/tauri/src/lib.rs`

Current `Pending::Emit` stores only `EmitArgs`. If filtered emit is deferred, replay goes through plain `emit()`, dropping the filter. Existing issue context: `https://redirect.github.com/tauri-apps/tauri/issues/15759`.

The public `Emitter::emit_filter` closure has no `Send` or `'static` bound. A prior repair tried storing the filter in the pending queue by adding those bounds; it was closed. A nonbreaking answer therefore needs a different ownership boundary.

### Callback panic path

The handler mutex is a `std::sync::Mutex`. `emit_filter` holds its guard across each user callback. If a callback unwinds:

```text
callback panic
  -> MutexGuard drops during unwind
  -> handler mutex becomes poisoned
  -> later handlers.try_lock() returns Poisoned
  -> code matches Err(_) as if lock were busy
  -> listen/unlisten/emit are appended to pending
  -> no successful emit remains to flush them
```

The handler map itself is not being mutated by the callback loop; reentrant map changes are redirected to the separate pending queue. That makes catching the callback panic inside the lock lifetime, dropping the lock normally, flushing pending actions, then resuming the same panic a plausible narrow repair.

A sibling implementation in `crates/tauri/src/scope/fs.rs` uses `AtomicBool emitting` plus a pending queue to prevent reentrant deadlock. Its callback loop also runs under a mutex, and a user panic skips `emitting.store(false, ...)`, giving us a second candidate after the core event probe is settled.

## First probe

Question: after one Rust event callback panics and the caller catches the unwind, can the same event manager still register and deliver a different event?

Expected invariant: callback panic propagates to the caller, while unrelated future event operations remain usable.

Baseline test:

1. register a callback that panics;
2. call `emit` inside `catch_unwind` and verify the panic propagated;
3. register a second event callback;
4. emit the second event;
5. require the second callback to run.

Current source predicts step 5 fails because the poisoned handler mutex is treated as contention and both later actions are only queued.

Candidate repair under test: catch callback unwind while the handler guard remains owned outside the catch boundary, let the guard drop normally, flush pending reentrant actions, then `resume_unwind` with the original panic payload.

## IPC hypotheses still open

H1 — page lifecycle is sufficient. Weakened: maintainers report the ordering works on current WebView2 and fails on WKWebView.

H2 — successful-custom-protocol memory is sufficient. Partial mitigation only: the very first invoke after a document load can still be duplicated.

H3 — callback/error ids can identify a fallback retry at the Rust boundary. Plausible: both transports preserve them. Needs a document-generation or stronger request identity so a new page cannot collide with an old in-flight call.

H4 — an explicit transport acknowledgment before command execution can remove the ambiguity. Clean semantics, larger protocol change. Needs comparison against backend deduplication and channel/streaming behavior.

## Ranked branch candidates

1. **Core event callback panic recovery** — correctness; small source boundary; target-native regression prepared. Promote if baseline fails and candidate passes.
2. **Filtered nested emit without public bound widening** — correctness; likely requires changing callback/lock ownership or representing filters without storing arbitrary closures. Continue after panic probe.
3. **IPC logical invoke identity across fallback and navigation** — high consequence; needs WebView2 + WKWebView execution and collision analysis before implementation.
4. **Filesystem scope callback panic recovery** — same family as candidate 1, separate state machine; test only after core event result is established.

## Negative results / stops

- Pagehide/beforeunload alone is not a cross-platform solution for the reload duplication case.
- Adding `Send + 'static` to the public filter closure solely to persist it in `Pending::Emit` widens the public contract and has already met upstream resistance.
- Existing open fixes for asset multi-range handling and immediate JS unlisten races are occupied work and are excluded from this scout.
- No upstream state was changed.

## Next transition

Run the focused core-event baseline and candidate repair on the pinned Tauri source. If the baseline reproduces and the candidate passes, retain the exact workflow receipt and inspect panic behavior for `once` plus the filesystem-scope sibling before drafting any human-facing packet.
