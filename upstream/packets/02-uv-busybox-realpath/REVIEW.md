# Review — Unit 02

## Disposition

`READY FOR HUMAN REVIEW`

## Subject

- Base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Current head: `17fb4489a71cc63a59b90ecc52b08f703ca0d0e8`
- Tree: `e0832686bd982b5c15f6e9bdd6d6631d30ec24cf`
- Branch: `teamleaderleo/uv:upstream/02-busybox-realpath`
- Relationship: one commit ahead, zero behind
- Public authority: none

The current head republishes the same validated source tree as earlier commit `047b724212905c034c15d4f4f6f9ef330bbd2daf`.

## Changed files

- `crates/uv-install-wheel/src/wheel.rs`
- `crates/uv-virtualenv/src/virtualenv.rs`
- `crates/uv/src/commands/project/run.rs`
- `crates/uv/tests/python/venv.rs`

## Complete-diff review result

No remaining product-code defect was found in the exact four-file diff.

Review focus:

1. Only `realpath --` is removed; every supported `dirname --` remains.
2. `realpath` itself remains, preserving externally symlinked relocatable entrypoints.
3. The project-run recognizer accepts four explicit migration forms: corrected/historical × `python`/`python3`.
4. The absolute-shebang fallback remains unchanged.
5. The private regression test verifies copied content and executable mode.
6. Existing relocatable-venv generated-text expectations move with the generator.

## Design challenge reviewed

A public issue comment suggested detecting BusyBox and conditionally post-processing generated text. The selected unconditional form is stronger for relocatable artifacts: generation host and execution host can differ, while `realpath "$operand"` passed on GNU, BusyBox, and macOS. Host-flavour branching would add state without protecting a demonstrated supported case.

## Completed gates

- exact four-file source and publication fences;
- format and affected-crate compilation;
- wheel, project-run, and relocatable-venv tests;
- full locked workspace clippy with warnings denied;
- GNU and BusyBox launcher and Bash activation probes;
- GNU, BusyBox, and macOS Fish activation probes;
- exact-source macOS main carrier;
- clean one-commit publication.

Main run `30753911776`:

- Linux/source `91621197004`: success
- macOS `91621196098`: success
- publication `91621231746`: success

Fish run `30755096609`:

- Linux GNU/BusyBox `91515786243`: success
- macOS `91515786224`: success

## Known limits

- The full repository test suite was not run.
- Public overlap and current-main applicability require one final refresh.
- The four explicit matcher strings are intentionally narrow. Broader parsing would need a concrete producer or migration case.

## Human decision

Approve this for upstream preparation when the reviewer agrees that:

- the four-string migration recognizer is preferable to a broader parser or refactor;
- exact current-main overlap remains clear;
- the public contribution policy and authorship requirements are satisfied;
- the final public action is explicitly authorized.

No public action has been taken.