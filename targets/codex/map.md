# Target Map: Codex

Repository: https://redirect.github.com/openai/codex

## In simple words

An agentic coding CLI that coordinates model interaction, tools, permissions, repository state, process execution, and terminal output. Failures can appear at the boundaries between those systems rather than in one isolated function.

## Areas worth understanding

- session and turn lifecycle;
- tool execution and approval boundaries;
- subprocess state, cancellation, and cleanup;
- terminal rendering and event ordering;
- repository and worktree state;
- retries, interruption, and recovery;
- extension or integration surfaces;
- tests for partial failure and unusual environments.

## Evidence we can produce

- deterministic process and event fixtures;
- interrupted-session experiments;
- terminal and subprocess harnesses;
- repository-state reproductions;
- comparison with owned agent and CLI projects;
- security-boundary maps.

## GitHub Actions execution prerequisites

Codex execution carriers should copy the target repository's current CI prerequisites from an exact public source revision before running repository entrypoints.

At `openai/codex@413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`:

- `./.github/actions/setup-ci` configures shared build paths and installs DotSlash and `just`;
- `setup-ci` does **not** install `uv`;
- `.github/workflows/repo-checks.yml` installs `uv` separately with `astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b` and version `0.11.3` before `just fmt-check`;
- root `just fmt` and `just fmt-check` call `scripts/format.py`, which invokes `uv run` for both the Python SDK and repository scripts;
- `just test` uses `cargo nextest`, so a carrier must install `cargo-nextest` when its selected setup path does not already provide it.

Therefore a GitHub Actions carrier that runs full repository formatting must install `uv` explicitly even after `setup-ci`. Do not infer that `setup-ci` is the complete toolchain. Treat the current upstream workflows and entrypoints as the source of truth, pin every external action, and record the exact target revision used to derive the setup.

A missing `just`, `uv`, formatter dependency, test runner, or other declared prerequisite is a carrier or harness failure. It supplies no Codex source-behavior evidence. Preserve the failed command and repair the environment before changing product source or weakening the gate.

The retained failure and repair history for the current convergence work lives in `findings/F239-codex-upstream-convergence/evidence/20260731-codex-ci-prerequisites.md`.

## Entry standard

Research is quiet. Confirm current contribution policy before proposing implementation. A useful finding must identify a real lifecycle, correctness, security, performance, or integration consequence.

## Stop conditions

- the result is only terminal styling or wording;
- the behavior cannot be reproduced independently of model nondeterminism;
- the proposal requires unsolicited architectural replacement;
- current policy requires maintainer direction before code work.
