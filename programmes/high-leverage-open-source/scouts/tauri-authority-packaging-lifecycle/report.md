# Tauri authority, IPC, packaging, and lifecycle scout

Date: 2026-08-09

Fieldwork lane: #118  
Programme: #114  
Target: `tauri-apps/tauri`  
Pinned source: `34ec18ba5e1acabebd66ae79d6fc746f63d8eb96` (`dev`)  
Upstream contact authorized: `false`

## In simple words

The deep pass found two reproduced lifecycle bugs, one high-consequence authority bug with a runnable test packet, a better candidate for the known duplicate-IPC problem, and several narrower follow-ups.

1. **Authority deny rules are applied too broadly.** `RuntimeAuthority::resolve_access` rejects a command whenever the command has any deny entry, even if that deny belongs to a different origin. It also ignores the denied rule's window/webview selectors. The resolver explicitly keeps those selectors on denied commands, and the allow path uses them. Three focused controls and a minimal candidate are prepared, but there is no retained target execution receipt yet.
2. **A panicking Rust event callback can permanently stall the event manager after the caller catches the panic.** This reproduces on the pinned Tauri source. A compact catch/flush/resume candidate preserves the original panic and restores later delivery in two corrected Linux executions. A separate `once()` panic control also passes, confirming queued one-shot cleanup happens before the panic is resumed.
3. **A panicking filesystem `Scope` listener can permanently stall later scope events.** This also reproduces on the pinned source. A separate catch/clear/drain/resume candidate passes the focused Linux regression.
4. **The current IPC fallback can execute one logical invoke twice.** A side-effecting custom-protocol `POST` may already have reached Rust when navigation makes `fetch()` reject; the frontend then resends the same message over `postMessage`. A revised candidate negotiates transport with one side-effect-free `HEAD` probe before dispatch and never replays an ambiguous command. Its state-machine model passes, including Android's destructive large-channel fetch and custom `HeadersInit` inputs. Real WebView2 and WKWebView execution is still required.
5. **`InvokeOptions.headers` advertises `HeadersInit`, while the postMessage receiver expects a string map.** Record headers fit. A `Headers` object loses its entries when JSON serialized, and tuple-list input serializes as a sequence. This is especially relevant on Android, where regular invokes already use postMessage.
6. **Two bundle resources can resolve to the same destination and silently overwrite.** The resource map is a `HashMap`, and `tauri-build` copies without a duplicate-target check. A focused regression and reject-before-copy candidate are prepared.
7. **Plugin, menu, tray, and public JS-filter callbacks expose more callback-under-mutex seams.** They are source-supported leads with non-hanging probes where practical; they are not promoted to executed bugs here.

The strongest ready-to-run human follow-up is the authority test packet. The strongest executed implementation packets are the core event callback panic and filesystem `Scope` panic repairs. The IPC proposal has the highest cross-platform leverage, but it still needs two real webview engines before a patch should be treated as ready.

## Evidence ledger

| Finding | Evidence | Durable artifact |
| --- | --- | --- |
| Authority deny scope | `target-test-prepared` | `authority-deny-scope-prepared-20260809.json`, `probe/authority_deny_scope_test.rs` |
| Core Rust event callback panic | `target-executed` | `listener-execution-receipt-20260809.json`, `probe/listener_panic_test.rs`, `probe/candidate.patch` |
| `once()` panic cleanup control | `target-executed` | `listener-once-execution-receipt-20260809.json`, `probe/listener_once_panic_test.rs` |
| Filesystem `Scope` callback panic | `target-executed` | `fs-scope-execution-receipt-20260809.json`, `probe/fs_scope_panic_test.rs`, `probe/fs_scope_candidate.patch` |
| IPC transport negotiation v2 | `model-executed`, target patch prepared | `ipc-candidate-model-receipt-20260809.json`, `probe/ipc_candidate_model.mjs`, `probe/ipc-protocol.candidate.js`, `probe/ipc-head-negotiation-v2.patch` |
| `InvokeOptions.headers` fallback mismatch | `model-executed` for serialization property; real IPC unexecuted | `invoke-headers-prepared-20260809.json`, `probe/invoke_headers_model.mjs`; also covered by the v2 IPC model |
| Resource target collision | `target-test-prepared` | `resource-target-collision-prepared-20260809.json`, `probe/resource_target_collision_test.rs` |
| Public JS filter panic | `target-test-prepared` | `js-filter-panic-prepared-20260809.json`, `probe/js_filter_panic_test.rs` |
| Plugin-store reentrancy | `target-test-prepared` | `plugin-store-reentrancy-prepared-20260809.json`, `probe/plugin_store_reentrancy_test.rs` |
| Menu/tray/plugin callback lock audit | `source-read` | `callback-lock-audit-20260809.md` |
| Nested filtered emit drops filter | `source-read`, existing upstream issue | source map below |

