# Campaign 0747: Tauri IPC transport selection

State: `claimed`

Issue: #747  
Parent scout: #118  
Target source: `34ec18ba5e1acabebd66ae79d6fc746f63d8eb96`  
Claim scope: `interface` after mechanism execution  
Upstream contact authorized: `false`

## In simple words

Current IPC can replay a side-effecting command through postMessage after a custom-protocol POST rejects, even though Rust may already have dispatched it. The candidate instead probes custom-protocol reachability before dispatch and never cross-transport replays an ambiguous command.

## Question

Can Tauri select IPC transport before the first side-effecting dispatch across WebView2, WKWebView, external pages, CSP restrictions, binary channels, and Android channel-data handling?

## Current evidence

- known public reload bug context is retained in issue #747 with redirect-safe references;
- `model-executed`: v2 state machine shares one HEAD probe, avoids pre-probe payload serialization, normalizes invoke headers, and does not replay ambiguous command or Android channel POST failures;
- `source-established`: only protocol POST dispatches commands; HEAD reaches the non-dispatch method-not-allowed path, which is sufficient as a reachability probe if fetch resolves.

## Required matrix

WebView2 and WKWebView local pages; external page where supported; CSP-blocked custom protocol; reload during a long command; custom headers; binary/channel traffic; failure after successful negotiation.

## Stop conditions

Stop if real webviews validate the pre-dispatch ownership model, or if platform behavior falsifies the HEAD probe. Never upgrade the Node model to cross-platform evidence.