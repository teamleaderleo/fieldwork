# uv first-contribution review — 2026-08-02

## In simple words

Fieldwork already contains enough uv work to learn the repository through real source, tests, and review rather than opening another broad issue hunt. The best prospective first upstream contribution remains the Alpine/BusyBox relocatable-launcher repair. A smaller lockfile diagnostic is now source-clean and useful as an internal learning exercise, but its public lane is crowded with prior and current attempts. The remaining `EnvironmentOptions` checklist is not a shortcut: apparently unoccupied variables cross real identity, initialization, or lower-level policy boundaries. No public upstream interaction occurred.

## Finding state

`comparative-evaluation-active`

Unit 02 is the selected provisional first-contribution direction. Its exact platform/source run remains queued. The lock diagnostic has an accepted fork-local source generation but remains routing-held and awaits a clean exact-head run.

## Assignment and authority

- Coordination: `teamleaderleo/fieldwork#210`.
- Canonical finding: this file.
- Supporting screen: `environment-options-screen.md` beside this file.
- Owned target repository: `teamleaderleo/uv`.
- Public target observed quietly: `astral-sh/uv`.
- Public upstream contact authorized: `false`.
- Public upstream contact performed: `false`.
- Retrieval date: 2026-08-02.

## Fieldwork method applied

This pass followed the current repository runbooks:

1. inventory existing owned uv work before opening another lane;
2. pin exact source and carrier identities;
3. read producer, consumer, and test owners directly;
4. search public issues, pull requests, branches, and prior attempts;
5. repair concrete defects in owned-fork work;
6. keep source candidates separate from execution carriers;
7. review complete exact diffs;
8. preserve negative results and losing reasons;
9. make no public contact.

## Existing uv work map

| Lane | Owned surface | Current use |
| --- | --- | --- |
| BusyBox relocatable launchers | `teamleaderleo/uv#7`; publication target `upstream/02-busybox-realpath` | Leading first-contribution candidate; exact final run pending. |
| `uv.lock` passed to `-r` | source `teamleaderleo/uv#12`; clean successor carrier `#15` | Source accepted internally; public routing held; exact clean run pending. |
| Alternative parse-failure diagnostic | carrier `teamleaderleo/uv#13` | Separate experiment; retained and not treated as execution authority for source #12. |
| local-directory source provenance | `teamleaderleo/uv#11` | Medium-depth resolver/serialization research; active overlap. |
| interrupted self-update recovery | `teamleaderleo/uv#8`, `#9`, `#10`; Fieldwork `#491` | High-consequence transaction work; too broad for a first patch. |
| extracted wheel cache corruption | `teamleaderleo/uv#1` | Confirmed integrity gap requiring independent durable authority. |
| PEP 723 symlink lock authority | `teamleaderleo/uv#4` | Policy/authority characterization, not a settled starter implementation. |

# Candidate A — BusyBox relocatable launchers

## Public problem and overlap

Public issue `astral-sh/uv#16209` records that Alpine/BusyBox `realpath` interprets `--` as a missing path, emits a diagnostic, and returns nonzero in relocatable launchers. The issue is open and unassigned. A fresh exact-topic search found no matching public repair pull request.

The public discussion correctly warns that blindly deleting every delimiter is weak: leading-hyphen operands still matter, and generation-host BusyBox detection was floated as an alternative.

## Current candidate

Owned carrier `teamleaderleo/uv#7` at `c8a5c36d60a5cc35f496f583146967e210f87810` generates an exact four-file candidate from public/fork base `79bbface771210df216b738e9bdc7df95e5a9e6b`:

- `crates/uv-install-wheel/src/wheel.rs`
- `crates/uv-virtualenv/src/virtualenv.rs`
- `crates/uv/src/commands/project/run.rs`
- `crates/uv/tests/python/venv.rs`

The candidate:

- removes only unsupported `realpath --` delimiters;
- preserves every `dirname --` delimiter;
- recognizes current and historical relocatable shebangs for both `python` and `python3`;
- updates existing relocatable virtualenv expectations;
- retains the old generated forms only as compatibility recognizers.

