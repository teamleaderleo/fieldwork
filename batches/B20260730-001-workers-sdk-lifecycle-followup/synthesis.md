# Workers SDK lifecycle follow-up synthesis

State: `ready-for-synthesis`

Batch: `B20260730-001`

Issue: #88

Upstream contact authorized: `false`

Upstream contact performed: `false`

## In simple words

The batch produced three distinct Workers SDK candidates:

1. Miniflare can delay or skip terminating `workerd` when earlier cleanup fails or never settles.
2. Wrangler and Vite can choose different configuration files from the same project layout.
3. Wrangler can activate new Worker code and then fail later without clearly reporting the activated version and failed phase.

All three now have fork branches and package-level test designs. A001 and A003 also have bounded repair prototypes. None of the package suites executed in the available environment, so implementation promotion remains gated on a full workspace run.

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

Disposition: **accept characterization; decide shared disclosure versus shared defaults before implementation**

Confidence: **high source confidence, medium execution confidence**

Workers SDK PR: `teamleaderleo/workers-sdk#2`

The package matrix demonstrates four independent policy dimensions:

- format precedence;
- upward versus root-only search;
- deploy-config redirect enablement;
- explicit-path convergence.

The strongest practical result is not that one selector is universally wrong. It is that callers cannot inspect one shared policy/result record explaining why a source or generated config was selected.

Next gate:

- run the Vite package matrix;
- review fixtures on Windows and POSIX;
- decide whether compatibility permits any default alignment;
- otherwise implement shared policy disclosure first.

## A003 — Post-activation deployment state

Disposition: **accept state-reporting direction; hold automatic rollback**

Confidence: **high source confidence, medium-high model confidence, medium execution confidence**

Workers SDK PR: `teamleaderleo/workers-sdk#3`

The source order confirms that code activation precedes container and trigger operations. The executable model confirms a bounded receipt can report phase and version while rethrowing the exact original error.

The current output order is especially weak on trigger failure: `Uploaded` appears before triggers, while `Current Version ID` appears only after triggers succeed.

Next gate:

- run helper tests;
- add mocked deploy-helper failures for new and legacy upload paths;
- review terminal and machine-readable output contracts;
- apply only the reporting integration after those tests pass.

Automatic rollback remains out of scope because triggers may partially apply, containers may be retryable, and rollback is another fallible deployment.

## Cross-review result

A standalone A004 lane was withdrawn at user direction. Review coverage was retained:

- coordinator reviewed A001;
- A001 reviewed the predecessor A002 matrix;
- coordinator built and reviewed A002 and A003;
- prior public discussion was reconciled in the scout and lane results;
- unexecuted package tests remain explicit blockers rather than being counted as review completion.

## Portfolio context

Recent Fieldwork work reinforces two useful conventions for these candidates:

- Playwright cleanup work records per-finalizer completion, failure, timeout, and not-started states instead of collapsing cleanup into one success bit.
- Codex operation work preserves the original operation result while adding bounded receipts for uncertain side effects.

A003 follows the same useful pattern: add a state receipt without replacing the original error. A001 should follow it when phased cleanup aggregation is designed.

Fieldwork PR #105 now provides a human review queue and evidence index as the first implementation slice for meta issue #87. This batch should feed that queue rather than create a second manually maintained board.

## Recommended order

1. Execute A001's first three package regressions and validate the minimal runtime-first patch.
2. Execute A003 helper and mocked deploy-flow tests; refine the output contract.
3. Execute A002's cross-selector matrix and make a compatibility decision.
4. Return to A001 error aggregation and named cleanup deadlines as a separate change.
5. Add accepted candidates to the human review queue with exact execution evidence.

## Batch boundary

No live Cloudflare deployment, route update, container rollout, retry, or rollback was performed.

No issue, pull request, comment, review, reaction, branch, or message was created in public upstream repositories.
