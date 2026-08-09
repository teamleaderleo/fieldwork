# Campaign 0752: Tauri menu and tray callback ownership

State: `claimed`

Issue: #752  
Parent scout: #118  
Target source: `34ec18ba5e1acabebd66ae79d6fc746f63d8eb96`  
Claim scope: `mechanism`  
Upstream contact authorized: `false`

## In simple words

Menu and tray event dispatch invokes application callbacks while the matching listener-registry mutex is held. Callback code can reach registration APIs that mutate those same registries, and panic can poison the registry for later events.

## Question

Can app-wide and specific menu/tray listeners be invoked after releasing registry ownership while preserving callback order and mutation semantics?

## Current evidence

- `source-established`: `on_event_loop_event` holds each of four registry mutexes across callback invocation: global menu, window menu, global tray, and per-tray listeners.
- menu registration source confirms public callbacks are appended under the same global registry lock.
- fresh open issue/PR searches found no matching active ownership repair at claim time.

## Next discriminator

Use real event dispatch with non-hanging callbacks that inspect `try_lock()` for each exact registry. Only after lock ownership is established should watchdog-safe registration reentry be attempted.

## Stop conditions

Stop with per-registry target execution and a bounded repair or negative result. Keep plugin-store ownership separate and do not propose a catch-all callback layer.