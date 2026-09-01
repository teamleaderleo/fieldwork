# Research notes: reliable stateful CLI precedents

Retrieved 2026-08-12. These are observations and design takeaways, not endorsements of whole projects.

## Homebrew — findings and remediation as separate concepts

Observed source:

- https://github.com/Homebrew/brew/blob/0d7b47e8d897dce76ee46a5d25636cf1c60fc39b/Library/Homebrew/diagnostic/finding.rb
- https://github.com/Homebrew/brew/blob/0d7b47e8d897dce76ee46a5d25636cf1c60fc39b/Library/Homebrew/diagnostic.rb

Useful idea: diagnostics can be represented as findings with remediation attached separately. That encourages reuse and lets a health/doctor surface aggregate several independent conditions without turning every condition into one ad-hoc command error.

BDFL takeaway: **store the finding; render the sentence.**

## pipx — health and repair are product operations

Observed source/docs:

- https://github.com/pypa/pipx/blob/04301bcce2fbf57b5498e12e91ee4c8509c56c7e/src/pipx/commands/health.py
- https://github.com/pypa/pipx/blob/04301bcce2fbf57b5498e12e91ee4c8509c56c7e/src/pipx/result.py
- https://github.com/pypa/pipx/blob/04301bcce2fbf57b5498e12e91ee4c8509c56c7e/docs/reference/json-output.rst
- https://github.com/pypa/pipx/blob/04301bcce2fbf57b5498e12e91ee4c8509c56c7e/docs/how-to/troubleshoot.rst

Useful ideas:

- explicit health inspection;
- explicit repair/rebuild behavior from retained install metadata;
- command result objects that can render human output or JSON;
- repair as a normal path instead of an undocumented deletion ritual.

Its changelog also contains useful battle scars around backup directories, environment repair, exposure ownership, and partial exposure failures. Those are reminders that package-manager bugs often live at the boundary between logical install state and arbitrary filesystem contents.

BDFL takeaway: **desired install intent should outlive a disposable environment.**

## Git — porcelain is a promise to machines

Observed docs:

- https://github.com/git/git/blob/11c6700f10234578d10523faf35656ca491425c9/Documentation/git-status.adoc

Git deliberately distinguishes long-form human status from stable porcelain formats intended for scripts.

BDFL takeaway: **do not freeze human prose merely because automation exists. Give automation a separate contract.**

## Nix — versioned profiles and rollback

Observed docs/source:

- https://github.com/NixOS/nix/blob/24b65e35d9d4c9d64c1bd5844a35f2a779356d63/doc/manual/source/package-management/profiles.md
- https://github.com/NixOS/nix/blob/24b65e35d9d4c9d64c1bd5844a35f2a779356d63/src/nix/profile-rollback.md

Useful idea: construct new profile generations separately, switch the active generation, preserve history, and make rollback an explicit operation.

BDFL takeaway: **activation should be a small atomic decision over already-complete state.**

## rustc/rustfix — suggestions have applicability

Observed public concept:

- https://doc.rust-lang.org/stable/nightly-rustc/rustc_errors/enum.Applicability.html

Rust diagnostics distinguish suggestions that tooling can confidently apply from suggestions requiring human judgement.

BDFL extension: applicability needs a second axis for operational tools:

```text
confidence × safety
```

A repair can be certain but destructive, or conditional but reversible. Automation policy should understand both.

## Cargo — fuzzy help is strongest for lexical mistakes

Observed source:

- https://github.com/rust-lang/cargo/blob/eb98b54bc9f3c74519f43d066cb3fd02ebc88df0/src/util/edit_distance.rs

Cargo keeps reusable edit-distance helpers for nearby-name suggestions.

BDFL takeaway: **“did you mean” is excellent for lexical ambiguity and dangerous when it pretends to understand semantic or ownership ambiguity.**

Do not turn an invalid managed-directory name into a suggestion to rename arbitrary state into a plausible identity unless the rest of the identity can be proven.

## Volta — stable dispatcher shims

Observed source:

- https://github.com/volta-cli/volta/blob/5eedd5fb2f682baceb47a242289111fcd79435a5/crates/volta-core/src/shim.rs
- https://github.com/volta-cli/volta/blob/5eedd5fb2f682baceb47a242289111fcd79435a5/src/volta-shim.rs

Volta demonstrates a useful indirection model: many public command names can dispatch through one stable shim implementation. Its Unix and Windows implementations differ while presenting one logical tool-routing concept.

BDFL takeaway: **public command identity can be stable while the selected runtime changes behind it.**

## mise — shims are useful and carry ergonomic debt

Observed docs/source:

- https://github.com/jdx/mise/blob/5c625afba01bcb9c91e9a26003e3a8fb07c2293c/docs/dev-tools/shims.md
- https://github.com/jdx/mise/blob/5c625afba01bcb9c91e9a26003e3a8fb07c2293c/src/shims.rs

Useful observations:

- shims work in non-interactive contexts where prompt-driven PATH activation does not;
- executable sets need reconciliation (`reshim`);
- ordinary `which` shows the shim rather than the selected real executable;
- an unresolved managed shim can optionally fall through to a same-named system executable.

BDFL choices:

- steal stable shims where they simplify activation/rollback;
- provide a first-party `which`/explain command;
- reconcile stale shims automatically from owned state;
- **reject silent fallback to unrelated same-named executables** for a manager that claims authority over that command name.

## uv — useful existing primitives and useful failure boundaries

Observed in the owned fork while investigating tool state:

- tool inventory currently derives package identity from child-directory basenames;
- malformed/missing receipt state can be retained per tool after enumeration succeeds;
- top-level enumeration errors are distinct from per-tool receipt errors;
- Unix tool entrypoints can be symlinked to environment scripts;
- Windows generated launchers are copied into the public bin directory;
- Windows trampoline metadata contains a readable Python target path;
- public entrypoint publication and receipt publication have separate durable steps.

The concrete diagnostic experiment remains under `experiments/uv-21058-diagnostics/`.

BDFL takeaway: **publication provenance and the logical active generation deserve explicit identities of their own.**

## Cross-project synthesis

The recurring pattern is that reliable tools separate these questions:

1. What did we observe?
2. Was observation complete?
3. Which objects do we own?
4. What state do we want?
5. Which proposed action follows from the exact finding?
6. How confident are we in that action?
7. How safe/reversible is it?
8. Who or what authorises it?
9. Did the process run?
10. Did a fresh observation prove the intended result?

Most nasty state-management bugs come from collapsing two or more of those questions into one boolean, one directory name, one receipt, one exit code, or one friendly sentence.
