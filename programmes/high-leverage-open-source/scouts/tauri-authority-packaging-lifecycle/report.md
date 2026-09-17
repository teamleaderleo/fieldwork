# Tauri authority, IPC, packaging, and lifecycle scout

Date: 2026-08-09

Fieldwork lane: #118  
Programme: #114  
Target: `tauri-apps/tauri`  
Pinned source: `34ec18ba5e1acabebd66ae79d6fc746f63d8eb96` (`dev`)  
Upstream contact authorized: `false`

## In simple words

The scout found two reproduced callback-panic failures, one high-consequence authority suspicion with a runnable target test, and a better direction for Tauri's known duplicate-IPC problem.

- A Rust event callback panic can poison the event-manager mutex. If the caller catches the panic, later event work stops progressing. This reproduces on the pinned target, and a small catch/flush/resume repair passes two corrected runs plus a panicking `once()` cleanup control.
- A filesystem `Scope` listener panic can leave its `emitting` flag set and poison its listener mutex. Later scope events stop progressing. This also reproduces, and a separate catch/clear/drain/resume repair passes the focused regression.
- `RuntimeAuthority::resolve_access` appears to discard deny-rule scope: its current `map(...).is_some()` branch takes the deny path whenever the command has any deny entry, even when the origin predicate returned false, and it does not test the denied rule's window/webview selectors. Source and resolved-capability contracts support this reading. A three-control regression is ready, but no retained target run exists yet, so this remains a source-supported suspicion rather than a reproduced bug.
- The current IPC fallback can resend one logical command over `postMessage` after a custom-protocol `POST` may already have reached Rust. A revised candidate negotiates transport before command dispatch and never replays an ambiguous command. Its state-machine model passes, including Android's destructive large-channel fetch. Real WebView2 and WKWebView execution is still required.

Several narrower leads remain: postMessage handling of the public `HeadersInit` contract, bundle-resource destination collisions, public JS-filter panic/reentrancy, and plugin/menu/tray callbacks invoked while shared mutexes are held.

## Evidence ledger

| Finding | Evidence | Durable artifact |
| --- | --- | --- |
| Core Rust event callback panic | `target-executed` | `listener-execution-receipt-20260809.json`, `probe/listener_panic_test.rs`, `probe/candidate.patch` |
| `once()` panic cleanup control | `target-executed` | `listener-once-execution-receipt-20260809.json`, `probe/listener_once_panic_test.rs` |
| Filesystem `Scope` callback panic | `target-executed` | `fs-scope-execution-receipt-20260809.json`, `probe/fs_scope_panic_test.rs`, `probe/fs_scope_candidate.patch` |
| Authority deny scope | `target-test-prepared` | `authority-deny-scope-prepared-20260809.json`, `probe/authority_deny_scope_test.rs` |
| IPC transport negotiation v2 | `model-executed`, target patch prepared | `ipc-candidate-model-receipt-20260809.json`, `probe/ipc_candidate_model.mjs`, `probe/ipc-protocol.candidate.js`, `probe/ipc-head-negotiation-v2.patch` |
| `InvokeOptions.headers` postMessage mismatch | `model-executed` for serialization property; real IPC unexecuted | `invoke-headers-prepared-20260809.json`, `probe/invoke_headers_model.mjs` |
| Resource target collision | `target-test-prepared` | `resource-target-collision-prepared-20260809.json`, `probe/resource_target_collision_test.rs` |
| Public JS-filter panic | `target-test-prepared` | `js-filter-panic-prepared-20260809.json`, `probe/js_filter_panic_test.rs` |
| Plugin-store reentrancy | `target-test-prepared` | `plugin-store-reentrancy-prepared-20260809.json`, `probe/plugin_store_reentrancy_test.rs` |
| Menu/tray/plugin callback lock audit | `source-read` | `callback-lock-audit-20260809.md` |
| Nested filtered emit drops filter | `source-read`, existing upstream issue | section 9 |

