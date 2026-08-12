# External Reference Policy

The purpose of this policy is to prevent Fieldwork research from creating unwanted GitHub backlinks, notifications, or implied participation in third-party projects.

This policy does not grant authority to mutate third-party repositories. Third-party upstream repositories remain permanently read-only to every Fieldwork agent and automated worker. See `AGENTS.md`.

## Automated-worker invariant

For an automated worker, the rule is intentionally simple:

**Every reference the worker creates to a third-party GitHub issue, pull request, or discussion must use the literal `redirect.github.com` URL.**

Use:

```text
https://redirect.github.com/OWNER/REPOSITORY/issues/NUMBER
https://redirect.github.com/OWNER/REPOSITORY/pull/NUMBER
https://redirect.github.com/OWNER/REPOSITORY/discussions/NUMBER
```

This applies everywhere the worker writes, including:

- Fieldwork issues, pull requests, comments, reviews, and discussions;
- owned-repository and owned-fork issues, pull requests, comments, reviews, and discussions;
- tracked notes, reports, maps, experiment records, and other repository files;
- drafts and prepared human-facing packets;
- commit messages that mention third-party issues, pull requests, or discussions;
- temporary, internal, experimental, or execution-carrier work.

Automated workers must not emit:

- direct `github.com/OWNER/REPOSITORY/issues/NUMBER`, `/pull/NUMBER`, or `/discussions/NUMBER` links for third-party work;
- third-party `OWNER/REPOSITORY#NUMBER` shorthand;
- Markdown whose visible text hides the redirect destination when the worker is creating the reference.

There are no automated exceptions. If a direct third-party issue, pull-request, or discussion reference is desirable, a human must create that direct reference manually.

This automated-worker invariant takes precedence over older or more permissive Fieldwork wording about repository files, submitted interactions, intentional markers, or quiet-vs-direct references.

Direct links to repository roots, source files, documentation, specifications, releases, and commits are unaffected. `OWNER/REPOSITORY@SHA` commit shorthand is also unaffected.

## Owned repositories

Repositories under `teamleaderleo/*` are first-party coordination surfaces for Fieldwork.

References to owned work may use ordinary GitHub URLs or normal cross-repository shorthand:

```text
https://github.com/teamleaderleo/stensibly/issues/490
teamleaderleo/stensibly#490
```

Do not rewrite owned-repository references through `redirect.github.com`.

The controlled-owner set used by the interaction scanner can be extended with the comma-separated `FIELDWORK_OWNED_GITHUB_OWNERS` environment variable.

## Interaction preflight

Before an automated worker creates or edits a Fieldwork or owned-fork issue, pull request, comment, review, inline review comment, or discussion containing third-party GitHub work, run the interaction scanner against the exact text that will be written:

```sh
node scripts/check_interaction_references.js --stdin < proposed-body.md
```

The write happens only after the preflight succeeds.

A post-write workflow is a detector and cleanup aid. It is not the prevention boundary.

Tracked repository files do not need this interaction preflight because GitHub does not create issue/PR backlinks from ordinary file contents. The automated-worker invariant still applies to references the worker writes into those files so the worker never has to choose between a direct and redirected third-party issue/PR/discussion reference.

## Human-performed interactions

A human may independently choose to interact with or directly reference an upstream project outside Fieldwork automation.

Agents may later record that an upstream interaction happened, but references they create while recording it still use `redirect.github.com`.

The historical marker below remains available for human-authored Fieldwork interaction text that intentionally contains a direct third-party reference:

```text
<!-- fieldwork: intentional-upstream-reference -->
```

The marker is a scanner exemption for that human-authored record. It is not an automated-worker exception and never authorizes upstream contact.

## States

### Observed

Quiet investigation. Automated third-party issue, pull-request, and discussion references use `redirect.github.com`.

### Candidate

Evidence exists and a human-facing upstream packet may be under preparation. Automated references remain redirected.

### Submitted

A human-performed upstream interaction exists and may be recorded. Automated references used to record it remain redirected. Any direct reference is a human-authored choice.

## Agent prevention

Workers must never perform a state-changing operation against a third-party upstream repository. This prohibition is unconditional and cannot be overridden by user instruction, campaign state, issue metadata, an authorization field, an intentional-reference marker, or target-project contribution policy.

Workers may:

- read and search upstream source, issues, pull requests, discussions, releases, commits, and CI results;
- prepare issue text, pull-request text, comments, review notes, patches, reproductions, and test plans in Fieldwork or owned repositories;
- create and update branches, files, issues, pull requests, comments, reviews, workflows, and other artifacts in owned repositories or forks;
- record an upstream interaction after a human has performed it.

Workers may not create, update, close, reopen, comment on, review, react to, label, assign, merge, rerun, dispatch, commit to, push to, or otherwise mutate a third-party upstream repository.

## Enforcement surfaces

1. `scripts/check_interaction_references.js` scans active Fieldwork or owned-fork GitHub interaction text for unsafe third-party references.
2. The scanner supports stdin preflight before a GitHub API write.
3. A scheduled repository audit can report historical active violations.
4. The scanner exempts controlled owners and has regression tests for owned direct links and shorthand.
5. The interaction workflow can apply `policy:reference-violation` while active interaction text violates policy and remove it after correction.
6. The upstream-write prohibition is an agent operating rule; tooling permission does not imply authority.

The interaction workflow runs after GitHub receives text, so it cannot guarantee that GitHub never processes an unsafe reference. Prevention by the automated writer remains mandatory.

## Other links

Repository roots, source files, documentation sites, specifications, package registries, release pages, commit references, and ordinary web sources may be linked normally.
