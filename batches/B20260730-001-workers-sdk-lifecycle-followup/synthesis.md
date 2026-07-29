# Workers SDK lifecycle follow-up synthesis

State: `ready-for-synthesis`

Batch: `B20260730-001`

Issue: #88

Upstream contact authorized: `false`

Upstream contact performed: `false`

`complete` in this batch means the bounded research result is complete. It does not mean the package tests ran or that source integration is ready.

## In simple words

The batch produced three distinct Workers SDK candidates:

1. Miniflare can delay or skip terminating `workerd` when earlier cleanup fails or never settles.
2. Wrangler and Vite can choose different configuration files from the same project layout.
3. Wrangler can activate new Worker code and then fail later without clearly reporting the activation path, activated version, and failed phase.

All three have fork branches and prepared package-level tests. A001 and A003 also have bounded repair prototypes. None of the package suites executed in the available environment, so implementation promotion remains gated on a full workspace run.

## A001 — Teardown lifecycle ownership

Disposition: **accept mechanism; hold source integration for execution and test-stack split**

Confidence: **high source confidence, medium execution confidence**

Workers SDK PR: `teamleaderleo/workers-sdk#1`

Reviewed head: `eb2574f8cf7f73f244fed9733ca1902ab1e3fe7a`

The real-runtime tests target the ownership invariant: browser or proxy cleanup must not prevent the synchronous `SIGKILL` request inside `Runtime.dispose()`.

Adversarial review strengthened the proof. The kill spy now inspects each call's `this` context and counts only `SIGKILL` calls made on a child whose executable basename starts with `workerd`; an unrelated child kill can no longer satisfy the assertion.

Coordinator and follow-up review accepted:

- early rejection path;
- deterministic pending-operation path;
- post-runtime negative control;
- workerd-specific kill ownership;
- careful refusal to identify the public parallel-test hang as proven root cause.

The fourth test, preserving both initialization and cleanup failures, requires phased error aggregation that the minimal runtime-first patch intentionally does not implement. The child-ownership fix and aggregation fix should remain separate green slices.

Next gate:

- execute the first three tests before and after `runtime-first-dispose.patch`;
- prove no child, worker thread, dispatcher, or unhandled rejection remains;
- then review aggregation separately.

## A002 — Configuration selection contract

Disposition: **accept behavior-preserving protocol direction; hold default changes for compatibility evidence**

Confidence: **high source confidence, high precedent confidence, medium execution confidence**

Workers SDK PR: `teamleaderleo/workers-sdk#2`

Reviewed head: `82ffab5d51abf7b5311891f31c6aa77f42bec41f`

The source trace distinguishes four policy dimensions, and the prepared matrix now contains five groups covering six layouts:

- format precedence;
- upward versus root-only search;
- deploy-config redirect enablement;
- explicit-path convergence.

Adversarial review tightened the matrix:

- a farther parent JSON is directly compared with both a nearer child JSONC and a nearer child TOML;
- redirect wording is caller-neutral and proves the behavior flag rather than attributing it to an unverified command profile;
- the explicit-path control begins with a Vite-relative path, verifies Vite root resolution, and then hands the selected absolute path to Workers Utils.

The predecessor dependency-free discovery and redirect probes executed successfully. The cross-package matrix is committed and formally source-reviewed but remains unexecuted.

The precedent review compares TypeScript, Prettier, ESLint, Vite, Biome, Cargo, and recent Workers SDK redirect work. It shows that no single discovery anchor is universally correct:

- file-oriented tools search from the target file;
- command tools often search from the working directory;
- Vite-style project tools anchor to an explicit root;
- explicit config paths consistently override automatic discovery.

The unusual Workers behavior is format-first ancestor discovery: a farther parent JSON can beat a nearer JSONC or TOML. Existing compatibility prevents changing that silently.

The recommended direction is a shared engine with named profiles and a selection trace, not one forced default. The trace should record invocation anchor, boundary, discovery mode, extension order, redirect policy, candidates, source config, effective generated config, and stable selection reason.

Next gate:

- run the Vite package matrix on Windows and POSIX;
- verify the selected path is also parsed, watched, and reported in a complete plugin flow;
- centralize current behavior without changing outcomes;
- add `config explain` or stable verbose output;
- warn on ambiguous layouts before considering any major-version default alignment.

