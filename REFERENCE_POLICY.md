# External Reference Policy

References to issues, pull requests, discussions, and commits in repositories we do not control are **non-invasive by default**.

## Why

A direct GitHub cross-reference can create backlinks, notifications, and implied involvement. Research should not enter an upstream project's attention merely because Fieldwork recorded a public note.

## Mandatory default

Use backlink-suppressing URLs:

```text
https://redirect.github.com/OWNER/REPOSITORY/issues/NUMBER
https://redirect.github.com/OWNER/REPOSITORY/pull/NUMBER
https://redirect.github.com/OWNER/REPOSITORY/discussions/NUMBER
https://redirect.github.com/OWNER/REPOSITORY/commit/SHA
```

Use descriptive link text. Preserve owner, repository, item number, retrieval date, and source revision where relevant.

Do not use external shorthand cross-references. Do not use closing keywords against external work.

## Intentional upstream contact

A direct link is allowed only when it records a specifically authorized interaction, such as:

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

Quiet investigation. External issue, PR, discussion, and commit references are wrapped.

### Candidate

Evidence exists and an upstream packet may be under preparation. References remain wrapped.

### Submitted

An intentional upstream interaction exists. Direct references are permitted only where they accurately record that interaction.

## Agent prevention

`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and Copilot instructions all require wrapping before any Fieldwork interaction is created. This is the primary safeguard.

## Enforcement surfaces

1. `scripts/check_external_references.py` scans tracked prose and data files on pushes to `main` and pull requests.
2. `scripts/check_interaction_references.js` scans new or edited issue bodies, PR bodies, conversation comments, submitted review text, and inline review comments.
3. The interaction workflow applies `policy:reference-violation` to the parent issue or PR when it detects a violation and removes the label after correction.
4. Issue forms disable blank issues in the web interface and require acknowledgement of the quiet-reference rule.

The interaction workflow runs after GitHub receives the text. It cannot guarantee that GitHub never processes the original direct reference. Workers must wrap references before posting. Branch protection can make the PR interaction check merge-blocking; it cannot make issue creation transactional.

## Exceptions

- Repository roots, documentation sites, specifications, package registries, and release pages are unaffected.
- References within a repository we control may be direct.
- Archived evidence imported from upstream should be sanitized or explicitly exempted before commit.
