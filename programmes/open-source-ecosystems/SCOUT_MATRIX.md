# Open-Source Ecosystem Scout Matrix

This matrix is an initial dispatch map. A named project is permission for quiet reconnaissance only.

| Lane | Scope | First targets | First return | Promotion signal | State |
|---|---|---|---|---|---|
| OE-01 | Distribution package collections | Nixpkgs, Homebrew Core, Debian, Fedora, Arch | contribution-surface map and ranked candidate queue | reproducible build failure, stale downstream patch, portability defect, architecture gap, or deterministic package variance | ready |
| OE-02 | Runtimes and standard libraries | CPython, Rust | code/test map plus reduced cross-platform or diagnostic cases | failing regression test, incorrect result, resource defect, or measurable hot-path improvement | ready |
| OE-03 | Developer tools | Ruff, Clippy, pytest, ShellCheck, Meson | parser/analysis/fix pipeline map and minimized cases | false positive, missed diagnostic, unsafe fix, mode disagreement, or cleanup failure | ready |
| OE-04 | Package managers and build tools | pip, uv, Cargo, Nix, Homebrew, CMake, Meson | resolver/cache/build-isolation map and environment matrix | deterministic resolution, cache, lockfile, offline, proxy, certificate, or platform-detection defect | ready |
| OE-05 | Foundational libraries | curl, libarchive, urllib3, serde, Tokio | dependency-use map and malformed/boundary input corpus | crash, leak, incorrect parse, portability difference, lifecycle defect, or protocol mismatch | ready |
| OE-06 | Databases and drivers | DuckDB, SQLite, PostgreSQL clients | query/transaction/storage/client boundary map | incorrect result, recovery defect, deterministic planner regression, conversion bug, or driver incompatibility | ready |
| OE-07 | Linux systems and containers | systemd, util-linux, Podman, BuildKit, containerd, Mesa | environment-gated target map linked to `linux-fieldwork` | reproducible lifecycle, namespace, mount, filesystem, resource, compatibility, or device-independent failure | ready |
| OE-08 | Reproducibility and supply chain | Reproducible Builds tools, diffoscope, reprotest, Sigstore, TUF | provenance and comparison workflow map | deterministic unverifiable output, normalization gap, metadata ambiguity, verification defect, or actionable diagnostic gap | ready |

## Dispatch order

1. Run OE-01, OE-02, and OE-03 first because they offer many small independent review units.
2. Start OE-04 and OE-05 when a specific environment or dependency boundary can be pinned.
3. Reuse the existing DuckDB target hub for OE-06 before adding more database hubs.
4. Route OE-07 execution through Linux Fieldwork lanes and investigations.
5. Begin OE-08 with reproducibility work already adjacent to package builds.

## Scout return contract

Each scout returns:

- exact repositories and revisions inspected;
- contribution and test commands;
- a compact code and test map;
- ranked candidate branches with consequence and likely owner;
- at least one runnable reproduction or a precise feasibility limit;
- prior issues or fixes that constrain the work;
- negative results worth retaining;
- a promotion, park, split, or stop recommendation.

## Candidate ranking

Rank candidates using these factors:

1. consequence for correctness, security, data integrity, lifecycle, compatibility, performance, or maintainability;
2. reproducibility and testability;
3. patch size and ownership clarity;
4. likelihood of independent review and acceptance;
5. environment cost;
6. overlap with active upstream work;
7. reuse of the resulting fixture, method, or understanding.

A candidate with a modest consequence and excellent evidence can outrank a grand possibility that requires speculative redesign.