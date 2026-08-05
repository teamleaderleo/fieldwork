# Upstream issue draft

## In simple words

A direct pull request is preferred because the behavior is reproduced, the owning code path is narrow, the repair has target-native regression coverage, and the source packet is ready for independent review. This file retains standalone issue text only in case Vite maintainers prefer discussion before source review.

## Route

`not applicable — direct pull request preferred`

Reason:

- the failure follows directly from inspected watcher control flow;
- a deterministic Vite-native reproduction exists;
- the change is two files with no public API addition;
- the proposed behavior extends the error-isolation intent of merged PR #22188;
- the remaining transition is independent acceptance and authorization, not an unresolved product-design choice.

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

This can remain local to the dev-server watcher orchestration and preserve generic plugin hook ordering and success-path behavior.

### Compatibility

This changes the failure path only. A plugin rejection no longer suppresses later Vite-owned invalidation or HMR. Multiple environment rejections may produce multiple log entries.

### Tests

A focused regression requires:

- exact error logging;
- change-path cache invalidation and refreshed virtual-module content;
- add/create continuation into `hotUpdate`;
- unlink/delete continuation into `hotUpdate`.

The retained candidate includes and has executed those controls.

## Publication notes

Before posting:

- use the target repository's preferred reference style for #22188;
- refresh the final public base and Vite version;
- repeat duplicate and contribution-policy checks;
- include only public-repository reproduction details;
- remove this route note and every Fieldwork reference;
- confirm whether Vite's current AI-contribution policy requires disclosure;
- obtain explicit authority for the exact public interaction.

Public posting remains unauthorized.
