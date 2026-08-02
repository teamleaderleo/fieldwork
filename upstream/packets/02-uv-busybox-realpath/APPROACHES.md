# Approaches — Unit 02

## Selected

Remove `--` only from generated `realpath` calls, retain every `dirname --`, update uv's existing generated-text expectations, and recognize corrected/historical `python`/`python3` shebangs in project-run.

## Why selected

- It fixes the exact BusyBox failure.
- It preserves delimiter protection where BusyBox supports it.
- It leaves utility order, quoting, symlink resolution, and command count unchanged.
- It handles persisted launchers across an upgrade.
- It changes exactly four source/test files.
- It passed the full declared Rust lint plus focused source and runtime gates.

## Rejected or deferred

- **Remove both delimiters:** works, but is broader than BusyBox requires.
- **Detect BusyBox at runtime or generation time:** adds branching and can encode the wrong host into a relocatable artifact.
- **Redirect stderr:** can hide genuine resolution failures.
- **Use `readlink -f`:** changes the utility and portability contract.
- **Normalize synthetic bare option-like `$0`:** direct shebang probes produce the script path; `./-tool` passes.
- **Recognize arbitrary interpreter basenames:** no exact producer was found beyond `python` and `python3`.
- **Cross-crate centralization:** broader refactor without a demonstrated need for this fix.

## Final source

- Base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Head: `047b724212905c034c15d4f4f6f9ef330bbd2daf`
- Tree: `e0832686bd982b5c15f6e9bdd6d6631d30ec24cf`

No public upstream contact occurred.