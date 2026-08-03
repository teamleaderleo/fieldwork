# Decision brief — uv BusyBox `realpath` compatibility

## Recommendation

Advance Unit 02 to human upstream preparation after the current-context CI run completes successfully.

This is one of the stronger candidates in the backlog: the public defect remains open and recently reproduced, the product change is narrow, historical behavior is preserved, every known source owner moves together, and the unchanged four source blobs already have exact cross-platform evidence.

## The user-visible problem

On Alpine and other BusyBox systems, a successful uv-generated command can print:

```text
realpath: --: No such file or directory
```

The command may still work. That makes the defect easy to dismiss technically and costly operationally: successful automation gains error-looking stderr, logs become noisy, and users investigate the wrong failure.

uv generates these launchers as durable user-facing artifacts. They can outlive the uv command that created them and can move between systems.

## The proposed change

Current generated fragment:

```sh
"$(dirname -- "$(realpath -- "$0")")"
```

Candidate:

```sh
"$(dirname -- "$(realpath "$0")")"
```

Only the unsupported `realpath --` delimiter is removed.

The source commit also:

- updates POSIX and Fish activation generation;
- updates uv's existing exact generated-text expectations;
- keeps `realpath` canonicalization for externally symlinked launchers;
- recognizes corrected and historical launchers using `python` or `python3` during project-run copying.

## Why this shape deserves support

### It fixes the demonstrated defect, not a broader theory

BusyBox `realpath` rejects the delimiter. BusyBox `dirname` supports it. The candidate changes the former and preserves the latter.

### It protects the historical reason `realpath` exists

Canonicalization exists so a launcher invoked through an external symlink still locates the original environment. The patch preserves that algorithm.

### It respects relocation

A generated environment may execute on a different host from the one that generated it. One portable fragment is safer than encoding generator-host BusyBox detection into a durable artifact.

### It handles upgrades

Generated launchers persist. The project-run recognizer accepts old and new text for both observed interpreter basenames, avoiding an upgrade-time migration regression.

### It is tested at the correct layers

Evidence includes source assertions, the consumer migration test, uv's existing relocatable-venv integration test, full workspace clippy, and executable launcher and activation matrices on GNU, Alpine/BusyBox, and macOS with Bash and Fish.

## Current reconciliation

- Canonical base: `92b7185783b56e8ad1dbe0bb7600432708f2c9fb`
- Clean head: `53a4bd1f7d715f57aed33bd1453954a14bb327e6`
- Tree: `9c6099ab9e6489377775d710b48855aae02079c3`
- One commit ahead, zero behind
- Four files, 89 insertions, 15 deletions
- Internal reconciliation PR: `teamleaderleo/uv#29`
- Current-context CI: `30844806321` — queued at last check

Canonical main advanced 12 commits from the prior reviewed base. None touched the four candidate paths. The branch was rebuilt with the same validated blobs on top of the current canonical tree.

## Likely objections

### “The command already succeeds.”

Successful commands should not emit false errors. CI wrappers, log scanners, and users treat stderr as a health signal.

### “Just detect BusyBox.”

Detection adds branching and can select the wrong artifact for a relocatable environment that later runs elsewhere. The unconditional candidate already passed the tested userlands.

### “Removing `--` weakens leading-dash safety.”

The candidate retains every `dirname --`. Direct launcher and activation matrices cover `./-tool` and `./-activate`; direct shebang probes show `$0` is supplied as the script path. No supported failing bare option-like `$0` case was demonstrated.

### “The project-run matcher is too much code for a one-token fix.”

The matcher is migration compatibility. Old generated text persists, and both `python` and `python3` are observed producer forms. Four exact strings keep the accepted grammar narrow and reviewable.

### “Why not centralize all fragments?”

That can be considered separately. Centralization broadens the patch without reducing the compatibility or migration work required here.

## Remaining risks

- The current-context CI run is not yet complete.
- The complete uv repository test suite was not run in the earlier exact validation; affected crates, focused tests, full workspace clippy, and platform matrices were green.
- Upstream overlap must be refreshed immediately before action.
- A human must verify Astral's current contribution and AI-assistance policy and own the public wording and submission.

## The ask

Review `CODE_WALKTHROUGH.md`, the exact four-file diff, `UPSTREAM_ISSUE.md`, and `UPSTREAM_PR.md`. If current-context CI is green and overlap remains clear, authorize preparation of a human-authored pull request referencing `astral-sh/uv#16209`.

No public upstream interaction occurred.