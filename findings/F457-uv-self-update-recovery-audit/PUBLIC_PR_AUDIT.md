# Public PR audit — staged Windows uv self-update

## In simple words

The public uv change takes the right first step: it lets the generated installer finish in a separate directory before changing the live `uv.exe`. An exact repaired control has already confirmed that cancellation during this installer phase keeps the actual running executable at its normal path.

That does not settle the whole update. The proposed regression checks the wrong file and is timing-sensitive. After staging succeeds, companion executables are copied into live names one at a time. The final `self-replace` helper renames the live `uv.exe` away before copying the replacement and has no rollback on later error. Custom/GHE updater routes still use axoupdater's older pre-rename flow.

Current review direction: retain the staged-installer implementation, repair its test and claims, and keep the remaining commit and custom-route work explicit rather than calling the update atomic.

## Reviewed surface

- Public target: `astral-sh/uv`
- Public pull request: `20855`, `Stage Windows self-updates before replacing uv.exe`
- Exact candidate head: `77e107dd2665f660c461998bc83174bf26ee7cf6`
- Exact candidate base: `ec8ad5b7c697b9cbbb8a65c8de00fdb461f2010b`
- Current public main inspected: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Current-main distance from candidate base: eight commits
- Relevant updater source changed in those eight commits: `no`
- Complete public candidate diff: one file, `crates/uv/src/commands/self_update.rs`
- Review class: `upstream-fork research / public candidate audit`
- Public contact authority: `no`

## Disposition by claim

| Claim | Disposition | Basis | Clearing condition |
| --- | --- | --- | --- |
| external installer cancellation should not pre-rename the running official Windows `uv.exe` | `ACCEPT` direction | candidate source plus repaired exact candidate control | retain exact receipt and replace weak public test |
| proposed regression proves the old failure and candidate repair | `REPAIR` | assertion targets unrelated `temp_dir/uv.exe`; first exact run also failed its one-second startup wait | actual-current-executable old/candidate negative controls pass |
| failed or interrupted official updates always leave canonical `uv.exe` available | `REPAIR` | final self-replace renames canonical executable before later fallible operations | add rollback/recovery or narrow claim to installer phase |
| companion binaries form one coherent generation | `HOLD` as broader property | live direct copies are sequential and have no rollback/recovery record | locked-file, partial-copy, and mid-sequence interruption design/tests |
| existing receipt remains valid after staged installation | `HOLD` compatibility check | new temporary receipt is discarded and old receipt remains | compare managed files/provider/source/layout across update and failure cases |
| public candidate fixes custom/GHE/base-URL update routes | `REJECT` claim | those routes still call axoupdater 0.10.0 | separate route repair or explicit exclusion |
| historical Linux cross-filesystem partial canonical copy is still current | `SUPERSEDED` | uv pins cargo-dist 0.31.0, which includes destination-filesystem staging repair | retain only mixed-generation residual limit |

## What the public implementation gets right

### Installer isolation

On Windows, the candidate creates:

- a temporary installation directory;
- a separate temporary configuration directory;
- a generated-installer process with PATH modification disabled;
- an installer destination pointing at the temporary installation directory.

The live installation is not changed until that installer returns success.

### Cancellation of the direct child

The direct Tokio child uses `kill_on_drop(true)`. A repaired exact candidate control:

- waits up to 30 seconds for the installer-start marker;
- checks whether the task ended early;
- requests cancellation;
- awaits the `JoinHandle`;
- asserts a cancelled join result;
- inspects `std::env::current_exe()` rather than an unrelated fixture.

That control passed at the exact candidate head on the owned Windows carrier. This supports only the direct installer phase and direct child.

### Single-file destination-side staging inside self-replace

After renaming the old executable, self-replace copies the new executable into a temporary file beside the canonical destination before the final rename. This avoids copying new bytes directly into the canonical filename. It does not repair errors after the old executable has already been renamed.

## Defect 1 — proposed regression is not a valid negative control

The public test writes:

```text
temp_dir/uv.exe
```

and later asserts that it still exists. The old production code never reads or renames this file. It renames:

```text
std::env::current_exe()
```

which is the Rust test executable.

Therefore the asserted fixture can remain present on both the old and new implementations. Passing that assertion does not distinguish the bug.

The test also performs:

```text
task.abort();
drop(task);
write finish marker
```

Dropping a Tokio `JoinHandle` detaches it. It does not establish that cancellation completed before the filesystem assertion or before the installer is allowed to finish.

### Exact observed harness failure

- carrier head: `b78837bc4837cf6cf74ecc558fb90f81b8897538`
- run: `30692969073`
- job: `91350907259`
- platform: Windows Server 2025 hosted runner
- Rust/Cargo: 1.97.1
- result: candidate compile completed; public test failed at `installer should have started`
- polling budget: 100 × 10 ms
- artifact: `8816406268`
- digest: `sha256:30943cc6afd6f943b9b5c64adcec6a0bc9e297b9875dea718500d4d9d02b0875`
- classification: `assertion-harness timing failure`

No updater conclusion is borrowed from that failure.

## Defect 2 — final self-replace can remove canonical uv on ordinary error

Exact self-replace 1.5.0 Windows ordering:

1. canonicalize the current executable;
2. rename it to a random relocated path;
3. schedule deletion of the relocated path;
4. create a random destination-side temporary path;
5. copy the proposed replacement to that temporary path;
6. rename the temporary path to the canonical executable.

