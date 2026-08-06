# Handoff — Unit 11: OpenTelemetry lifecycle fanout

## Current state

`SUBMITTED — WAITING ON REVIEWERS`

- issue: [open-telemetry/opentelemetry-js#6977](https://redirect.github.com/open-telemetry/opentelemetry-js/issues/6977)
- pull request: [open-telemetry/opentelemetry-js#6980](https://redirect.github.com/open-telemetry/opentelemetry-js/pull/6980)
- final signed head: `1e5bd20fb823a9c47a2b2ccc974e18d88b765f16`
- EasyCLA: passing
- owned-fork exact-head workflows: all passing
- upstream workflow state: maintainer approval required before jobs run
- dashboard: waiting on reviewers

## Next actions

1. Wait for a maintainer to approve workflow execution and review the patch.
2. Respond to concrete review comments in the contributor's own words.
3. Rebase only when upstream movement or review makes it necessary.
4. Sign every replacement commit and preserve both trailers.
5. Re-run exact-head checks after any code, test, or changelog change.
6. Give reviewers a few days before any ping.

## Lessons for the next upstream contribution

### Prepare the final publication sequence early

The real sequence was:

```text
prepare source
file issue
open PR to obtain PR number
add numbered changelog entries
amend and sign
force-push
verify exact head
```

A changelog that requires the PR number cannot be final before the upstream PR exists. Plan for one immediate signed amendment after opening.

### Inspect the changed-file list after every amendment

The first AI-disclosure amendment updated the commit message while the changelog files were absent from the commit. The reliable check is:

```sh
git status --short
git diff --cached --stat
git show --stat --oneline HEAD
```

Then verify the live PR's changed-file list.

### Keep mutable commit identities out of the PR body

An exact SHA in the description became stale after the changelog amendment. Record stable facts in the public body and keep exact-head identities in Fieldwork receipts.

### Treat signatures, sign-off, CLA, and AI disclosure as separate gates

- `-S` creates the cryptographic signature.
- `-s` adds the `Signed-off-by` trailer.
- EasyCLA authorizes the contributor.
- `Assisted-by:` records significant model assistance.

One does not substitute for another.

### Distinguish workflow approval from workflow failure

For a first-time fork contribution, GitHub can report `action_required` with no jobs. That means a maintainer must approve execution. It is not a failing test result.

### Match the repository's changelog conventions

The stable and experimental changelogs used different link styles. Follow the local section rather than forcing one global format.

### Use quiet links in Fieldwork interaction text

Fieldwork pull-request bodies and comments should cite third-party GitHub work through `redirect.github.com`. Repository files may link directly, but this packet uses redirect links consistently.

### Keep the production explanation small

The implementation is three opening-set snapshots plus a local direct-throw adapter. The tests are larger because trace, logs, and provider paths have separate result policies. Explain that mapping directly.

## Contact record

Public upstream interaction authorized: `true`  
Public upstream interaction performed: `true`
