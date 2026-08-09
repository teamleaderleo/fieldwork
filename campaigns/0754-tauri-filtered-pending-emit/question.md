# Campaign 0754: Tauri filtered pending emit

State: `claimed — comparative evaluation`

Issue: #754  
Parent scout: #118  
Related implementation campaign: #749  
Target source: `34ec18ba5e1acabebd66ae79d6fc746f63d8eb96`  
Claim scope: `interface` and event-ordering mechanism  
Upstream contact authorized: `false`

## In simple words

Nested or contended `emit_filter` loses its filter because `Pending::Emit` stores only the payload. Storing the closure directly requires adding `Send + 'static` to a public API that currently accepts a plain borrowed `Fn`. This campaign compares no-bound alternatives against the ordering behavior created by the existing pending queue.

## Question

Can filtered pending emits preserve their target selection without widening the public filter bound and without changing listener mutation or nested-emission ordering?

## Current evidence

- public issue exists; there is no matching open repair PR at this refresh;
- prior closed repair stored the filter in shared pending state and widened public bounds;
- current source still exposes `F: Fn(&EventTarget) -> bool` without `Send`, `Sync`, or `'static`;
- candidate B (snapshot callbacks + immediate mutations + prepared nested emissions) passes simple ordering controls but fails a deeper child-emission discriminator; see `ordering-model-receipt-20260809.md`.

## Alternatives

A. Store filter closure in shared pending state and widen the public API.

B. Snapshot callbacks/targets, release the registry lock, mutate the registry immediately, and queue selected emissions. **Negative on deep ordering.**

C. Preserve a scoped/virtual event state so a queued emission and its descendants observe registry state at the exact pending-action position. Pursue only if the required machinery stays bounded and reviewable.

## Stop conditions

Stop with a no-bound design that matches the ordering discriminators, or retain a negative result that the no-bound fix requires a disproportionate queue redesign. Do not displace #749's target-validated narrow panic repair without stronger evidence.