# uv first-contribution review — 2026-08-02

## In simple words

Fieldwork already contains enough uv work to learn the repository through real source, tests, and review rather than opening another broad issue hunt. The best prospective first upstream contribution remains the Alpine/BusyBox relocatable-launcher repair. Its complete Linux source, lint, GNU, and BusyBox gates are green. A review then found one changed shell that had only textual coverage—Fish activation—so a separate GNU/BusyBox/macOS Fish execution carrier was added instead of weakening the evidence claim. A smaller lockfile diagnostic is now source-clean and useful as an internal exercise, but its public lane is crowded with prior and current attempts. No public upstream interaction occurred.

## Finding state

`comparative-evaluation-active`

Unit 02 remains the selected provisional first-contribution direction. Linux evidence is complete; macOS, Fish runtime coverage, publication, and final generated-source review remain open. The lock diagnostic has an accepted fork-local source generation, remains routing-held, and awaits clean exact-head execution.

## Assignment and authority

- Coordination: `teamleaderleo/fieldwork#210`.
- Canonical finding: this file.
- Supporting architecture screen: `environment-options-screen.md` beside this file.
- Owned target repository: `teamleaderleo/uv`.
- Public target observed quietly: `astral-sh/uv`.
- Public upstream contact authorized: `false`.
- Public upstream contact performed: `false`.
- Retrieval date: 2026-08-02.

## Method applied

This pass inventoried existing owned uv work, pinned exact source/carrier identities, read producer and consumer code, searched public overlap, repaired owned-fork defects, added producer-backed tests, separated source from execution carriers, reviewed complete diffs, and preserved negative results. A green workflow is treated as evidence, not as a landing decision.

## Existing uv work map

| Lane | Owned surface | Current use |
| --- | --- | --- |
| BusyBox relocatable launchers | main carrier `teamleaderleo/uv#7`; Fish supplement `#18`; publication target `upstream/02-busybox-realpath` | Leading first-contribution candidate; Linux green, remaining gates pending. |
| `uv.lock` passed to `-r` | source `teamleaderleo/uv#12`; clean carrier `#15` | Source accepted internally; public routing held; execution pending. |
| Alternative parse-failure diagnostic | carrier `teamleaderleo/uv#13` | Separate experiment; retained and not treated as execution authority for source #12. |
| local-directory source provenance | `teamleaderleo/uv#11` | Medium-depth resolver/serialization research; active overlap. |
| interrupted self-update recovery | `teamleaderleo/uv#8`, `#9`, `#10`; Fieldwork `#491` | High-consequence transaction work; too broad for a first patch. |
| extracted wheel cache corruption | `teamleaderleo/uv#1` | Confirmed integrity gap requiring independent durable authority. |
| PEP 723 symlink lock authority | `teamleaderleo/uv#4` | Policy/authority characterization, not a settled starter implementation. |

# Candidate A — BusyBox relocatable launchers

## Public problem and current-main state

Public issue `astral-sh/uv#16209` records that Alpine 3.22 / BusyBox 1.37 `realpath` interprets `--` as a missing path, emits a diagnostic, and returns nonzero in relocatable launchers. It remains open and unassigned. A fresh exact-topic search found no matching public repair pull request. Current public main `79bbface771210df216b738e9bdc7df95e5a9e6b` still contains the failing generated `realpath --` forms.

The issue discussion correctly warns that blindly deleting every delimiter is weak: leading-hyphen operands still matter, and generation-host BusyBox detection was floated as an alternative.

## Candidate and generator review

Owned carrier `teamleaderleo/uv#7` at `c8a5c36d60a5cc35f496f583146967e210f87810` generates an exact candidate from public/fork base `79bbface771210df216b738e9bdc7df95e5a9e6b` changing only:

- `crates/uv-install-wheel/src/wheel.rs`
- `crates/uv-virtualenv/src/virtualenv.rs`
- `crates/uv/src/commands/project/run.rs`
- `crates/uv/tests/python/venv.rs`

The candidate removes only unsupported `realpath --`, preserves every `dirname --`, recognizes current and historical relocatable shebangs for both `python` and `python3`, updates existing virtualenv expectations, and keeps old forms as recognition-only compatibility inputs.

Generator review receipt:

- review `4839008092`
- exact carrier head `c8a5c36d60a5cc35f496f583146967e210f87810`
- disposition `ACCEPT CARRIER DESIGN / EXECUTION AND GENERATED SOURCE PENDING`

