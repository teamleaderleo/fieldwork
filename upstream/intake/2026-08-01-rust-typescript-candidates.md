# Rust and TypeScript upstream candidate intake — 2026-08-01

## In simple words

This record keeps eleven current Rust and TypeScript tooling leads visible without turning them into numbered upstream contribution units before source work exists.

The strongest compact implementation lead remains Biome `.htm` recognition. The strongest new correctness lead is Rspack persistent-cache recovery accepting integrity-valid data under the wrong logical key. Bevy has one deterministic deferred-rendering crash and one GPU-allocation investigation. Dioxus has an unresolved Windows hot-patch linker environment gap. Zed has a reopened Windows SSH askpass-lifetime failure that needs a current deterministic reproducer.

No public upstream interaction is authorized. None of these leads has a Fieldwork source candidate at intake time.

## Retrieval boundary

- Retrieval date: 2026-08-01
- Fieldwork coordination issue: https://github.com/teamleaderleo/fieldwork/issues/457
- Priority-zero backlog: https://github.com/teamleaderleo/fieldwork/issues/435
- Public records were read as issue, comment, branch, and pull-request metadata only.
- Evidence class: source-not-yet-read; public-record triage only.
- Internal duplicate search: no open Fieldwork issue matching the exact added behaviors was found before this intake update.
- Duplicate rule: every lead must receive a fresh issue, pull-request, branch, and source sweep at claim time.

## Activation order

1. Biome `.htm` recognition.
2. Jujutsu redacted operation details.
3. Bevy deferred SSR plus contact-shadows pipeline parity.
4. Rspack persistent-cache logical-key recovery.
5. Dioxus Windows hot-patch linker environment.
6. uv interrupted self-update recovery.
7. Bevy mesh-allocation lifecycle investigation.
8. Oxc `unicorn/no-impossible-length-comparison`.
9. one remaining uv `EnvironmentOptions` variable.
10. Zed Windows SSH askpass lifetime reproduction.
11. ty auto-indent ecosystem and test design.

The order reflects boundedness, consequence, current competition, and likely reviewability rather than project popularity.

## Candidate A — Biome `.htm` recognition

- Repository: https://github.com/biomejs/biome
- Public issue: https://github.com/biomejs/biome/issues/11112
- Intake state: open, unassigned, good-first-issue.
- Maintainer signal: a maintainer invited a pull request and described the change as easy.
- Likely work class: Rust implementation plus target-native parser, formatter, or language-detection tests.
- First bounded question: where is file-extension language recognition owned, and which native tests prove `.htm` follows the same path as `.html`?
- Required claim-time checks:
  - pin current default-branch SHA;
  - search open and recently closed pull requests for `.htm`, HTML extension recognition, and language detection;
  - read contribution and AI-disclosure guidance;
  - identify all extension registries, generated tables, snapshots, and editor-facing detection paths;
  - produce one focused failing native test before changing behavior.
- Promotion threshold: a source-only branch with the extension change, target-native regression coverage, ordinary relevant gates, and complete-diff review.
- Initial recommendation: activate first.

## Candidate B — uv interrupted Windows self-update recovery

- Repository: https://github.com/astral-sh/uv
- Public issue: https://github.com/astral-sh/uv/issues/12142
- Intake state: open, unassigned, `help wanted`, Windows-specific.
- Maintainer signal: maintainers consider narrowing the failure window or moving the running executable to a temporary name; exact atomic replacement is constrained by Windows executable semantics.
- Likely work class: Rust updater and recovery behavior, possibly involving dependency-owned replacement code.
- First bounded question: which layer owns download completion, executable staging, rename, rollback, and cleanup, and at which interruption points can `uv.exe` become absent or unusable?
- Required claim-time checks:
  - pin uv and relevant updater dependency revisions;
  - map direct uv code versus dependency-owned replacement behavior;
  - identify existing Windows update tests and CI capabilities;
  - model or execute failure at download, validation, first rename, second rename, and cleanup boundaries;
  - compare at least two replacement sequences and state their rollback invariants.
- Promotion threshold: deterministic evidence for the identified failure boundary, a bounded repair owned by the correct repository, Windows-focused tests, and explicit residual interruption windows.
- Initial recommendation: deeper systems lead.

## Candidate C — Jujutsu redacted `jj op log -d`

- Repository: https://github.com/jj-vcs/jj
- Public issue: https://github.com/jj-vcs/jj/issues/9375
- Intake state: open, unassigned, good-first-issue, no comments at retrieval.
- Reported behavior: `builtin_op_log_redacted` redacts ordinary operation-log content, while the changed-commits section emitted with `-d` remains unredacted.
- Likely work class: Rust rendering or template plumbing plus command-output tests.
- First bounded question: is the changed-commits section already templated, or does redaction require a new rendering boundary?
- Required claim-time checks:
  - pin current default-branch SHA;
  - find the operation-log renderer, changed-commits renderer, redacted template, and output fixtures;
  - prove one leaking field under the redacted template;
  - determine whether the repair is local or requires a generalized template parameter;
  - stop after mapping if the issue expands into a broad templating redesign.
