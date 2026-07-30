# External Reference Policy

References to issues, pull requests, discussions, and commits in third-party repositories we do not control are **non-invasive by default**.

## Owned repositories

Repositories under `teamleaderleo/*` are first-party coordination surfaces for Fieldwork.

Direct GitHub URLs and normal cross-repository shorthand are allowed for them:

```text
https://github.com/teamleaderleo/stensibly/issues/490
teamleaderleo/stensibly#490
```

Do not rewrite owned-repository references through `redirect.github.com`. Do not require an intentional-upstream marker for them. Fieldwork may link freely among owned issues, pull requests, commits, branches, files, experiments, and testbed records.

The controlled-owner set is implemented by the scanners and can be extended with the comma-separated `FIELDWORK_OWNED_GITHUB_OWNERS` environment variable.

## Why third-party links remain quiet

A direct GitHub cross-reference can create backlinks, notifications, and implied involvement. Research should not enter a third-party upstream project's attention merely because Fieldwork recorded a public note.

## Mandatory default for third-party repositories

Use backlink-suppressing URLs:

```text
https://redirect.github.com/OWNER/REPOSITORY/issues/NUMBER
https://redirect.github.com/OWNER/REPOSITORY/pull/NUMBER
https://redirect.github.com/OWNER/REPOSITORY/discussions/NUMBER
https://redirect.github.com/OWNER/REPOSITORY/commit/SHA
```

Use descriptive link text. Preserve owner, repository, item number, retrieval date, and source revision where relevant.

Do not use bare third-party issue or pull-request shorthand. Do not use bare third-party commit shorthand. Do not use closing keywords against third-party work.

Inline code spans and fenced code blocks are inert evidence text. The interaction scanner ignores third-party references inside those code regions while continuing to scan prose and Markdown link destinations.

## Preflight before GitHub receives text

A draft pull request is already a live GitHub interaction. GitHub parses its title and body when the pull request is created, before CI can run. The same timing applies to issues, comments, reviews, and inline review comments.

Run the interaction scanner against the complete proposed text before creating or editing any Fieldwork interaction, including interactions in owned forks:

```sh
node scripts/check_interaction_references.js --stdin < proposed-body.md
```

For generated text, pipe the exact final title and body through the scanner immediately before the GitHub API write. A post-write workflow remains a detector and cleanup aid; preflight is the prevention boundary.

## Intentional upstream contact

A direct third-party link is allowed only when it records a specifically authorized interaction, such as:

- opening or updating the actual upstream issue or pull request;
- replying in an existing upstream conversation;
- recording an already-submitted campaign;
- explicitly notifying upstream as part of an approved action.

Place this marker on the direct-link line or immediately above it:

```text
<!-- fieldwork: intentional-upstream-reference -->
```

The marker exempts only the marked line or the immediately following line. It does not authorize an entire document or conversation.

## States

### Observed

Quiet investigation. Third-party issue, PR, discussion, and commit references are wrapped. Owned-repository references remain direct.

### Candidate

Evidence exists and an upstream packet may be under preparation. Third-party references remain wrapped. Owned-repository references remain direct.

### Submitted

An intentional upstream interaction exists. Direct third-party references are permitted only where they accurately record that interaction.

## Agent prevention

`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and Copilot instructions require wrapping only for third-party upstream work. They explicitly permit direct links and shorthand within `teamleaderleo/*`.

Workers must run the preflight scanner before creating or editing an issue, pull request, comment, review, or inline review comment. This rule applies to Fieldwork coordination in this repository and to Fieldwork-authored text posted in owned forks.

## Enforcement surfaces

1. `scripts/check_external_references.py` scans tracked prose and data files on pushes to `main` and pull requests.
2. `scripts/check_interaction_references.js` scans the complete active issue or pull-request thread after issue-body, PR-body, comment, review, or inline-review changes.
3. The interaction scanner also supports stdin preflight before a GitHub API write.
4. A scheduled repository audit scans all issue and pull-request threads and reports historical active violations.
5. Both scanners exempt controlled owners and have regression tests for owned direct links and shorthand.
6. The interaction workflow applies `policy:reference-violation` to the parent issue or PR while any active text in its thread violates policy and removes the label after the complete thread is corrected.
7. Issue forms disable blank issues in the web interface and require acknowledgement of the third-party quiet-reference rule.

The interaction workflow runs after GitHub receives the text. It cannot guarantee that GitHub never processes the original third-party reference. Workers must wrap third-party references before posting. Branch protection can make the PR interaction check merge-blocking; it cannot make issue or pull-request creation transactional.

## Other exceptions

- Repository roots, documentation sites, specifications, package registries, and release pages are unaffected.
- Archived evidence imported from third-party upstream work should be sanitized or explicitly exempted before commit.
