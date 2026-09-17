# Playwright fixture teardown CI run 1 — 2026-07-30

## Run

| Field | Value |
|---|---|
| Repository | `teamleaderleo/playwright` |
| Execution PR | `#5` |
| Workflow | `Fieldwork fixture teardown` |
| Run ID | `30476774439` |
| Job ID | `90660339493` |
| Head at run | `82c045c9223f590a7147fe75a2d8816cdcff6dec` |
| Budget prototype base | `1f791156928090242d05d42daa420712c4f1f171` |
| Runner | GitHub-hosted Ubuntu 24.04.4, Node 22 through the repository's `run-test` action |
| Result | Failed due to three attachment-array assertions |

No upstream contact occurred.

## Setup result

The repository's standard composite test action completed checkout, dependency installation, build, and browser installation sufficiently to execute the targeted Playwright Test runner suite.

This removes the previous environment uncertainty: the fork can execute the exact JavaScript runner tests on GitHub Actions.

## Targeted suite

The workflow ran:

```bash
npm run ttest -- \
  tests/playwright-test/fixture-teardown-resumption.spec.ts \
  tests/playwright-test/fixture-teardown-fairness.spec.ts \
  --workers=1
```

The outer targeted suite displayed `F····`: five tests executed and three failed.

## Failure classification

All three failures had the same form. The expected attachment arrays contained only campaign sentinel attachments, while the actual report also contained Playwright's automatic `error-context` attachment.

### Fairness case

Expected:

```text
[
  [sentinel-0],
  [sentinel-1]
]
```

Received:

```text
[
  [error-context, sentinel-0],
  [error-context, sentinel-1]
]
```

### Multiple deferred finalizers

Expected:

```text
[
  [sentinel-b-0, sentinel-a-0],
  [sentinel-b-1, sentinel-a-1]
]
```

Received:

```text
[
  [error-context, sentinel-b-0, sentinel-a-0],
  [error-context, sentinel-b-1, sentinel-a-1]
]
```

### Narrow retention case

Expected:

```text
[
  [sentinel-0],
  [sentinel-1]
]
```

Received:

```text
[
  [error-context, sentinel-0],
  [error-context, sentinel-1]
]
```

## What the run establishes

The run provides positive evidence for the prototype behaviour despite the outer assertion failures:

1. retained sentinel teardown ran on attempt 0 and retry 1;
2. worker replacement occurred;
3. sentinel attachments were present in each test result before `testEnd`;
4. after a slow deferred blocker timed out, a later sentinel still finalized;
5. with three deferred fixtures, both later quick finalizers produced attachments in teardown order on both attempts;
6. the budgeted fairness intervention carried enough time forward for later finalizers.

The failures were test-harness expectation errors, not missing finalizers or missing attachments.

## Correction

The attachment assertions now filter names to the `sentinel-` prefix before comparing. This retains the pre-`testEnd` invariant while allowing standard harness diagnostics.

Corrected branch heads:

| Layer | Head after correction |
|---|---|
| Narrow retention | `9a55ea15dd8bf26551179ced71602ffcb84eaa9f` |
| Fairness invariant | `3909dab6578ee3f49d79126b291674785447abf2` |
| Budgeted fairness | `424b81b4352cfaca14f1ded145dab53f1fdf6b82` |
| CI execution branch | `57bfcad3b495cd7b261a18d91aaf074e2f16fbba` |

## Confidence update

| Claim | Before run | After run 1 |
|---|---|---|
| Exact JavaScript runner checkout is executable | unknown | confirmed |
| Narrow retention reaches sentinel teardown before `testEnd` | medium | high for Ubuntu/Node 22 |
| Budget allocation lets later deferred finalizers run | medium | high for tested cases on Ubuntu/Node 22 |
| Multiple later attachments preserve teardown order | medium | high for tested case on Ubuntu/Node 22 |
| Cross-platform behaviour | unknown | still unknown |
| Diagnostic quality and timing policy | unresolved | still unresolved |

## Next run

Rerun the same targeted suite with filtered attachment assertions. A clean pass would validate the current Ubuntu/Node 22 experiment stack. Cross-platform and negative-control runs remain separate work.
