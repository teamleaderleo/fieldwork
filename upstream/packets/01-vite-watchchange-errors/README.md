# Unit 01 — Vite `watchChange` error isolation

## Current disposition

`ACCEPT`

The exact three-file source at `ba8ac979ee91c77fdd91304ccde38942e9752133` passed the complete current Vite CI matrix and Zizmor. A final complete-diff pre-review found no blocking source defect.

This is an owned-fork review packet. It does not authorize merge or public upstream interaction.

## Assignment

- Unit: `01`
- Routing board: `teamleaderleo/fieldwork#435`
- Target: `vitejs/vite`
- Proposed title: `fix(dev): continue invalidation after watchChange errors`
- Source PR: `teamleaderleo/vite#4`
- Packet PR: `teamleaderleo/fieldwork#438`
- Public upstream contact authorized: `no`
- Public upstream interactions: `zero`

## Exact revisions

- Public Vite base and current public main: `e6b6b167afa0a80548829d1f24a0712f9194389a`
- Canonical source branch: `fix/fieldwork-25-watchchange-error-isolation`
- Canonical source head: `ba8ac979ee91c77fdd91304ccde38942e9752133`
- Packet branch: `p0/435-unit-01-vite-watchchange-errors`

Any source or public-base movement expires this fence.

## Failure model

The public watcher transaction awaits plugin `watchChange` notifications before cache invalidation, public-file/deletion work, and HMR. A rejected hook escapes that transaction, so listener-level logging happens only after Vite-owned work has already been skipped.

A first repair settled environments, but each environment still used fail-fast parallel hook execution. One fast rejection could let Vite continue while a slower sibling hook remained live, hide later failures, and skip a later `sequential: true` barrier.

## Selected repair

For watcher-driven server events only:

- run every applicable plugin notification;
- catch synchronous throws and asynchronous rejections per plugin;
- report each plugin failure;
- preserve parallel hook groups and `sequential: true` barriers;
- wait for every applicable hook before invalidation and HMR;
- track asynchronous hook promises so environment close waits them;
- settle environment-level infrastructure failures separately;
- keep the documented direct `pluginContainer.watchChange()` path fail-fast and unchanged.

The specialized method is internal and was verified absent from generated declarations.

## Source scope

Exactly three files:

1. `packages/vite/src/node/server/index.ts`
2. `packages/vite/src/node/server/pluginContainer.ts`
3. `packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js`

No workflow, restart trigger, dependency, lockfile, generated output, research fixture, or Fieldwork-only file is present on the canonical source branch.

## Repairs discovered during continuation

The live source PR had temporarily drifted to a five-file carrier head. The workflow and restart-trigger files were removed from the canonical branch.

Ordinary type checking then found two source errors:

1. the sorted-hook loop did not narrow the optional hook before `getHookHandler`;
2. `shouldRunWatchChange()` could return `undefined` despite declaring `boolean`.

Head `ba8ac979...` repairs both narrowly without changing lifecycle policy or public API.

## Target-native coverage

The focused suite covers:

1. change rejection logs, invalidates the virtual-module cache, reaches HMR, and refreshes `alpha` to `beta`;
2. add rejection reaches create-typed HMR;
3. unlink rejection reaches delete-typed HMR;
4. two failing sibling hooks both settle and both errors are reported;
5. HMR cannot overtake a blocked sibling;
6. a sequential barrier and later hook retain their order;
7. a synchronous throw does not skip later hooks or HMR.

## Exact execution

### Zizmor

Run `30753769710`: **success**.

### CI

Run `30753769684`: **success**.

Passed:

- changed-file discovery;
- repository build;
- lint;
- formatting;
- typecheck;
- documentation tests;
- workflow-file checks;
- complete Build&Test on Ubuntu Node 20, 22, 24, and 26;
- complete Build&Test on macOS Node 24;
- complete Build&Test on Windows Node 24.15.0;
- final `Build & Test Passed or Skipped` aggregate.

Every Build&Test job completed build, unit tests, ordinary serve tests, bundled-development serve tests, and build tests. The failure aggregate was skipped.

Preview run `30753769692` skipped as expected for the internal PR.

## Complete-diff pre-review

Accepted observations:

- the helper sits at the watcher/server ownership boundary;
- plugin failures are contained per hook rather than per environment;
- sequential barriers still wait for the preceding parallel group;
- all environments are awaited before later Vite-owned work;
- infrastructure failures remain observable through the outer settle-all layer;
- change/add/unlink ordering after notification remains unchanged;
- the direct public hook path retains its existing fail-fast behavior;
- a throwing custom logger can still interrupt reporting, matching existing logger assumptions and remaining outside this unit;
- no source, test, lifecycle, or compatibility blocker was found.

## Prior art and duplicate result

Merged Vite PR `#22188` added listener-level catches and logging tests for add/change/unlink. It did not continue the inner watcher transaction after hook failure and did not settle sibling plugin hooks.

Fresh searches found no open overlapping repair. Repeat current-main, duplicate, and contribution-policy checks immediately before any authorized public submission.

## Compatibility limits

- Plugin failures remain visible but no longer veto sibling notifications or Vite-owned invalidation/HMR.
- Successful hooks retain parallel execution and sequential barriers.
- Simultaneous error ordering is not promised.
- A throwing custom logger remains a separate policy question.
- Separate filesystem events remain independently concurrent.
- The repair does not undo arbitrary partial state inside a failing plugin.
- Add/unlink controls prove event mapping and continuation, not every platform-specific downstream mutation.

## Packet navigation

- `ADVERSARIAL_AUDIT.md` — sibling-plugin race and repair contract
- `DEEP_DIVE.md` — ownership, lifecycle, compatibility, and evidence model
- `APPROACHES.md` — selected, losing, rejected, and deferred approaches
- `TESTS.md` — exact execution ledger
- `REVIEW.md` — exact three-file inspection guide
- `UPSTREAM_ISSUE.md` — optional issue route
- `UPSTREAM_PR.md` — held public-facing draft
- `receipts/current-head-2026-08-01.md` — compact final receipt

## Next transition

Human review may inspect source PR #4 and this packet. Before any public filing, refresh public main, duplicates, contribution instructions, and the public draft, then obtain explicit authorization for the exact upstream action.
