# L01 follow-up after delivery, diagnostics, and Rust SDK review

Review date: 2026-07-30  
Related work: issue #40, draft PR #77, issue #43, merged PR #81, and implementation campaign #84

## Status correction

Campaign #31 is closed through merged PR #51. L06 is complete through merged PR #81.

Any earlier L01 wording that says L06 is still open or that its receipt remains pending is superseded by this note. Receipt v1 classifies eight normalized campaign cases: seven distinct first divergences, one healthy control, zero expectation mismatches, and seven focused tests passed. Recovery remains advisory.

## What the deeper L05 pass changes

The L01 lifecycle result remains intact: saved host dynamic tools and selected capability roots survive cold reconstruction, and the public resume/fork requests provide no current-host replacement fields.

The deeper L05 pass sharpens how that state is classified:

1. A logical discovery loader counts as effective only when it is delivered on the generated wire request or the same manifest is verified as inherited through `previous_response_id`.
2. A stale saved host generation can still have a valid, executable discovery route. That is a lifecycle-provenance warning, not a discovery-route failure.
3. A stale thread catalogue can also have a valid loader that searches an old index. That belongs to catalogue convergence rather than lifecycle provenance.

The resulting ownership split is:

- L01: saved/current generation, preserve/clear/replace/reject semantics, and lifecycle mismatch;
- L02: direct wire delivery or verified previous-response inheritance;
- L04: catalogue, binding, and search-index generation convergence;
- L05: logical loader presence, searchable metadata, and executable load-existing semantics;
- L06: first-divergence receipt joining these observations.

## Effect on the L01 fixture

The `host_old` mismatch remains a valid demonstration. It should now be read as:

```text
saved declaration preserved
+ loader may be valid
+ saved generation differs from current host generation
= stale_saved_provenance warning
```

It should not be used as evidence that discovery itself is absent.

## Current Codex recheck

The campaign pin was `openai/codex@3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`. A post-closeout recheck through `openai/codex@85c082ccccf6b5ac4d6c31d14f960057348b78f4` does not overturn the result:

- `thread/start` accepts `dynamicTools` and `selectedCapabilityRoots`;
- `thread/resume` and `thread/fork` still provide no equivalent replacement or clear fields;
- Codex pins `rmcp = 3.0.0`;
- MCP client reuse still compares configured transport, environment, credentials, authentication, and protocol-related inputs, but not remote server identity or the current tool-catalogue digest;
- `ManagedClient` still retains server information and its startup-listed tool vector;
- environment-native MCP file-upload path handling does not alter lifecycle or catalogue publication;
- the newest MCP change moves optional startup grace into the shared regular-tool catalogue cache without adding remote identity, executable-content, or catalogue-digest validation.

The recent Rust MCP dependency upgrade improves discovery identity handling and preserves typed OAuth discovery failures. It does not add host replacement semantics or invalidate a reusable Codex client when the remote identity or catalogue changes behind a stable configured connection.

## Shared regular-MCP catalogue boundary

Current Codex now shares more than cached tool definitions across connection sets. For cacheable regular stdio servers, one process-scoped entry contains:

- the cached tool snapshot and publication time;
- the newest accepted fetch generation;
- whether the server disabled caching;
- the optional-server startup deadline.

The cache key contains the configured server name, stdio command/config fingerprint, environment object identity, and local fallback directory. It does not contain the initialized server identity, executable content digest, or returned tool-catalogue digest. Replacing a server behind the same configured identity can therefore retain the old cache entry until publication, disablement, or expiry.

A later request can advertise cached catalogue A while the replacement optional client is still pending. The captured request binding contains the cached tool declarations but no prepared calls for that pending client.

Dispatch has a separate late-binding path. `handle_mcp_tool_call` refreshes dirty MCP state, asks `current_binding_for_call` to wait for the selected server's startup, and then captures the latest binding. The call therefore does not immediately fail solely because the original request binding lacked a prepared call.

The actual transition is:

```text
model plans against cached catalogue A
→ selected tool call waits for replacement client startup
→ dispatch captures live catalogue and binding B
→ tool removed in B: fail closed as unavailable
→ same-name tool changed in B: use B's metadata, approval, client, and execution behavior
```

This can be safe when A and B have the same accepted catalogue digest. Without a digest check, the model advertisement and execution authority can belong to different catalogue revisions. The current shared-deadline test proves immediate cached advertisement, but it does not compare the advertised revision with the later execution revision.

The focused falsification cases are:

1. cache A advertises a tool that B removes; verify the call waits for startup and then fails closed;
2. A and B keep the same tool name but change schema or authority metadata; verify which revision governs approval, arguments, and execution;
3. A and B have the same accepted digest; verify the delayed rebind is accepted without a mismatch warning.

The diagnostic class is `advertisement_execution_revision_mismatch`, with the cached catalogue generation, model-advertised digest, live execution digest, client startup state, and prepared-call revision recorded separately.

## Rust MCP SDK boundary

Official SDK recheck: `modelcontextprotocol/rust-sdk@cb50ae7890d8a5daacae1a4ad95f395f06733c07`.

