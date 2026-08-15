# External Reference Policy

The purpose of this policy is to prevent Fieldwork research from creating unwanted GitHub backlinks, notifications, or implied participation in third-party projects.

This reference policy does not itself grant authority to mutate third-party repositories. Third-party upstream repositories are read-only by default; the `upstream greenlight` gate in `AGENTS.md` is the explicit authorization boundary for a bounded state-changing interaction.

## Automated-worker invariant

For an automated worker, the rule is intentionally simple:

**Every third-party GitHub URL the worker creates must use the literal `redirect.github.com` host.**

Examples:

```text
https://redirect.github.com/OWNER/REPOSITORY
https://redirect.github.com/OWNER/REPOSITORY/issues/NUMBER
https://redirect.github.com/OWNER/REPOSITORY/pull/NUMBER
https://redirect.github.com/OWNER/REPOSITORY/discussions/NUMBER
https://redirect.github.com/OWNER/REPOSITORY/blob/REVISION/PATH
https://redirect.github.com/OWNER/REPOSITORY/commit/SHA
```

This applies everywhere the worker writes, including:

- Fieldwork issues, pull requests, comments, reviews, and discussions;
- owned-repository and owned-fork issues, pull requests, comments, reviews, and discussions;
- tracked notes, reports, maps, experiment records, and other repository files;
- drafts and prepared human-facing packets;
- commit messages that contain third-party GitHub URLs;
- temporary, internal, experimental, or execution-carrier work.

Automated workers must not emit direct `github.com` URLs to third-party GitHub content. For third-party issues, pull requests, and discussions, they must also not emit `OWNER/REPOSITORY#NUMBER` shorthand.

There are no automated exceptions. If a direct third-party GitHub URL is desirable, a human must create it manually.

This automated-worker invariant takes precedence over older or more permissive Fieldwork wording.

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

## Upstream authorization gate

A worker must not perform a state-changing operation against a third-party upstream repository unless the human has supplied the phrase `upstream greenlight` for the current repository and interaction reasonably clear from context.

Ordinary approval or an explicit request to post, send, reply, review, react, open, close, rerun, or otherwise mutate upstream does not satisfy this gate without the phrase `upstream greenlight`.

A greenlight is bounded to that interaction and does not authorize unrelated writes, merge, release, deployment, credentials, spending, or private-data access. A later human instruction may narrow or revoke it.

Workers may always read and search upstream material and prepare drafts, patches, reproductions, review notes, tests, and manual steps without a greenlight. Owned repositories and owned forks remain writable under their normal authority.

## Enforcement surfaces

1. `scripts/check_interaction_references.js` scans active Fieldwork or owned-fork GitHub interaction text for unsafe third-party references.
2. The scanner supports stdin preflight before a GitHub API write.
3. A scheduled repository audit can report historical active violations.
4. The scanner exempts controlled owners and has regression tests for owned direct links and shorthand.
5. The interaction workflow can apply `policy:reference-violation` while active interaction text violates policy and remove it after correction.
6. The upstream greenlight gate is an agent operating rule; tooling permission or ordinary approval does not imply authority.

The interaction workflow runs after GitHub receives text, so it cannot guarantee that GitHub never processes an unsafe reference. Prevention by the automated writer remains mandatory.

## Other links

Third-party GitHub URLs use `redirect.github.com` regardless of whether they point to a repository root, source file, documentation, release, commit, issue, pull request, or discussion. Non-GitHub web sources may be linked normally. Owned GitHub repositories remain first-party and may use ordinary GitHub URLs as described above.