The generator uses exact-count replacements and a four-file fence. Its native copy test exercises current and legacy `python`/`python3` headers, rewritten content, and executable-mode preservation. No generator defect was found.

## Main execution evidence

Run `30753911776`:

### Linux/source job `91512671857` — success

All declared Linux steps passed:

- exact carrier fence and candidate generation;
- exact four-file source diff;
- generator unit tests;
- formatting and affected-crate compilation;
- wheel shebang tests;
- current/legacy `python` and `python3` copy tests;
- existing relocatable `pyvenv.cfg` integration coverage;
- `cargo clippy --locked --workspace --all-targets --all-features -- -D warnings`;
- GNU and Alpine 3.22 / BusyBox 1.37 launcher matrices;
- GNU and BusyBox Bash activation matrices;
- direct shebang `$0` probes;
- assertion markers and retained receipts.

The retained artifact confirms the changed-file fence, clippy invocation, generated patch, compatibility-recognizer counts, and platform transcripts. On BusyBox, the current form produces the reported `realpath: --:` diagnostic; the candidate form produces no stderr. GNU current and candidate forms remain clean. Explicit `./-tool` and `./-activate` controls cover leading-hyphen names.

### Remaining main-run jobs

- macOS job `91512671833` — queued at the latest check;
- source publication job `91513239430` — queued and dependent on required platform jobs.

No final source branch or source acceptance is claimed yet.

## Fish runtime gap and supplement

The generated source also changes Fish activation, but the main carrier executes only Bash activation; Fish was initially covered only by string assertions. This was treated as an evidence defect, not ignored.

Separate execution-only supplement:

- PR `teamleaderleo/uv#18`
- carrier head `59ee7456984806a0f065b71a937d6f39131087d1`
- run `30755096609`
- Linux Fish job `91515786243` — queued at the latest check
- macOS Fish job `91515786224` — queued at the latest check
- review `4839025463` — `ACCEPT EXECUTION CARRIER / RUN PENDING`

The probe sources the exact generated Fish expressions—current `realpath -- (status -f)` and candidate `realpath (status -f)`—through absolute, relative, spaces, leading-hyphen, and symlink paths on GNU, Alpine 3.22 / BusyBox 1.37, and macOS. It verifies the exact `VIRTUAL_ENV` and stderr contract.

## Design comparison

Generation-host BusyBox detection loses provisionally. A relocatable launcher or environment can be produced under one implementation and executed after movement under another. Encoding the generator host's tool flavour would make the artifact depend on where it was produced.

The selected portable form keeps `dirname --`, which BusyBox accepts; removes `realpath --`, which BusyBox rejects; tests path names beginning with `-` through explicit relative invocation; and uses the same artifact across platform families.

This remains an internal technical selection. Human-owned upstream framing must reconcile it with the public issue discussion before any proposal.

## Disposition

`LEADING CANDIDATE / LINUX ACCEPTED / HOLD FOR MACOS, FISH, PUBLICATION, AND SOURCE REVIEW`

After all execution gates pass, the published one-commit four-file source must receive a fresh complete-diff review and a current public-overlap refresh.

# Candidate B — lockfile passed to `-r`

## Public problem and overlap

Public issue `astral-sh/uv#16192` asks for a clearer error when a uv project or PEP 723 script lockfile is passed as a requirements file. Closed attempts include `astral-sh/uv#16282`, `#17893`, `#19617`, `#19618`, `#20057`, and `#20094`; `astral-sh/uv#20683` remained open but exposed no changed files during this pass. Prior discussion records false-positive and content-sniffing concerns. This history keeps the lane internal even after source repair.

## Accepted fork-local source

Owned source PR `teamleaderleo/uv#12` exact head:

`ba55497fe83ea9bb07c04452f8ba190fa4440a05`

Changed files:

- `crates/uv-requirements/src/sources.rs`
- `crates/uv/tests/pip_install/main.rs`
- `crates/uv/tests/pip_install/uv_lock_requirements.rs`

Behavior:

1. exact existing `uv.lock` is diagnosed as a uv lockfile;
2. `<script>.lock` is diagnosed only when the complete sibling filename currently parses as PEP 723;
3. arbitrary `.lock` files remain requirements inputs;
4. constraints and overrides retain existing behavior;
5. lockfile bytes are not inspected.