The SDK 3.0 line adds modern discovery and lifecycle negotiation, subscription support, client-side TTL response caching, and more accurate discovery errors. Those capabilities matter, but they do not own Codex's application-level catalogue snapshot or request binding.

For tool-list changes, the SDK performs two bounded actions:

1. it invalidates its own cached `tools/list` response before notification routing;
2. it delivers `notifications/tools/list_changed` to `ClientHandler::on_tool_list_changed` or an accepted subscription channel.

The default callback is a no-op. The SDK's integration test responds to each notification by explicitly calling `list_tools` again. Codex overrides the callback only to log the notification; it does not relist tools, validate a new catalogue digest, increment a catalogue revision, or publish a new binding. The SDK cache can therefore be current while Codex's separate `ManagedClient.tools` vector remains stale.

The SDK response cache has a private generation counter. Notification invalidation advances the generation, and responses from an older in-flight generation are not written back. This is the correct ordering pattern for cache safety, but the counter is private to the SDK cache and does not order Codex's application catalogue publication.

The subscription API also leaves lifecycle policy with the caller. A subscription can end gracefully, abruptly, by cancellation, or because its bounded channel lagged; streams are not resumable after reconnect. A reusable refresh helper would therefore need to coalesce notifications, reject late relist results, expose a generation or fetch ticket, and define reconnect behavior rather than treating one callback as a complete refresh.

That separates the repair boundary:

- Codex should own relist/reconnect policy, remote identity and catalogue validation, publication revision, and request-scoped binding replacement;
- the Rust SDK could provide an opt-in relist coordinator that combines cache invalidation, notification coalescing, generation ordering, and reconnect signals, but it should not silently replace a client's published catalogue or active request binding.

The SDK current head is one fix beyond the 3.0.0 release. Release PR #1081 proposes 3.0.1 for server-information metadata on graceful subscription results. That change does not alter this lifecycle finding.

## Existing Codex publication pattern

Codex Apps already contains most of the required safe publication model:

- `hard_refresh_codex_apps_tools_cache` serializes relist and publication;
- fetch tickets accept only the newest catalogue fetch;
- each accepted publication increments one exact `tool_catalog_revision`;
- `McpBinding` freezes the advertised tools and captured clients for a request;
- `PreparedMcpCall` checks its captured revision before irreversible preparation;
- a call which already holds the old revision may finish while publication waits;
- an old prepared call that has not started irreversible preparation is rejected after the revision changes.

Generic MCP should generalize this existing policy instead of creating another publication model. Cached-startup late binding needs an additional advertised-revision check because execution may deliberately capture a newer binding.

## Receipt additions

The diagnostic receipt should retain bounded digests or generations for:

- logical advertised loader;
- direct wire manifest;
- inherited manifest and verification state;
- host catalogue, thread binding, and deferred search index;
- saved and current dynamic-tool generations;
- observed remote server identity and catalogue revision;
- shared regular-tool cache identity, snapshot generation, age, and optional startup deadline;
- model-advertised catalogue digest and live execution-binding digest;
- client startup state and prepared-call revision at dispatch;
- tool-list-change notification receipt, SDK cache invalidation, relist generation, and publication outcome;
- subscription ending state and reconnect decision when subscriptions are used;
- whether irreversible preparation had begun before publication.

These additions preserve the separate repair boundaries. Loader absence, wire omission, stale catalogue, stale saved provenance, advertisement/execution revision mismatch, and ignored or superseded list-change notification require different actions.

## CI harness rule

Owned-fork validation should be scoped to the changed language and package unless the deliverable explicitly requires the complete repository toolchain.

- For a Rust-only patch, use `cargo fmt --all -- --check` plus focused `just test -p ...` targets.
- Before using repository-wide `just fmt`, install every formatter it invokes, including `uv` and `dotslash`, or establish that those formatters are unrelated and use a narrower command.
- Record a missing runner tool as `harness_unavailable`, not as a source or behavior failure.
- Install required tools before applying or testing the candidate so the harness contract is explicit.

The first owned Codex PR #5 run applied its patch and then failed in unrelated formatters because `uv` and `dotslash` were absent. The revised workflow uses Rust-only formatting and focused tests.

## Implementation handoff

Campaign #84 is now claimed through owned Codex draft PR #5. Its first slice tests reconnecting at the host config-reload boundary while preserving ordinary per-turn reuse.

The full authority contract should follow existing Codex Apps behavior:

- a call already executing or preparing under the old revision may finish while publication waits;
- an old prepared call that has not begun irreversible preparation fails closed after publication;
- newly captured steps receive the accepted new revision.

The generic-MCP follow-up should also test cached catalogue A followed by execution binding B and require one of:

- verified equal catalogue digests;
- a typed fail-closed revision mismatch;
- an explicit policy permitting the late rebind and recording both revisions.

A separate Rust SDK scout is justified only if it tests a generic relist coordinator across concurrent notifications, out-of-order list responses, lagged subscription channels, and reconnect. Codex-specific catalogue publication remains in #84.

Public Codex and the official Rust SDK remained read-only. No upstream contact occurred.