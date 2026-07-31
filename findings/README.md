# Findings Directory

## In simple words

Each retained investigation gets one directory here. The issue coordinates people. The canonical `finding.md` explains the current answer. Pull requests update that answer and preserve disagreements through review and Git history.

Read [`FINDINGS.md`](../FINDINGS.md) before creating or editing a finding.

## Naming

```text
findings/F<fieldwork-issue>-<short-slug>/
```

## Ownership

- A worker owns each unique evidence, artifact, or review file they create.
- The canonical `finding.md` is a shared reviewed integration surface.
- Multiple pull requests may propose changes to it.
- Merge conflicts require reconciliation of the current conclusion and retained evidence.
- Issue comments should point to the finding and record issue-state or finding-state changes, heads, receipts, decisions, or blockers.

## Minimum files

A retained finding needs:

```text
finding.md
```

Add these only when useful:

```text
evidence/
artifacts/
reviews/
```

Use [`templates/finding.md`](../templates/finding.md) for the canonical file.
