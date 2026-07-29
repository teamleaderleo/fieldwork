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

All three now have fork branches and prepared package-level test designs. A001 and A003 also have bounded repair prototypes. None of the package suites executed in the available environment, so implementation promotion remains gated on a full workspace run.

## A001 — Teardown lifecycle ownership

Disposition: **accept mechanism; hold source integration for execution and test-stack split**

Confidence: **high source confidence, medium execution confidence**

Workers SDK PR: `teamleaderleo/workers-sdk#1`

The real-runtime tests correctly target the ownership invariant: browser or proxy cleanup must not prevent the synchronous `SIGKILL` request inside `Runtime.dispose()`.

Coordinator review accepted:

- early rejection path;
- deterministic pending-operation path;
- post-runtime negative control;
- careful refusal to identify the public parallel-test hang as proven root cause.

Coordinator review also found that the fourth test, preserving both initialization and cleanup failures, requires phased error aggregation that the minimal runtime-first patch intentionally does not implement. The child-ownership fix and aggregation fix should be separate green slices.

Next gate:

- execute the first three tests before and after `runtime-first-dispose.patch`;
- prove no child, worker thread, dispatcher, or unhandled rejection remains;
- then review aggregation separately.

## A002 — Configuration selection contract

Disposition: **accept behavior-preserving protocol direction; hold default changes for compatibility evidence**

Confidence: **high source confidence, high precedent confidence, medium execution confidence**

Workers SDK PR: `teamleaderleo/workers-sdk#2`

The source trace distinguishes four independent policy dimensions, and the prepared package matrix is designed to verify them:

- format precedence;
- upward versus root-only search;
- deploy-config redirect enablement;
- explicit-path convergence.

The predecessor dependency-free discovery and redirect probes executed successfully. The cross-package matrix is committed and source-reviewed but remains unexecuted.

The precedent review compares TypeScript, Prettier, ESLint, Vite, Biome, Cargo, and recent Workers SDK redirect work. It shows that no single discovery anchor is universally correct:

- file-oriented tools search from the target file;
- command tools often search from the working directory;
- Vite-style project tools anchor to an explicit root;
- explicit config paths consistently override automatic discovery.

The unusual Workers behavior is format-first ancestor discovery: a farther parent JSON can beat a nearer JSONC or TOML. Existing compatibility prevents changing that silently.

Merged upstream PR `cloudflare/workers-sdk#14897` strengthens the concern about caller drift: `wrangler triggers deploy` had to opt into the generated-config redirect already used by other deployment commands.

The recommended direction is a shared engine with named profiles and a selection trace, not one forced default. The trace should record invocation anchor, boundary, discovery mode, extension order, redirect policy, candidates, source config, effective generated config, and stable selection reason.

Next gate:

- run the Vite package matrix;
- review fixtures on Windows and POSIX;
- centralize current behavior without changing outcomes;
- add `config explain` or stable verbose output;
- warn on ambiguous layouts before considering any major-version default alignment.

## A003 — Post-activation deployment state

Disposition: **accept guarded state-reporting direction; hold automatic rollback and source integration for execution**

Confidence: **high source confidence, high model confidence, medium execution confidence**

Workers SDK PR: `teamleaderleo/workers-sdk#3`

The source order confirms that code activation precedes some later container and trigger operations. The deeper review corrected the path matrix:

- container workers are excluded from the versions/deployments path at the pinned revision;
- container rollout failure follows a legacy script upload;
- trigger failure can follow either a versions deployment or a legacy upload.

The corrected executable model reports activation method, failed phase, activated version when available, and possible partial application while rethrowing the exact original error.

A review found that the original helper could let a throwing diagnostic callback replace the deployment error. The fork now treats receipt reporting as best-effort. The dependency-free model was updated with a throwing receipt sink and executed successfully, proving that the original operation error remains authoritative. The equivalent package regression is prepared but remains unexecuted.

The current output order is especially weak on trigger failure: `Uploaded` appears before triggers, while `Current Version ID` appears only after triggers succeed.

The receipt is needed because an exit code describes whole-command completion, not the remote state already changed. This follows established partial-apply practice: Terraform records successful changes even when apply later fails; CloudFormation exposes preserve, retry, update, and rollback as distinct policies; Kubernetes separates desired state from observed status and conditions.

Next gate:

- run the helper package tests, including the reporting-failure regression;
- add mocked legacy-upload/container failure;
- add mocked versions-deployment/trigger failure;
- add mocked legacy-upload/trigger failure;
- review terminal and machine-readable output contracts;
- apply only the reporting integration after those tests pass.

Automatic rollback remains out of scope because triggers may partially apply, containers may be retryable, activation paths differ, and rollback is another fallible deployment.

## Cross-review result

A standalone A004 lane was withdrawn at user direction. Review coverage was retained:

- coordinator reviewed A001;
- A001 reviewed the predecessor A002 matrix;
- coordinator built and reviewed A002 and A003;
- later review corrected A002's evidence wording and exposed A003's reporting-failure edge case;
- the A003 dependency-free model was strengthened and rerun after that review;
- prior public discussion and broader tool precedent were reconciled in the lane results;
- unexecuted package tests remain explicit blockers rather than being counted as review completion.

## Portfolio context

Recent Fieldwork work reinforces two useful conventions for these candidates:

- Playwright cleanup work records per-finalizer completion, failure, timeout, and not-started states instead of collapsing cleanup into one success bit.
- Codex operation work preserves the original operation result while adding bounded receipts for uncertain side effects.

A003 follows the same useful pattern: add a state receipt without replacing the original error. A001 should follow it when phased cleanup aggregation is designed.

Fieldwork PR #105 now provides a human review queue and evidence index as the first implementation slice for meta issue #87. This batch should feed that queue rather than create a second manually maintained board.

## Recommended order

1. Execute A001's first three package regressions and validate the minimal runtime-first patch.
2. Execute A003 helper and corrected mocked deploy-flow tests; refine the output contract.
3. Execute A002's cross-selector matrix and implement behavior-preserving policy disclosure.
4. Return to A001 error aggregation and named cleanup deadlines as a separate change.
5. Consider compatibility migrations only after execution evidence and ambiguous-layout review.
6. Add accepted candidates to the human review queue with exact execution evidence.

## Batch boundary

No live Cloudflare deployment, route update, container rollout, retry, or rollback was performed.

No issue, pull request, comment, review, reaction, branch, or message was created in public upstream repositories.