The first listener execution attempt, Fieldwork run `31283181973`, is invalid harness evidence. Its baseline ran Cargo from the Fieldwork root rather than the Tauri checkout, and its candidate stopped at a malformed patch hunk. It is retained in `listener-execution-invalid-20260809.json` and contributes no target claim.

The first IPC candidate model is retained as historical evidence in `ipc-model-receipt-20260809.json`; that candidate is marked superseded. Only the v2 IPC candidate is current.

No owned-application WebView2 or WKWebView integration run has been completed for this scout.

## 1. Core Rust event callback panic stalls later event work

Target file: `crates/tauri/src/event/listener.rs`.

Normal path:

```text
emit_filter
  -> handlers.try_lock()
  -> user callbacks run while MutexGuard is alive
  -> nested event operations cannot take the lock and enter Pending
  -> callback returns
  -> guard drops normally
  -> Pending flushes
```

Panic path at the pinned baseline:

```text
user callback panics
  -> MutexGuard unwinds
  -> handlers mutex becomes poisoned
  -> caller catches the panic
  -> later try_lock() returns Poisoned
  -> current Err(_) branch treats poison like ordinary contention
  -> later listen/unlisten/emit work is appended to Pending
  -> no healthy handler-lock path remains to drain it
```

Focused regression:

1. register a panicking listener;
2. call `emit` inside `catch_unwind` and verify the panic reaches the caller;
3. register a listener for another event;
4. emit that event;
5. require later delivery.

Repair retained in `probe/candidate.patch`:

- catch the callback unwind while the mutex guard is owned outside the catch boundary;
- let the guard drop normally;
- flush pending reentrant actions;
- resume the original panic with `resume_unwind`.

### Executed evidence

Pinned target: `34ec18ba5e1acabebd66ae79d6fc746f63d8eb96`  
Runner: Ubuntu 24.04.4 x86_64  
Rust: `1.97.1`  
Cargo: `1.97.1`

Primary corrected run `31284095629`:

- baseline exited `101` and matched `event manager stopped dispatching after callback panic`;
- repair applied;
- focused repair test exited `0`.

Confirmation run `31284174704` repeated the same before/after result. The intentional callback panic still reached the test's `catch_unwind` before later delivery succeeded.

### `once()` cleanup control

`once()` queues `Pending::Unlisten(id)` before invoking its `FnOnce`. If recovery resumed the panic before flushing, the one-shot handler could remain registered after its closure had already been consumed.

Run `31284550759` established:

- baseline poisoned the handler mutex;
- the same repair flushed self-removal before resuming the original panic;
- later delivery through a newly registered listener succeeded.

**Disposition:** reproduced and repair-validated on focused Linux tests. Run the nearby event test set and independent review before preparing a human-facing upstream packet.

## 2. Filesystem `Scope` listener panic stalls later scope events

Target file: `crates/tauri/src/scope/fs.rs`.

`Scope::emit` uses:

- `event_listeners: Mutex<...>`;
- `emitting: AtomicBool`;
- a pending action queue.

It sets `emitting = true`, invokes user listeners while the listener mutex is held, clears `emitting`, then drains pending work.

Panic path:

```text
listener panics
  -> event-listener guard unwinds and poisons
  -> emitting = false is skipped
  -> caller catches panic
  -> future scope event sees emitting == true
  -> future work queues instead of being delivered
```

The focused regression catches one listener panic, removes that listener, registers a healthy listener, allows another path, and requires the second scope event to arrive.

Run `31284564752` established:

- baseline matched `filesystem scope stopped dispatching after callback panic`;
- `probe/fs_scope_candidate.patch` applied;
- repair test exited `0`.

The repair catches the callback unwind, clears `emitting`, lets the guard drop normally, drains pending work, then resumes the original panic.

This is adjacent to the reentrant filesystem-scope deadlock fixed for `https://github.com/tauri-apps/tauri/issues/15468`; panic cleanup is a separate invariant.

