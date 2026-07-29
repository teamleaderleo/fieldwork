# Deferred discovery Rust probe

This zero-dependency crate models the contract found during Fieldwork campaign #31. It does not copy Codex implementation code and it does not claim to reproduce private service behavior.

The contract is mode-aware:

- Direct mode may defer a runtime only when a model-visible, registered client-executed `tool_search` route exists.
- Code Mode may omit nested `tool_search` when `exec` exposes the deferred runtime through `ALL_TOOLS` and the global `tools` object.
- Responses Lite may carry the effective surface through an `additional_tools` item.
- A generated WebSocket request may omit an already-sent manifest only when a receipt proves that `previous_response_id` contains the identical manifest.
- Catalogue freshness is separate from route existence.

Run:

```sh
cargo test --all-targets --locked
```

The integration tests cover intended deferral, the Code Mode alternative route, direct Responses Lite delivery, verified and unverified WebSocket inheritance, missing search metadata, search-disabled fallback, and stale catalogue warnings.

The repair model is deliberately narrow:

1. Promote only logically unloadable deferred runtimes to direct exposure.
2. Send a full manifest when transport inheritance is not verified.
3. Rebuild the catalogue when the route exists but its generation is stale.