The first listener execution attempt, Fieldwork run `31283181973`, is **invalid harness evidence**. The baseline Cargo command ran from the Fieldwork root, and the candidate job stopped at a malformed patch hunk. It is retained in `listener-execution-invalid-20260809.json` and contributes no target claim.

No owned-application WebView2 or WKWebView integration run has been completed for this scout.

## 1. Runtime authority: denied command scope is discarded

Relevant target files:

- `crates/tauri/src/ipc/authority.rs`
- `crates/tauri-utils/src/acl/resolved.rs`
- `crates/tauri-utils/src/acl/capability.rs`

Capabilities are resolved with:

- execution context (`Local` or remote URL pattern),
- window patterns,
- webview patterns,
- allowed commands,
- denied commands.

`Resolved::resolve` copies the same capability context/window/webview selectors into both allowed and denied `ResolvedCommand` entries.

The allow branch of `RuntimeAuthority::resolve_access` correctly requires:

```text
origin matches command context
AND
(webview matches one selector OR window matches one selector)
```

The deny branch currently does this instead:

```rust
if self
  .denied_commands
  .get(command)
  .map(|resolved| resolved.iter().any(|cmd| origin.matches(&cmd.context)))
  .is_some()
{
  None
}
```

Two independent problems follow.

### 1a. Origin predicate result is discarded

`Option::map(...).is_some()` is true whenever the command has a deny vector, whether `any(origin.matches(...))` returns true or false.

So a remote-only deny entry can reject a local invoke of the same command.

### 1b. Denied window/webview selectors are ignored

Even if the origin check were changed to `is_some_and`, the current branch does not test `cmd.windows` or `cmd.webviews`. A deny scoped to an `admin` window can therefore reject the command from `main`.

Prepared controls:

1. allow `Local` + window `main`; deny remote `https://denied.example/*` + window `main`; local `main` must remain allowed;
2. allow `Local` + window `main`; deny `Local` + window `admin`; local `main` must remain allowed;
3. allow and deny `Local` + `main`; matching deny must still win.

Prepared candidate:

```rust
if self.denied_commands.get(command).is_some_and(|resolved| {
  resolved.iter().any(|cmd| {
    origin.matches(&cmd.context)
      && (cmd.webviews.iter().any(|w| w.matches(webview))
        || cmd.windows.iter().any(|w| w.matches(window)))
  })
}) {
  None
}
```

This mirrors the allow selector semantics while preserving deny precedence when the deny actually applies.

A separate debug diagnostic in `resolve_access_message` also treats any command-level deny as “explicitly denied”; review that message path for qualifier accuracy if the behavioral fix is taken.

Search of current upstream issues and pull requests did not find a matching report.

**Status:** high-priority, `target-test-prepared`. Do not call reproduced until the retained three-control test actually executes against the pinned target.

## 2. Core Rust event callback panic stalls later event work

Relevant target file: `crates/tauri/src/event/listener.rs`.

Normal event path:

```text
emit_filter
  -> handlers.try_lock()
  -> iterate matching handlers while MutexGuard is alive
  -> invoke user callback while guard is alive
  -> if callback performs nested event work, that work is queued in Pending
  -> callback returns
  -> guard drops
  -> pending queue flushes
```