**Disposition:** reproduced and repair-validated on a focused Linux test. Keep separate from the core event-manager patch because the state machine differs.

## 3. Authority deny scope: high-consequence source suspicion

Target files:

- `crates/tauri/src/ipc/authority.rs`
- `crates/tauri-utils/src/acl/resolved.rs`
- `crates/tauri-utils/src/acl/capability.rs`

Resolved capabilities carry:

- execution context (`Local` or remote URL pattern),
- window selectors,
- webview selectors,
- allowed commands,
- denied commands.

`Resolved::resolve` copies the same capability context/window/webview selectors into both allowed and denied `ResolvedCommand` entries.

The allow branch of `RuntimeAuthority::resolve_access` requires:

```text
origin matches command context
AND
(webview matches one selector OR window matches one selector)
```

The deny branch currently does:

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

Source reading yields two suspicious properties.

### Origin result is discarded

`Option::map(...).is_some()` is true whenever the command has a deny vector, even when `any(origin.matches(...))` returns false.

### Denied window/webview selectors are not tested

The deny branch does not inspect `cmd.windows` or `cmd.webviews`, even though those selectors are retained on denied `ResolvedCommand` values.

Prepared target controls:

1. allow `Local` + window `main`; deny remote `https://denied.example/*` + window `main`; local `main` should remain allowed;
2. allow `Local` + window `main`; deny `Local` + window `admin`; local `main` should remain allowed;
3. allow and deny `Local` + `main`; the matching deny should still win.

If those controls reproduce over-denial, the smallest repair is to require a denied command to match both the origin and the same window/webview selector rule used by the allow path.

A separate debug diagnostic in `resolve_access_message` describes any command-level deny as explicit; its wording should be checked after the behavior is established.

Search of current upstream issues and pull requests did not find a matching report.

**Disposition:** `target-test-prepared`. Do not describe this as reproduced until the retained three-control test executes against the pinned target.

## 4. IPC fallback can duplicate one logical invoke

Target files:

- `crates/tauri/scripts/ipc-protocol.js`
- `crates/tauri/scripts/process-ipc-message-fn.js`
- `crates/tauri/src/ipc/protocol.rs`
- `crates/tauri/src/ipc/channel.rs`
- `crates/tauri/src/webview/mod.rs`

Existing upstream context: `https://github.com/tauri-apps/tauri/issues/14154`.

Current path:

```text
frontend invoke
  -> custom-protocol POST
  -> Rust may dispatch the command
  -> navigation / transport loss rejects frontend fetch
  -> frontend marks custom protocol failed
  -> same logical message is resent over postMessage
  -> backend can dispatch it again
```

A rejected frontend fetch cannot say whether the request failed before Rust saw it or after side effects began. Cross-transport replay after that ambiguous failure cannot promise at-most-once command execution.

### Revised candidate: select transport before dispatch

Tauri dispatches IPC commands only for custom-protocol `POST`. A `HEAD` request follows the non-dispatch path and returns a normal HTTP response through the protocol response wrapper. The v2 candidate uses one shared document-local `HEAD` probe before the first side-effecting command.

```text
first desktop invoke(s)
  -> share one HEAD probe carrying IPC headers/content-type class
  -> probe resolves => custom protocol selected
  -> probe rejects => postMessage selected
  -> serialize and dispatch each command once

later custom POST rejects ambiguously
  -> reject that invoke
  -> mark custom protocol blocked for future invokes
  -> never replay the ambiguous command

future invokes
  -> postMessage
```

Android has a separate state because regular commands already use postMessage while the large-channel fetch uses the custom protocol.

The Android channel fetch removes queued payload data from `ChannelDataIpcQueue`. The v2 candidate therefore negotiates that path before the destructive fetch and never replays an ambiguous channel POST.

### First draft rejected during review

The first draft had two defects:

