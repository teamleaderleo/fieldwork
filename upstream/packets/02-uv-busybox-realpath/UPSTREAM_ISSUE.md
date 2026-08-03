# Upstream issue inputs — Unit 02

The existing public report is `astral-sh/uv#16209`. It remains open. No duplicate issue is needed.

## Latest overlap check

- The issue remains open.
- No active or closed equivalent pull request was found by searching the canonical repository for the issue number, BusyBox, Alpine, and `realpath`.
- Current indexed canonical source still contains the affected generated fragments at reviewed head `79bbface771210df216b738e9bdc7df95e5a9e6b`.
- The latest issue discussion includes a recent report that the diagnostic still appears in the official `python3.12-alpine` image.

Refresh this check immediately before any public action.

## Useful facts for a human submission

- BusyBox supports `dirname --` but not `realpath --`; the candidate changes only `realpath`.
- `realpath` remains to preserve historical external-symlink behavior.
- A generation-host BusyBox branch is weaker for a relocatable artifact that may execute on another host.
- The exact source boundary is four files, including uv's existing relocatable-venv expectation test.
- Existing corrected and historical `python` and `python3` launchers remain recognizable across the generated-text transition.
- GNU, Alpine/BusyBox, and macOS launcher/activation evidence is green, along with full workspace clippy.
- Clean source: `17fb4489a71cc63a59b90ecc52b08f703ca0d0e8` on reviewed base `79bbface771210df216b738e9bdc7df95e5a9e6b`.

A public issue comment is optional. A human may instead open a pull request that references and closes the existing issue.

Public interaction authorized: `no`. No public issue comment, reaction, assignment, or other upstream interaction occurred.