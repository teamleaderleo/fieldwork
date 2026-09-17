# Callback-under-lock audit

## In simple words

The verified event and filesystem-scope panic bugs are part of a wider callback ownership pattern in the pinned Tauri tree. Plugin setup/invoke/lifecycle hooks and menu/tray event listeners also execute while a shared `std::sync::Mutex` is held. These are retained as source-level leads only: they can deadlock on same-thread re-entry into the matching registration API, and a panic can poison the store/listener mutex, but each surface needs its own focused control before promotion.

Target: `tauri-apps/tauri@34ec18ba5e1acabebd66ae79d6fc746f63d8eb96`  
Evidence: `source-read` except where an explicit prepared probe is named.  
Upstream contact authorized: `false`.

## Plugin store

Relevant files:

- `crates/tauri/src/app.rs`
- `crates/tauri/src/manager/mod.rs`
- `crates/tauri/src/plugin.rs`

Observed call paths:

```text
AppHandle::plugin_boxed
  -> manager.plugins.lock()
  -> PluginStore::initialize
  -> TauriPlugin::initialize
  -> user plugin setup(AppHandle, PluginApi)

plugin setup callback
  -> can call AppHandle::plugin / remove_plugin
  -> those acquire manager.plugins again
```

and:

```text
AppManager::run_plugin_invoke_handler
  -> manager.plugins.lock()
  -> PluginStore::run_command
  -> selected plugin extend_api / invoke handler
  -> command handler can access AppHandle
```

and every app event:

```text
on_event_loop_event
  -> manager.plugins.lock()
  -> PluginStore::on_event
  -> user plugin lifecycle hooks
```

A same-thread nested register/remove can therefore try to reacquire the global non-reentrant plugin-store mutex. A panic in one of these callbacks can also poison a mutex later acquired with `lock().unwrap()` / `expect("poisoned plugin store")`.

Prepared non-hanging control: `probe/plugin_store_reentrancy_test.rs`. It checks `try_lock()` from inside a dynamic plugin setup callback rather than recursively calling `plugin()` and hanging the runner.

Repair is not selected yet. Simply initializing outside the mutex would remove the setup deadlock, but it would also allow concurrent same-name plugin initializations and could change replacement/side-effect ordering. The invoke-handler path is a separate ownership problem because the selected plugin is mutably borrowed from the store while its callback runs.

## Menu and tray listener registries

`on_event_loop_event` iterates both global and specific menu listeners directly from mutex guards:

```text
menu.global_event_listeners.lock().unwrap()
  -> call each user listener
menu.event_listeners.lock().unwrap()
  -> call matching window listener
```

The tray path does the same for `tray.global_event_listeners` and `tray.event_listeners`.

Registration APIs (`on_menu_event`, per-window menu hooks, tray event registration) mutate these same listener collections. A callback that registers another callback on the same registry is therefore a re-entrancy/deadlock candidate. A callback panic is also a mutex-poison candidate.

This is `source-read` only. Before promotion, add non-hanging controls that inspect lock availability from the actual dispatched callback and distinguish global vs specific registries.

## Stop condition

Do not create a combined “catch every callback panic” patch. Each registry has different ordering and mutation semantics. Promote a surface only after a focused control identifies the intended re-entrant operation or post-panic invariant and a repair can preserve listener/plugin ordering.
