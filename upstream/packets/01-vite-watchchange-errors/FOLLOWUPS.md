# Follow-up research map — Vite `watchChange` failure boundaries

## Purpose

This file separates work that can still change Unit 01's disposition from adjacent research that should not inflate the current contribution.

Current canonical source: `79fa097750158790ec9bf03d74e6f83d702dd4c2`

Current disposition: `REPAIR` while exact-head ordinary gates and packet reconciliation remain open.

Public upstream interaction remains unauthorized and zero.

## Promotion-critical work

### 1. Exact-head ordinary reconciliation

Required:

- CI build, unit, serve, bundled-development, and build tests on Linux Node 20/22/24/26;
- the same complete sequence on macOS Node 24 and Windows Node 24.15;
- lint pipeline including build, formatting, typecheck, docs, and workflow checks;
- Zizmor;
- exact failure classification for any non-green job.

Current partial result:

- macOS Node 24: complete success;
- Windows Node 24.15: complete success, including the previously flaky HMR/SSR families;
- Linux jobs and lint: queued at the latest snapshot;
- Zizmor: queued.

### 2. Complete-diff source review

Review the exact three-file fence for:

- plugin scheduler ordering and barrier preservation;
- synchronous throw handling;
- asynchronous promise tracking;
- environment filtering parity;
- direct compatibility path parity;
- internal method stripping;
- logger and error-identity behavior;
- cleanup behavior on assertion failure;
- no temporary execution machinery.

### 3. Packet and public-draft reconciliation

The following must name one final source and packet head:

- `README.md`;
- `DEEP_DIVE.md`;
- `ADVERSARIAL_AUDIT.md`;
- `APPROACHES.md`;
- `TESTS.md`;
- `REVIEW.md`;
- current receipt;
- source PR body;
- packet PR body;
- routing-board handoff;
- upstream issue and PR drafts.

### 4. Independent acceptance

The author can perform complete-diff self-review but cannot be the sole final accepter. Independent review should focus on the scheduler boundary rather than re-running only the original stale-cache case.

## High-value optional controls inside Unit 01

These controls add confidence but are not automatically source requirements. Add them only if exact review finds an unproven material branch.

### A. Per-environment settlement

Why it matters:

Vite creates `client` and `ssr` environments by default. For backward compatibility, ordinary plugins receive `watchChange` only in `client`. Plugins can opt into per-environment calls with the experimental `perEnvironmentWatchChangeDuringDev` flag.

Potential control:

- opt one plugin into per-environment notification;
- block or reject one environment while another settles;
- prove Vite does not start HMR until both environment notifications finish;
- prove both environment errors remain visible;
- verify `hotUpdate` still runs in its documented environment order.

Reason not yet added:

The current source uses explicit environment-level `Promise.allSettled`, and the focused plugin-level control already proves the harder sibling-hook race. Adding an experimental-environment fixture may add more setup than discrimination unless review identifies a credible outer-fanout regression.

### B. Close while a notification hook is blocked

Potential control:

- start a blocked asynchronous `watchChange` hook;
- call `server.close()` before releasing it;
- prove close remains pending;
- release the hook;
- prove close completes without abandoning or double-running the hook.

Supporting source trace:

- the specialized scheduler wraps async results with `handleHookPromise`;
- `handleHookPromise` stores the original promise in `_processesing` and removes it only on settlement;
- `EnvironmentPluginContainer.close()` waits that set;
- `DevEnvironment.close()` awaits `pluginContainer.close()`.

Reason not yet added:

The lifecycle path is direct and existing source already uses the same tracker for other plugin hooks. Add this control if independent review requires executable lifecycle evidence.

### C. Direct compatibility path

Potential control:

Call `server.pluginContainer.watchChange(id, change)` directly without the internal method and assert the prior fail-fast rejection behavior.

Reason not yet added:

The public method body still calls the original generic `hookParallel` path, and the specialized method is separate and stripped from declarations. A test would lock an internal failure policy that may not deserve stronger public-contract status.

### D. Public-file and deletion side effects

Potential controls:

- add a file under `publicDir`, reject `watchChange`, and prove public-file bookkeeping updates before HMR;
- unlink a transformed module, reject `watchChange`, and prove delete graph maintenance removes or invalidates expected nodes before HMR.

Reason not yet added:

Current add/unlink controls prove event mapping and HMR continuation. These deeper state assertions would expand fixture complexity and platform sensitivity. Add them only if maintainers require direct evidence for every downstream branch.

## Separate future candidates

These are related findings but should not ride in Unit 01 without a new reproduction and ownership decision.

### 1. Overlapping filesystem-event transactions

Current behavior:

Change, add, and unlink listeners start independent asynchronous workers. Separate events can overlap even after each event waits its own plugin notifications.

Questions:

- Can rapid events for the same path reorder invalidation or HMR?
- Should Vite serialize per path, debounce, coalesce, or preserve maximum concurrency?
- How do editors' atomic-save patterns interact with create/delete/update sequences?
- Does restart-sensitive config handling race ordinary file events?

Why separate:

Global or per-path serialization affects latency and plugin expectations and is not required by the reproduced rejection defect.

### 2. Throwing custom logger policy

Current behavior:

The specialized path calls the configured logger while handling plugin failures. A custom logger that throws can interrupt reporting. Existing watcher listener catches also assume logger calls return normally.

Questions:

- Should logging failures ever veto Vite-owned cleanup or HMR?
- Should logging be wrapped, deferred, or sent through a non-throwing fallback?
- How should the original plugin error and logger error both remain observable?

Why separate:

This is a general logging reliability policy, not a `watchChange`-specific contract.

### 3. Error attribution

Current behavior:

Each original error object is passed to the configured logger. The server does not add environment or plugin identity.

Questions:

- Should watcher errors include plugin name and environment name?
- Can attribution be added without changing error identity or duplicating Rollup diagnostics?
- Is structured logger metadata preferable to message wrapping?

Why separate:

Attribution changes diagnostics, not continuation correctness.

### 4. Generic parallel-hook failure policy

Current behavior:

Generic `hookParallel()` remains fail-fast for hooks other than the specialized watcher path.

Questions:

- Do other notification-style parallel hooks own similar settle-all semantics?
- Which hooks are advisory notifications versus transaction veto points?
- Can a reusable internal scheduler policy avoid duplicate barrier logic without broad behavior change?

Why separate:

Hook contracts differ. A global settle-all change would be unsafe without hook-by-hook analysis.

### 5. Scheduler implementation reuse

Current implementation duplicates the small ordinary parallel-group loop in a specialized helper.

Questions:

- Would a shared private scheduler accepting a hook runner reduce maintenance drift?
- Can that abstraction preserve generic fail-fast behavior and specialized promise tracking exactly?
- Is the abstraction clearer than the current localized duplication?

Current decision:

Do not refactor during exact-head validation. The duplicate helper is bounded and tested; changing private generic scheduling would enlarge the review surface without fixing a demonstrated defect.

## Explicitly rejected expansion

- serializing every plugin hook;
- changing generic `hookParallel()` failure behavior globally;
- introducing a new aggregate error type;
- adding a public configuration option;
- recovering arbitrary partial plugin state;
- modifying production-build watcher behavior;
- changing logger policy inside this contribution;
- contacting public upstream without explicit authorization.

## Research order after Unit 01 stabilizes

1. characterize same-path overlapping event transactions;
2. test close/restart with a deliberately blocked watcher hook;
3. decide whether error attribution is useful to maintainers;
4. audit other notification-style parallel hooks for the same ownership boundary;
5. only then consider scheduler abstraction reuse.
