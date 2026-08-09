# Postmortem: repeated submission-commit materialization

Date: 2026-08-07  
Status: closed; preventive changes applied

> **2026-08-10 follow-up:** The correctly attributed submission commit recorded below was later replaced during maintainer-requested history cleanup. An API-created squash briefly reintroduced an identity/DCO mismatch even though GitHub resolved the commit to the correct account and the `Signed-off-by:` text looked correct. The human submitter repaired that rewrite locally. See `research/postmortems/2026-08-10-cloud-hypervisor-dco-squash-followup.md`. Commit references below describe the state at the close of this original incident, not the current PR head.

## Summary

While preparing a small Cloud Hypervisor contribution, Fieldwork used a GitHub Actions workflow as a repeatable **submission-commit materializer**. The workflow checked out a clean upstream base, applied the candidate patch, created a new signed-off commit, and force-pushed that commit to a clean submission branch.

That design produced two avoidable failures:

1. repeated workflow executions created many distinct temporary commits whose messages referenced the canonical issue, producing a cascade of upstream issue timeline backlinks;
2. an early version of the materializer configured Git with the identity of an unrelated real upstream contributor, so temporary fork commits were falsely authored and DCO-signed as that person.

The final human-submitted upstream pull request was verified before review and is correctly attributed to Leo Li <cheerleaderleo@outlook.com>. No upstream code was merged under the wrong identity, and the final source change was not affected.

Upstream pull request:  
https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/pull/8699

Canonical issue:  
https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/issues/8046

## Impact

- The canonical issue timeline contains many historical cross-reference events from temporary fork commits.
- Several obsolete commits in the controlled fork were associated by GitHub with the real account `leo03164` because the workflow used that contributor's verified email address.
- The visible noise is disproportionate to the actual source change and may confuse anyone reading the issue history.
- The final upstream PR commit is correctly attributed and contains the correct DCO footer.
- No canonical branch, release, or unrelated repository state was modified.

The historical issue events cannot usefully be removed after GitHub records them, so prevention matters more than retrospective cleanup.

## What happened

The research branch contained diagnostic workflow files, retained patch material, and handoff evidence that did not belong in an upstream contribution. To produce a clean one-commit branch, a workflow was introduced that effectively did this:

```text
mutable research branch
        |
        v
GitHub Actions run
        |
        +-- checkout clean upstream base
        +-- apply retained source patch
        +-- configure Git identity
        +-- git commit -s
        +-- force-push clean submission branch
```

The workflow had `permissions: contents: write`, so the GitHub Actions token was intentionally allowed to create and push repository history. That capability is normal and useful for release automation, generated files, dependency updates, and similar workflows. The mistake was using it here as a repeatedly triggered **human-contribution commit factory**.

Each execution created a new Git commit object. Even when the source diff was identical, commit timestamps and metadata made the resulting SHA different. Repeated edits to the research/workflow branch therefore queued multiple independent runs, and each run could manufacture and force-push another clean-candidate SHA.

The generated commit message also contained `Fixes #8046`. GitHub treated every pushed commit containing that reference as another commit associated with the canonical issue. Multiple queued runs therefore became multiple upstream timeline events.

## Attribution failure

The most serious error was contributor identity handling.

An early materializer contained:

```text
git config user.name leo03164
git config user.email leo03164@gmail.com
git commit -s
```

`leo03164` is a real Cloud Hypervisor contributor. That identity appeared in a legitimate upstream commit used during the investigation. It had no relationship to the identity of the new contribution.

Because `git commit -s` derives the `Signed-off-by:` trailer from the configured Git identity, the workflow created new commits that falsely asserted that contributor's authorship and DCO sign-off. GitHub then correctly associated those commits with the real account because the email address belonged to it.

This was a Fieldwork process error. Contributor identity must never be inferred from a base commit, nearby upstream author, repository owner, or historical configuration.

## Root causes

### 1. CI and submission packaging were conflated

The same automation both validated the candidate and created the commit intended for human submission. Testing is naturally repeatable; authorship and DCO assertion should not be.

### 2. Human identity was treated as build configuration

The materializer treated `user.name` and `user.email` as values that could be copied from surrounding repository state. For DCO-bearing commits, they are human attribution data and require an explicit source of truth.

### 3. The materializer was attached to a mutable trigger

