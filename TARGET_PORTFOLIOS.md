# Active Target Portfolios

Snapshot date: 2026-07-31

This index maps the research that sits behind the short publication queue. It is organized by target and includes target hubs, programme lanes, Fieldwork pull requests, owned working-copy pull requests, campaign issues, durable file paths, and current gates.

A target-label search is only one discovery method. Cross-target work can live under another target label when the code sits in an integration package. The largest example is Cloudflare Vite plugin work: those candidates are labeled `target:workers-sdk`, even though Vite owns a major part of the mechanism.

## Playwright

### Entry points

- Target hub: [issue #10](https://github.com/teamleaderleo/fieldwork/issues/10)
- Target map: [`targets/playwright/map.md`](targets/playwright/map.md)
- Programme: [Web tooling and runtime correctness, issue #15](https://github.com/teamleaderleo/fieldwork/issues/15)
- Scout lane: [issue #26](https://github.com/teamleaderleo/fieldwork/issues/26)
- Central Fieldwork review PR: [PR #49](https://github.com/teamleaderleo/fieldwork/pull/49)
- Durable restart handoff: [issue #181](https://github.com/teamleaderleo/fieldwork/issues/181)
- Scout directory: `programmes/web-tooling-runtime-correctness/scouts/playwright-execution-isolation-artifacts/`

PR #49 contains 25 retained files: the central report, fixture teardown deep dives and execution receipts, expected-failure accounting review, Python shutdown execution, MCP video finalization execution, follow-up notes, and runnable probes.

### Owned working copies

- `teamleaderleo/playwright`
- `teamleaderleo/playwright-python`
- `teamleaderleo/playwright-mcp`
- `teamleaderleo/playwright-cli`

### Primary findings and candidates

1. **Skipped fixture cleanup before `afterAll` — issue #141.**
   - Executed Playwright PR #26 at `dfdb02284c26a179f8266a2dfe10b4787035d024`.
   - Cross-platform focused stack passed on Linux, macOS, and Windows.
   - Separation repair lives in `teamleaderleo/playwright#34` because the executed branch also carried temporary expected-failure status work.
   - Durable evidence includes `fixture-teardown-final-cross-platform-2026-07-30.md` and the related scheduler, dependency, receipt, and repository-intent notes.

2. **Unexpected cleanup failure after an expected `test.fail()` body failure — issue #142.**
   - Negative execution used `teamleaderleo/playwright#28/#29`.
   - Prototype accounting work is in `teamleaderleo/playwright#33`.
   - The unresolved design is an internal unexpected-cleanup result dimension that reaches worker replacement, retry selection, retained errors, and final outcome without mutating public status solely to force a retry.

3. **Python async stop retriability after cancellation — issue #149.**
   - Reproduction and execution used `teamleaderleo/playwright-python#1/#2` on Python 3.10 and 3.14.
   - The focused candidate is tracked in `teamleaderleo/playwright-python#3`.
   - The remaining decision compares a shared shutdown task, an explicit state machine, and resumable cleanup while preserving caller cancellation and one authoritative shutdown owner.

4. **Completed MCP video receipts after partial finalization failure — issue #153.**
   - Exact target reproduction used `teamleaderleo/playwright-mcp#1/#2`.
   - The test proved one completed video existed before a second destination failed with `EISDIR`, while the stop receipt omitted the completed path.
   - Corrected per-recording prototype work is also retained in `teamleaderleo/playwright#30`.

### Retained lower-confidence Playwright notes

- crash-resilient blob report durability;
- exact heartbeat-loss process-tree behavior;
- separate Playwright CLI video finalization behavior.

These remain bounded follow-ups. They should never be promoted by generalizing the four executed findings.

## Vercel AI SDK

### Entry points

- Target hub: [issue #2](https://github.com/teamleaderleo/fieldwork/issues/2)
- Target map: [`targets/vercel-ai/map.md`](targets/vercel-ai/map.md)
- Programme: [SDK behaviour and integration, issue #13](https://github.com/teamleaderleo/fieldwork/issues/13)
- Scout lane: [issue #17](https://github.com/teamleaderleo/fieldwork/issues/17)
- Scout PR: [PR #34](https://github.com/teamleaderleo/fieldwork/pull/34)
- Scout directory: `programmes/sdk-integration-lifecycle/scouts/vercel-ai-stream-tool-lifecycle/`
- Pinned target revision: `2b872b0db3769decf69945830c66a897c1e37347`

PR #34 contains nine retained files: the lifecycle report, plain-language explainer, adjacent SDK review, terminal-outcome follow-up, surrounding candidates, verification notes, README, and a synthetic cancellation probe with retained output.

### Owned working copy

- `teamleaderleo/ai`

### Four promoted campaigns

1. **Explicit-abort terminal settlement — issue #76.**
   - Canonical research candidate: `teamleaderleo/ai#1` at `e685a4c92a5869aec306718ab5a440b7cb4fa5b1`.
   - Repair carrier: `teamleaderleo/ai#7` at `373640d1470a89b83dcf53a218f3f03375168a90`.
   - Target execution confirmed result settlement can occur before a blocked provider read, then exposed defective ordering: callbacks can run before provider-reader cancellation and outward stream closure.

2. **Truncated provider-stream outcome classification — issue #94.**
   - Durable Fieldwork path: `campaigns/vercel-ai-truncated-stream-outcomes/`.
   - The open API question is how callers distinguish ordinary finish reason `other` from a provider connection ending before a terminal protocol event after partial semantic output.

3. **Resumable Stop state scoped to one run — issue #95.**
   - Owned candidate: `teamleaderleo/ai#3`.
   - Stable source/test head: `56453af2c2688d158d4291293a11dfe34db260e7`.
   - Current validation head: `8d46e532dfcf7af4fe776f9703bf044450c0f6da`.
   - The narrow sequential mitigation is target-executed; delayed Stop from an older run still needs durable run identity and conditional registration, Stop, finish, and persistence ownership.

4. **Idle UI stream keep-alive behind reverse proxies — issue #150.**
   - Owned candidate: `teamleaderleo/ai#4`.
   - Current candidate head: `7c8b95b12e7a47e0f614ff949b645e546488eea7`.
   - This campaign owns HTTP/SSE response liveness and explicitly excludes provider timeout, abort arbitration, resumable run identity, and incomplete-provider-stream classification.

## Gemini CLI

### Entry points

- Target hub: [issue #5](https://github.com/teamleaderleo/fieldwork/issues/5)
- Target map: [`targets/gemini-cli/map.md`](targets/gemini-cli/map.md)
- Programme: [Agent and CLI execution, issue #14](https://github.com/teamleaderleo/fieldwork/issues/14)
- Primary scout: [issue #22](https://github.com/teamleaderleo/fieldwork/issues/22)
- Primary scout PR: [PR #45](https://github.com/teamleaderleo/fieldwork/pull/45)
- Cross-agent comparison: [issue #24](https://github.com/teamleaderleo/fieldwork/issues/24) and [PR #50](https://github.com/teamleaderleo/fieldwork/pull/50)
- Scout directory: `programmes/agent-cli-execution/scouts/gemini-tool-session-recovery/`
- Pinned target revision: `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`

PR #45 contains eight retained files: the report, review packet, exploration log, follow-up, two fixed-input Node probes, and their retained outputs. PR #50 adds the neutral Gemini/Codex process vocabulary and reusable POSIX case pack.

### Owned working copy

- `teamleaderleo/gemini-cli`

### Current candidate heads

1. **Discovered-tool abort handoff — `teamleaderleo/gemini-cli#1`.**
   - Head: `30da6f7566d394150f9d62522e374c42c931c072`.
   - The project-discovered subprocess adapter receives an abort signal and discards it, allowing arbitrary child work to continue after the scheduler call is cancelled.

2. **Inline approval call affinity — `teamleaderleo/gemini-cli#2`.**
   - Head: `a7f5cc934446849e19a08cc8f4527473ada74401`.
   - Parallel modification can select the scheduler's first active call while applying the response to a different call ID.

3. **Approval waiting-state cleanup — `teamleaderleo/gemini-cli#3`.**
   - Head: `974f6e288bf3e86af0c06cb445b9626bd5d2280f`.
   - Abort or rejection can leave `onWaitingForConfirmation(true)` without the balancing `false` transition.

4. **Asynchronous kill ownership contract — `teamleaderleo/gemini-cli#4`.**
   - Head: `e33c6715cd289f912574025580cd74e4da9fe5bc`.
   - Current behavior acknowledges external process kill before asynchronous process-tree termination finishes. This remains a lifecycle-contract decision as well as a test-only candidate.

The broad execution carrier `teamleaderleo/gemini-cli#5` is closed and was never a product candidate. Three deterministic defects have target-native evidence; clean production repairs should be separate branches after the exact modification and lifecycle boundaries are accepted.

### Additional retained Gemini finding

Session persistence stores tool calls and eventual results but lacks a durable execution-lifecycle receipt. An interrupted call can resume with a context-truncation explanation even when the actual state was approval wait, cancellation, process interruption, completed side effect with lost output, or a still-running child. This needs a separate durable-recovery design.

## Vite

### Entry points

- Target hub: [issue #9](https://github.com/teamleaderleo/fieldwork/issues/9)
- Target map: [`targets/vite/map.md`](targets/vite/map.md)
- Programme: [Web tooling and runtime correctness, issue #15](https://github.com/teamleaderleo/fieldwork/issues/15)
- Primary scout: [issue #25](https://github.com/teamleaderleo/fieldwork/issues/25)
- Primary scout PR: [PR #48](https://github.com/teamleaderleo/fieldwork/pull/48)
- Scout directory: `programmes/web-tooling-runtime-correctness/scouts/vite-plugin-hmr-invalidation/`
- Pinned Vite revision: `8a245726944ed29225920d49be77c33c6e03afc8`

PR #48 contains eight retained files: the report, review audit, three execution updates, and a disposable Vite probe with README and package metadata.

### Owned working copies

- `teamleaderleo/vite`
- `teamleaderleo/vite-plus`
- `teamleaderleo/workers-sdk` for the Cloudflare Vite plugin portfolio

### Direct Vite scout candidates

1. **`watchChange` error isolation — `teamleaderleo/vite#1`.**
   - A rejecting plugin `watchChange` reaches logging and exits before Vite-owned invalidation and HMR, so later transforms can return stale cached output.
   - This is framed after merged upstream logging work; the remaining question is continuation of the file-event transaction.

2. **Post-transform import graph accuracy — `teamleaderleo/vite#2`.**
   - A hook-level `transform: { order: 'post' }` can inject imports after dev import analysis.
   - Served code and production build contain the dependency while the dev graph and HMR boundary omit it.
   - The corrected final head passed the full Vite CI matrix.

3. **Bundled-development `hotUpdate` delivery — `teamleaderleo/vite#3`.**
   - Ordinary dev delivers the plugin custom event and updates browser state.
   - Experimental bundled dev observes `watchChange` but skips `hotUpdate`, leaving stale browser state.
   - This is also documented as an experimental compatibility boundary and needs an owned integration trial before a repair decision.

### Cloudflare Vite plugin and Workers SDK portfolio

These candidates are easy to miss because they are filed under target hub #3 and label `target:workers-sdk`.

- Parent review hub: [issue #88](https://github.com/teamleaderleo/fieldwork/issues/88)
- Workers SDK scout: issue #18 and Fieldwork PR #41
- Follow-up batch: `batches/B20260730-001-workers-sdk-lifecycle-followup/`
- Batch synthesis PR: [PR #112](https://github.com/teamleaderleo/fieldwork/pull/112)

The batch includes six Vite-specific notes:

- `notes/vite-container-cleanup-ownership.md`
- `notes/vite-shared-context-ownership.md`
- `notes/vite-build-marker-scope.md`
- `notes/vite-remote-proxy-session-ownership.md`
- `notes/vite-container-registry-auth-scope.md`
- `notes/vite-wrangler-import-proxy-dispatcher.md`

The corresponding candidate issues are:

1. **#165 — preserve every container cleanup owner across preparation and exit.**
   - Per-instance exit cleanup, early ownership during partial preparation, retry ownership after failed restart cleanup, and preview close cleanup.

2. **#179 — scope Cloudflare Vite runtime state to one logical server.**
   - Isolates Miniflare, restart accounting, tunnel managers and loggers, export metadata, warning state, and process-exit warning renderers across concurrent servers and restart generations.

3. **#183 — scope build preview selection to one operation.**
   - Replaces a sticky process-wide `CLOUDFLARE_VITE_BUILD` marker with an operation-scoped build context and requires success, failure, concurrency, and child-preview characterization.

4. **#186 — own and revalidate remote binding proxy sessions.**
   - Covers account, compliance region, profile directory, Worker name, binding updates, disposed-entry reuse, session logger ownership, restart handoff, and final-close disposal.

5. **#187 — isolate container registry credentials per operation.**
   - The per-operation credential invariant is accepted; actual generated-request execution must prove endpoint, bearer token, logger, auth clearing, external-only zero-request behavior, and secret redaction.

6. **#190 — keep Wrangler library imports from replacing host fetch routing.**
   - Moves proxy dispatcher installation out of import-time module evaluation and requires explicit operation routing for embedded Wrangler/Vite API work.

## Discovery and maintenance rules

For every active target, search all of these surfaces before declaring the portfolio mapped:

1. target hub and `targets/<target>/map.md`;
2. direct target label;
3. programme hub and scout lanes;
4. open and closed Fieldwork PRs;
5. owned working-copy PRs and current exact heads;
6. campaign and batch directories;
7. handoff and review issues;
8. integration packages whose labels follow the code owner rather than the user-facing target;
9. current review queue and Delivery Desk;
10. retained negative results and superseded carriers.

The short queue answers what should finish first. This file answers what research exists.