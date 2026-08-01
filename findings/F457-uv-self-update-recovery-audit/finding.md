# F457 — uv self-update interruption and partial-commit recovery

## In simple words

`uv self update` is not one file replacement. The official installer downloads a release containing `uv`, `uvx`, and, on Windows, `uvw`; installs those files; writes an install receipt; and may update shell configuration. An interruption can therefore affect several pieces that are expected to describe one installation.

The historical Windows implementation made the most severe mistake first: it renamed the running `uv.exe` to `uv.exe.previous.exe` before starting the installer. Cancelling the update could leave the normal `uv` command absent. A public uv pull request now stages the official Windows release elsewhere and delays replacement of the running executable. That direction is correct and public CI is green.

The public regression test, however, checks an unrelated temporary `uv.exe`, not the actual executable that the old code renames. It also requests cancellation without awaiting task termination. The implementation additionally copies companion executables into the live directory one at a time before replacing `uv.exe`, with no rollback if a later copy fails. Finally, custom-source and enterprise/base-URL updates still delegate to axoupdater 0.10.0, whose Windows path pre-renames the running executable.

The old Linux cross-filesystem partial-copy mechanism appears already repaired in the exact cargo-dist version uv pins: cargo-dist 0.31.0 stages complete bytes in temporary directories inside the destination filesystem before final renames. Linux can still be interrupted between final per-binary renames, leaving a mixed `uv`/`uvx` generation, but current source no longer supports the stronger claim that a cross-filesystem move can partially overwrite the canonical `uv` binary.

Current answer: do not duplicate the public Windows pull request. Audit and repair its evidence, define the installation-wide recovery invariant, and decide whether the remaining generic axoupdater path belongs in uv or axoupdater.

## State

Disposition: `EXECUTE`

