# External Reference Policy

This policy owns automated external-reference mechanics and the preflight/recording procedure for any authorized upstream interaction. The authority boundary itself lives in [`AGENTS.md`](AGENTS.md): third-party upstream repositories remain read-only unless a human gives one fresh bounded `upstream greenlight` for an exact destination, action, and final content.

## Automated-worker invariant

**Every reference an automated worker creates to a third-party GitHub issue, pull request, or discussion uses the literal `redirect.github.com` URL.**

```text
https://redirect.github.com/OWNER/REPOSITORY/issues/NUMBER
https://redirect.github.com/OWNER/REPOSITORY/pull/NUMBER
https://redirect.github.com/OWNER/REPOSITORY/discussions/NUMBER
```

The invariant applies everywhere the worker writes: Fieldwork and owned-repository GitHub interactions, tracked files, drafts, reports, experiment records, human-facing packets, commit messages, temporary work, and execution carriers.

Automated workers never create direct third-party issue/PR/discussion URLs, third-party `OWNER/REPOSITORY#NUMBER` shorthand, or Markdown that hides the redirect destination. There are no automated exceptions; a human may create a direct reference manually.

Repository roots, source files, documentation, specifications, package registries, releases, and commit links may be linked normally. `OWNER/REPOSITORY@SHA` commit shorthand is also unaffected.

## Owned repositories

Repositories under `teamleaderleo/*` are first-party Fieldwork surfaces. References to owned work may use ordinary GitHub URLs or cross-repository shorthand and must not be rewritten through `redirect.github.com`.

The interaction scanner's controlled-owner set may be extended with the comma-separated `FIELDWORK_OWNED_GITHUB_OWNERS` environment variable.

## Interaction preflight

Before an automated worker creates or edits a Fieldwork or owned-fork issue, pull request, comment, review, inline review comment, or discussion containing third-party GitHub work, run the scanner against the exact final text:

```sh
node scripts/check_interaction_references.js --stdin < proposed-body.md
```

Proceed only after preflight succeeds. Refresh the destination before an authorized upstream write and preflight the exact final content again immediately before the write.

Tracked repository files do not require this interaction preflight because ordinary file contents do not create GitHub issue/PR backlinks. The redirect invariant still applies to third-party issue/PR/discussion references in those files.

Post-write workflows detect and help clean up violations after GitHub receives text; prevention remains the writer's responsibility.

## Bounded upstream interaction

Without the `upstream greenlight` from `AGENTS.md`, an automated worker may read and search third-party upstream source, issues, pull requests, discussions, releases, commits, and CI results, and may prepare or implement work in Fieldwork, owned repositories, and owned forks.

A greenlight authorizes exactly one named state-changing upstream interaction. Creating, updating, closing, reopening, commenting, reviewing, reacting, labeling, assigning, merging, rerunning, dispatching, committing, pushing, or any other mutation requires that exact authorization. Campaign state, issue metadata, authorization fields, intentional-reference markers, target policy, apparent intent, and tool permission grant no upstream authority.

After the authorized write, record in the owning Fieldwork record:

- resulting URL;
- exact written text or a digest;
- interaction time;
- exact greenlight scope consumed.

## Human-performed interactions

A human may independently interact with or directly reference an upstream project. Automated workers may record that interaction, while the references they create still follow the redirect invariant.

For human-authored Fieldwork interaction text that intentionally contains a direct third-party reference, the historical scanner exemption remains:

```text
<!-- fieldwork: intentional-upstream-reference -->
```

The marker exempts that human-authored reference from the scanner. Upstream authority still comes only from the bounded greenlight in `AGENTS.md`.

## Reference states

- **Observed** — quiet investigation; automated third-party issue/PR/discussion references are redirected.
- **Candidate** — evidence exists and a human-facing upstream packet may be prepared; automated references remain redirected.
- **Submitted** — a human or authorized agent interaction exists and may be recorded; automated references used in the record remain redirected.

These states describe evidence/contact status. They do not grant upstream authority or change evidence class.

## Enforcement

- `scripts/check_interaction_references.js` scans Fieldwork and owned-fork interaction text and supports stdin preflight.
- Scanner regression tests cover controlled owners, direct-link rejection, and shorthand rejection.
- Repository automation may flag active reference-policy violations and remove the flag after correction.
- Post-write detection is a cleanup aid; exact-text preflight is the prevention boundary.
- Tool permission never grants third-party upstream authority.
