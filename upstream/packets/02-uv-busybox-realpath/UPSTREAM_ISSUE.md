# Upstream issue inputs — BusyBox `realpath` diagnostic in relocatable launchers

Status: `existing public issue #16209; duplicate filing rejected`  
Public interaction authorized: `no`

## Existing issue

The canonical public report is [`astral-sh/uv#16209`](https://github.com/astral-sh/uv/issues/16209), “Generated shebang lines output 'realpath: --: No such file or directory'.” It contains an Alpine reproduction, expected and actual output, the BusyBox utility explanation, and the leading-hyphen trade-off.

The issue remained open when checked on 2026-08-01. A second issue would duplicate the report.

## Verified additional evidence

A human may use these facts when deciding whether a comment adds value:

- the generated pattern is owned by wheel and virtualenv source, with an exact project-run recognizer;
- final source commit `c42973ef0490c75df1c7e7f4e9a54d46c6bca059` changes exactly those three source files;
- newly generated launchers omit the unsupported utility delimiters;
- project-run keeps recognizing both corrected and previously generated historical shebangs;
- `cargo fmt --all --check`, affected-crate compilation, the wheel shebang test, and a direct current/legacy recognizer test pass;
- GNU, Alpine 3.22 BusyBox, and macOS 15 matrices pass across absolute, relative, PATH, spaces, `./-tool`, and external symlink invocation;
- BusyBox current cases succeed with the expected diagnostic while corrected cases remain quiet;
- direct shebang probes on Linux and macOS show shell `$0` is the script path even when caller argv0 is forced to `-tool` or `--help`.

## Exact private receipt

- Public source base/current main: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Clean private source head: `c42973ef0490c75df1c7e7f4e9a54d46c6bca059`
- Execution carrier: `teamleaderleo/uv#7@6fbdf4d7fb0ff577f5be24972b1a5bba73111793`
- Workflow: `30690034279`
- Linux/source job: `91342987834`
- macOS job: `91342987814`
- Publication job: `91343684491`

Private fork and Fieldwork links should stay out of public issue text unless the human author deliberately chooses otherwise.

## Human comment decision

A public issue comment is optional. A clean pull request referencing #16209 may carry the useful technical evidence without adding another issue message.

Recommended default: keep #16209 untouched until the human author decides a pre-PR comment helps maintainers.

## Checklist

- [x] Current upstream issue search repeated on 2026-08-01.
- [x] Existing issue and comments read.
- [x] Duplicate filing rejected.
- [x] Severity and prevalence kept bounded.
- [x] Final source, migration behavior, platform tests, and option-like `$0` evidence recorded privately.
- [x] Target contribution and AI policies recorded.
- [ ] Human author decides whether a public comment adds value.
- [ ] Explicit authorization obtained before any public interaction.

No public issue comment, reaction, assignment, or other upstream interaction occurred.
