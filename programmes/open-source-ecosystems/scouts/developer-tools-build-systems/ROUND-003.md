# Developer tools and runtimes — Hotness Round 003

Snapshot: 2026-08-01  
Programme: [`open-source-ecosystems`](../../README.md) / issue [`#207`](https://github.com/teamleaderleo/fieldwork/issues/207)  
Scout lane: [`#210`](https://github.com/teamleaderleo/fieldwork/issues/210)  
Prior report: [`ROUND-002.md`](ROUND-002.md)  
Public upstream contact: **none; unauthorized**

## Verdict in simple words

**uv is not the hottest ecosystem by raw bug severity. It is the hottest unclaimed, current-CI, plausibly bounded contribution lane found in this pass.**

Several Node and Bun reports are more severe on impact alone: silent test-verdict loss, process aborts, truncated responses reported as complete, disabled payload limits, and suppressed database errors. Every one checked in this pass was already assigned, had an active equivalent pull request, was a duplicate with a fix, or was already repaired on current main.

The live work therefore splits into three different winners:

1. **Best bounded patch: uv #20875** — configured prerelease policy is discarded before isolated build-requirement resolution. Current source contains a direct code-level explanation and no equivalent pull request was found.
2. **Highest-upside experiment: uv #20871** — `uvx` may run a tool with an incompatible dependency from the surrounding project, reportedly even with `--isolated`; consequence is higher, but the mechanism still needs a local distinguishing fixture.
3. **Closest non-uv challenger: Deno #36334** — a failed global npm install leaves published partial state, and a retry can silently skip the failed lifecycle script and complete. It is unassigned with no matching pull request found, but its transactional boundary and fixture are broader than uv #20875.

So the answer is: **yes, stay on uv first—but promote #20875 ahead of #20871 for implementation. Keep Deno #36334 as the parallel challenger.**

## What “hot” means in this round

Candidates were ranked by:

- user consequence, especially silent success, data loss, security-boundary bypass, false-green tests, or poisoned persistent state;
- current reproducibility on an exact revision;
- absence of an assignee, contributor claim, matching pull request, or current-main repair;
- clarity of the owning code and native regression-test boundary;
- ability to use a local, deterministic fixture without private infrastructure;
- likely review size and whether behavior is already specified rather than requiring a product decision.

A high-impact issue that somebody already owns is a **stop**, not a better contribution target.

## Exact source revisions inspected

| Target | Revision | Purpose |
| --- | --- | --- |
| Fieldwork | [`041d29ab9c5e5859cb69518a432354be71b67af8`](https://github.com/teamleaderleo/fieldwork/commit/041d29ab9c5e5859cb69518a432354be71b67af8) | branch base for this report |
| uv | [`79bbface771210df216b738e9bdc7df95e5a9e6b`](https://github.com/astral-sh/uv/commit/79bbface771210df216b738e9bdc7df95e5a9e6b) | build frontend, tool runner, build dispatch, tool tests |
| Deno | [`fbe07f1a79d4bd8142ada44b562c8dd14e005149`](https://github.com/denoland/deno/commit/fbe07f1a79d4bd8142ada44b562c8dd14e005149) | global installer integration boundary and tests |
| Node.js | [`b9dacd417fa4feae384892d8462d6740ec0e2c88`](https://github.com/nodejs/node/commit/b9dacd417fa4feae384892d8462d6740ec0e2c88) | ownership and current-main reconciliation for severe candidates |
| Bun | [`a7838c5c84ae2e833c44310fb3dfce60292da40c`](https://github.com/oven-sh/bun/commit/a7838c5c84ae2e833c44310fb3dfce60292da40c) | current-head tests and duplicate/fix reconciliation |

A dated scan reserves nothing. Refresh issues, comments, assignments, contributor intent, branches, pull requests, and current-head tests immediately before creating an implementation branch.

## Ranked live queue

| Rank | Target | Candidate | Why it is hot | Remaining uncertainty | Disposition |
| ---: | --- | --- | --- | --- | --- |
| 1 | uv | [`#20875`](https://github.com/astral-sh/uv/issues/20875) — prerelease policy does not reach build requirements | cross-platform regression; explicit opt-in is silently ignored; current source discards the setting; bounded resolver-plumbing and test surface | whether maintainers want the existing global prerelease policy forwarded or a build-specific policy | **promote characterization, then patch or issue-first depending on contract** |
| 2 | Deno | [`#36334`](https://github.com/denoland/deno/issues/36334) — failed global install leaves half-installed state | failed lifecycle script publishes persistent partial state; retry can skip the failed script and report success; unassigned and no matching PR found | needs a local-registry or test-server fixture and careful rollback/commit boundary | **promote transactional experiment in parallel** |
| 3 | uv | [`#20871`](https://github.com/astral-sh/uv/issues/20871) — `uvx` can use incompatible project dependencies | possible tool-isolation failure and exact-requirement violation; `--isolated` reportedly insufficient | must distinguish import-path leakage, project shadowing, cached-env reuse, and entry-point/interpreter selection | **promote experiment; no behavior patch yet** |
| 4 | Meson | [`#16046`](https://github.com/mesonbuild/meson/issues/16046) — source introspection emits dependency `unknown` | invalid distro build requirements generated from ordinary option-derived dependencies | output contract for dynamic dependency names needs design care | **retain as next non-runtime current-CI probe** |
| 5 | Cargo | [`#16574`](https://github.com/rust-lang/cargo/issues/16574) — local patch still contacts original Git source | private/offline development blocked despite local replacement | broad behavior is intentionally source-aware and labeled needs-design; narrow exact-version regression must be separated | **issue-first experiment** |

## Winner 1 — uv #20875: prerelease build requirements cannot opt in

### Observed contract failure

uv 0.12 changed ordinary prerelease selection behavior. The reporter can opt ordinary resolution into prereleases with the supported command, environment, or configuration mechanisms, but isolated resolution of `build-system.requires` ignores those mechanisms and selects an older stable backend without a warning.

This is more than a request for a new feature: an accepted resolver policy is present in command settings and silently disappears at the build boundary.

### Current source explanation

`crates/uv/src/commands/build_frontend.rs` destructures `ResolverSettings` and explicitly ignores the field:

```rust
let ResolverSettings {
    index_locations,
    index_strategy,
    keyring_provider,
    resolution: _,
    prerelease: _,
    fork_strategy: _,
    // ...
} = settings;
```

The same build path constructs a `BuildDispatch` without a prerelease argument.

`crates/uv-dispatch/src/lib.rs` likewise has no prerelease field in `BuildDispatch`. Its `resolve()` method builds resolver options with `exclude_newer`, `index_strategy`, `build_options`, and fixed flexibility, but no prerelease policy.

That is the strongest code signal in this research pass: the issue maps directly to discarded configuration and absent resolver state rather than a vague emergent interaction.

### Smallest credible characterization

Use uv’s local package-index test machinery. Publish only local fixtures:

- `fieldwork-build-backend==1.0.0` — stable backend, writes `selected=stable` into generated metadata or wheel content;
- `fieldwork-build-backend==2.0.0rc1` — prerelease backend, writes `selected=prerelease`;
- a source project with:

```toml
[build-system]
requires = ["fieldwork-build-backend>=1"]
build-backend = "fieldwork_build_backend"
```

Run a matrix against exact current head:

1. no prerelease opt-in — stable backend is selected;
2. command-line prerelease opt-in — prerelease backend should be eligible;
3. environment-variable prerelease opt-in — same expected eligibility;
4. configuration-file prerelease opt-in — same expected eligibility;
5. an ordinary runtime dependency control proving the option still works outside build isolation;
6. a requirement that explicitly names the prerelease, proving direct prerelease requirements continue to work independently of the policy.

The test must assert the backend version actually executed, not merely resolution output.

### Likely implementation surfaces

- `crates/uv/src/commands/build_frontend.rs`
- `crates/uv-dispatch/src/lib.rs`
- resolver option construction used by isolated build requirements
- focused `uv build` / source-build integration tests using the local test index

### Contract fork to surface before final patch

Two credible policies exist:

1. forward the existing global prerelease policy into build-requirement resolution; or
2. add a distinct build-requirement prerelease policy because build backends are a separate trust and compatibility surface.

The current state—accepting a policy and silently dropping it—is the bad outcome either way. A characterization branch is justified now. A behavior patch should either follow existing maintainer intent or be preceded by an issue comment after authorization.

### Promotion gate

Promote from characterization to implementation when:

- the local two-version backend fixture fails on exact current head;
- overlap is refreshed and still empty;
- the test confirms the option reaches ordinary resolution but not `BuildDispatch`;
- the chosen policy is supported by existing docs or maintainer direction.

## Winner 2 — Deno #36334: failed global install publishes partial state

### Observed transaction failure

A global npm install with allowed lifecycle scripts creates the hidden per-command directory before all install work succeeds. If the lifecycle script fails:

- the install command correctly exits with an error;
- the executable shim is absent;
- the hidden `~/.deno/bin/.<name>` directory remains;
- uninstall cannot cleanly treat the command as installed;
- repeating the install can skip the lifecycle script and complete successfully.

That final transition is the hot part: a previously failed required script is converted into a later false success by persistent partial state.

### Ownership state

At the snapshot:

- issue open;
- unassigned;
- zero comments;
- no matching implementation pull request found.

### Native test boundary

Current Deno integration coverage for global installs lives in `tests/integration/install_tests.rs`. Existing tests already isolate `HOME`, `USERPROFILE`, and `DENO_INSTALL_ROOT`, and inspect both the generated shim and hidden per-command configuration directory. That is a suitable outer boundary for rollback assertions.

The test should avoid a public registry. Prefer the repository’s local npm registry/test server if it supports lifecycle-script fixtures; otherwise add a static local package fixture and registry metadata to the existing test harness.

### Distinguishing transactional test

1. Create a local npm package with a deterministic failing install script and one executable.
2. Run `deno install --global --allow-scripts` against the local registry.
3. Assert non-zero exit.
4. Assert both the public shim and hidden per-command directory are absent.
5. Run the same command again.
6. Assert the lifecycle script runs and fails again rather than being skipped.
7. Change only the fixture so the script succeeds.
8. Install again and assert the shim and complete hidden state appear atomically.
9. Uninstall and assert both are removed.

### Likely repair shapes

- stage the hidden command directory under a temporary sibling and rename it into place only after lifecycle scripts and package preparation succeed;
- or install in place with an explicit rollback guard that removes every published artifact on any downstream error;
- ensure retry detection validates completion rather than treating directory existence as success.

The first shape is easier to reason about because publication becomes one commit point. The actual code owner still needs mapping before implementation.

### Why it ranks below uv #20875

The consequence is arguably higher, but the fixture requires more infrastructure, the state machine is broader, and cleanup behavior is cross-platform. It is excellent parallel research, not the first patch to start while uv #20875 has a direct source-level gap.

## Winner 3 — uv #20871: tool isolation versus current project

### Why it remains hot

A command presented as an ephemeral tool runner can reportedly execute with a dependency version from the surrounding project even though the tool declares an exact incompatible version. The report also says `--isolated` changes paths but does not restore the declared dependency behavior.

### Why it is not yet the first patch

Current `tool/run.rs` creates or reuses a separate tool environment and launches the tool with that environment’s scripts directory first in `PATH`. It does not contain an intentional current-project layering path; a TODO discusses project-level tool support as future work.

The observed result could therefore arise from several different boundaries:

- `PYTHONPATH`, `PYTHONHOME`, or site customization inherited by the child;
- the current project package shadowing the registry package during requirement-name resolution;
- installed-tool or cached-environment reuse with an identity key missing relevant context;
- a console-script shebang or interpreter mismatch;
- import precedence introduced by editable metadata or the current working directory.

A patch before distinguishing these would be guesswork.

### Refined fully local experiment

Create a local index with:

- `fieldwork-dep==1.0.0`, exposing `ORIGIN = "tool"`;
- `fieldwork-dep==2.0.0`, exposing `ORIGIN = "project"`;
- `fieldwork-tool==1.0.0`, requiring `fieldwork-dep==1.0.0`, with an entry point printing:
  - dependency version and `ORIGIN`;
  - dependency `__file__`;
  - `sys.executable`, `sys.prefix`, and `sys.base_prefix`;
  - complete `sys.path`;
  - relevant environment variables.

Create a parent project requiring `fieldwork-dep==2.0.0`, sync its `.venv`, do not activate it, then run inside and outside the project with:

- default `uvx`;
- `uvx --isolated`;
- a sanitized process environment;
- explicit hostile `PYTHONPATH` as a negative control;
- a parent project whose own name matches the tool package, to test project shadowing separately from dependency leakage.

Promote only after the failing arm identifies the ingress path.

## Higher-severity findings stopped by ownership or reconciliation

| Target | Finding | Why it looked hotter | Stop reason |
| --- | --- | --- | --- |
| Node | [`#64833`](https://github.com/nodejs/node/issues/64833) — concurrent `--test-force-exit` loses verdicts and exits 0 | false-green test runs silently omit executed tests | active contributor work and PR #64875 |
| Node | [`#64850`](https://github.com/nodejs/node/issues/64850) — HTTP/2 session teardown reaches internal assertion | ordinary API use can abort the process; deterministic main regression | assigned to core maintainer/reporter `mcollina` |
| Node | [`#64822`](https://github.com/nodejs/node/issues/64822) — SQLite callback error suppresses next database error | later invalid SQL silently returns `undefined` | assigned to reporter and PR #64823 |
| conda | [`#16473`](https://github.com/conda/conda/issues/16473) — failed install removes environment registration | existing environment disappears from normal discovery after failed operation | assigned and PR #16474 |
| pnpm | [`#13503`](https://github.com/pnpm/pnpm/issues/13503) — `dedupe --check` mutates `node_modules` | a check-only command removes installed packages | public contributor intent; coordinate rather than compete |
| pnpm | [`#13525`](https://github.com/pnpm/pnpm/issues/13525) — sandbox creates project-local store | AI-agent sandboxing silently dirties repositories | accepted, fully specified, but PR #13536 already exists |
| Bun | [`#36477`](https://github.com/oven-sh/bun/issues/36477) — failed streamed body sent as complete | silent truncated-transfer data corruption | exact regression test already present on current main; reconcile/close rather than implement |
| Bun | [`#36494`](https://github.com/oven-sh/bun/issues/36494) — filtered `cpSync` skips overwrite | silent filesystem divergence from Node | reporter repro passes on current main according to project bot |
| Bun | [`#36419`](https://github.com/oven-sh/bun/issues/36419) — piped `console.log` truncates at 64 KiB | silent output corruption with exit 0 | active PR #33560 |
| Bun | [`#36160`](https://github.com/oven-sh/bun/issues/36160) — deleting `TZ` freezes later timezone resolution | later tests can become false-green | active PR #35003 |
| Bun | [`#36116`](https://github.com/oven-sh/bun/issues/36116) — `ws` ignores `maxPayload` | denial-of-service guard silently disabled | duplicate #33284; active fix PR #33287 |
| Bun | [`#36227`](https://github.com/oven-sh/bun/issues/36227) — NFS cache replacement race | concurrent installers fail on shared cache | active PR #36229 |
| Bun | [`#36572`](https://github.com/oven-sh/bun/issues/36572) — SQLite close fails past query-cache threshold | file handles remain open and strict close throws | reporter has explicitly volunteered and requested design direction; coordinate only |

These are retained as test and design references. Do not create competing branches while the listed ownership remains active.

## Negative-result lessons

### Open issue does not mean live bug

Bun #36477 and #36494 were attractive enough to outrank uv on the first pass. Current-head inspection removed both: one already has the exact regression contract in the test suite, and the other reporter script passes on main. Issue state alone would have produced duplicate work.

### Zero assignees does not mean unowned

pnpm #13503 has public contributor intent. Bun #36572’s reporter explicitly offered a patch and asked for maintainers’ preferred design. Both are ownership signals under Fieldwork rules even without a formal assignee.

### Highest severity is not always highest-value next action

Node’s regressions are more severe, but core maintainers or active contributors already own them. The useful action is to preserve their reproducers and avoid adding review contention.

## Execution order

1. **uv #20875 characterization branch**
   - refresh main, issue, comments, linked work, and PR search;
   - add the local stable/prerelease build-backend matrix;
   - confirm exact current-head failure;
   - map the smallest policy-plumbing patch;
   - obtain maintainer direction before public behavior change if existing docs do not decide the contract.
2. **Deno #36334 transactional characterization**
   - reduce the registry fixture into Deno’s existing integration harness;
   - prove failed install leaves state and retry skips the script on current head;
   - identify the publication commit point and rollback owner.
3. **uv #20871 local isolation matrix**
   - distinguish project shadowing from import/environment leakage;
   - do not patch until one ingress path is proven.
4. Retain Meson #16046 and Cargo #16574 as next probes if all three leaders become owned or fail reproduction.

## Current decision

`INVESTIGATE`, with **uv #20875 promoted to first implementation-quality characterization**. Deno #36334 is the parallel non-uv lane. uv #20871 remains the highest-upside experiment, but not yet a responsible patch target.

No target-repository branch, issue comment, pull request, release, or deployment was created in this round.