- Promotion threshold: one focused redaction invariant, native output tests, and no accidental loss of useful non-sensitive operation detail.
- Initial recommendation: activate second.

## Candidate D — Oxc `unicorn/no-impossible-length-comparison`

- Repository: https://github.com/oxc-project/oxc
- Public tracker: https://github.com/oxc-project/oxc/issues/684
- Upstream rule reference: https://github.com/sindresorhus/eslint-plugin-unicorn/blob/v72.0.0/docs/rules/no-impossible-length-comparison.md
- Intake state: listed as unimplemented in the generated tracker; no exact-title pull request was found during intake.
- Likely work class: Rust AST lint rule, diagnostics, fixtures, snapshots, and parity cases.
- First bounded question: can the Unicorn rule semantics be reproduced without type information and without overlapping an existing Oxc correctness rule?
- Required claim-time checks:
  - re-read the generated tracker immediately before claiming;
  - search branches and pull requests by exact rule name and diagnostic wording;
  - run `just new-unicorn-rule no-impossible-length-comparison` only after the claim;
  - derive a semantic matrix from upstream rule tests rather than copying implementation blindly;
  - add false-positive controls for unknown values, computed properties, optional chains, and non-literal bounds where applicable;
  - check overlap with existing Oxc comparison and length rules.
- Promotion threshold: target-native rule tests, snapshots, focused clippy and test gates, and an explicit compatibility statement against the referenced Unicorn version.
- Initial recommendation: activate after the more consequential deterministic defects unless a competing pull request appears.

## Candidate E — one uv `EnvironmentOptions` migration

- Repository: https://github.com/astral-sh/uv
- Public issue: https://github.com/astral-sh/uv/issues/14720
- Intake state: open, unassigned, `help wanted`.
- Maintainer signal: move one environment variable at a time using the established `EnvironmentOptions` abstraction.
- Unchecked variables at retrieval included:
  - `UV_COMPILE_BYTECODE_TIMEOUT`;
  - `UV_RUN_RECURSION_DEPTH`;
  - `UV_RUN_MAX_RECURSION_DEPTH`;
  - `UV_GITHUB_FAST_PATH_URL`;
  - `UV_GIT_LFS`;
  - `UV_CUDA_DRIVER_VERSION`;
  - `UV_AMD_GPU_ARCHITECTURE`;
  - `UV_STACK_SIZE`;
  - `TRACING_DURATIONS_FILE`;
  - `UV_LOCK_TIMEOUT`.
- First bounded question: which single unchecked variable has no active pull request and a clean parsing, precedence, and error-reporting contract?
- Required claim-time checks:
  - inspect every recent pull request linked from the issue and search each candidate variable;
  - choose exactly one variable;
  - read at least two merged migration precedents;
  - preserve CLI, config, and environment precedence;
  - add invalid-value, unset-value, and compatibility tests appropriate to that variable.
- Promotion threshold: one-variable diff, ordinary relevant gates, and no unrelated environment parsing cleanup.
- Initial recommendation: reserve entry task.

## Candidate F — ty auto-indent through LSP on-type formatting

- Repository: https://github.com/astral-sh/ty
- Public issue: https://github.com/astral-sh/ty/issues/2276
- Intake state: open, unassigned, `help wanted`.
- Maintainer signal: `textDocument/onTypeFormatting` is the likely protocol path; maintainers requested ecosystem analysis, practical heuristics, parser-recovery consideration, and an extensive test strategy before implementation.
- Likely work class: research-first LSP and editor behavior spanning Rust server code, Python token or parser recovery, and TypeScript extension configuration.
- First bounded question: what heuristics do Pylance and existing Python indentation extensions use, and which cases need parser recovery rather than line-level indentation rules?
- Required claim-time checks:
  - identify protocol registration and editor-client capability handling;
  - inspect the referenced Python indentation extension and publicly visible Pylance behavior without copying proprietary implementation;
  - build a case corpus covering block headers, parenthesized conditions, continuations, comments, strings, incomplete syntax, decorators, match/case, and dedent triggers;
  - state whether the first deliverable is an ecosystem report, parser support change, server implementation, or extension configuration change;
  - keep client-setting changes separate unless the protocol implementation requires them.
- Promotion threshold: a reviewed heuristic and test design, followed by an `ISSUE FIRST` or bounded implementation recommendation.
- Initial recommendation: research-first; activate last among these leads.

## Candidate G — Dioxus Windows hot-patch linker environment