## A003 — Post-activation deployment state

Disposition: **accept guarded state-reporting direction; hold automatic rollback and source integration for execution**

Confidence: **high source confidence, high model confidence, medium execution confidence**

Workers SDK PR: `teamleaderleo/workers-sdk#3`

Reviewed head: `bc0dc5b064f3f4fd684b9ca8afa0b34de8489376`

The source order confirms that code activation precedes some later container and trigger operations. The deeper review corrected the path matrix:

- container workers are excluded from the versions/deployments path at the pinned revision;
- container rollout failure follows a legacy script upload;
- trigger failure can follow either a versions deployment or a legacy upload.

The receipt reports activation method, failed phase, activated version when available, and possible partial application while rethrowing the exact original error.

A review found that the original helper could let a throwing diagnostic callback replace the deployment error. The fork now wraps receipt reporting separately and treats it as best-effort. The package regression covers a throwing reporter.

The refreshed dependency-free model was executed with:

```sh
node /tmp/post-activation-state-reporting.mjs
```

The executed `/tmp` content was identical to the subsequently committed model. It passed operation-error preservation, reporting-failure preservation, activation-method distinctions, possible-partial-state receipts, and success without a receipt. The package regression remains unexecuted.

The current output order is especially weak on trigger failure: `Uploaded` appears before triggers, while `Current Version ID` appears only after triggers succeed.

Next gate:

- run the helper package tests, including the reporting-failure regression;
- add mocked legacy-upload/container failure;
- add mocked versions-deployment/trigger failure;
- add mocked legacy-upload/trigger failure;
- review terminal and machine-readable output contracts;
- apply only the reporting integration after those tests pass.

Automatic rollback remains out of scope because triggers may partially apply, containers may be retryable, activation paths differ, and rollback is another fallible deployment.

## Adjacent exploration — Vite container cleanup ownership

Disposition: **source-confirmed adjacent ownership gap; hold production changes for plugin tests**

The Vite dev and preview plugins install their current-session container tag sets and exit cleanup callbacks only after `prepareContainerImagesForDev()` fully resolves. Image preparation is sequential, and a later image build, pull, duplicate-tag cleanup, port validation, or egress-image pull can fail after earlier image work completed.

This proves a cleanup-ownership registration gap. It does not prove that a running container exists on every preparation failure path.

A dependency-free model was executed and passed these desired properties:

- cleanup ownership exists before asynchronous preparation;
- preparation failure triggers cleanup while preserving the original preparation error;
- successful cleanup clears the tag set and becomes idempotent;
- failed cleanup warns and retains the tag set for a later close/exit retry.

The A001 branch now contains:

- `container-build-cleanup.mjs` — executed model;
- `container-build-cleanup.patch` — bounded dev/preview candidate;
- updated adjacent lifecycle analysis.

The patch remains an artifact rather than a production edit. It needs mocked plugin tests for partial preparation failure, programmatic preview close, cleanup failure, and retry ownership.

## Cross-review result

A standalone A004 lane was withdrawn at user direction. Review coverage was retained and strengthened:

- coordinator reviewed A001;
- A001 reviewed and tightened A002;
- a formal A002 review accepted characterization but required execution before promotion;
- A003's activation-path matrix was corrected;
- A003's reporting-failure flaw was found, fixed, modeled, and formally reviewed;
- A001's kill assertion was narrowed to the actual workerd child;
- prior public discussion and broader tool precedent were reconciled in the lane results;
- unexecuted package tests remain explicit blockers rather than being counted as review completion.

## Recommended order

1. Execute A001's first three package regressions and validate the minimal runtime-first patch.
2. Execute A003 helper and corrected mocked deploy-flow tests; refine the output contract.
3. Execute A002's cross-selector matrix and implement behavior-preserving policy disclosure.
4. Return to A001 error aggregation and named cleanup deadlines as a separate change.
5. Add mocked Vite container-preparation/close cleanup tests before applying the adjacent patch.
6. Consider compatibility migrations only after execution evidence and ambiguous-layout review.
7. Add accepted candidates to the human review queue with exact execution evidence.

## Batch boundary

No live Cloudflare deployment, route update, container rollout, retry, or rollback was performed.

No issue, pull request, comment, review, reaction, branch, or message was created in public upstream repositories.
