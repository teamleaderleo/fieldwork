# Upstream pull-request draft

## Proposed title

`fix(dev): continue invalidation after watchChange errors`

## Proposed public body

### Description

A rejected plugin `watchChange` hook currently exits the dev-server file-event transaction before Vite completes the remaining plugin notifications, module-graph invalidation, and HMR work for that event.

The watcher listener logs the escaped rejection, so the first error is visible, but later hooks can be skipped and a previously transformed virtual module can remain cached after its watched backing file changes.

This follows the error-reporting work in #22188. That change handles escaped watcher promises; this change keeps a plugin notification failure from ending the file-event work Vite owns.

### Change

- add a watcher-specific plugin notification path;
- catch synchronous throws and asynchronous rejections per plugin;
- report each hook failure through the configured logger;
- preserve parallel hook groups and `sequential: true` barriers;
- wait for every applicable hook and environment before invalidation/HMR;
- use the same path for change, add, and unlink events;
- keep the existing direct `pluginContainer.watchChange()` path fail-fast.

### Regression coverage

The server regression covers:

- change rejection still invalidates a virtual-module cache and refreshes `alpha` to `beta`;
- add and unlink rejection still reach HMR with `create` and `delete` respectively;
- two failing sibling hooks both settle and both errors are reported;
- HMR cannot overtake a blocked sibling;
- a `sequential: true` hook and a later hook retain their order;
- a synchronous throw does not skip later hooks or HMR.

### Compatibility

The behavior change is limited to watcher-driven `watchChange` notifications. Hook failures remain visible, but no single plugin can veto sibling notifications or the cache/HMR work Vite owns for the filesystem event.

Successful hooks retain their existing parallel grouping and sequential barriers. The direct plugin-container method retains its current fail-fast behavior.

No public API, configuration option, dependency, generated output, or lockfile changes.

### Tests

- Vite build, lint, formatting, typecheck, documentation, and workflow checks
- focused `watchChange` error-isolation regression
- complete Build&Test on Ubuntu with Node 20, 22, 24, and 26
- complete Build&Test on macOS with Node 24
- complete Build&Test on Windows with Node 24.15.0
- Zizmor

## Internal synchronization notes — do not include publicly

- Public base/current main at preparation: `e6b6b167afa0a80548829d1f24a0712f9194389a`
- Canonical source head: `ba8ac979ee91c77fdd91304ccde38942e9752133`
- Exact source diff: three files
- CI: `30753769684` — success
- Zizmor: `30753769710` — success
- Pre-review disposition: `ACCEPT`
- Public upstream contact: unauthorized; interactions zero

## Filing checklist

Before public use:

1. confirm current Vite main and duplicate/prior-art state;
2. confirm current contribution and AI-disclosure requirements;
3. re-run focused and ordinary gates if source or base moves materially;
4. copy only the proposed title and proposed public body;
5. obtain explicit authority for the exact public pull request.
