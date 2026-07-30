# Open-Source Ecosystems and Upstream Contribution Campaigns

## In simple words

Find consequential work across package collections, runtimes, tools, libraries, databases, and Linux systems; prove each candidate locally; then carry the strongest fixes upstream with tests and a compact evidence packet.

- Programme hub: #207
- State: `ready`
- Coordinator: `teamleaderleo`
- Upstream contact: unauthorized by default

## Current direction

Run a wide discovery portfolio while keeping implementation and review bounded.

1. Start with package collections because one contribution surface exposes many upstream projects and build systems.
2. Run runtime, standard-library, diagnostic, and developer-tool scouts in parallel.
3. Promote foundational-library and database candidates when a reduced input or deterministic fixture exists.
4. Route Linux package, process, filesystem, service, privilege, container, and kernel-facing work through `linux-fieldwork`.
5. Keep security-sensitive, compiler-backend, hardware-specific, and kernel work behind stronger reproduction and environment gates.

## Execution waves

### Wave A — broad high-yield surfaces

- Nixpkgs, Homebrew Core, Debian, Fedora, and Arch packaging;
- CPython and Rust diagnostics or regression coverage;
- Ruff, Clippy, pytest, Meson, and package-manager correctness;
- reproducibility and downstream-patch retirement.

### Wave B — depended-on boundaries

- HTTP, URL, archive, compression, Unicode, date/time, path, and configuration libraries;
- database engines and client drivers;
- cancellation, cleanup, cache, lockfile, and compatibility behavior.

### Wave C — systems work

- systemd, util-linux, Podman, BuildKit, containerd, Mesa, and selected compiler or kernel-facing tools;
- VM, privileged, architecture, filesystem, and kernel-matrix investigations.

## Portfolio rules

- Candidate inventory may grow large.
- Scouts return ranked branches, reproducible evidence, negative results, and a recommendation.
- Experiments answer one distinguishing question.
- Implementation begins after a reproduction, failing test, deterministic difference, or clearly bounded missing capability exists.
- Keep at most three new implementation branches awaiting first review at once.
- Each promoted contribution has one canonical branch, one owner, an exact source revision, and explicit remaining gates.
- Park stale work with the blocker, preserved evidence, and the condition that would reopen it.

## First outputs

- [`SCOUT_MATRIX.md`](SCOUT_MATRIX.md) — initial portfolio and promotion gates;
- ranked package-collection candidates;
- runtime and developer-tool reduced reproducers;
- a reusable contribution packet template backed by actual submissions;
- a ledger of accepted, declined, superseded, and retained-negative-result work.

## Current decision

Begin broad reconnaissance immediately. Prefer candidates that can reach a failing test or deterministic build difference in current CI. Use the larger ambition to create parallel choice, then concentrate review effort on branches with the clearest consequence and smallest credible patch.