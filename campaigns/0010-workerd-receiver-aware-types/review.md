# Campaign 0010 Review Record

## In simple words

This is upstream-fork research, not an owned product merge. The candidate has strong source and model evidence, but its final head has not received independent acceptance and its expensive native workflows were cancelled. The correct next action is execution and review, not publication.

## Review classification

- Work class: upstream-fork research
- Canonical repository: `teamleaderleo/workerd`
- Canonical pull request: `teamleaderleo/workerd#1`
- Canonical branch: `research/issue-474-receiver-aware-types`
- Reviewed/materialized head: `e7b15f8014e8ed49255d2f0c6774f0b3bfe1714a`
- Base revision: `6aa890be9fa547e3907c805b312e39917a274221`
- Fieldwork parent: #230
- Upstream contact authorized: existing submitted issue only; no new interaction

## Complete-diff scope at materialization

The candidate reports 10 changed files, 21 commits, 721 additions, and 49 deletions relative to its pinned base. The changed surface covers:

- focused fork-only workflow;
- initial method generation;
- transform ordering;
- generated receiver provenance and cleanup;
- global extraction;
- override merging;
- generator snapshot;
- global transform fixtures;
- override fixtures;
- fetch receiver type fixture.

## Claim-by-claim evidence

| Claim | Evidence class | Receipt or limit |
| --- | --- | --- |
| JSG/V8 enforces receiver compatibility | `source-read` and `integration-executed` | source trace plus native runtime matrix |
| TypeScript can encode direct legal calls | `model-executed` | TypeScript 5.8.3 fixtures |
| local wrapper fixes the production path | `integration-executed` | merged Stensibly native-workerd regression |
| candidate preserves legacy override receiver policy | `source-read` and `target-test-prepared` | candidate source and fixtures; final target run absent |
| candidate preserves explicit receiver policy | `source-read` and `target-test-prepared` | candidate source and fixtures |
| candidate handles generic and inherited globals | `source-read` and `target-test-prepared` | candidate source and snapshots |
| candidate excludes static globals | `source-read` and `target-test-prepared` | implementation plus repaired expectations |
| candidate passes exact-head lint | `target-executed` | workerd Lint workflow completed successfully |
| candidate passes exact-head focused generator tests | none | focused workflow cancelled |
| candidate passes repository Tests/Coverage/CodSpeed | none | workflows cancelled |
| candidate is upstream-ready | none | clearing conditions remain |

## Review history

Tess issued `REPAIR` for head `d08e2e968b6db600c220e2babe0a07befa728ba2` because the global-transform test still expected ambient declarations for a static method and static property.

The branch later removed those stale expectations and moved through five commits to `e7b15f8…`. That repair addresses the named defect, but the old review is no longer a valid acceptance disposition because the head and fixtures changed.

## Execution interpretation

- Lint success proves the checked source satisfies the repository lint gate.
- Cancelled workflows do not establish failing product assertions.
- The focused type target pulls in full type generation and the native workerd/V8 build, which is expensive relative to the declaration change.
- A small synthetic in-memory compiler receipt is appropriate for the development gate.
- One target-native exact-head run remains appropriate as the final integration gate before publication.

## Current disposition

**EXECUTE**

Next transition:

1. produce and retain the small exact-head generator/compiler receipt;
2. run or honestly bound target-native execution;
3. request independent review of the complete resulting diff;
4. only an `ACCEPT` for upstream preparation may move the campaign to a publishable pull-request draft.

## Reviewer eligibility

- Candidate builders may self-review and repair.
- Final acceptance for upstream preparation should come from a reviewer other than the builder.
- Human approval remains required to publish any Cloudflare pull request.
