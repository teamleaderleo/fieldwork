# Upstream issue draft

## In simple words

A direct pull request is preferred because the behavior is reproduced, the owning code path is narrow, and the repair has target-native regression coverage. This file retains standalone issue text in case Vite maintainers prefer discussion before source review.

## Route

`not applicable — direct pull request preferred`

Reason:

- the failure follows directly from current watcher control flow;
- a deterministic Vite-native reproduction exists;
- the change is two files with no public API addition;
- the proposed behavior extends the error-isolation intent of merged PR #22188;
- the remaining work is execution and review, not an unresolved product-design choice.

## Optional issue title

`watchChange` errors can skip module invalidation and HMR

## Optional issue body

### Description

When a plugin's `watchChange` hook rejects during a dev-server file event, Vite logs the error but exits the event handler before it performs its own module-graph invalidation and HMR processing.

This can leave a cached transform active after the watched backing file has changed.

### Prior behavior

The watcher handlers await all environment `watchChange` hooks before later Vite work. The listener-level catch reports a rejection, but it runs after the inner handler has already stopped.

This is a follow-up to #22188. That change correctly made watcher rejections observable for change, add, and unlink events. The remaining gap is continuation after the error is reported.

### Reproduction

Create a plugin that:

1. resolves a virtual module;
2. reads a text file from `load`;
3. registers that file with `this.addWatchFile`;
4. rejects `watchChange` for that file.

Transform the virtual module while the text file contains `alpha`, rewrite it to `beta`, and trigger the file-change event.

Observed result:

- the `watchChange` error is logged;
- the cached transform remains active;
- the plugin HMR path is skipped;
- the next transform still contains `alpha`.

Control result with a successful hook:

- the cache is invalidated;
- the next transform contains `beta`.

### Expected behavior

The plugin error should remain visible, while Vite continues the cache invalidation and HMR work it owns for the accepted filesystem event.

The same policy should apply to change, add, and unlink.

### Proposed direction

Settle every environment-level `watchChange` notification, log each rejection, then continue the existing event-specific Vite path.

This can remain local to the dev server watcher orchestration and preserve generic plugin hook ordering and success-path behavior.

### Compatibility

This changes the failure path only. A plugin rejection no longer suppresses later Vite-owned invalidation or HMR. Multiple environment rejections may produce multiple log entries.

### Tests

A focused regression can require:

- exact error logging;
- change-path cache invalidation and refreshed virtual-module content;
- add/create continuation into `hotUpdate`;
- unlink/delete continuation into `hotUpdate`.

## Publication notes

Before posting:

- replace shorthand `#22188` with the target repository's preferred reference style if needed;
- confirm the final public base and Vite version;
- include only public-repository reproduction details;
- remove this route note and every Fieldwork reference;
- confirm whether Vite's current AI-contribution policy requires disclosure.

Public posting remains unauthorized.