Every operation after step 2 is fallible. There is no rollback to the canonical name.

Examples:

- cleanup helper creation or spawning fails;
- replacement source disappeared or cannot be read;
- destination temporary copy fails because of disk or access errors;
- final rename fails;
- process terminates between the old rename and new canonical rename.

The public candidate invokes this primitive after copying companions, so the broad claim that all failed updates leave `uv.exe` available is stronger than the implementation.

Exact owned control: `teamleaderleo/uv#10`, run `30693674419`.

## Defect 3 — companion files commit directly and sequentially

The candidate loops over the temporary installation directory and calls `fs_err::copy` for every entry except the currently running executable. Only after the loop succeeds does it call self-replace.

This permits:

- partial live companion bytes if the process dies during a copy;
- new `uvx.exe` with old `uvw.exe` and old `uv.exe`;
- an error after one companion was updated but a later companion was locked;
- no durable record of which files changed;
- no rollback when a later copy or final self-replace fails.

The issue history contains a real Windows update failure caused by `uvx.exe` being in use. A maintainer said detecting running companions is not reliable and favored moving/renaming files instead. The repair should therefore operate on file state, not process enumeration.

## Defect 4 — custom and override routes keep the original window

The official staged route is selected only for the ordinary public Astral source without GitHub/GHE installer-base overrides.

When custom-source or override conditions apply, uv calls axoupdater 0.10.0. On Windows axoupdater:

1. downloads the generated installer;
2. renames `std::env::current_exe()` to `.previous.exe`;
3. runs the installer against the live prefix;
4. restores the old executable only after an ordinary returning failure;
5. schedules deletion after success.

Process termination, dropped execution, or power loss can bypass restoration. The public candidate does not modify this path.

Exact copied-uv target control: `teamleaderleo/uv#8`, current run `30693322755`.

## Defect 5 — receipt generation is outside the commit

The candidate gives the generated installer a temporary configuration root. The new install receipt is written there and disappears with the temporary directory. The existing receipt remains in place.

uv overwrites the receipt's version with its compiled package version when running a future self-update, so a stale version alone is not fatal. Other fields still matter:

- install prefix;
- managed binary list;
- aliases and libraries;
- source/provider identity;
- future schema or layout changes;
- PATH behavior.

The candidate needs either:

- an explicit proof that the old receipt is semantically identical for the staged release; or
- a receipt commit step included in the same recovery protocol as the binaries.

## Stronger recovery contract

Do not use “atomic” without naming the property. There are two nested contracts:

### Contract A — canonical command availability

After handled failure or cancellation, an executable exists and runs at the canonical `uv` path.

This is the immediate issue and the public implementation meaningfully improves it during the installer phase.

### Contract B — coherent installation generation

After failure, interruption, or recovery, all managed binaries and the receipt describe one old or one new generation, or a durable recovery record can deterministically finish or roll back.

This requires destination-side staging and recovery metadata. It is not implied by Contract A.

## Candidate repair sequence

### Required in the existing public direction

1. Replace the regression with an actual-current-executable control.
2. Use a realistic bounded startup wait and stop early if the task completes.
3. Await cancellation and assert the cancelled result.
4. Narrow the PR body to the installer-phase guarantee unless final replacement is repaired.
5. Add a final-replacement failure control.

### Smallest robust single-file commit

1. copy the new executable to a complete destination-side temporary file before moving the old executable;
2. start a recovery helper before the destructive rename;
3. rename canonical old executable to a backup;
4. rename the complete new temporary file to canonical;
5. make the helper restore the backup if the parent exits before a durable commit signal;
6. only after commit, delete the backup.

An in-process `rename` rollback improves ordinary errors but does not cover process death between renames. A surviving helper or durable journal is required for that claim.

### Installation-wide recoverability

1. stage every managed binary and the new receipt on the destination filesystem;
2. atomically write a `prepared` recovery journal;
3. rename old files to backups and staged files to live names;
4. atomically mark the journal `committed` only after all live names and receipt are new;
5. recover any non-committed journal to the coherent old generation;
6. retain committed new files and clean backups;
7. make recovery idempotent across repeated interruption.

See [`model/RESULTS.md`](./model/RESULTS.md).

## Exact execution surfaces

| Purpose | Owned PR | Exact head | Run | Current state |
| --- | --- | --- | --- | --- |
| first public-test attempt | `teamleaderleo/uv#8` historical head | `b78837bc4837cf6cf74ecc558fb90f81b8897538` | `30692969073` | harness failure retained |
| custom/GHE interruption | `teamleaderleo/uv#8` current head | `93aa1451bf283710c03d97b1e68a28f42184f859` | `30693322755` | running |
| repaired old/candidate negative controls | `teamleaderleo/uv#9` | `e9249cae28746d44fcd2a84307923e50bf2f6041` | `30693451279` | candidate control passed; old controls running |
| final self-replace copy failure | `teamleaderleo/uv#10` | `e5e3d2dcb047bfbaea61c1eb9675340183e9ac08` | `30693674419` | queued/running |

## Current review disposition

`REPAIR`

The staged official-Windows implementation direction should continue. The current public diff should not be rejected wholesale. Before it can accurately claim interruption/failure recovery, it needs:

- a discriminating and non-flaky regression;
- exact final-replacement failure handling or narrower wording;
- explicit scope for custom/override routes;
- visible limits for companion and receipt coherence.

Public upstream interaction remains unauthorized. This audit has not commented on, reviewed, reacted to, or modified the public issue or pull request.
