# Current-head receipt — 2026-08-01

## Review fence

- Work class: upstream-fork source candidate
- Public Vite base: `e6b6b167afa0a80548829d1f24a0712f9194389a`
- Canonical owned source: `a2ab7ca6183ad74d64066d6706e57a546e355224`
- Canonical source branch: `fix/fieldwork-25-watchchange-error-isolation`
- Canonical source PR: [`teamleaderleo/vite#4`](https://github.com/teamleaderleo/vite/pull/4)
- Diff relation: two commits ahead, zero behind
- Diff inventory: exactly two files, 198 additions, 12 deletions
- Current self-review: [`comment 5148481573`](https://github.com/teamleaderleo/vite/pull/4#issuecomment-5148481573)

Any source-head movement expires this receipt.

## Complete-diff source review

Result:

- server-local environment fanout is the narrow ownership boundary;
- `EnvironmentPluginContainer.watchChange` is async and exposes synchronous throws and asynchronous rejections as rejected environment promises;
- settle-all preserves the successful-path ordering boundary and reports every rejection;
- existing invalidation, public-file, deletion, restart, and HMR work remains in place after notification;
- complete source diff contains no temporary workflow, research artifact, dependency, lockfile, generated output, or internal-only documentation;
- no blocking product-code defect was found by self-review.

## Current-head workflows

### Zizmor

- Run: [`30674314445`](https://github.com/teamleaderleo/vite/actions/runs/30674314445)
- Result: `success`

### CI

- Run: [`30674314447`](https://github.com/teamleaderleo/vite/actions/runs/30674314447)
- Changed-files: `success`
- Lint pipeline: `success`
  - dependency installation
  - repository build
  - lint
  - formatting check
  - typecheck
  - documentation tests
  - workflow-file checks
- Linux Node 20 Build&Test: `success`
- Linux Node 22 Build&Test: `success`
- Linux Node 24 Build&Test: `success`
- Linux Node 26 Build&Test: `success`
- macOS Node 24 Build&Test: `success`

Successful Build&Test jobs completed the Vite workflow's unit, serve, bundled-development, and build-mode steps.

### Windows retained evidence

Attempt 1, job [`91298369805`](https://github.com/teamleaderleo/vite/actions/runs/30674314447/job/91298369805):

- build passed;
- unit suite passed;
- Unit 01 focused file passed 3/3;
- later ordinary serve failed in existing `playground/hmr-ssr` while waiting for an HMR console update.

Attempt 2, job [`91344104649`](https://github.com/teamleaderleo/vite/actions/runs/30674314447/job/91344104649):

- build passed;
- unit suite passed;
- Unit 01 focused file passed 3/3;
- ordinary serve passed: 91 files passed, 17 skipped; 1128 tests passed, 165 skipped;
- bundled-development later failed three timing/state assertions in the same existing HMR/SSR playground;
- build-mode was not reached because the bundled-development step stopped the job.

Classification: unrelated Windows HMR/SSR integration flakiness. The failure moved between ordinary serve and bundled-development while the Unit 01 regression stayed green and all Linux/macOS full jobs passed. This is an accepted ordinary-gate limitation, not a product or focused-test failure.

Attempt 3, job [`91344668365`](https://github.com/teamleaderleo/vite/actions/runs/30674314447/job/91344668365), was requested as supplementary evidence and was queued at receipt reconciliation. Its outcome should be appended if it changes the evidence, but source changes require a Unit 01-linked failure rather than another unrelated HMR/SSR timeout.

### Preview

- Run: [`30674314449`](https://github.com/teamleaderleo/vite/actions/runs/30674314449)
- Result: `skipped`
- Classification: expected internal-source PR behavior; no product claim

## Synthetic merge note

The pull-request workflow checkout used a synthetic merge containing source head `a2ab7ca6183ad74d64066d6706e57a546e355224` on the owned repository's current default-branch head. The canonical source and complete-diff fence remain the explicit comparison `e6b6b167...a2ab7ca6`.

Do not cite the synthetic merge as the canonical source revision. It is retained as compatibility execution containing the exact source head.

## Disposition

`ACCEPT`

The exact source candidate is suitable for independent final review. The author is not the sole eligible final accepter. This receipt does not authorize merge or public upstream interaction.

## Next transition

- independent complete-diff review at the unchanged source head;
- current-main, duplicate, contribution-policy, and validation refresh immediately before any authorized public submission;
- explicit user authority for the exact public interaction.

Public upstream interactions for Unit 01: zero.
