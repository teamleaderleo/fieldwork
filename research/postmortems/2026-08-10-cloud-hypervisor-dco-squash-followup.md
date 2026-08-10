# Postmortem follow-up: DCO mismatch after API squash

Date: 2026-08-10  
Status: repaired; guardrail update required

Related incident: `research/postmortems/2026-08-07-cloud-hypervisor-submission-materializer.md`

Upstream pull request:  
https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/pull/8699

Canonical issue:  
https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/issues/8046

## In simple words

The Cloud Hypervisor source change was already reviewed and approved, but a later one-commit squash was created through GitHub's low-level commit API without an explicit raw Git author/committer identity.

The replacement commit still contained the correct text:

```text
Signed-off-by: Leo Li <cheerleaderleo@outlook.com>
```

and GitHub associated both author and committer with the `teamleaderleo` account. That looked correct in the connector output, so the squash was incorrectly treated as DCO-clean.

It was not enough. The maintainer later reported that the Signed-off-by identity did not match the commit identity and asked for `git commit -s`.

The human submitter repaired the commit locally with an explicit Git identity, verified the raw author and committer using ordinary Git, and force-updated the existing branch. The final source diff did not change.

## Sequence

The contribution initially reached review with correctly attributed commit:

```text
f7e386b074138700cb57101b8c3ef0ecc069a018
```

A small review follow-up removed four redundant comments. The maintainer then requested that the follow-up be squashed into the original commit.

The squash was performed through an owned-fork GitHub API path. The resulting one-commit head was:

```text
160a1468edac6a8e396972c8809ad066f0afe789
```

Its tree and commit message were correct. The message included:

```text
Signed-off-by: Leo Li <cheerleaderleo@outlook.com>
```

The available GitHub readback showed:

```text
GitHub-resolved author:    teamleaderleo
GitHub-resolved committer: teamleaderleo
```

That verification was accepted as sufficient. It was not.

After approving the source change, the maintainer subsequently commented that the SoB did not match and requested `git commit -s`.

The human submitter then repaired the commit locally by using the explicit identity:

```text
Leo Li <cheerleaderleo@outlook.com>
```

and verified the commit with Git itself. The decisive readback was:

```text
Author:    Leo Li <cheerleaderleo@outlook.com>
Commit:    Leo Li <cheerleaderleo@outlook.com>
Signed-off-by: Leo Li <cheerleaderleo@outlook.com>
```

The repaired head pushed to the existing PR branch is:

```text
39d446bcb31ccd2004c9a05bdb474bff85921740
```

The PR remains one commit and one changed source file with the same final diff.

## What actually failed

Three identity layers were incorrectly collapsed into one:

1. **Raw Git author/committer identity** — the name and email stored in the commit object.
2. **GitHub account association** — the GitHub account GitHub can associate with an author or committer email.
3. **Commit-message trailers** — for example `Signed-off-by:`.

These are related, but they are not interchangeable.

A DCO check cares about the Git identity represented by the commit and the certification asserted by the `Signed-off-by:` trailer. A GitHub UI or API response resolving an author to `teamleaderleo` proves account association; it does not prove the underlying name/email exactly match the sign-off.

The API squash preserved layer 3 and appeared correct at layer 2, while layer 1 was not independently controlled or verified.

## Root cause

The low-level commit creation path used for the squash accepted a tree, parent, and message but did not expose an explicit author/committer identity in the available connector action.

Instead of treating that limitation as a stop condition, the flow created the commit anyway and relied on GitHub account resolution afterward.

That was the process error.

The earlier materializer incident taught that contributor identity must not be inferred from surrounding history. This follow-up adds a second rule: **contributor identity must also not be inferred from provider account resolution after commit creation**.

## Why the source review was still valid

The failure was commit metadata, not source behavior.

The maintainer had already reviewed and approved the one-commit source state. The human repair changed commit identity metadata and therefore the SHA, but did not change the intended source diff.

A changed SHA still requires exact-head bookkeeping, but the DCO repair should not be described as a new product-code revision.

## Guardrails added from this follow-up

### Raw Git identity is the DCO source of truth

For a DCO-bearing submission commit, verify all three independently:

```text
raw author:     %an <%ae>
raw committer:  %cn <%ce>
Signed-off-by:  exact expected human identity
```

Useful local checks include:

```sh
git show --no-patch --format=fuller HEAD
git log -1 --format='%an <%ae>%n%cn <%ce>%n%B'
```

GitHub-resolved account identity may be checked as additional evidence, but it is not a substitute for the raw fields.

### A tool that cannot set or expose raw identity cannot finalize a DCO commit

If a commit-writing tool cannot explicitly set the required author/committer identity, or cannot provide an independent raw metadata readback, it must not be used to create, amend, squash, or rebuild the final DCO-bearing submission commit.

It may still prepare the tree, patch, branch, test evidence, or exact command for a human/local Git step.

### Prefer normal Git for final history rewrites

For a new contribution commit:

```sh
git config user.name 'Leo Li'
git config user.email 'cheerleaderleo@outlook.com'
git commit -s
```

For an existing commit whose sign-off text is already correct but whose author identity needs repair, normal Git author-reset behavior is appropriate, followed by raw metadata verification before force-updating the branch.

Do not repair an author/sign-off mismatch by merely editing or appending a `Signed-off-by:` line.

### Every squash or amend reopens identity verification

A squash, rebase, amend, cherry-pick, API recreation, or other history rewrite creates a new commit object. Even when the source tree is identical, all final-commit checks must be repeated:

- raw author;
- raw committer;
- DCO trailer;
- assistance/coauthor trailers;
- source diff;
- parent/base;
- exact new SHA.

### Phone-first contribution flow needs an explicit final-commit primitive

The broader workflow remains useful from a phone: source research, candidate edits, test orchestration, review analysis, and owned-fork maintenance can all be automated safely.

The unresolved product/process gap is final human-attributed Git history creation. Until the tool path can explicitly control and verify raw author/committer metadata, the reliable boundary is:

```text
automation prepares and validates candidate
                |
                v
human/local Git creates or rewrites final DCO commit
                |
                v
raw identity verification
                |
                v
force-with-lease / push
```

This is a tooling limitation to remove later, not a reason to add another commit materializer.

## Current outcome

- The source change remains the same narrow Cloud Hypervisor lifecycle-test fix.
- The maintainer approval preceded the DCO metadata comment; the source review itself was not rejected.
- Bad API-squash head `160a1468...` was replaced on the fork branch.
- Human-repaired head is `39d446bcb31ccd2004c9a05bdb474bff85921740`.
- Raw author, raw committer, and `Signed-off-by:` were verified locally as `Leo Li <cheerleaderleo@outlook.com>` before push.
- No additional upstream interaction was performed by Fieldwork automation.

## Durable lesson

A correct sign-off string is not proof of a correctly signed-off commit.

For DCO work, the final unit to verify is the **commit object**, not the GitHub avatar attached to it and not the trailer alone.