Panic path in the pinned baseline:

```text
user callback panics
  -> unwinding drops MutexGuard
  -> std::sync::Mutex becomes poisoned
  -> caller catches the panic
  -> later listen/unlisten/emit calls handlers.try_lock()
  -> try_lock returns Poisoned
  -> current Err(_) branch treats poison as ordinary contention
  -> work is appended to pending
  -> no healthy handler-lock path remains to make progress
```

Focused regression:

1. register a panicking listener;
2. catch the unwind from `emit` and verify the panic reached the caller;
3. register another event listener;
4. emit the other event;
5. require later delivery.

Prepared candidate:

- catch the callback unwind while the handler guard is owned outside the catch boundary;
- let the guard drop normally, avoiding poison;
- flush pending reentrant actions;
- resume the original panic with `resume_unwind`.

### Executed evidence

Pinned target: `34ec18ba5e1acabebd66ae79d6fc746f63d8eb96`  
Runner: Ubuntu 24.04.4 x86_64  
Rust: `1.97.1`  
Cargo: `1.97.1`

Primary corrected Fieldwork run `31284095629`:

- baseline exited `101` and matched the exact post-panic assertion `event manager stopped dispatching after callback panic`;
- candidate patch applied;
- candidate focused test exited `0`.

Independent confirmation run `31284174704` repeated the same before/after result. The candidate still printed the intentional callback panic before the test passed, confirming the unwind remained visible to the test's `catch_unwind`.

### `once()` control

`once()` queues its own `Pending::Unlisten(id)` before calling the user's `FnOnce`. If the callback panics, resuming before flushing would leave the one-shot handler installed after its closure has already been consumed.

Run `31284550759` established:

- baseline poisoned the handler mutex on the panicking `once` callback;
- the same catch/flush/resume candidate flushed self-removal before resuming the panic;
- later delivery through a newly registered listener succeeded.

**Status:** `target-executed`, focused Linux. Good compact patch candidate; still run the surrounding event test set before a human submission packet is called complete.

## 3. Filesystem `Scope` listener panic stalls later scope events

Relevant target file: `crates/tauri/src/scope/fs.rs`.

The scope event system uses:

- `event_listeners: Mutex<...>`;
- `emitting: AtomicBool`;
- a pending action queue.

`Scope::emit` sets `emitting = true`, runs user listeners while `event_listeners` is locked, then clears `emitting` and drains pending work.

If a listener panics:

```text
listener panic
  -> event_listeners guard unwinds and poisons
  -> emitting = false is skipped
  -> caller catches panic
  -> future scope event sees emitting == true
  -> event is queued instead of delivered
```

This is adjacent to the reentrant filesystem-scope deadlock fixed by the merged work for `https://github.com/tauri-apps/tauri/issues/15468`, but the panic-cleanup invariant is distinct.

Focused regression catches one listener panic, removes that listener, registers a healthy listener, allows another path, and requires the second scope event to arrive.

Run `31284564752` established:

- baseline hit `filesystem scope stopped dispatching after callback panic`;
- candidate patch applied;
- candidate test exited `0`.

Candidate ordering:

1. catch callback unwind;
2. clear `emitting` while the guard still drops normally;
3. drain queued operations;
4. resume the original panic.

**Status:** `target-executed`, focused Linux. Keep it as a separate patch from the core event manager because the state machine is different.

## 4. IPC reload/fallback can duplicate one logical invoke

Relevant target files:

- `crates/tauri/scripts/ipc-protocol.js`
- `crates/tauri/scripts/process-ipc-message-fn.js`
- `crates/tauri/src/ipc/protocol.rs`
- `crates/tauri/src/ipc/channel.rs`
- `crates/tauri/src/webview/mod.rs`

Existing upstream context: `https://github.com/tauri-apps/tauri/issues/14154`.

Current path:

```text
frontend invoke
  -> custom-protocol fetch POST
  -> Rust may parse and dispatch command
  -> navigation / transport loss rejects the frontend fetch
  -> rejection handler marks custom protocol failed
  -> same logical message is resent over postMessage
  -> backend can dispatch the command again
```

