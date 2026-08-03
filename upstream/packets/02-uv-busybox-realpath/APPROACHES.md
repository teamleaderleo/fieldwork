# Approaches — Unit 02

## Selected

Remove `--` only from generated `realpath` calls, retain every `dirname --`, update uv's existing generated-text expectations, and recognize corrected/historical `python`/`python3` shebangs in project-run.

## Why selected

- It fixes the exact BusyBox failure.
- It preserves delimiter protection where BusyBox supports it.
- It leaves utility order, quoting, symlink resolution, and command count unchanged.
- It generates one artifact format that works on GNU, BusyBox, and macOS regardless of the generation host.
- It handles persisted launchers across an upgrade.
- It changes exactly four source/test files.
- It passed the full declared Rust lint plus focused source and runtime gates.

## Alternatives reviewed

### Remove both delimiters

This works in the tested ordinary cases but is broader than the defect. BusyBox `dirname` supports `--`, so removing it discards useful operand protection without buying compatibility.

### Detect BusyBox at generation time

Rejected. Relocatable artifacts may execute on a different host from the host that generated them. Host detection can encode the wrong launcher form into a moved environment, and the unconditional candidate already passes all tested platforms.

### Detect BusyBox at launcher runtime

Rejected. It adds process and branching complexity to every generated launcher. No supported platform requires that branch because the selected realpath-only form is already portable across the completed matrix.

### Redirect `realpath` stderr

Rejected. It hides genuine path-resolution errors together with the false BusyBox diagnostic.

### Replace `realpath` with `readlink -f`

Rejected. This changes the utility and portability contract and risks the historical symlink behavior the canonicalization was added to protect.

### Remove `realpath`

Rejected. External-symlink invocation would derive the interpreter from the alias location instead of the original relocatable environment.

### Normalize speculative bare option-like `$0`

Deferred. Direct shebang probes supply the script path; `./-tool` passes. No supported invocation producing a bare `-tool` `$0` was demonstrated.

### Recognize arbitrary interpreter basenames

Rejected. Exact producers were found for `python` and `python3`. A broader grammar would expand migration authority without a concrete generated case.

### Cross-crate centralization

Deferred. A shared fragment may be a useful cleanup later, but it would broaden this compatibility fix and does not reduce the required migration recognition.

## Final source

- Base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Current head: `17fb4489a71cc63a59b90ecc52b08f703ca0d0e8`
- Previous byte-identical head: `047b724212905c034c15d4f4f6f9ef330bbd2daf`
- Tree: `e0832686bd982b5c15f6e9bdd6d6631d30ec24cf`

No public upstream contact occurred.