- Repository: https://github.com/DioxusLabs/dioxus
- Public issue: https://github.com/DioxusLabs/dioxus/issues/4911
- Intake state: open, unassigned, `bug`, `help wanted`, `windows`, `subsecond`.
- Reported behavior: `dx serve --hot-patch` fails outside a Visual Studio Native Tools prompt because `rust-lld` cannot locate standard Windows import libraries, while ordinary Rust builds and the same Dioxus project work in the configured VS prompt.
- Maintainer signal: a maintainer wants the issue fixed but is unsure how the CLI should discover and set the required toolchain and SDK environment in a normal prompt.
- First bounded question: which code path launches fat-binary linking, which MSVC or Windows SDK variables are absent outside VS prompts, and can `dx` derive them without inheriting shell-specific state?
- Required claim-time checks:
  - pin current Dioxus and `dx` revisions;
  - reproduce in cmd, PowerShell, Nushell, and a VS Native Tools prompt;
  - compare ordinary `cargo build` and hot-patch linker invocations;
  - capture relevant `PATH`, `LIB`, `VCToolsInstallDir`, Windows SDK, target, and linker arguments without retaining user paths;
  - inspect existing `vswhere`, compiler-discovery, and linker-environment helpers before adding new discovery code;
  - distinguish a missing Build Tools installation from a present-but-undiscovered installation;
  - include x64 and ARM64 considerations explicitly.
- Promotion threshold: a source-owned discovery or invocation repair, shell-independent tests where feasible, clear missing-tool diagnostics, and no hardcoded SDK paths.
- Initial recommendation: activate after the deterministic Bevy and Rspack lanes.

## Candidate H — Rspack persistent-cache logical-key recovery

- Repository: https://github.com/web-infra-dev/rspack
- Anchor issue: https://github.com/web-infra-dev/rspack/issues/14862
- Related family: issues 14860 through 14865 cover distinct partial-corruption and recovery failures.
- Intake state: the anchor is open, unassigned, reproducible, and had no matching repair pull request during this sweep.
- Reported behavior: swapping two equal-length persistent-cache keys and recomputing integrity can make a recovered build emit valid JavaScript under the wrong asset names; the build exits successfully while `a.js` contains B and `b.js` contains A.
- Current competition: sibling 14864 has pull request 14944 and sibling 14865 has pull request 15034. The remaining family must be rechecked independently at claim time.
- First bounded question: does each recovered persistent-cache entry bind validated bytes to the caller's exact logical key and occasion identity, or can integrity-valid but mis-keyed data be accepted?
- Required claim-time checks:
  - pin current Rspack main and the cache format version;
  - run the anchor reproduction in a fresh process and compare with a cold build;
  - map occasion key composition, serialization, integrity validation, lookup, recovery, and recomputation;
  - distinguish filesystem corruption from a product recovery-policy defect;
  - compare reject-and-recompute with adding explicit logical identity to each record;
  - test only one unoccupied sibling at a time and keep sibling ownership separate;
  - prove ordinary valid cache hits remain reusable.
- Promotion threshold: one bounded cache-identity invariant, deterministic corruption fixtures, correct recomputation, no silent cross-wiring, and focused plus ordinary cache gates.
- Initial recommendation: highest-consequence new lead.

## Candidate I — Bevy mesh-allocation lifecycle investigation

- Repository: https://github.com/bevyengine/bevy
- Public issue: https://github.com/bevyengine/bevy/issues/24892
- Intake state: open, unassigned, high priority, ready for implementation, modest difficulty, rendering/assets/performance.
- Reported behavior: repeated in-place replacement of mesh data can cause unbounded process or GPU-memory growth in the reporter's Windows AMD Vulkan case.
- Contradictory evidence: simpler controls remained stable on macOS Metal and Windows NVIDIA. Later discussion indicates mesh size and replacement method may be decisive, and one retained test direction reaches a slab-allocator debug assertion.
- First bounded question: is the growth owned by Bevy allocator lifecycle, backend or driver retention, or a distinct `insert` versus mutable-replacement invariant breach?
- Required claim-time checks:
  - pin current Bevy main and relevant wgpu revision;
  - build a deterministic large-mesh churn fixture with fixed topology and update cadence;
  - track Bevy slab diagnostics, process memory, and VRAM separately;
  - compare `get_mut` replacement, `Assets::insert`, removal and reinsertion, and stable-size versus changing-size meshes;
  - run Windows AMD and NVIDIA controls when available, with a Metal control if useful;
  - preserve the debug-assert case and compare against prior related fixes before selecting an implementation.
- Promotion threshold: reproduced ownership at a named layer, a failing target-native test or platform receipt, bounded steady-state memory after repair, and no claim broader than tested backends.
- Initial recommendation: research-first high-value lane.

## Candidate J — Bevy deferred contact-shadows pipeline parity