The frontend cannot tell whether a rejected fetch failed before Rust saw the request or after side effects started. Therefore retrying that same logical invoke over another transport cannot preserve at-most-once side effects.

Maintainer discussion in the existing issue already records WebView2 and macOS reproduction and differing page lifecycle timing. A `pagehide`/`beforeunload` guard is therefore not a cross-engine proof.

### Revised candidate: negotiate before dispatch

Tauri's custom-protocol Rust handler dispatches commands only for `POST`. A `HEAD` request follows the non-dispatch path and returns a normal HTTP response (currently 405) through the response/CORS wrapper. Use that as a document-local transport capability probe before any command POST.

Candidate state machine:

```text
first desktop invoke(s)
  -> share one pending HEAD probe carrying IPC headers/content-type class
  -> probe resolves => custom protocol selected
  -> probe rejects => postMessage selected
  -> serialize and dispatch each command exactly once through selected transport

later custom POST rejects ambiguously
  -> fail that invoke to its error callback
  -> mark custom protocol blocked for future invokes
  -> do not replay the ambiguous command

future invokes
  -> postMessage
```

Android needs a second state because regular command bodies already use postMessage, while the special large-channel fetch uses the custom protocol.

The Android channel fetch is destructive on the Rust side: retrieving queued channel data removes it from `ChannelDataIpcQueue`. The revised candidate therefore probes the channel custom-protocol path before dispatch as well and never retries an ambiguous channel POST.

### Two first-draft errors were caught and removed

The original draft is intentionally superseded.

1. It serialized the payload to derive probe headers and then serialized again for the real request. `process-ipc-message-fn.js` can call a user `__TAURI_TO_IPC_KEY__()` hook, so that could execute serialization hooks twice.
2. It retained ambiguous retry for Android's destructive channel fetch.

Version 2 infers the probe content-type class without serializing the payload and gives the channel path its own pre-dispatch negotiation.

### Executed model

`probe/ipc_candidate_model.mjs`, run `31284728324`, Node `v22.23.1`:

```text
PASS candidate probe does not serialize payload before transport selection
PASS concurrent first invokes share one HEAD probe
PASS blocked probe preserves record, Headers, and tuple-list headers over postMessage
PASS ambiguous custom POST is not replayed; later invoke recovers
PASS Android channel fetch negotiates before destructive dispatch and never replays an ambiguous POST
```

The candidate JavaScript also passed `node --check` and `git diff --check`; `probe/ipc-head-negotiation-v2.patch` was generated by Git from the pinned target tree.

**Status:** `model-executed`, target patch prepared. Required next gate: real Windows/WebView2 and macOS/WKWebView trials covering local page, externally loaded page, CSP-blocked custom protocol, custom invoke headers, reload during a long command, binary channel traffic, and a transport failure after successful negotiation.

## 5. `InvokeOptions.headers` and postMessage disagree on accepted input shape

Public API file: `packages/api/src/core.ts`.

`InvokeOptions.headers` is declared as `HeadersInit`, so callers may provide:

- a plain record;
- a `Headers` object;
- an array/iterable of `[name, value]` pairs.

The custom-protocol path normalizes with `new Headers(...)` and therefore supports all three forms.

The postMessage path embeds `options.headers` into an object passed through the IPC serializer. Rust then deserializes `options.headers` as `HashMap<String, String>`.

Serialization consequence:

- record -> JSON object, compatible;
- `Headers` object -> JSON `{}`, entries disappear;
- tuple list -> JSON sequence, not the Rust map shape.

Android regular commands use postMessage directly, so this is a normal Android contract mismatch as well as a custom-protocol fallback mismatch.

Narrow candidate:

```js
const headers = Object.fromEntries(
  new Headers((options && options.headers) || {}).entries()
)
```

and serialize that plain object in the postMessage options.

The v2 IPC model exercises record, `Headers`, and tuple-list normalization successfully. The standalone retained model documents the raw JSON behavior too.

