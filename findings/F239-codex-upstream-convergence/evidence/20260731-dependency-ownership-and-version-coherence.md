# Codex dependency ownership and version coherence

Date: 2026-07-31

Public source inspected: `openai/codex@775fb21d2af9b9936618fe22dd62e6f0cb3ba4a3`

## Governing conclusion

Dependency presence, declared compatibility, resolved lock state, generated artifacts, and shipped runtime identity are different facts with different owners.

A package-level test can establish behavior against its resolved local graph. It cannot independently establish that release packaging, generated protocol exports, or the runtime binary shipped beside the SDK has the same identity.

## Rust workspace

The Rust workspace contains more than one hundred internal path crates covering app-server, execution, MCP, extensions, persistence, sandboxing, model providers, TUI, and utilities. Internal path dependencies express source ownership inside the monorepo; `Cargo.lock`, Bazel lock material, and release builds own the resolved external graph.

### Exact or deliberately constrained dependencies

- `rmcp = "=3.0.0"` — protocol/runtime compatibility boundary;
- `v8 = "=150.4.0"` — native runtime and host-tool boundary;
- `tar = "=0.4.45"` — exact archive implementation pin;
- `libsqlite3-sys = "0.37"` with an explicit WAL-reset corruption-fix comment;
- `sqlx = "0.9.0"` with bundled SQLite;
- `nucleo` and `runfiles` use exact Git revisions;
- `crossterm`, `tokio-tungstenite`, and `tungstenite` are replaced by exact OpenAI-fork revisions through workspace patches.

These pins need different review controls:

- registry exact pins: release notes, lock delta, behavior tests, and package compatibility;
- Git revisions: immutable commit review, source diff, provenance, and lock/Bazel synchronization;
- native runtimes: host-tool, target-platform, packaging, and sandbox tests;
- bundled SQLite: migration, WAL, durability, corruption-recovery, and platform-file-system tests.

### Native and platform-sensitive boundaries

`openssl-sys`, keyring, Landlock, seccompiler, portable PTY, Wayland clipboard support, bundled SQLite, and V8 depend on platform libraries or target-specific behavior. Cargo compilation on one hosted Linux image cannot establish macOS, Windows, musl, credential-store, or sandbox behavior.

The workspace cargo-shear configuration explicitly ignores `icu_provider`, `openssl-sys`, and `codex-v8-poc`, confirming that mechanical unused-dependency tooling has declared blind spots which require owner review.

## Node workspace

The root Node package is private maintenance tooling, while the pnpm workspace includes:

- `codex-cli`;
- `codex-rs/responses-api-proxy/npm`;
- `sdk/typescript`.

The root requires Node 22 and pnpm 10.33.0 with an integrity-qualified package-manager string. The workspace also enables supply-chain controls:

- seven-day minimum release age;
- exotic subdependencies blocked;
- strict dependency builds;
- no-downgrade trust policy;
- no packages granted install-time build permission.

Root `resolutions` own the effective versions of selected transitive dependencies. For example, the TypeScript SDK declares `@modelcontextprotocol/sdk ^1.24.0`, while the root resolves it to `1.26.0`. The package manifest expresses an accepted range; the root lock and resolution express the graph actually tested in the monorepo.

A release check should therefore record both:

1. package-local declared range;
2. root-resolved version and lock integrity.

## Python SDK and runtime package

The Python SDK declares:

- package version `0.0.0-dev` in source;
- Python `>=3.10`;
- `pydantic>=2.12`;
- exact runtime dependency `openai-codex-cli-bin==0.144.4`;
- `uv_build>=0.11.19,<0.12`;
- seven-day dependency age filtering, with a dated exception for the runtime package.

The runtime setup code derives the exact CLI runtime version from the SDK dependency, selects a platform-specific `codex-package-*` archive, downloads the matching GitHub release asset, installs it, and verifies the installed runtime package version.

This creates a cross-package contract:

```text
Python SDK dependency pin
→ normalized Codex release tag
→ platform release archive
→ bundled CLI package
→ installed runtime version verification
```

A Python API test cannot prove this chain. Required release controls include:

- SDK dependency pin equals intended release version;
- release tag exists;
- every supported platform asset exists under the expected name;
- archive contents carry the same CLI identity;
- installed runtime reports the requested normalized version;
- source-generated client types match the app-server protocol implemented by that runtime.

## Generated protocol and schema boundary

App-server protocol fixtures and SDK-generated types are derived artifacts. Their successful generation proves generator execution, not runtime compatibility by itself.

The complete release fact requires agreement among:

- Rust protocol source;
- generated JSON schema and fixtures;
- TypeScript/Python generated clients;
- checked-in generated outputs;
- runtime app-server request/response behavior;
- package versions and release assets.

Generator changes, source protocol changes, and generated-output refreshes should be reviewed as separate facts even when one commit carries all three.

## Proposed dependency-owner matrix

| Dependency class | Primary owner | Minimum proof before current acceptance |
| --- | --- | --- |
| internal path crate | source crate and workspace graph | complete diff, affected-crate tests, reverse-consumer compile |
| registry semver range | package manifest | compatibility tests across resolved version; lock review |
| exact registry pin | workspace manifest and lock | release/source delta, focused behavior tests, lock/Bazel sync |
| Git revision or patch fork | exact commit plus workspace patch | immutable source diff, provenance, lock/Bazel sync, regression tests |
| native/system dependency | platform adapter and packaging | target-platform build/run, sandbox/credential/file-system controls |
| generated schema/client | source protocol plus generator | clean regeneration, checked-in diff, runtime round trip |
| SDK runtime package | SDK manifest plus release workflow | exact version, asset existence, archive identity, installed-version check |
| root pnpm resolution | root workspace and lock | package-local range compatibility plus root-resolved graph tests |

## Candidate controls

1. Emit a machine-readable dependency-owner report from Cargo metadata, pnpm lock, Python metadata, and generator manifests.
2. Fail when an exact Git revision or patched fork changes without an owner note and focused test declaration.
3. Compare package-local dependency intent with root-resolved versions and flag untested range edges.
4. Verify Python and TypeScript SDK release versions against the exact Codex runtime tag and protocol generation revision.
5. Build a generated-artifact receipt containing source SHA, generator command/version, output file hashes, and runtime round-trip tests.
6. Keep native-runtime certification per target; do not infer Windows/macOS behavior from Linux compilation.

## Current disposition

This is a source and packaging map, not a defect claim. The strongest next bounded packet is SDK/runtime/version coherence because the Python SDK already encodes an exact runtime dependency and performs runtime installation/verification. A separate packet may later cover exact Git/fork dependency review and Bazel/Cargo lock synchronization.

No merge or public upstream interaction is included.
