# cargo-binstall installer executable-mode experiment

State: `execution queued`

Parent scout: `#561`  
Exact target: `cargo-bins/cargo-binstall@f3284c9c2dd42d52f4437bf415a5712669699999`  
Public upstream issue: `cargo-bins/cargo-binstall#2520`  
Upstream contact authorized: `false`

## In simple words

The official Unix installer extracts a downloaded `cargo-binstall` launcher and immediately executes it. This experiment asks what happens when the archive contains the correct bytes but the extracted file is not executable.

## Claim boundary

This is a fork-free installer-contract experiment. It does not claim that current official release archives have bad modes. It tests whether the installer has its own bounded recovery when extraction produces mode `0644`.

## Exact matrix

The probe executes the unmodified installer with local fake Linux release archives:

1. launcher mode `0755` — healthy control;
2. launcher mode `0644` — losing control;
3. launcher mode `0644` after inserting `chmod u+x ./cargo-binstall` immediately before the existing launch site;
4. launcher mode `0755` with the same narrow repair — compatibility control.

The fake launcher records its received arguments and its mode at execution. The fake network command only supplies the local archive bytes. The target installer script, archive extraction command, temporary-directory behavior, launch expression, fallback expression, and path handling remain real.

## Acceptance criteria

- exact target head is asserted before execution;
- the `0755` control executes `--self-install` successfully;
- the current installer cannot execute the `0644` launcher and produces no launcher receipt;
- the narrow repair changes `0644` to `0744`, not `0755` or another widened mode;
- the repair leaves an existing `0755` launcher at `0755`;
- no external repository is modified or contacted beyond read-only source checkout.

## Decision rule

If the matrix passes as predicted, retain `chmod u+x` as the smallest demonstrated repair direction. That does not yet prove it is the maintainers' preferred policy; a later source candidate must also compare explicit malformed-artifact rejection and verify macOS zip extraction behavior.

If `0644` already executes or another step repairs the mode implicitly, stop the candidate as not reproduced.
