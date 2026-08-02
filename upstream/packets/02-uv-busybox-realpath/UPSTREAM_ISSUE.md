# Upstream issue inputs — Unit 02

The existing public report is `astral-sh/uv#16209`. It remains open and is labeled as a bug/compatibility issue. A duplicate issue is unnecessary.

Useful facts for a human-authored submission:

- BusyBox supports `dirname --` but not `realpath --`; the candidate changes only `realpath`.
- The exact source boundary is four files, including uv's existing relocatable-venv expectation test.
- Existing `python` and `python3` launchers remain recognizable across the generated-text transition.
- GNU and BusyBox focused behavior passes, along with the full declared Rust clippy gate.
- Clean source: `047b724212905c034c15d4f4f6f9ef330bbd2daf` on base `79bbface771210df216b738e9bdc7df95e5a9e6b`.
- Exact final macOS execution remains unclaimed; earlier macOS evidence is supporting context only.

A public issue comment is optional. A human may instead open a pull request that references the existing issue.

Public interaction authorized: `no`. No public issue comment, reaction, assignment, or other upstream interaction occurred.