Last source review: `2026-08-01`  
Worker: `OpenAI GPT-5.6 Thinking`  
Intake parent: [`teamleaderleo/fieldwork#457`](https://github.com/teamleaderleo/fieldwork/issues/457)  
Owned branch: `research/457-b2-uv-self-update-recovery-audit`  
Owned execution carrier: [`teamleaderleo/uv#8`](https://github.com/teamleaderleo/uv/pull/8)  
Public upstream contact authorized: `no`

Clearing condition: exact Windows negative controls establish whether the public regression discriminates old and candidate behavior, and the result is reconciled with the remaining multi-binary and custom-source windows.

## Exact source identities

| Surface | Exact revision | Role |
| --- | --- | --- |
| uv current public main inspected | [`astral-sh/uv@79bbface771210df216b738e9bdc7df95e5a9e6b`](https://github.com/astral-sh/uv/commit/79bbface771210df216b738e9bdc7df95e5a9e6b) | current routing, dependency pins, release configuration, tests |
| public Windows candidate | [`astral-sh/uv@77e107dd2665f660c461998bc83174bf26ee7cf6`](https://github.com/astral-sh/uv/commit/77e107dd2665f660c461998bc83174bf26ee7cf6) | staged official-Windows implementation and proposed regression |
| public Windows candidate base | [`astral-sh/uv@ec8ad5b7c697b9cbbb8a65c8de00fdb461f2010b`](https://github.com/astral-sh/uv/commit/ec8ad5b7c697b9cbbb8a65c8de00fdb461f2010b) | exact negative-control source |
| public Windows pull request | [`astral-sh/uv#20855`](https://github.com/astral-sh/uv/pull/20855) | occupied implementation lane; do not duplicate |
| original Windows report | [`astral-sh/uv#12142`](https://github.com/astral-sh/uv/issues/12142) | missing canonical `uv.exe` after interrupted update |
| Linux/Windows interruption report | [`astral-sh/uv#15933`](https://github.com/astral-sh/uv/issues/15933) | historical Linux partial binary and later Windows confirmation |
| axoupdater used by uv | [`axodotdev/axoupdater@122313e5b119f0f7f1aa02b95bd13d10b37637ff`](https://github.com/axodotdev/axoupdater/commit/122313e5b119f0f7f1aa02b95bd13d10b37637ff) | generic/custom self-update path; crate version 0.10.0 |
| installer generator pinned by uv | [`axodotdev/cargo-dist@v0.31.0`](https://github.com/axodotdev/cargo-dist/tree/v0.31.0) | exact shell and PowerShell installer generation model |
| self-replacement implementation | [`mitsuhiko/self-replace@d1356fdb346e191b90eec3a21b310c19ac24d2d9`](https://github.com/mitsuhiko/self-replace/commit/d1356fdb346e191b90eec3a21b310c19ac24d2d9) | final running-executable replacement primitive |
| owned execution source base | [`teamleaderleo/uv:fieldwork/457-b2-base-uv-pr-20855`](https://github.com/teamleaderleo/uv/tree/fieldwork/457-b2-base-uv-pr-20855) | exact public candidate, no Fieldwork source changes |
| owned execution carrier | [`teamleaderleo/uv@b78837bc4837cf6cf74ecc558fb90f81b8897538`](https://github.com/teamleaderleo/uv/commit/b78837bc4837cf6cf74ecc558fb90f81b8897538) | one temporary workflow only |

## Change thesis

### Current behavior

The public official-Windows candidate downloads and installs the new release into a temporary install prefix. After that installer succeeds, uv copies every non-current executable into the live executable directory, then calls `self_replace::self_replace` for the currently running executable.

Custom-source, GitHub Enterprise/base-URL override, and other non-official routes still call `AxoUpdater::run`. axoupdater 0.10.0 renames the running executable to `.previous.exe` before starting the generated installer and restores it only when control returns with an ordinary failure.

cargo-dist installers update multiple files sequentially. The exact Unix template stages complete files on the destination filesystem first; the exact PowerShell template copies directly into final live paths.

### Consequence

The candidate narrows and fixes the most visible official-Windows failure: cancellation during the external installer no longer removes canonical `uv.exe`.

It does not yet establish an installation-wide transaction:

- a companion can be updated before a later companion copy fails;
- a companion destination can be overwritten directly rather than by a destination-side staged rename;
- a locked `uvx.exe` or `uvw.exe` can fail after earlier live changes;
- the temporary generated receipt is discarded while the existing receipt remains;
- custom-source updates retain the old pre-rename failure window;
- Linux still permits mixed generations between final per-binary renames.

### Proposed improvement

Define and test two nested invariants instead of calling the whole operation atomic:

1. **Canonical command availability:** after any handled failure or cancellation, a runnable `uv` exists at the canonical executable path.
2. **Installation generation recovery:** after any failure or cancellation, either all managed binaries and receipt describe the old generation, all describe the new generation, or a durable recovery record identifies exactly which generation is authoritative and how to finish or roll back.

The first invariant is necessary and substantially addressed by the public candidate. The second needs explicit design; it cannot be inferred from keeping `uv.exe` present.

### Boundary

This finding does not propose replacing cargo-dist, redesigning uv installation generally, or duplicating the public pull request. It covers interruption, copy/rename failure, companion-file locks, receipt consistency, and routing differences between official and custom update paths.

## End-to-end control flow

### Official public uv route

1. Load and validate the existing standalone install receipt.
2. Resolve an exact target version through uv's own release resolution.
3. Download the target version's generated installer into a temporary directory.
4. Execute the generated installer.
5. Report success.

At current main, the generated installer targets the existing install prefix on every platform. The public Windows candidate changes steps 4–5:

1. create a temporary install prefix and temporary receipt/config prefix;
2. run the generated installer there with PATH modification disabled;
3. enumerate staged files;
4. copy each companion file directly to the live executable directory;
5. replace the running executable with `self_replace`.

### Custom and override route

When the receipt source is not the official public `astral-sh/uv` GitHub source, or when GitHub/GHE installer base URL overrides are set, uv constructs an axoupdater request and calls `AxoUpdater::run`.

axoupdater 0.10.0:

1. downloads the generated installer to a temporary directory;
2. on Windows renames `std::env::current_exe()` to `.previous.exe`;
3. runs the installer against the live install prefix;
4. restores the previous executable only after an ordinary installer failure returns;
5. schedules old-file deletion after success.

Cancellation, process termination, power loss, or a future dropped before restore can bypass step 4.

### Generated Unix installer

cargo-dist 0.31.0:

1. downloads and unpacks all release files to an ordinary temporary directory;
2. creates temporary directories *inside* the live binary/library destination directories;
3. moves all release bytes into those destination-filesystem temporary directories;
4. performs final per-file renames into live names;
5. removes staging directories;
6. writes the install receipt.

This removes the long cross-filesystem copy from the canonical-name replacement step. It does not make the group of final renames atomic.

### Generated PowerShell installer

cargo-dist 0.31.0:

1. downloads and unpacks all release files;
2. copies each binary directly to the live destination with `Copy-Item`;
3. removes each temporary source after copying;
4. creates aliases;
5. copies libraries;
6. writes the receipt.

There is no destination-side temporary file and final rename for each Windows binary.

### self-replace on Windows

`self_replace`:

1. renames the running executable to a random relocated name;
2. schedules deletion of the relocated file after process exit;
3. copies the new executable to a random temporary file beside the canonical destination;
4. renames that destination-side temporary file to the canonical executable path.

This is a strong primitive for one running executable, but it starts only after uv has already copied companions in the public candidate.

## Public candidate audit

### Direction that is correct

- The generated installer completes in an isolated temporary install prefix before the running executable is touched.
- `kill_on_drop(true)` is set on the direct PowerShell child.
- The final running-executable replacement uses `self-replace`, which stages the new bytes beside the destination before the final rename.
- The canonical source diff is one file and public CI completed successfully at the exact candidate head.

### Regression-test defect

The proposed test creates `temp_dir/uv.exe` and asserts that this file still exists after cancellation. The old implementation never refers to that path. It renames `std::env::current_exe()`, which is the Rust test executable. Therefore the test's asserted file is not the resource whose availability distinguishes old and candidate behavior.

The test also calls:

```text
task.abort();
drop(task);
write finish marker;
```

Dropping a Tokio `JoinHandle` detaches it; it does not prove the cancellation completed. Although `abort()` requests cancellation, immediately releasing the installer may let normal completion race the requested cancellation. A reliable control must await the handle and assert a cancelled join result before inspecting filesystem state.

The owned carrier tests both facts against the exact public base and candidate.

### Companion commit window

`replace_from_temporary_install` enumerates the temporary installation directory and calls `fs_err::copy` for every entry except the current executable. Only after the loop completes does it call `self_replace`.

Properties:

- directory iteration order is not a transaction contract;
- successful earlier copies are not rolled back when a later copy fails;
- direct copy can expose a partially written companion after process loss;
- a running/locked companion can reject replacement;
- `uv.exe` can remain old while `uvx.exe` or `uvw.exe` is new;
- the function returns an error without recording which companions changed.

A user already reported an update failure while `uvx.exe` was in use. Keeping the old canonical `uv.exe` is better than losing it, but it does not make the installation coherent.

### Receipt generation window

The candidate supplies a temporary `XDG_CONFIG_HOME`, so the generated installer writes the new receipt outside the existing receipt location. That temporary receipt disappears when its `TempDir` is dropped. The old receipt remains.

Current uv reads only `modify_path` from its local receipt struct after axoupdater has validated the receipt, but the full receipt also carries install prefix, managed binaries, source/provider, version, aliases, and related installation metadata. Discarding the new receipt may be harmless for a release with an identical managed-file set and layout, but that is an assumption requiring an explicit compatibility check. It is not an installation commit.

### Child-process boundary

Tokio's `kill_on_drop(true)` applies to the direct PowerShell process. It does not by itself state a Windows job-object or descendant process-tree guarantee. The generated installer may launch external archive tools. The current cancellation test uses only a PowerShell loop, so it cannot establish descendant termination for a real release installer.

## Linux report disposition

The original RHEL report used uv 0.8.16 and described a partially overwritten, segfaulting `uv`. Later source analysis identified a generated-shell-installer move from an arbitrary temporary directory to the live path. Across filesystems, that move could become a long copy into the canonical destination.

The exact cargo-dist 0.31.0 template pinned by current uv now creates staging directories inside the live destination filesystem, moves complete release bytes there first, and only then performs final renames. This directly addresses the identified cross-filesystem mechanism.

Current source still acknowledges a remaining interruption window during the final per-file loop. The expected consequence is a mixed generation, such as new `uv` with old `uvx`, rather than a partially copied canonical `uv` file. This matches the latest issue assessment.

Current disposition for the strong Linux partial-binary claim: `SUPERSEDED BY GENERATOR REPAIR`, pending a release-artifact hash only if a submission packet requires artifact-level proof beyond the exact pinned generator source.

Current disposition for multi-binary generation coherence on Linux: `RETAIN`, but it is an installation transaction question shared with Windows rather than the historical cross-filesystem partial-copy defect.

## Evidence table

| Claim | Evidence class | Exact basis | Limit |
| --- | --- | --- | --- |
| old official Windows path pre-renames the actual running executable | `source-read` | uv base `ec8ad5...`, `execute_official_installer` | source ordering only until carrier completes |
| public candidate stages official Windows install before touching current executable | `source-read` | uv candidate `77e107d...` | official route only |
| public regression asserts an unrelated fixture path | `source-read` | candidate unit test at `77e107d...` | carrier owns old-head negative control |
| public regression does not await cancellation completion | `source-read` | `task.abort(); drop(task);` | scheduler race consequence inferred until execution |
| candidate copies companions before replacing current executable | `source-read` | `replace_from_temporary_install` at `77e107d...` | no injected live-copy failure yet |
| successful companion copies have no rollback on later failure | `source-read / inferred` | straight-line loop and `?` propagation | consequence follows control flow; exact Windows lock control pending |
| custom/override route still delegates to axoupdater | `source-read` | current uv routing and integration tests | exact cancellation execution pending |
| axoupdater 0.10.0 pre-renames current executable on Windows | `source-read` | axoupdater `122313e...` | generic/custom route only |
| current Unix generator stages bytes on destination filesystem | `source-read` | cargo-dist `v0.31.0` shell template | exact generated release artifact not retained here |
| current Windows generator copies directly into final live paths | `source-read` | cargo-dist `v0.31.0` PowerShell template | public candidate isolates this installer before a second live-copy phase |
| public candidate CI is green | `target-executed` | public run `30616203874` | existing suite; does not prove test discrimination |
| exact old/candidate cancellation boundary | `target-test-prepared` | owned carrier `teamleaderleo/uv#8`, head `b78837b...` | becomes target-executed after Windows receipt completes |

## Discriminating test matrix

| Control | Old base expected | Candidate expected | Why it matters |
| --- | --- | --- | --- |
| published arbitrary `temp_dir/uv.exe` fixture | passes | passes | proves whether the public assertion is non-discriminating |
| await cancellation, inspect `std::env::current_exe()` | canonical path absent; `.previous.exe` present | canonical path present; no `.previous.exe` | exercises the real resource boundary |
| cancel direct PowerShell child and await task | dropped future; child may survive without old `kill_on_drop` | cancelled task and killed direct child | separates request from completed cancellation |
| lock live `uvx.exe` during companion commit | old `uv.exe` preserved only if staging path is used | candidate returns copy failure | must inspect earlier companion changes and recovery record |
| inject failure after first successful companion copy | not applicable to old official direct installer model | mixed live generation unless rollback/staging protocol exists | tests installation-wide transaction claim |
| update through GHE/base-URL override | old axoupdater pre-rename path | still old axoupdater pre-rename path | exposes non-official routing gap |
| Unix source temp directory on another filesystem | canonical copy can be interrupted on historical generator | current generator first stages on destination filesystem | validates supersession of historical mechanism |
| interrupt between Unix final `uv` and `uvx` renames | mixed generation | mixed generation | retained group-commit limit |
| compare old/new receipt after staged Windows success | old receipt may remain | candidate discards temporary new receipt | tests compatibility and managed-file generation |

## Candidate repair directions

### A. Repair the public uv candidate's tests and commit helper

Preferred near-term direction because the public implementation lane is occupied.

- make the final live commit helper accept explicit source/destination paths so tests do not mutate the test runner accidentally;
- assert actual canonical executable availability, not an unrelated fixture;
- await task cancellation;
- stage each companion into a destination-side temporary path before rename;
- define rollback or durable recovery metadata for multi-file failure;
- test a locked companion and a failure after one successful companion commit;
- reconcile or deliberately preserve the receipt with an exact compatibility assertion.

This can remain a focused repair to the existing direction rather than a competing design.

### B. Move generic Windows staging into axoupdater

Potential broader owner because uv custom-source routes and other axoupdater consumers retain the same pre-rename logic.

- download and run installers into an isolated staging prefix when the generated installer supports one;
- keep the current executable at its canonical path until staged installation succeeds;
- expose a caller-owned finalization hook or a staged-install result;
- use `self_replace` only at final commit;
- preserve receipt and managed-file semantics;
- add cancellation and ordinary-failure negative controls.

Risk: axoupdater supports arbitrary generated installers and may not have a universal staging contract. A generic fix may need a capability flag rather than an unconditional behavior change.

### C. Add a generated-installer transactional primitive in cargo-dist

Most reusable but broadest direction.

- destination-side stage every file on Windows and Unix;
- write a manifest of staged old/new paths;
- commit with per-file rename and a recovery journal;
- update receipt last or include it in the journal;
- recover or finish on the next installer invocation.

Risk: a true multi-file atomic rename is unavailable on ordinary filesystems. This direction must promise recoverability, not atomicity.

### Rejected directions

- **Duplicate public PR 20855:** rejected because the implementation lane is occupied and directionally correct.
- **Call the candidate fully atomic:** rejected because companion and receipt commits remain sequential.
- **Reopen the historical Linux cross-filesystem patch unchanged:** rejected because cargo-dist 0.31.0 already stages on the destination filesystem.
- **Only restore `.previous.exe` on error:** rejected because cancellation and process death can bypass language-level restoration.
- **Only keep `uv.exe` available:** insufficient as an installation-wide invariant, though necessary as the first safety guarantee.
- **Block updates whenever `uvx` might be running:** detection is incomplete and does not address interruption, receipt, or other companion failures.

## Compatibility and authority risks

- uv supports official releases, mirrors, GHE/base-URL overrides, and custom receipt sources; routing changes can alter supported enterprise behavior.
- installer layout and managed binary sets can evolve between releases.
- Windows executable locking differs between `uv.exe`, companions, antivirus/indexers, and network filesystems.
- self-replace's single-file behavior is not a multi-file transaction.
- cleanup code must not erase the original error or make a recoverable old generation unavailable.
- a recovery journal must be bounded, non-secret, and robust to repeated interruption.
- no real user installation, credential, public endpoint, or production environment is required for the planned controls.

## Current execution carrier

Owned PR: [`teamleaderleo/uv#8`](https://github.com/teamleaderleo/uv/pull/8)  
Carrier head: `b78837bc4837cf6cf74ecc558fb90f81b8897538`  
Canonical source under test: public candidate `77e107dd2665f660c461998bc83174bf26ee7cf6`  
Exact negative-control base: `ec8ad5b7c697b9cbbb8a65c8de00fdb461f2010b`  
Workflow run: [`30692969073`](https://github.com/teamleaderleo/uv/actions/runs/30692969073)  
Platform: Windows hosted runner  
State at report creation: `queued`

The carrier changes one workflow file only and must close without merge after receipt transfer.

## Next decision after execution

- If the public fixture passes on the old base while the real-executable control distinguishes old and candidate behavior, mark the public test `REPAIR` and retain the implementation direction.
- If the candidate fails the real-executable control, mark the implementation `REPAIR` and isolate whether task cancellation or self-replace owns the failure.
- If both controls pass as expected, prepare a clean owned-fork test/commit-helper repair only if it does not duplicate an updated public head.
- Independently retain the custom axoupdater route as an issue-first or source candidate only after a real exact-path cancellation control confirms the same pre-rename consequence.

## Upstream authority

No public upstream issue, comment, review, reaction, branch, or pull request was created or modified by this lane. Public interaction remains unauthorized.
