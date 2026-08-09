# Campaign 0744: Tauri JS filter callback safety

State: `claimed`

Issue: #744  
Parent scout: #118  
Target source: `34ec18ba5e1acabebd66ae79d6fc746f63d8eb96`  
Claim scope: `mechanism`  
Upstream contact authorized: `false`

## In simple words

Tauri evaluates the public event filter predicate while the JS-listener registry mutex is held. A predicate panic can poison the registry, while a predicate that re-enters listener management can try to lock the same mutex again. These are separate failure mechanisms and need separate controls.

## Question

Can JS listener selection invoke user filtering code without holding the registry lock while preserving target selection and emission ordering?

## Current evidence

- `source-established`: `emit_js_filter` holds `js_event_listeners` across predicate evaluation.
- `target-test-prepared`: retained panic control catches the user panic and then requires the registry to remain readable.
- reentrancy is source-supported but has no executed discriminator yet.

## Next discriminator

Execute panic poisoning first. Then use a watchdog-safe lock-availability/reentry control to decide whether listener metadata must be snapshotted before predicate execution.

## Stop conditions

Stop after panic and reentrancy are independently classified with target execution or explicit negative/infeasible results. Do not claim the Rust event-manager panic repair solves this distinct registry.