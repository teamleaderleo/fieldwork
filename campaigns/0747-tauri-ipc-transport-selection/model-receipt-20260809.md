# Tauri IPC transport ownership model receipt — 2026-08-09

## In simple words

A fresh independent Node model rechecked the pre-dispatch transport-selection invariants without reusing the scout's original model implementation. It supports the candidate's ownership logic but does not substitute for WebView2 or WKWebView execution.

Evidence class: `model-executed`  
Environment: Node `v22.16.0`  
Campaign: #747  
Upstream contact authorized: `false`

## Results

```text
PASS concurrent first invokes share one probe and serialize once per dispatched command
PASS blocked probe selects normalized postMessage without a side-effecting POST
PASS ambiguous POST is rejected exactly once; only later invokes change transport
PASS Android regular and channel transports have independent selection state
PASS independent transport-ownership model
```

## Instrumented properties

The model counted capability probes, side-effecting custom POSTs, postMessage sends, payload serializations, user serialization-hook calls, and callback delivery.

It established that:

- concurrent first commands share a single capability probe;
- the probe does not serialize command payloads;
- a blocked probe chooses postMessage before any command POST;
- a failed custom POST rejects that invoke without cross-transport replay;
- only later invokes change transport after the ambiguous failure;
- Android regular commands and destructive channel-fetch selection use separate state.

## Limitations

This model does not execute Tauri, WebView2, WKWebView, CSP enforcement, custom URI-scheme delivery, or real channel queues. Those remain required before an interface or cross-platform claim.