Research continued while the workflow was enabled. Small changes to comments, commit wording, workflow logic, or base selection could launch another commit-producing run.

### 4. Old runs were allowed to remain useful after supersession

Several workflow executions could be queued at once. A stale run could wake later and force-push a commit that was already conceptually obsolete.

### 5. Ephemeral commits carried canonical closing metadata

`Fixes #8046` belongs on the final submission commit. Putting it on disposable generated candidates made every temporary SHA externally visible through GitHub's issue-reference machinery.

### 6. The mechanism was disproportionate to the change

For a one-file, roughly thirty-line test cleanup, a repeatable commit materializer introduced substantially more state, authority, and failure modes than it removed.

## Why GitHub allowed it

Nothing special was bypassed. The workflow was running in a repository we control and was explicitly granted `contents: write`. GitHub Actions executes arbitrary repository automation with the permissions granted to its token. A workflow with write access can create commits, update refs, and push branches just as other authorized automation can.

The lesson is not "GitHub Actions should never write." The lesson is that **write-capable CI should not manufacture human-attributed contribution commits on repeatable triggers**.

## What went well

- The final upstream branch was rebuilt with the explicit human identity `Leo Li <cheerleaderleo@outlook.com>`.
- The final upstream commit was verified to resolve to the submitting GitHub account and to contain the correct DCO footer.
- The source diff remained focused and runtime evidence remained valid.
- The obsolete clean branch was moved to the correct final commit.
- The fork-only diagnostic and final-carrier PRs were archived/closed after submission.
- The commit-producing materializer was disabled.
- The incident exposed a reusable process weakness before it affected a merged upstream change.

## Preventive rules

### Submission commits are created once

Research branches may be noisy and mutable. When a candidate is accepted for submission, create the human-attributed submission commit once. After that, CI tests that exact SHA; CI does not recreate it.

### DCO identity is explicit human data

Never derive contributor name or email from:

- the base commit;
- an upstream author or maintainer;
- the repository owner;
- GitHub account display names;
- old workflow configuration;
- nearby commits.

Before an upstream compare/PR is handed to the human submitter, verify all of:

```text
expected branch
expected source diff
expected GitHub-resolved author
expected GitHub-resolved committer
expected Signed-off-by trailer
expected assistance/coauthor trailers
```

The 2026-08-10 follow-up tightens this further: provider account resolution is only secondary evidence. For DCO-bearing commits, the raw Git author and committer name/email must also be inspected directly after every history rewrite.

### Ephemeral commits do not close or directly reference external issues

Disposable/internal commits should omit `Fixes`, `Closes`, and similar canonical issue references. GitHub interaction text should use `redirect.github.com` for quiet external references until deliberate upstream contact is intended.

### Repeatable workflows validate; they do not impersonate release decisions

A workflow may build, test, lint, package artifacts, and prove an exact candidate. If a write-capable packaging workflow is genuinely necessary, it must have a bounded one-time trigger, explicit identity handling, stale-run cancellation, and no external-closing metadata until the final artifact is selected.

### Disable scaffolding after promotion

Temporary materializers, publication carriers, and force-push workflows must be disabled or removed immediately after the durable submission branch exists.

## Better submission pattern

```text
research / reproduce / test
          |
          v
human accepts exact candidate
          |
          v
create one submission commit
with explicit human identity
          |
          v
CI tests that exact SHA
          |
          v
human opens upstream PR
```

Not:

```text
research update
      |
      v
CI creates another would-be submission commit
      |
      v
research update
      |
      v
CI creates another one
```

## Follow-up applied

- The Cloud Hypervisor materializer was archived and stripped of write behavior.
- The obsolete clean branch was moved to the correctly attributed final commit.
- Linux Fieldwork now carries an explicit contributor-identity guardrail.
- Active internal GitHub surfaces were converted to backlink-suppressing redirect links where applicable.
- The Cloud Hypervisor lane is recorded as submitted upstream, with the final upstream PR as the review source of truth.

## Durable lesson

Automation is excellent at repeating mechanical work. Authorship, DCO certification, and the decision that a commit is the one intended for upstream are **not** merely mechanical build outputs.

Treat the final contribution commit as a human-attributed release artifact: create it deliberately, verify it exactly, and then make automation prove that artifact rather than continually recreating it.
