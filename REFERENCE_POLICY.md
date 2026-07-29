# External Reference Policy

References to issues, pull requests, discussions, and commits in repositories we do not control are **non-invasive by default**.

## Why

A direct GitHub cross-reference can create backlinks, notifications, and implied involvement. Research should not enter an upstream project's attention merely because we wrote private-to-us notes in public.

## Default

Use a backlink-suppressing URL with the same owner, repository, resource kind, and number:

```text
https://redirect.github.com/OWNER/REPOSITORY/issues/NUMBER
https://redirect.github.com/OWNER/REPOSITORY/pull/NUMBER
https://redirect.github.com/OWNER/REPOSITORY/discussions/NUMBER
https://redirect.github.com/OWNER/REPOSITORY/commit/SHA
```

Use descriptive link text. Preserve the owner, repository, item number, retrieval date, and source revision where relevant.

Do not use shorthand cross-references combining an external owner, repository, and item number. Do not use closing keywords against external work.

## Intentional upstream contact

A direct link is allowed only when the reference represents deliberate interaction, such as:

- opening or updating the actual upstream issue or pull request;
- replying in an existing upstream conversation;
- recording an already-submitted campaign;
- explicitly notifying upstream as part of an approved action.

Place this marker on the direct-link line or immediately above it:

```text
<!-- fieldwork: intentional-upstream-reference -->
```

## States

### Observed

Quiet investigation. All external issue, pull-request, discussion, and commit references are wrapped.

### Candidate

Evidence exists and an upstream packet may be under preparation. References remain wrapped.

### Submitted

An intentional upstream interaction exists. Direct references are permitted where they clarify that interaction.

## Exceptions

- Links to repository roots, documentation sites, specifications, package registries, and release pages are unaffected.
- References within a repository we control may be direct.
- Archived evidence imported from an upstream source should be sanitised or explicitly exempted before commit.

## Enforcement

`scripts/check_external_references.py` scans tracked prose and data files. The reference-policy workflow runs it for pushes and pull requests. A marker is an auditable exception, not a convenient bypass.
