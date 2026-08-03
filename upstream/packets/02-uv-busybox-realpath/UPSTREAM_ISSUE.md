# Existing issue and optional comment draft — Unit 02

The public report already exists as `astral-sh/uv#16209`. It remains open. **Do not open a duplicate issue.**

## Optional issue comment draft

I investigated this against the current launcher and activation generators.

BusyBox supports the existing `dirname --` calls but treats `--` passed to `realpath` as another pathname. A narrow compatibility change is therefore sufficient: preserve `realpath` canonicalization and every `dirname --`, while generating `realpath "$path"` instead of `realpath -- "$path"`.

I tested the resulting launcher and activation forms across GNU, Alpine 3.22 / BusyBox 1.37, and macOS, including absolute and relative paths, PATH lookup, spaces, `./-tool` / `./-activate`, and external symlinks. The BusyBox baseline reproduced the false diagnostic; the candidate kept the same resolved interpreter or environment with clean stderr. Bash and Fish activation matrices also passed.

The matching `uv run` entrypoint-copy recognizer needs to accept both corrected and historical generated text, including the observed `python` and `python3` forms, so existing relocatable environments remain compatible after an upgrade.

I have a four-file source candidate and focused tests prepared. I can open a pull request referencing this issue after a final policy and overlap check.

## Latest overlap and source check

- Canonical head checked: `92b7185783b56e8ad1dbe0bb7600432708f2c9fb`.
- The canonical repository advanced 12 commits from the prior reviewed base; none touched the candidate's four paths.
- No equivalent active or closed canonical pull request was found in the latest searches for the issue number, BusyBox, Alpine, and `realpath`.
- The issue includes a recent report against the official `python3.12-alpine` image.
- Current internal source head: `53a4bd1f7d715f57aed33bd1453954a14bb327e6`.
- Internal current-context CI run: `30844806321`, queued at last check.

Refresh all of these immediately before any public action.

## Human decision

An issue comment is optional because the report already contains a clear reproduction. The cleaner route may be a pull request that references and closes the existing issue.

Public interaction authorized: `no`. No public issue comment, reaction, assignment, or other upstream interaction occurred.