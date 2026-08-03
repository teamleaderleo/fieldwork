# Decision brief — uv BusyBox `realpath` compatibility

## Recommendation

Advance Unit 02 to human upstream preparation.

This is one of the stronger contribution candidates in the current backlog: the public defect is still open and recently reproduced, the product change is narrow, the historical behavior is preserved, all known source owners move together, and exact cross-platform evidence is green.

## The user-visible problem

On Alpine and other BusyBox systems, a successful uv-generated command can print:

```text
realpath: --: No such file or directory
```

The command may still work. That makes the defect easy to dismiss technically and costly operationally: successful automation gains error-looking stderr, logs become noisy, and users investigate the wrong failure.

uv generates these launchers as durable user-facing artifacts. They outlive the command that created them and may move between systems.

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

Canonicalization was introduced for symlinked relocatable entrypoints. The patch preserves the algorithm and removes one incompatible token.

### It respects relocation

A generated environment may execute on a different host from the one that generated it. One portable fragment is safer than encoding generator-host BusyBox detection into the artifact.

### It handles upgrades

Generated launchers persist. The project-run recognizer accepts old and new text for both observed interpreter basenames, avoiding an upgrade-time migration regression.

### It is tested at the right layers

The evidence includes source assertions, consumer migration tests, uv's existing relocatable-venv integration test, full workspace clippy, and executable launcher/activation matrices on GNU, Alpine/BusyBox, and macOS with Bash and Fish.

## Evidence summary

Exact source:

- base `79bbface771210df216b738e9bdc7df95e5a9e6b`
- head `17fb4489a71cc63a59b90ecc52b08f703ca0d0e8`
- tree `e0832686bd982b5c15f6e9bdd6d6631d30ec24cf`
- one commit; four files; 89 insertions; 15 deletions

Terminal runs:

- main Linux/source, macOS, and publication jobs: success
- GNU and Alpine/BusyBox Fish job: success
- macOS Fish job: success

Baseline BusyBox behavior reproduced the false diagnostic. The candidate preserved successful resolution with empty stderr. GNU and macOS stayed clean.

## Likely objections

### “The command already succeeds.”

Successful commands should not emit false errors. CI wrappers, log scanners, and users treat stderr as a health signal. The issue has continued to attract reports because the noise looks actionable.

### “Just detect BusyBox.”

Detection adds branching and can select the wrong artifact for a relocatable environment that later runs elsewhere. The unconditional candidate already passes the supported platforms tested.

### “Removing `--` weakens leading-dash safety.”

The candidate retains every `dirname --`. Direct launcher and activation matrices cover `./-tool` and `./-activate`; direct shebang probes show `$0` is supplied as the script path. No supported bare option-like `$0` case was demonstrated.

### “The project-run matcher is too much code for a one-token fix.”

The matcher is migration compatibility, not the BusyBox fix itself. Generated text is consumed later, old launchers persist, and both `python` and `python3` are observed producer forms. Four explicit strings keep the accepted grammar narrow and reviewable.

### “Why not refactor all fragments into one helper?”

That can be considered separately. Centralization broadens the change without reducing the compatibility work or migration requirement.

## Remaining risks

- The complete uv repository test suite was not run.
- The patch is pinned to the reviewed upstream base and needs one final current-main reconciliation.
- A human must verify Astral's current contribution and AI-assistance policy and own the public wording and submission.

## The ask

Approve one final human review of the exact four-file diff and current upstream overlap. When those remain clear, authorize preparation of a human-authored pull request referencing `astral-sh/uv#16209`.

No public upstream interaction has occurred.