Positive tests generate project and script locks through uv's real producers. A Unix regression generates a real PEP 723 lockfile for a script filename containing invalid UTF-8. The detector uses `Path`/`OsStr` operations, preserving the complete filename without UTF-8 conversion.

Source review:

- review `4838994246`
- disposition `ACCEPT SOURCE / HOLD ROUTING / EXECUTE`

No source defect was found in this generation.

## Execution identities

Clean carrier:

- PR `teamleaderleo/uv#15`
- head `b794c91c9bf50b2ee28cd588cd44e51eb44c1d09`
- exact source `ba55497fe83ea9bb07c04452f8ba190fa4440a05`
- focused run `30754710006`, job `91514796254` — queued at latest check
- ordinary fork CI `30754710091` — queued at latest check
- carrier review `4839008193` — `ACCEPT CARRIER / EXECUTION PENDING`

The uv crate's default `test-defaults` feature includes `test-python` and `test-pypi`, so the focused integration module is not a zero-test configuration.

Earlier PR `teamleaderleo/uv#13` and run `30753915919` contain a separate parse-failure experiment and are not execution authority for this source generation.

## Remaining limits and disposition

A genuine script lock is deliberately not classified if the sibling script is missing or no longer valid PEP 723; this conservative false negative avoids arbitrary `.lock` false positives. Public overlap remains the routing blocker regardless of execution.

Disposition: `ACCEPT SOURCE INTERNALLY / HOLD PUBLIC ROUTING / EXECUTE`.

# EnvironmentOptions screen

The adjacent `environment-options-screen.md` records that most unchecked variables in `astral-sh/uv#14720` have prior public attempts. Apparently unoccupied `UV_GIT_LFS`, `UV_STACK_SIZE`, and `UV_LOCK_TIMEOUT` cross leaf-crate identity, early thread initialization, or lower-level global-policy/error-semantics boundaries.

Disposition: `STOP AS FIRST-PATCH LANE / RETAIN AS CODEBASE MAP`.

# Selected direction and losing reasons

## Selected provisional direction

Finish and independently review Unit 02 as the first prospective upstream contribution.

## Why the alternatives lose first position

- Lock diagnostic: crowded implementation history, open attempt, lower consequence, and a public-routing hold despite source quality.
- EnvironmentOptions: checklist state does not establish ownership; available-looking entries require propagation and semantics design.
- Deeper lanes: source provenance needs resolver/serialization policy alignment; self-update needs interruption/platform transaction ownership; wheel-cache repair needs independent durable integrity authority; PEP 723 symlink behavior needs an authority-policy decision.

## Reopening trigger

Promote another lane above Unit 02 only if Unit 02 fails its macOS/Fish/source-review gates or a fresh public-state change makes another small lane clearly available and maintainer-aligned.

# Recommended gradual uv path

1. Settle Unit 02 macOS, Fish, and source-publication gates; review the exact published source commit.
2. Settle clean lock-diagnostic execution while retaining the public-routing hold.
3. Continue learning through generated snapshots, native integration fixtures, Cargo feature gates, pinned Actions, and producer/consumer pairs.
4. After one genuinely accepted small contribution, advance to one medium-depth lane such as source provenance or a bounded self-update subcase.
5. Keep every public issue, PR, comment, and maintainer message human-owned and separately authorized.

# Self-review

- Existing Fieldwork uv work and P0 backlog were inventoried.
- Public issues, comments, prior pull requests, and current main were searched.
- Exact source producers and consumers were read.
- The lock diagnostic received producer-backed positive controls and a non-UTF-8 producer-backed regression.
- Complete lock source and execution-carrier diffs were reviewed.
- Unit 02 generator and complete Linux evidence were reviewed.
- Fish activation runtime coverage was identified as missing and added in a separate carrier.
- `realpath --` and `dirname --` behavior were distinguished.
- Unchecked environment variables were screened by source owner and prior work.
- Queued jobs are not described as passed.
- No public upstream interaction occurred.

# Handoff

State: `comparative-evaluation-active`

Read next:

1. Unit 02 macOS job `91512671833` and publication job `91513239430` in run `30753911776`;
2. Fish run `30755096609`;
3. clean lock runs `30754710006` and `30754710091`;
4. Fieldwork integrity for the current PR #534 head;
5. exact published Unit 02 source diff;
6. fresh public overlap immediately before any human upstream decision.