**Status:** serialization property `model-executed`; real Android/Rust IPC path unexecuted.

## 6. Bundle resource target collisions can overwrite silently

Relevant target files:

- `crates/tauri-utils/src/resources.rs`
- `crates/tauri-build/src/lib.rs`

A resource map can produce distinct sources with the same relative target. `tauri-build::copy_resources` currently:

1. canonicalizes a source;
2. joins `resource.target()` under the output directory;
3. copies immediately;
4. performs no duplicate-target check.

The copy helper creates/truncates the destination, so the later source wins. The configured source-to-target mapping is stored in a `HashMap`, which means there is no stable user-authored source order that could make the winner intentional.

Prepared regression maps two different files to `same.txt` and requires an error.

Prepared candidate resolves all source/target pairs first, rejects a target owned by multiple distinct canonical sources, then copies only after validation.

**Status:** `target-test-prepared`. Exact path collision only; case-insensitive aliases, Unicode normalization, and final installer output are not established.

## 7. Public JS event filter can poison the JS-listener registry

Relevant target file: `crates/tauri/src/event/listener.rs`.

Public `Emitter::emit_filter` traverses JS listeners before Rust listeners. `emit_js_filter` locks `js_event_listeners` and evaluates the caller's predicate while that guard is live.

A predicate panic can therefore poison the JS-listener mutex before the verified Rust callback-panic candidate is reached. Later JS-listener operations use `lock().unwrap()` and can panic on the poisoned registry.

Prepared non-hanging regression:

- create a MockRuntime webview;
- register a JS listener;
- call `emit_js_filter` with a predicate that intentionally panics under `catch_unwind`;
- require `has_js_listener` to remain usable afterward.

A catch/drop/resume candidate can address poisoning, but **does not** address re-entrancy: a predicate that calls back into a JS-listener operation can still attempt to reacquire the same mutex while it is held.

**Status:** `target-test-prepared`. Keep separate from the verified Rust callback patch.

## 8. Dynamic plugin callbacks run under the global plugin-store mutex

Relevant target files:

- `crates/tauri/src/app.rs`
- `crates/tauri/src/manager/mod.rs`
- `crates/tauri/src/plugin.rs`

Source paths:

```text
AppHandle::plugin_boxed
  -> manager.plugins.lock()
  -> PluginStore::initialize
  -> TauriPlugin::initialize
  -> user setup(AppHandle, PluginApi)
```

The setup callback receives an `AppHandle`; `AppHandle::plugin` and `remove_plugin` acquire the same plugin-store mutex. A setup callback that composes/removes dynamic plugins can therefore attempt a same-thread re-lock of a non-reentrant mutex.

The same ownership pattern appears in:

```text
AppManager::run_plugin_invoke_handler
  -> manager.plugins.lock()
  -> selected plugin extend_api / invoke handler
```

and:

```text
on_event_loop_event
  -> manager.plugins.lock()
  -> PluginStore::on_event
  -> plugin lifecycle callbacks
```

Prepared safe control `probe/plugin_store_reentrancy_test.rs` uses `try_lock()` from inside setup rather than deliberately hanging on nested `plugin()`.

Repair is not selected: dropping the lock before initialization could allow concurrent same-name plugin initialization and change side-effect/replacement ordering; invoke handlers have an additional mutable-borrow ownership problem.

**Status:** `target-test-prepared` for setup lock ownership; invoke/lifecycle variants `source-read`.

## 9. Menu and tray callbacks are also invoked under registration mutexes

`on_event_loop_event` directly iterates:

```text
menu.global_event_listeners.lock().unwrap()
menu.event_listeners.lock().unwrap()
tray.global_event_listeners.lock().unwrap()
tray.event_listeners.lock().unwrap()
```

while invoking user callbacks from those collections.

Registration APIs mutate those same registries. Registering another global/specific menu or tray listener from inside the corresponding callback is therefore a re-entrancy/deadlock lead; a callback panic is also a mutex-poison lead.

