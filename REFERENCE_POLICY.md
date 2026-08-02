# External Reference Policy

Third-party GitHub issue, pull-request, and discussion references are **non-invasive by default in GitHub conversations**. The purpose of this policy is to prevent research coordination from creating backlinks, notifications, or implied participation in an upstream project before that interaction is authorized.

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

## Preflight before posting interaction text

A draft pull request is already a live GitHub interaction. GitHub parses its title and body when it is created, before CI can run. The same applies to issues, comments, reviews, and inline review comments.

Run the interaction scanner against generated or carefully prepared interaction text before posting:

```sh
node scripts/check_interaction_references.js --stdin < proposed-body.md
```

A post-write workflow remains a detector and cleanup aid. Preflight is the prevention boundary for automated writers.

A plain repository-file write that creates no issue, pull request, comment, review, or discussion does not require this preflight.

## Intentional upstream contact

A direct third-party issue, pull-request, or discussion link in interaction text is allowed only when it records a specifically authorized interaction, such as:

- opening or updating the actual upstream issue or pull request;
- replying in an existing upstream conversation;
- recording an already-submitted campaign;
- explicitly notifying upstream as part of an approved action.

Place this marker on the direct-link line or immediately above it:

```text
<!-- fieldwork: intentional-upstream-reference -->
```

The marker exempts only the marked line or the immediately following line. It does not authorize an entire document or conversation.

Repository files do not need this marker merely to cite upstream work. Authority to contact upstream remains a separate decision.

## States

### Observed

Quiet investigation. Third-party issue, pull-request, and discussion references in GitHub interaction text are backlink-suppressing. Repository evidence may link normally.

### Candidate

Evidence exists and an upstream packet may be under preparation. Issue, pull-request, and discussion references remain quiet. Repository evidence may link normally.

### Submitted

An intentional upstream interaction exists. Direct third-party issue, pull-request, and discussion references are permitted only where they accurately record that interaction.

## Agent prevention

Workers must run the interaction preflight before creating or editing an issue, pull request, comment, review, inline review comment, or discussion containing third-party issue, pull-request, or discussion references. This applies to Fieldwork-authored interaction text posted in owned forks too.

Workers do not need to scan notes, reports, maps, data records, or other tracked files for this policy.

## Enforcement surfaces

1. `scripts/check_interaction_references.js` scans the complete active issue or pull-request thread after issue-body, PR-body, comment, review, or inline-review changes.
2. The interaction scanner supports stdin preflight before a GitHub API write.
3. A scheduled repository audit scans issue and pull-request threads and reports historical active violations.
4. The scanner exempts controlled owners and has regression tests for owned direct links and shorthand.
5. The interaction workflow applies `policy:reference-violation` while active interaction text violates policy and removes it after correction.
6. Issue forms require acknowledgement of the third-party quiet-interaction rule.

The interaction workflow runs after GitHub receives the text. It cannot guarantee that GitHub never processes the original third-party reference. Prevention by an automated writer remains mandatory.

## Other links

Repository roots, files, documentation sites, specifications, package registries, release pages, commit references, and ordinary web sources may be linked normally.