1. it serialized the payload to derive probe headers, then serialized again for the real request; `process-ipc-message-fn.js` can invoke a user `__TAURI_TO_IPC_KEY__()` hook, so that could execute serialization-side effects twice;
2. it retained ambiguous retry for Android's destructive large-channel fetch.

The v2 candidate infers the probe content-type class without serializing the payload and gives the Android channel path its own pre-dispatch negotiation.

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

Maintainer discussion in the existing issue already records Windows and macOS reproduction plus different page-lifecycle timing, so a `pagehide` / `beforeunload` guard alone is not a cross-engine answer.

**Disposition:** `model-executed`, target patch prepared. Required gate: real WebView2 and WKWebView trials covering local pages, externally loaded pages, CSP-blocked custom protocol, custom invoke headers, reload during a long command, binary channel traffic, and a transport failure after successful negotiation.

## 5. `InvokeOptions.headers` postMessage mismatch

Public `packages/api/src/core.ts` declares `InvokeOptions.headers` as `HeadersInit`, so callers may provide:

- a record;
- a `Headers` object;
- tuple-list / iterable pairs.

The custom-protocol path normalizes with `new Headers(...)`. The postMessage path serializes the original `options.headers`. Rust then deserializes that field as `HashMap<String, String>`.

Serialization behavior:

```text
record       -> JSON object -> compatible map shape
Headers      -> JSON {}     -> entries lost
tuple list   -> JSON array  -> not the Rust map shape
```

Android regular commands already use postMessage, so this is relevant even without a custom-protocol fallback.

The v2 IPC model verifies that normalizing through `new Headers(...)` and `Object.fromEntries(...entries())` produces a plain string map for all three public input forms.

**Disposition:** serialization property `model-executed`; real Android/Rust IPC path unexecuted.

## 6. Bundle resource destination collision

Target files:

- `crates/tauri-utils/src/resources.rs`
- `crates/tauri-build/src/lib.rs`

`ResourcePaths::from_map` can yield distinct sources with the same relative target. `tauri-build::copy_resources` joins each target under the output directory and copies immediately without a duplicate-target check. The copy helper truncates the destination.

Source reading therefore predicts a silent last-writer overwrite when two distinct sources resolve to the same target. The configured source-to-target mapping is a `HashMap`, so there is no stable user-authored source order that makes one winner intentional.

Prepared regression maps two different files to `same.txt` and requires an error.

If reproduced, a narrow repair can resolve all source/target pairs first, reject a target owned by multiple distinct canonical sources, then copy only after validation succeeds.

**Disposition:** `target-test-prepared`. Exact target collision only; case-insensitive aliases, Unicode-normalization aliases, and final installer output remain untested.

## 7. Public JS-filter panic and reentrancy

Target file: `crates/tauri/src/event/listener.rs`.

Public `Emitter::emit_filter` traverses JS listeners before Rust listeners. `emit_js_filter` locks `js_event_listeners` and evaluates the caller's predicate while the guard is live.

Source reading predicts two separate hazards:

- a predicate panic can poison the JS-listener mutex;
- a predicate that reenters a JS-listener operation can try to acquire the same mutex while it is already held.

The retained non-hanging regression catches a predicate panic, then checks whether the JS-listener registry remains usable.

A catch/drop/resume repair sketch could address poisoning. It would not fix reentrancy; that needs a different ownership approach.

**Disposition:** `target-test-prepared`. Keep separate from the verified Rust callback-panic repair.

## 8. Plugin, menu, and tray callbacks under shared mutexes

Detailed audit: `callback-lock-audit-20260809.md`.

Dynamic plugin registration follows:

```text
AppHandle::plugin_boxed
  -> manager.plugins.lock()
  -> PluginStore::initialize
  -> TauriPlugin::initialize
  -> user setup(AppHandle, PluginApi)
```

