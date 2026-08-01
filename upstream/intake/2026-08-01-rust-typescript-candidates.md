# Rust and TypeScript upstream candidate intake — 2026-08-01

## In simple words

This record keeps six current Rust and TypeScript tooling leads visible without turning them into numbered upstream contribution units before source work exists.

The strongest compact implementation lead is Biome `.htm` recognition. The strongest deeper systems lead is uv interrupted self-update recovery. Jujutsu offers a small privacy-oriented Rust CLI task. Oxc offers a bounded Rust AST rule with direct JavaScript and TypeScript impact. A one-variable uv `EnvironmentOptions` migration is a lower-risk entry task. ty auto-indent is a research-first editor behavior problem.

No public upstream interaction is authorized. None of these leads has a Fieldwork source candidate at intake time.

## Retrieval boundary

- Retrieval date: 2026-08-01
- Fieldwork coordination issue: https://github.com/teamleaderleo/fieldwork/issues/457
- Priority-zero backlog: https://github.com/teamleaderleo/fieldwork/issues/435
- Public records were read as issue, comment, and pull-request metadata only.
- Evidence class: source-not-yet-read; public-record triage only.
- Internal duplicate search: no open Fieldwork issue matching the exact candidate behavior was found before issue 457 was created.

## Activation order

1. Biome `.htm` recognition.
2. Jujutsu redacted operation details.
3. uv interrupted self-update recovery.
4. Oxc `unicorn/no-impossible-length-comparison`.
5. one remaining uv `EnvironmentOptions` variable.
6. ty auto-indent ecosystem and test design.

The order reflects boundedness and likely reviewability, not public-project importance.

## Candidate A — Biome `.htm` recognition

- Repository: https://github.com/biomejs/biome
- Public issue: https://github.com/biomejs/biome/issues/11112
- Intake state: open, unassigned, good-first-issue.
- Maintainer signal: a maintainer invited a pull request and described the change as easy.
- Likely work class: Rust implementation plus target-native parser/formatter or language-detection tests.
- First bounded question: where is file-extension language recognition owned, and which native tests prove `.htm` follows the same path as `.html`?
- Required claim-time checks:
  - pin current default-branch SHA;
  - search open and recently closed pull requests for `.htm`, HTML extension recognition, and language detection;
  - read contribution and AI-disclosure guidance;
  - identify all extension registries, generated tables, snapshots, and editor-facing detection paths;
  - produce one focused failing native test before changing behavior.
- Promotion threshold: a source-only branch with the extension change, target-native regression coverage, ordinary relevant gates, and complete-diff review.
- Initial recommendation: activate first.

## Candidate B — uv interrupted Windows self-update recovery

- Repository: https://github.com/astral-sh/uv
- Public issue: https://github.com/astral-sh/uv/issues/12142
- Intake state: open, unassigned, `help wanted`, Windows-specific.
- Maintainer signal: maintainers consider narrowing the failure window or moving the running executable to a temporary name; exact atomic replacement is constrained by Windows executable semantics.
- Likely work class: Rust updater/recovery behavior, possibly involving `axoupdater` or `self-replace` ownership boundaries.
- First bounded question: which layer owns download completion, executable staging, rename, rollback, and cleanup, and at which interruption points can `uv.exe` become absent or unusable?
- Required claim-time checks:
  - pin uv and relevant updater dependency revisions;
  - map direct uv code versus dependency-owned replacement behavior;
  - identify existing Windows update tests and CI capabilities;
  - model or execute failure at download, validation, first rename, second rename, and cleanup boundaries;
  - compare at least two replacement sequences and state their rollback invariants.
- Promotion threshold: deterministic evidence for the identified failure boundary, a bounded repair owned by the correct repository, Windows-focused tests, and explicit residual interruption windows.
- Initial recommendation: strongest deeper systems lead.

## Candidate C — Jujutsu redacted `jj op log -d`

- Repository: https://github.com/jj-vcs/jj
- Public issue: https://github.com/jj-vcs/jj/issues/9375
- Intake state: open, unassigned, good-first-issue, no comments at retrieval.
- Reported behavior: `builtin_op_log_redacted` redacts ordinary operation-log content, while the changed-commits section emitted with `-d` remains unredacted.
- Likely work class: Rust rendering/template plumbing plus command-output tests.
- First bounded question: is the changed-commits section already templated, or does redaction require a new rendering boundary?
- Required claim-time checks:
  - pin current default-branch SHA;
  - find the operation-log renderer, changed-commits renderer, redacted template, and output fixtures;
  - prove one leaking field under the redacted template;
  - determine whether the repair is local or requires a generalized template parameter;
  - stop after mapping if the issue expands into a broad templating redesign.
- Promotion threshold: one focused redaction invariant, native output tests, and no accidental loss of useful non-sensitive operation detail.
- Initial recommendation: activate second.

## Candidate D — Oxc `unicorn/no-impossible-length-comparison`