## Platform and native gates

Exact run `30753911776` is still queued. Its declared gates include:

- formatting and exact four-file fence;
- affected-crate compile checks;
- wheel shebang tests;
- current/legacy `python` and `python3` copy tests;
- existing relocatable `pyvenv.cfg` integration test;
- locked workspace/all-target/all-feature clippy with warnings denied;
- executable launcher matrices on GNU, Alpine BusyBox, and macOS;
- sourced Bash activation matrices on GNU, Alpine BusyBox, and macOS;
- absolute, relative, PATH, spaces, leading-hyphen, and symlink controls;
- direct shebang `$0` probes;
- one exact source-only publication commit after all required jobs succeed.

## Design comparison

Generation-host BusyBox detection loses provisionally. A relocatable launcher or environment can be created under one implementation and executed after movement under another. Encoding the generator host's tool flavour would make the artifact depend on where it was produced.

The selected portable form instead:

- keeps `dirname --`, which the BusyBox control accepts;
- removes `realpath --`, which the BusyBox control rejects;
- validates paths beginning with `-` through explicit `./-tool`/`./-activate` execution controls;
- uses the same generated artifact across platform families.

This is still an internal technical selection. Human-owned upstream framing must reconcile it with the public issue discussion before any proposal.

## Disposition

`LEADING CANDIDATE / HOLD FOR EXACT EXECUTION AND SOURCE REVIEW`

A terminal green run is necessary but insufficient. The published one-commit source must still receive a fresh complete-diff review and a current public overlap refresh.

# Candidate B — lockfile passed to `-r`

## Public problem and overlap

Public issue `astral-sh/uv#16192` asks for a clearer error when a uv project or PEP 723 script lockfile is passed as a requirements file. The public history is crowded:

- closed attempts include `astral-sh/uv#16282`, `#17893`, `#19617`, `#19618`, `#20057`, and `#20094`;
- `astral-sh/uv#20683` remains open but exposed no changed files during this pass;
- prior discussion records false-positive and content-sniffing concerns.

That history keeps this lane internal even after source repair.

## Source map

At base `1da26a68629be6ae5fd7f924a7d49ff54763a7df`:

- `RequirementsSource::from_requirements_txt` owns explicit `-r` classification;
- `LockTarget::lock_path` defines project `uv.lock` and script `<complete filename>.lock`;
- `Pep723Metadata::parse` identifies a valid sibling PEP 723 script;
- `uv-requirements` already depends on `uv-scripts`.

## Accepted fork-local source generation

Owned source PR `teamleaderleo/uv#12` now has exact head:

`ba55497fe83ea9bb07c04452f8ba190fa4440a05`

It changes exactly:

- `crates/uv-requirements/src/sources.rs`
- `crates/uv/tests/pip_install/main.rs`
- `crates/uv/tests/pip_install/uv_lock_requirements.rs`

Behavior:

1. exact existing `uv.lock` is diagnosed as a uv lockfile;
2. `<script>.lock` is diagnosed only when the complete sibling filename currently parses as PEP 723;
3. arbitrary `.lock` files remain requirements inputs;
4. constraints and overrides retain existing behavior;
5. lockfile bytes are not inspected or guessed from TOML keys.

## Repairs completed

The initial tests merely touched empty positive lockfiles. They now generate project and script locks through uv's real producers.

A fresh source review then found a Unix filename defect: the detector converted the complete filename to UTF-8, while uv's generator uses `OsString`. The source now compares `OsStr` directly and removes the final `.lock` through `Path::extension`/`file_stem` operations.

A Unix regression generates a real PEP 723 lockfile for a script filename containing invalid UTF-8 and verifies the `-r` diagnostic.

Exact complete-diff review:

- review `4838994246`
- head `ba55497fe83ea9bb07c04452f8ba190fa4440a05`
- disposition `ACCEPT SOURCE / HOLD ROUTING / EXECUTE`

No source defect was found in this generation.

## Execution identities

Clean successor carrier:

