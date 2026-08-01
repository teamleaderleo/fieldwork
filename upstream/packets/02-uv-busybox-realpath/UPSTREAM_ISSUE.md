# Upstream issue draft — BusyBox `realpath` diagnostic in relocatable launchers

Draft status: `not applicable — existing public issue #16209`  
Public interaction authorized: `no`

---

## Existing issue

The canonical public report is [`astral-sh/uv#16209`](https://github.com/astral-sh/uv/issues/16209), “Generated shebang lines output 'realpath: --: No such file or directory'.” It contains an Alpine reproduction, expected and actual output, the BusyBox utility explanation, and the leading-hyphen trade-off.

The issue remained open when checked on 2026-08-01. Its discussion includes maintainer acknowledgement, a suggestion to consider a BusyBox-specific branch, later Alpine reproduction, and a 2026 confirmation that the behavior still occurs in the Alpine image.

## Internal issue-first assessment

A second public issue would duplicate the existing report. The contribution path should use #16209 as related work and focus human review on the bounded source correction and its compatibility evidence.

## Additional evidence available for a human-authored comment

A human may choose to summarize, in their own words:

- the pattern has three current owners: wheel generation, activation generation, and project-run recognition;
- a 24-case GNU/BusyBox matrix preserves status, interpreter selection, arguments, spaces, `./-tool`, relative/PATH invocation, and external symlinks;
- removing the delimiters makes BusyBox quiet and leaves tested GNU behavior unchanged;
- the synchronized source candidate removes five `realpath --` and seven `dirname --` occurrences across exactly three source files;
- bare option-like `$0`, macOS, and BSD remain explicit limits.

## Versions and environment

- public source checked: `79bbface771210df216b738e9bdc7df95e5a9e6b`;
- Alpine fixture: `alpine:3.22`, BusyBox 1.37.0;
- GNU fixture: GitHub-hosted Ubuntu 24.04;
- current execution carrier: `teamleaderleo/uv#5@1e1a66d96b4ef827ef470848cd19c504a6bdd739`.

## Filing checklist

- [x] Current upstream issue search repeated on 2026-08-01.
- [x] Existing issue found and read with all comments.
- [x] Duplicate filing rejected.
- [x] Severity and prevalence remain bounded.
- [x] Private and Fieldwork-only links excluded from any proposed public text.
- [x] Target contribution and AI policies read.
- [ ] Human author decides whether any comment adds value.
- [ ] Exact user authorization obtained before any public interaction.

No public issue comment, reaction, assignment, or other upstream interaction occurred.