- Repository: https://github.com/oxc-project/oxc
- Public tracker: https://github.com/oxc-project/oxc/issues/684
- Upstream rule reference: https://github.com/sindresorhus/eslint-plugin-unicorn/blob/v72.0.0/docs/rules/no-impossible-length-comparison.md
- Intake state: listed as unimplemented in the generated tracker; no exact-title pull request was found during intake.
- Likely work class: Rust AST lint rule, diagnostics, fixtures, snapshots, and parity cases.
- First bounded question: can the Unicorn rule semantics be reproduced without type information and without overlapping an existing Oxc correctness rule?
- Required claim-time checks:
  - re-read the generated tracker immediately before claiming;
  - search branches and pull requests by exact rule name and diagnostic wording;
  - run `just new-unicorn-rule no-impossible-length-comparison` only after the claim;
  - derive a semantic matrix from the upstream rule tests rather than copying implementation blindly;
  - add false-positive controls for unknown values, computed properties, optional chains, and non-literal bounds where applicable;
  - check overlap with existing Oxc comparison and length rules.
- Promotion threshold: target-native rule tests, snapshots, focused clippy/test gates, and an explicit compatibility statement against the referenced Unicorn version.
- Initial recommendation: activate after Biome or Jujutsu unless a competing pull request appears.

## Candidate E — one uv `EnvironmentOptions` migration

- Repository: https://github.com/astral-sh/uv
- Public issue: https://github.com/astral-sh/uv/issues/14720
- Intake state: open, unassigned, `help wanted`.
- Maintainer signal: move one environment variable at a time using the established `EnvironmentOptions` abstraction.
- Unchecked variables at retrieval included:
  - `UV_COMPILE_BYTECODE_TIMEOUT`;
  - `UV_RUN_RECURSION_DEPTH`;
  - `UV_RUN_MAX_RECURSION_DEPTH`;
  - `UV_GITHUB_FAST_PATH_URL`;
  - `UV_GIT_LFS`;
  - `UV_CUDA_DRIVER_VERSION`;
  - `UV_AMD_GPU_ARCHITECTURE`;
  - `UV_STACK_SIZE`;
  - `TRACING_DURATIONS_FILE`;
  - `UV_LOCK_TIMEOUT`.
- First bounded question: which single unchecked variable has no active pull request and a clean parsing, precedence, and error-reporting contract?
- Required claim-time checks:
  - inspect every recent pull request linked from the issue and search each candidate variable;
  - choose exactly one variable;
  - read at least two merged migration precedents;
  - preserve CLI/config/environment precedence;
  - add invalid-value, unset-value, and compatibility tests appropriate to that variable.
- Promotion threshold: one-variable diff, ordinary relevant gates, and no unrelated environment parsing cleanup.
- Initial recommendation: reserve entry task.

## Candidate F — ty auto-indent through LSP on-type formatting

- Repository: https://github.com/astral-sh/ty
- Public issue: https://github.com/astral-sh/ty/issues/2276
- Intake state: open, unassigned, `help wanted`.
- Maintainer signal: `textDocument/onTypeFormatting` is the likely protocol path; maintainers requested ecosystem analysis, practical heuristics, parser-recovery consideration, and an extensive test strategy before implementation.
- Likely work class: research-first LSP/editor behavior spanning Rust server code, Python token or parser recovery, and TypeScript extension configuration.
- First bounded question: what heuristics do Pylance and existing Python indentation extensions use, and which cases need parser recovery rather than line-level indentation rules?
- Required claim-time checks:
  - identify protocol registration and editor-client capability handling;
  - inspect the referenced Python indentation extension and publicly visible behavior from Pylance without copying proprietary implementation;
  - build a case corpus covering block headers, parenthesized conditions, continuations, comments, strings, incomplete syntax, decorators, match/case, and dedent triggers;
  - state whether the first deliverable is an ecosystem report, parser support change, server implementation, or extension configuration change;
  - keep client-setting changes separate unless the protocol implementation requires them.
- Promotion threshold: a reviewed heuristic and test design, then an `ISSUE FIRST` or bounded implementation recommendation.
- Initial recommendation: research-first; activate last among these leads.

## Occupied ty work excluded from activation

The following public tasks had active work at retrieval and should not be duplicated:

- https://github.com/astral-sh/ty/issues/953 — a contributor stated they were working on dynamic configuration support.
- https://github.com/astral-sh/ty/issues/1771 — a contributor reported stacked pull requests for all remaining checkboxes.
- https://github.com/astral-sh/ty/issues/1364 — a repair pull request was linked from the issue.

## Claim record

A claim on issue 457 must name:

- candidate letter and public record;
- worker identity;
- exact target SHA and retrieval date;
- owned Fieldwork path and branch;
- intended target-source branch or explicit no-fork state;
- claim scope;
- first discriminating source question or test;
- stop condition;
- upstream-contact authorization, which remains `false`.

One worker claims one candidate. Intake does not authorize public upstream issues, comments, reactions, pull requests, or reviews.

## Disposition

Current disposition: `QUEUED LEADS`.

No candidate receives a numbered `upstream/INDEX.md` unit until a source candidate or sufficiently complete issue-first packet exists. The next coordinator action is to accept one claim on issue 457, beginning with candidate A unless current duplicate work changes the order.