- PR `teamleaderleo/uv#15`
- carrier head `b794c91c9bf50b2ee28cd588cd44e51eb44c1d09`
- source head checked out directly: `ba55497fe83ea9bb07c04452f8ba190fa4440a05`
- run: not yet registered at the latest check

Earlier PR `teamleaderleo/uv#13` and run `30753915919` are historical for this source generation because that carrier contains a separate parse-failure experiment and checks an older source head.

## Remaining limits

1. A genuine script lock is deliberately not classified if the sibling script is missing or no longer valid PEP 723. This conservative false negative avoids arbitrary `.lock` false positives.
2. Public overlap remains unresolved and blocks a new public proposal without fresh human maintainer direction.
3. Clean exact-head execution is still pending.

## Disposition

`ACCEPT SOURCE INTERNALLY / HOLD PUBLIC ROUTING / EXECUTE`

This remains a good codebase-learning and design-comparison lane, not the selected first public contribution.

# EnvironmentOptions screen

The adjacent `environment-options-screen.md` records the negative result from public issue `astral-sh/uv#14720`:

- most unchecked variables have prior public implementation attempts;
- apparently unoccupied `UV_GIT_LFS` crosses leaf-crate identity and propagation;
- `UV_STACK_SIZE` is needed during early main/Rayon/client thread initialization;
- `UV_LOCK_TIMEOUT` is a lower-level process-global policy with nonfatal invalid-value semantics.

Disposition: `STOP AS FIRST-PATCH LANE / RETAIN AS CODEBASE MAP`.

# Selected direction and losing reasons

## Selected provisional direction

Finish and independently review Unit 02 as the first prospective upstream contribution.

## Why the lock diagnostic loses first position

- crowded public implementation history;
- one open public attempt;
- lower user consequence than a real platform compatibility failure;
- public routing needs explicit human maintainer direction even though the internal source is now clean.

## Why EnvironmentOptions loses first position

- checklist state does not establish ownership;
- easy-looking entries have prior attempts;
- unoccupied entries require real propagation and semantics design.

## Why deeper lanes lose first position

- source provenance requires resolver/serialization policy alignment;
- self-update requires interruption and platform-specific transaction ownership;
- wheel-cache repair requires independent durable integrity authority;
- PEP 723 symlink behavior requires an authority-policy decision.

## Reopening trigger

Promote another lane above Unit 02 only if Unit 02 fails its exact source/design gates or a fresh public-state change makes a smaller lane clearly available and maintainer-aligned.

# Recommended gradual uv path

1. Settle run `30753911776`, fetch its source-publication receipt, and review the exact four-file source commit.
2. Settle the clean PR #15 execution for `ba55497fe83ea9bb07c04452f8ba190fa4440a05` and retain the public-routing hold.
3. Continue learning through generated snapshots, native integration fixtures, Cargo feature gates, pinned Actions, and producer/consumer pairs.
4. After one genuinely accepted small contribution, advance to one medium-depth lane such as source provenance or a bounded self-update subcase.
5. Keep every public issue, PR, comment, and maintainer message human-owned and separately authorized.

# Self-review

- Existing Fieldwork uv work and P0 backlog were inventoried.
- Public issues, comments, prior pull requests, and current overlap were searched.
- Exact source producers and consumers were read.
- The lock diagnostic received producer-backed positive controls and a non-UTF-8 producer-backed regression.
- Complete exact source diff `ba55497fe83ea9bb07c04452f8ba190fa4440a05` was reviewed.
- The unrelated parse-failure carrier was preserved rather than overwritten.
- Unit 02's `realpath --` and `dirname --` behavior was distinguished.
- Unchecked environment variables were screened by source owner and prior work, not treated as free starter patches.
- Queued or unregistered runs are not described as passed.
- No public upstream interaction occurred.

# Handoff

State: `comparative-evaluation-active`

Read next:

1. Unit 02 run `30753911776` and publication receipt;
2. clean lock diagnostic carrier PR `teamleaderleo/uv#15` and its eventual run;
3. Fieldwork integrity on the current PR #534 head;
4. exact published Unit 02 source diff;
5. fresh public overlap immediately before any human upstream decision.