**Status:** `source-read` only. The exact global vs per-item/per-window registry controls should be tested independently before promotion.

## 10. Nested filtered emit still drops its filter

Current `Pending::Emit` stores only `EmitArgs`. If `emit_filter` is called while the handler lock is already held, the deferred action is queued as a plain emit. `flush_pending` later replays it through `emit()`, broadcasting to targets that the original filter excluded.

Existing upstream issue: `https://github.com/tauri-apps/tauri/issues/15759`.

A previous repair attempted to put the filter closure into the pending queue, which requires `Send + 'static` and widens the existing public `Emitter::emit_filter` closure contract. This scout does not recommend that as the default repair.

**Status:** known source defect / occupied upstream work; no duplicate contribution unit opened here.

## Ranked branches

1. **Authority deny scope** — highest consequence. Run the retained three-control unit test manually against the pinned revision. If it behaves as source reading predicts, promote immediately to a narrow authority campaign/packet.
2. **Core event callback panic recovery** — already reproduced and candidate-validated twice, plus `once()` cleanup control. Run the nearby event test set and review panic/callback semantics; then prepare a human-facing patch packet.
3. **Filesystem `Scope` panic recovery** — already reproduced and candidate-validated. Run the scope test set and keep separate from core event manager changes.
4. **IPC pre-dispatch transport negotiation v2** — highest cross-platform leverage. Needs WebView2 and WKWebView execution before promotion.
5. **`InvokeOptions.headers` postMessage normalization** — narrow contract fix; include it with IPC work only if the webview trial confirms no conflicting transport assumptions, otherwise keep it as its own tiny packet.
6. **Resource destination collision validation** — low implementation risk and concrete data-integrity consequence; execute the retained unit test before promotion.
7. **JS filter panic/reentrancy** — execute poison regression first, then design reentrancy separately.
8. **Plugin-store setup/invoke/lifecycle reentrancy** — execute non-hanging lock-ownership controls before selecting a repair.
9. **Menu/tray callback reentrancy** — retain as next scout material unless a real caller/repro makes it urgent.

## Negative results, exclusions, and uncertainty

- The first listener execution run was invalid harness evidence and is explicitly excluded.
- The first IPC `HEAD` draft was rejected after code review found double payload serialization and ambiguous retry of Android's destructive channel fetch.
- `pagehide` / `beforeunload` timing is not a sufficient cross-platform duplicate-invoke fix.
- Remembering that custom-protocol IPC worked once does not solve an ambiguous later POST failure.
- A side-effecting command cannot be safely replayed over another transport after an ambiguous fetch rejection without a stronger request identity/idempotency contract.
- `OPTIONS` is less attractive as the explicit JS capability request because it is not a CORS-safelisted method; the `HEAD` idea still needs real webview confirmation of custom-header/CORS behavior.
- The verified Rust event callback patch does not repair JS-filter panic/reentrancy.
- The filesystem `Scope` patch and core event-manager patch should remain separate.
- Resource collision evidence does not yet include case-insensitive path aliases or final platform installers.
- The authority finding is source-strong but is intentionally not called reproduced until the retained three-control test executes.
- Existing active upstream work for asset multi-range responses and immediate JS unlisten cleanup was treated as occupied and not duplicated.
- No automated third-party upstream mutation was attempted or performed.

## Recommended next transition

If one manual target execution is available, spend it on the authority controls first.

Then, in order:

1. run broader target tests around the two executed panic candidates;
2. run the IPC v2 candidate on Windows/WebView2 and macOS/WKWebView with predeclared transport cases;
3. execute the resource collision and JS-filter poison unit controls;
4. execute the safe plugin-store `try_lock` control, then decide whether setup, invoke, and lifecycle callbacks deserve separate campaigns.

The scout is complete as reconnaissance: it has pinned source, code/test maps, executable evidence, ranked contribution units, negative results, and explicit evidence limits. Coordinator decision should be to promote the executed panic fixes and the authority test packet, retain the IPC work until platform execution, and leave the remaining callback-lock surfaces as findings until their focused controls run.
