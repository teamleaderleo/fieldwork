# Campaign 0746: Tauri plugin-store callback ownership

State: `claimed`

Issue: #746  
Parent scout: #118  
Target source: `34ec18ba5e1acabebd66ae79d6fc746f63d8eb96`  
Claim scope: `mechanism`  
Upstream contact authorized: `false`

## In simple words

Dynamic plugin setup runs while Tauri holds the global plugin-store mutex. Plugin invoke and lifecycle callbacks also have callback-under-store-lock paths. A setup hook receives `AppHandle`, so it can synchronously reach plugin APIs that need the same mutex.

## Question

Which plugin callbacks can safely run after releasing global store ownership, and what ordering or mutable-plugin invariants prevent a simple unlock-before-callback repair?

## Current evidence

- `source-established`: `AppHandle::plugin_boxed` locks the store, initializes the plugin, then registers it; builder plugin initialization reaches application setup under that guard.
- prepared setup discriminator checks mutex availability without hanging.
- invoke/lifecycle paths are source-level child hypotheses because they have different mutable ownership requirements.

## Next discriminator

Execute dynamic setup first. If RED, compare two-phase initialization/registration against same-name concurrency and failed-initialize behavior. Keep invoke dispatch separate until a bounded ownership model preserves per-plugin mutable state.

## Stop conditions

Stop when each promoted callback surface has its own focused execution result and repair boundary. Do not replace the global store architecture speculatively and do not combine unrelated menu/tray registries.