The setup callback receives an `AppHandle`; `AppHandle::plugin` and `remove_plugin` acquire the same plugin-store mutex. A nested register/remove operation can therefore try to reacquire that non-reentrant mutex on the same thread.

The same plugin-store lock stays held while selected plugin invoke handlers and lifecycle callbacks run.

Prepared safe setup probe: `probe/plugin_store_reentrancy_test.rs`. It checks `try_lock()` inside plugin setup instead of deliberately hanging on a nested `plugin()` call.

Menu and tray event dispatch similarly invokes user callbacks while holding global or specific registration mutexes. Reentrant listener registration and callback-panic poisoning are source-level leads there.

**Disposition:** plugin setup `target-test-prepared`; plugin invoke/lifecycle and menu/tray variants `source-read`. No repair selected yet because plugin registration ordering and same-name replacement behavior must be preserved.

## 9. Nested filtered emit drops its filter

Current `Pending::Emit` stores only `EmitArgs`. If `emit_filter` is called while the handler mutex is held, the deferred action is queued as a plain emit. `flush_pending` later replays it through `emit()`, so targets excluded by the original filter can receive the event.

Existing upstream issue: `https://github.com/tauri-apps/tauri/issues/15759`.

A previous repair attempted to store the filter closure in the pending queue, which requires `Send + 'static` and widens the public `Emitter::emit_filter` closure contract. This scout does not duplicate that occupied contribution unit.

## Ranked next branches

1. **Execute authority deny-scope controls.** Highest consequence, smallest missing evidence step. If baseline reproduces both cross-scope cases while matching deny still wins, promote to a narrow authority campaign/packet.
2. **Harden core event callback-panic repair.** Run the surrounding event test set and independent review, then prepare a human-facing patch packet.
3. **Harden filesystem `Scope` panic repair.** Run the surrounding scope tests and keep it separate from the core event manager.
4. **Run IPC v2 in WebView2 and WKWebView.** This is the largest remaining cross-platform evidence gap.
5. **Execute resource-collision and JS-filter poison controls.** Both are small target-native tests.
6. **Execute plugin-store `try_lock` control.** If setup lock ownership is confirmed, test invoke/lifecycle paths separately before selecting a repair.
7. **Retain menu/tray callback reentrancy as a finding** until a focused control or realistic caller raises its priority.

## Negative results and exclusions

- Run `31283181973` is invalid harness evidence and is excluded from every target claim.
- The first IPC candidate draft is superseded; its double-serialization and Android channel-retry defects were removed before v2 was retained.
- `pagehide` / `beforeunload` timing is not a sufficient cross-platform duplicate-invoke repair.
- Remembering that the custom protocol succeeded once does not remove ambiguity from a later failed command POST.
- Replaying a side-effecting command after an ambiguous transport rejection needs a stronger request identity/idempotency contract; the v2 candidate avoids that replay instead.
- The verified Rust callback-panic repair does not cover JS-filter panic or reentrancy.
- The two executed panic repairs remain separate because their state machines differ.
- Authority, resource collision, JS-filter panic, and plugin-store reentrancy remain below `target-executed`; prepared tests are not executions.
- Existing active upstream work for asset multi-range responses, immediate JS unlisten cleanup, and nested filtered emit was treated as occupied rather than duplicated.
- No automated third-party upstream mutation was attempted or performed.

## Recommended transition

If one manual target execution is available, spend it on the authority controls first.

Then:

1. run broader target tests around the two executed panic repairs;
2. run the IPC v2 candidate on Windows/WebView2 and macOS/WKWebView;
3. execute the resource collision and JS-filter poison regressions;
4. execute the safe plugin-store lock-ownership probe and split setup/invoke/lifecycle work only if the controls warrant it.

This scout is complete as reconnaissance: source is pinned, code and test boundaries are mapped, executable evidence and invalid evidence are retained separately, narrower suspicions have runnable probes instead of promoted claims, and contribution units are ranked by consequence and missing evidence.
