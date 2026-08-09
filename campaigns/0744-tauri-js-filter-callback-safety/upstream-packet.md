# Upstream Packet: avoid running filtered-event predicates under JS listener and webview-store locks

Campaign: #744  
Target: `tauri-apps/tauri`  
State: `candidate — preparation only`

> Preparation only. Fieldwork automation must never mutate third-party upstream repositories. A human must perform any upstream interaction manually.

## Proposal

Snapshot the webviews and JS listener metadata selected at dispatch start, release the internal mutexes, and only then evaluate the caller-supplied event filter and emit to the selected listener IDs.

## Current behavior

`AppManager::emit_filter` passes `self.webview.webviews_lock().values()` into `Listeners::emit_js_filter`. `emit_js_filter` then holds `js_event_listeners` while evaluating the public filter predicate.

Consequences established by owned-fork controls:

- a filter panic can poison the JS-listener registry;
- synchronous listener mutation from the predicate conflicts with the registry lock;
- synchronous `get_webview()` from the public predicate conflicts with the webview-store lock.

## Candidate behavior

```text
dispatch starts
  -> clone current Webview handles
  -> clone current JsHandler metadata for this event
  -> release both guards
  -> evaluate caller filter
  -> emit using the dispatch-start snapshots
```

Listener additions/removals during filtering affect the next dispatch. The current dispatch keeps its start-of-dispatch selection.

## Scope

Included:

- `crates/tauri/src/event/listener.rs`
- `crates/tauri/src/manager/mod.rs`
- panic/add/remove listener regressions
- serialized and string-payload webview lookup regressions
- normal `tauri` patch-level change record

Excluded:

- Rust-side handler mutex panic recovery (campaign #749)
- event API redesign
- callback ordering changes beyond explicit dispatch-start snapshot semantics
- public API changes

## Verification

Exact-source snapshot candidate and true-reentrancy run `31330593081` passed:

- predicate panic recovery;
- listener-registry lock availability;
- reentrant `unlisten_js`;
- reentrant `listen_js` with next-dispatch visibility;
- webview-store lock availability;
- serialized-payload `get_webview()` reentry;
- string-payload `get_webview()` reentry.

Current-public-dev canonical run `31330943085` passed:

- candidate application;
- canonical `cargo fmt` normalization and idempotent `cargo fmt --check`;
- `git diff --check`;
- reviewer-facing listener regressions;
- reviewer-facing manager regressions;
- nearby event/listener tests;
- nearby manager tests;
- clippy with warnings denied.

Exact canonical patch artifact:

- name: `fieldwork-744-js-filter-candidate`
- SHA-256: `9fd45e7447710c1458415377337786e5b8e088c2e005acf2277d5d900c9fcbac`
- durable copy: `campaigns/0744-tauri-js-filter-callback-safety/candidate.patch`

## Suggested change entry

```md
---
'tauri': 'patch:bug'
---

Avoid holding JS listener and webview-store locks while evaluating filtered event predicates.
```

## Review notes

The candidate intentionally uses dispatch-start snapshots. A cloned webview handle or listener record may remain in the current dispatch even if the manager/registry changes while the filter is running. This is what permits synchronous reentry and is explicitly covered for listener add/remove semantics.

The Rust-side listener path also evaluates the same filter closure under its handler mutex, but nested Rust listener operations use the pending queue rather than blocking. Its remaining panic-poisoning case belongs to #749; that campaign's existing catch/drop/flush/resume candidate encloses filter evaluation and now has a dedicated filter-panic discriminator queued.

## AI assistance and human accountability

AI systems mapped the source, generated/refined candidate code and tests, and coordinated owned-fork validation. Tauri's current contribution policy requires the human submitter to personally review and test all LLM-generated content and forbids using AI to answer review comments except translation.

Before any human submission, the human should inspect every changed line, rerun the stated tests as desired, write the PR explanation in their own words, and handle all maintainer discussion personally.

No automated upstream interaction occurred.
