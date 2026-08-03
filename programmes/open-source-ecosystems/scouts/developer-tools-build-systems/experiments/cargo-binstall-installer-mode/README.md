# cargo-binstall installer executable-mode experiment

State: `confirmed — bounded repair direction retained`

Parent scout: `#561`  
Exact target: `cargo-bins/cargo-binstall@f3284c9c2dd42d52f4437bf415a5712669699999`  
Public upstream issue: `cargo-bins/cargo-binstall#2520`  
Executed Fieldwork head: `f1afb7a14d40f35c5ba3f1d4eff5213bcab38a7a`  
Workflow run: `30794557938` — success  
Job: `91625089482` — success  
Artifact: `8848325651`, 461 bytes  
Artifact SHA-256: `bd37b970b9f0acb87f75cd305a9d8d82ddc9a0cdd986170b24868c9761c1c294`  
Upstream contact authorized: `false`

## In simple words

The official Unix installer extracts a downloaded `cargo-binstall` launcher and immediately executes it. When the archive supplied the correct launcher bytes at mode `0644`, the current installer could not execute either launch attempt. Adding only the owner execute bit made the same launcher usable without widening group or other permissions.

## Claim boundary

This is a fork-free installer-contract experiment. It does not claim that current official release archives have bad modes. It proves that the installer has no independent recovery when extraction produces mode `0644`.

Evidence class: `target-executed-installer-fixture`.

## Exact matrix and result

The probe executed the unmodified target installer with local fake Linux release archives:

1. current installer + launcher mode `0755` — passed; launcher received `--self-install` and observed mode `755`;
2. current installer + launcher mode `0644` — failed twice with `Permission denied`, exit status `126`, and no launcher receipt;
3. installer with `chmod u+x ./cargo-binstall` + launcher mode `0644` — passed; launcher received `--self-install` and observed mode `744`;
4. the same narrow repair + launcher mode `0755` — passed and remained mode `755`.

The final workflow receipt was:

```text
RESULT current-0755=pass current-0644=permission-failure patched-0644=pass-mode-744 patched-0755=pass-mode-755
```

The fake launcher recorded its arguments and its mode at execution. The fake network command only supplied local archive bytes. The target installer script, tar extraction, temporary-directory behavior, launch expression, fallback expression, and path handling were real.

## Selected direction

Retain `chmod u+x ./cargo-binstall` immediately before the existing launch expression as the smallest demonstrated repair direction.

Why it currently wins:

- it repairs exactly the missing authority required by the next operation;
- it converts `0644` to `0744`, not `0755`;
- it leaves an existing `0755` launcher unchanged;
- it does not change download selection, archive extraction, self-install arguments, fallback behavior, or destination permissions.

This is not yet a submission-shaped source candidate. A later target branch should compare explicit malformed-artifact rejection, execute the macOS zip path, and run the repository's normal install-script matrix.

## Remaining limits

- The experiment used Linux tar extraction on Ubuntu 24.04.
- It did not execute the macOS zip path or Windows installers.
- It did not prove that an official cargo-binstall release archive currently ships or extracts with mode `0644`.
- It did not select whether maintainers prefer normalization or rejection as project policy.

## Disposition

`PROMOTE — one bounded source-and-test candidate is justified.`

No public issue, pull request, comment, review, reaction, branch, or message was created or modified in the target repository.