- Repository: https://github.com/bevyengine/bevy
- Public issue: https://github.com/bevyengine/bevy/issues/25090
- Intake state: open, unassigned, zero comments at retrieval, rendering bug needing triage.
- Reported behavior: combining screen-space reflections and contact shadows causes the application to quit after a wgpu bind-group-layout validation failure.
- Reported cause: the shared mesh-view bind group includes the contact-shadows uniform while the deferred lighting pipeline omits the matching `CONTACT_SHADOWS` key and shader definition.
- First bounded question: does the deferred pipeline key, layout, and shader-definition set remain identical to the shared view bind group for every feature-gated binding?
- Required claim-time checks:
  - pin current Bevy main and verify the issue remains after the earlier forward-path repair;
  - reproduce the validation failure with the minimal camera and scene;
  - add no-SSR, no-contact-shadows, forward-rendering, and deferred controls;
  - inspect deferred query inputs, pipeline-key construction, layout specialization, and shader definitions together;
  - search current pull requests and adjacent deferred-parity fixes before implementation;
  - prefer a deterministic specialization or validation regression test over screenshot-only evidence.
- Promotion threshold: the combined feature set runs without validation failure, contact shadows are actually enabled in deferred lighting, forward behavior stays unchanged, and relevant rendering gates pass.
- Initial recommendation: strongest deterministic new Rust implementation lead.

## Candidate K — Zed Windows SSH askpass lifetime reproduction

- Repository: https://github.com/zed-industries/zed
- Public issue: https://github.com/zed-industries/zed/issues/40276
- Intake state: open and reopened, unassigned, Windows remote-development failure, currently needs reproduction.
- Reported behavior: SSH or Git operations try to execute a generated `askpass.ps1` from a temporary directory that no longer exists; the path changes on retries while direct shell SSH works.
- Prior work: an earlier partial fix was linked in the discussion, but the issue was reopened after reports persisted.
- First bounded question: which owner deletes the askpass temporary directory relative to SSH or Git child startup, retry, and process exit?
- Required claim-time checks:
  - pin current stable and nightly revisions;
  - reproduce local Git fetch and remote SSH separately;
  - compare Windows OpenSSH agent, 1Password or Windows Hello agent integration, and a no-agent control;
  - log redacted creation, deletion, child-spawn, retry, and child-exit timestamps;
  - test concurrent operations and repeated authentication attempts;
  - stop or reroute if the failure is entirely external-agent behavior rather than Zed-owned lifetime.
- Promotion threshold: a current deterministic reproducer, source ownership at the temp-directory or child-process boundary, lifetime tied to the actual child operation, and Windows-focused regression coverage.
- Initial recommendation: reproduce before proposing source work.

## Occupied, superseded, or weakly owned work excluded from activation

The following looked promising from issue listings but should not be duplicated now:

- Tauri asynchronous commands re-invoked after WebView reload: four competing repair pull requests.
- Bun `findPackageJSON` and `threadCpuUsage` compatibility gaps: multiple active pull requests.
- Bun async-generator inspection: a contributor claimed the issue and opened a pull request.
- pnpm noninteractive modules-purge prompt: multiple active pull requests.
- Nushell IPv6 zone identifiers: a contributor announced a draft repair.
- Wasmtime WASI `initial-cwd`: active current repair plus older prior work.
- rust-analyzer macro-by-example performance benchmark: current optimization pull request.
- Dioxus PNG re-encoding and production body panic: active or duplicate pull requests.
- Deno stdin cancellation, vendored `--no-remote`, test teardown masking, and cross-target install: active fixes or explicit maintainer ownership.
- Bevy boundary-sized font atlas panic: active pull request 25225.
- Rspack family issues 14864 and 14865: active pull requests 14944 and 15034.
- Typst watcher freeze: recent discussion indicates the original failure may already be fixed.
- eza Windows long path report: current evidence points to PowerShell 5.1 quoting behavior rather than eza ownership.
- Vitest Vue-style breakpoint mapping: current evidence points toward editor-plugin source maps rather than a bounded Vitest-owned repair.

These exclusions are point-in-time results. A later claim may reopen one only after proving the competing work was abandoned, rejected, merged incompletely, or owned by a different boundary.

## Claim record

A claim on issue 457 must name:

- candidate letter and public record;
- worker identity;
- exact target SHA and retrieval date;
- owned Fieldwork path and branch;
- intended target-source branch or explicit no-fork state;
- claim scope;
- first discriminating source question or test;
- stop condition;
- upstream-contact authorization, which remains `false`.

One worker claims one candidate. Intake does not authorize public upstream issues, comments, reactions, pull requests, or reviews.

## Disposition

Current disposition: `QUEUED LEADS`.

No candidate receives a numbered `upstream/INDEX.md` unit until a source candidate or sufficiently complete issue-first packet exists. The next coordinator action is to accept one bounded claim on issue 457 after a current duplicate sweep.