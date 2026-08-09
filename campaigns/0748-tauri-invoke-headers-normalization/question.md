# Campaign 0748: Tauri invoke-header normalization

State: `claimed`

Issue: #748  
Parent scout: #118  
Target source: `34ec18ba5e1acabebd66ae79d6fc746f63d8eb96`  
Claim scope: `interface`  
Upstream contact authorized: `false`

## In simple words

The JS API accepts all `HeadersInit` forms, but custom-protocol IPC normalizes them while postMessage JSON does not. Native `Headers` loses entries and tuple-list input has the wrong shape for Rust's required string map.

## Question

Can both IPC transports preserve the same public `HeadersInit` contract by normalizing once to a plain string map before postMessage serialization?

## Current evidence

- `source-established`: public type is `HeadersInit`; custom protocol uses `new Headers`; postMessage serializes raw options; Rust postMessage receiver deserializes a `HashMap<String, String>`.
- `model-executed` twice: retained scout receipt plus fresh Node `v22.16.0` confirmation. Record input survives today, `Headers` becomes `{}`, tuple list remains an array; standard `Headers` normalization produces a plain map for all three.

## Next discriminator

Run a real Tauri postMessage invoke for record, `Headers`, and tuple-list inputs and inspect the Rust `HeaderMap`. Preserve existing browser header normalization semantics rather than adding a second policy.

## Stop conditions

Stop with target-executed mismatch plus repair validation, or a negative result showing another runtime layer normalizes before the Rust deserializer.