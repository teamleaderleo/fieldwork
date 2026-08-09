# Tauri InvokeOptions header model receipt — 2026-08-09

## In simple words

A fresh Node execution confirmed that current postMessage JSON keeps record headers, drops entries from a native `Headers` object, and preserves tuple-list input as an array that does not match Rust's required map shape. Normalizing through the standard `Headers` API produces one plain string map for all three public `HeadersInit` forms.

Evidence class: `model-executed`  
Environment: Node `v22.16.0`  
Campaign: #748  
Upstream contact authorized: `false`

## Results

```text
record: current={"X-Record":"record"} normalized={"x-record":"record"}
Headers: current={} normalized={"x-headers":"headers"}
tuple-list: current=[["X-Tuple","tuple"]] normalized={"x-tuple":"tuple"}
PASS current postMessage JSON preserves record headers but loses Headers entries and emits tuple-list as a sequence
PASS standard Headers normalization produces a plain string map for all public HeadersInit forms
```

## Source boundary

Current source declares `InvokeOptions.headers` as `HeadersInit`. Custom-protocol IPC constructs `new Headers(...)`; postMessage serializes raw options. The Rust postMessage receiver deserializes headers through `HashMap<String, String>` before constructing `http::HeaderMap`.

## Limitations

No real Tauri JS-to-Rust postMessage invoke was executed in this receipt. Target execution remains required to confirm the end-to-end failure and candidate.