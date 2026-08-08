# External Reference Policy

Third-party GitHub issue, pull-request, and discussion references are **non-invasive by default in GitHub conversations**. The purpose of this policy is to prevent research coordination from creating backlinks, notifications, or implied participation in an upstream project.

This reference policy does not grant authority to mutate third-party repositories. For every Fieldwork agent and automated worker, third-party upstream repositories are permanently read-only. See `AGENTS.md`.

## Where the backlink risk exists

Apply this policy to text GitHub treats as conversation or activity metadata:

- issue titles and bodies;
- pull-request titles and bodies;
- issue and pull-request comments;
- pull-request reviews and inline review comments;
- discussion text when Fieldwork uses discussions;
- commit messages that intentionally reference third-party issues or pull requests.

GitHub does not create autolinked issue and pull-request references in repository files or wikis. Notes, reports, maps, JSON records, and other tracked repository files therefore do not need an automated external-reference check.

Repository files may use ordinary direct links when those links help the reader. Authors may still use `redirect.github.com` for consistency or caution, but it is not a repository-file requirement and CI must not reject a document for using a direct third-party GitHub link.

## Owned repositories

Repositories under `teamleaderleo/*` are first-party coordination surfaces for Fieldwork.

Direct GitHub URLs and normal cross-repository shorthand are allowed for them:

```text
https://github.com/teamleaderleo/stensibly/issues/490
teamleaderleo/stensibly#490
```

Do not rewrite owned-repository references through `redirect.github.com`. Do not require an intentional-upstream marker for them.

The controlled-owner set used by the interaction scanner can be extended with the comma-separated `FIELDWORK_OWNED_GITHUB_OWNERS` environment variable.

## Quiet interaction references

In issue, pull-request, comment, review, or discussion text, use backlink-suppressing URLs for third-party issue, pull-request, and discussion references:

```text
https://redirect.github.com/OWNER/REPOSITORY/issues/NUMBER
https://redirect.github.com/OWNER/REPOSITORY/pull/NUMBER
https://redirect.github.com/OWNER/REPOSITORY/discussions/NUMBER
```

Use descriptive link text. Do not use bare third-party issue or pull-request shorthand in interaction prose. Do not use closing keywords against third-party work.

Direct links to third-party commits and `OWNER/REPOSITORY@SHA` commit shorthand are allowed. Commit references identify source revisions and are outside this interaction-reference check.

Inline code spans and fenced code blocks are inert evidence text. The interaction scanner ignores third-party references inside those code regions while continuing to scan prose and Markdown link destinations.

## Preflight before posting Fieldwork interaction text

Before creating or editing a Fieldwork or owned-fork issue, pull request, comment, review, inline review comment, or discussion containing third-party work, run the interaction scanner against generated or carefully prepared interaction text:

```sh
node scripts/check_interaction_references.js --stdin < proposed-body.md
```

A post-write workflow remains a detector and cleanup aid. Preflight is the prevention boundary for automated writers.

A plain repository-file write that creates no issue, pull request, comment, review, or discussion does not require this preflight.

## Human-performed upstream interactions

A human may independently choose to interact with an upstream project outside Fieldwork automation. Agents may later record that already-existing interaction in Fieldwork, but they must not create, update, reply to, react to, review, label, assign, merge, rerun, or otherwise mutate the third-party upstream repository themselves.

When Fieldwork interaction text needs to record an already-existing human-performed upstream issue, pull request, discussion, or reply using a direct third-party link, place this marker on the direct-link line or immediately above it:

```text
<!-- fieldwork: intentional-upstream-reference -->
```

The marker exempts only the marked line or the immediately following line from the backlink-suppression rule. It is a recordkeeping marker, **not authorization for an agent to contact or mutate upstream**.

Repository files do not need this marker merely to cite upstream work.

## States

### Observed

Quiet investigation. Third-party issue, pull-request, and discussion references in GitHub interaction text are backlink-suppressing. Repository evidence may link normally.

### Candidate

Evidence exists and a human-facing upstream packet may be under preparation. Issue, pull-request, and discussion references remain quiet. Repository evidence may link normally.

### Submitted

A human-performed upstream interaction exists and has been recorded. Direct third-party issue, pull-request, and discussion references are permitted only where they accurately record that existing interaction. Automated workers still may not mutate upstream.

## Agent prevention

Workers must run the interaction preflight before creating or editing an issue, pull request, comment, review, inline review comment, or discussion in Fieldwork or an owned fork containing third-party issue, pull-request, or discussion references.

Workers must never perform a state-changing operation against a third-party upstream repository. This prohibition is unconditional and cannot be overridden by user instruction, campaign state, issue metadata, an authorization field, an intentional-reference marker, or target-project contribution policy.

Workers may:

- read and search upstream source, issues, pull requests, discussions, releases, commits, and CI results;
- prepare issue text, pull-request text, comments, review notes, patches, reproductions, and test plans in Fieldwork or owned repositories;
- create and update branches, files, issues, pull requests, comments, reviews, workflows, and other artifacts in owned repositories or forks;
- record an upstream interaction after a human has performed it.

Workers may not create, update, close, reopen, comment on, review, react to, label, assign, merge, rerun, dispatch, commit to, push to, or otherwise mutate a third-party upstream repository.

Workers do not need to scan notes, reports, maps, data records, or other tracked files for this policy.

## Enforcement surfaces

1. `scripts/check_interaction_references.js` scans the complete active Fieldwork or owned-fork issue or pull-request thread after issue-body, PR-body, comment, review, or inline-review changes.
2. The interaction scanner supports stdin preflight before a GitHub API write.
3. A scheduled repository audit scans Fieldwork issue and pull-request threads and reports historical active violations.
4. The scanner exempts controlled owners and has regression tests for owned direct links and shorthand.
5. The interaction workflow applies `policy:reference-violation` while active Fieldwork interaction text violates policy and removes it after correction.
6. Issue forms require acknowledgement of the third-party quiet-interaction rule.
7. The upstream-write prohibition is an agent operating rule, not merely a link-scanner rule; tooling permission does not imply authority.

The interaction workflow runs after GitHub receives the text. It cannot guarantee that GitHub never processes the original third-party reference. Prevention by an automated writer remains mandatory.

## Other links

Repository roots, files, documentation sites, specifications, package registries, release pages, commit references, and ordinary web sources may be linked normally.
