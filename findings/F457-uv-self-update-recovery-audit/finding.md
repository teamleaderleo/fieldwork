# F457 — uv self-update interruption and partial-commit recovery

## In simple words

The public Windows repair takes the correct first step: it completes the generated installer in a temporary location before touching the live `uv.exe`. An exact repaired control confirms that cancellation during this isolated installer phase leaves the actual running executable at its canonical path.

That is not the complete update transaction.

- The public regression asserts an unrelated fixture and also passes on the broken old implementation.
- The final Windows `self-replace` primitive renames canonical `uv.exe` before later fallible operations and has no rollback.
- Companion executables are copied into live names sequentially before `uv.exe` is replaced.
- The staged receipt is discarded while the old receipt remains.
- Custom/GHE/base-URL routes still use axoupdater 0.10.0, which pre-renames the running executable and can leave the canonical command absent after interruption.
- The historical Linux cross-filesystem partial-copy mechanism is superseded by cargo-dist 0.31.0 destination-filesystem staging, but mixed `uv`/`uvx` generations remain possible between final per-file renames.

Current answer: **do not duplicate public PR 20855**. Retain its official-installer staging direction, repair its evidence and claims, close the generic/custom route separately, and use a recoverable transaction model for the remaining single-file and multi-file commit windows.

## State

Disposition: `REPAIR / EXECUTE`

Last review: `2026-08-02`  
Worker: `OpenAI GPT-5.6 Thinking`  
Intake parent: `teamleaderleo/fieldwork#457`  
Fieldwork PR: `teamleaderleo/fieldwork#491`  
Owned branch: `research/457-b2-uv-self-update-recovery-audit`  
Public upstream contact authorized/performed: `false` / `false`

Supporting records:

- [`PUBLIC_PR_AUDIT.md`](./PUBLIC_PR_AUDIT.md)
- [`EXECUTION.md`](./EXECUTION.md)
- [`PROPOSAL.md`](./PROPOSAL.md)
- [`ROUTING.md`](./ROUTING.md)
- [`model/RESULTS.md`](./model/RESULTS.md)

## Exact identities

| Surface | Exact identity | Role |
| --- | --- | --- |
| current uv source inspected | `astral-sh/uv@79bbface771210df216b738e9bdc7df95e5a9e6b` | routing, dependency, installer, test, and release configuration |
| public Windows candidate | `astral-sh/uv@77e107dd2665f660c461998bc83174bf26ee7cf6` | occupied official-route implementation |
| candidate base | `astral-sh/uv@ec8ad5b7c697b9cbbb8a65c8de00fdb461f2010b` | old-head negative control |
| public PR | `astral-sh/uv#20855` | open, mergeable, unchanged at last review |
| axoupdater | `axodotdev/axoupdater@122313e5b119f0f7f1aa02b95bd13d10b37637ff` | custom/GHE route, crate 0.10.0 |
| cargo-dist | `axodotdev/cargo-dist@v0.31.0` | exact generator version pinned by uv |
| self-replace | `mitsuhiko/self-replace@d1356fdb346e191b90eec3a21b310c19ac24d2d9` | final Windows running-executable primitive, crate 1.5.0 |
| deferred finalizer experiment | `teamleaderleo/uv#14@ef509a215af602cbc904aed467b4ac5edd66f827` | internal source experiment only |

## Disposition by mechanism

| Mechanism | Disposition | Reason |
| --- | --- | --- |
| official Windows installer-time pre-rename | `DIRECTION ACCEPTED` | isolated staging plus repaired candidate control preserves actual canonical executable during cancellation |
| public regression test | `REPAIR` | wrong file boundary, non-discriminating old control, brittle one-second startup wait, detached cancellation |
| final Windows `uv.exe` replacement | `REPAIR` | old canonical file is renamed before later fallible work; ordinary failure and process death can leave it absent |
| Windows companion commit | `HOLD / DESIGN` | direct sequential copies permit partial bytes, mixed generations, and no rollback record |
| staged receipt handling | `HOLD / COMPATIBILITY` | new temporary receipt is discarded; old receipt is assumed valid rather than committed or compared |
| custom/GHE/override Windows route | `OPEN DEFECT` | axoupdater retains pre-rename behavior; exact owned characterization observed canonical absence |
| historical Linux partial canonical copy | `SUPERSEDED` | cargo-dist 0.31.0 stages complete bytes on the destination filesystem before final renames |
| Linux multi-binary generation coherence | `RETAIN` | final `uv` and `uvx` renames remain sequential |

## What is execution-proven

### Narrow candidate installer-phase guarantee

The repaired candidate control at exact public candidate head:

- inspected `std::env::current_exe()`;
- used a 30-second bounded startup wait;
- stopped if the updater task completed early;
- requested cancellation;
- awaited the join handle;
- asserted a cancelled join result;
- confirmed canonical executable presence and absence of `.previous.exe`.

Result: passed.

Supported conclusion: **official-route cancellation during the isolated generated-installer phase does not pre-rename the actual running candidate executable.**

### Public fixture is invalid as a regression discriminator

The exact old base passed the public test's unrelated `temp_dir/uv.exe` assertion.

Supported conclusion: the published assertion can pass without the repair and must be replaced.

### Custom/GHE route reaches the destructive state

An exact copied-uv integration control entered the custom/GHE route and observed:

- canonical `uv.exe` absent;
- `.previous.exe` present;
- target assertion passed.

The workflow then remained alive because the intentionally blocked PowerShell descendant inherited output handles. That tail is a harness-lifetime defect; it does not erase the retained filesystem observation.

## What remains source-supported or queued

- old exact base actual-current-executable displacement after cancellation;
- self-replace missing-source failure returning with canonical path absent;
- clean completion of the repaired custom/GHE test;
- deferred finalizer hostile matrix;
- locked-companion and mid-sequence live-copy outcomes;
- receipt compatibility across managed-file/layout changes;
- generated-installer descendant-tree termination.

Exact repaired heads and queued runs are in [`EXECUTION.md`](./EXECUTION.md). No queued run is counted as target evidence.

## Public candidate audit

### Correct architecture move

For the ordinary public Windows route the candidate:

1. resolves the target release;
2. creates a temporary install prefix and temporary config prefix;
3. runs the cargo-dist PowerShell installer there with PATH modification disabled;
4. waits for installer success;
5. copies companions into the live directory;
6. calls `self_replace` for the running executable.

The live installation is no longer exposed during download and generated-installer execution. That materially narrows the interruption window.

### Weak regression

The added test creates `temp_dir/uv.exe`, but old production code renames `std::env::current_exe()`. The fixture is not the resource under test. It also uses only 100 × 10 ms to wait for PowerShell startup and drops the cancelled task instead of awaiting completion.

The first exact owned run compiled the candidate and then failed before cancellation at `installer should have started`. This is retained as a harness timing failure, not a product failure.

### Companion window

`replace_from_temporary_install` enumerates staged files and uses direct `copy` into live destinations for every entry except the current executable. Earlier successful copies are not rolled back if a later companion is locked, a copy fails, or final self-replace fails.

Consequences:

- a process interruption can expose partial bytes in a companion live name;
- new `uvx.exe` or `uvw.exe` can coexist with old `uv.exe`;
- no durable record says which files changed;
- the old receipt can describe a different managed-file set or layout;
- retry authority is ambiguous after a partial live commit.

Keeping `uv.exe` callable is necessary but does not make the installation coherent.

### self-replace window

The inspected self-replace Windows source:

1. canonicalizes current executable;
2. renames it to a relocated path;
3. schedules deletion of that relocated path;
4. copies replacement bytes to a destination-side temporary file;
5. renames the temporary file to canonical.

There is no rollback after step 2. The candidate therefore cannot accurately promise that every final replacement failure leaves canonical `uv.exe` available.

### Receipt window

The isolated installer writes a new receipt under temporary configuration storage. That receipt disappears when staging is dropped. The previous canonical receipt remains.

A safe design must either:

- prove every relevant field remains semantically identical and deliberately retain the old receipt; or
- include the staged receipt in the managed generation commit.

Version alone is not the full contract. Install prefix, managed binaries, aliases, libraries, source/provider, layout, schema, and PATH policy can matter.

### Descendant ownership

`kill_on_drop(true)` owns the direct PowerShell child. It does not by itself guarantee termination of archive tools or detached descendants. A complete interruption claim requires a Windows Job Object or an explicit installer process-tree contract.

## Linux disposition

The RHEL report described a partially overwritten, segfaulting `uv` under an older installer. The identified mechanism was a move from an arbitrary temporary filesystem into the canonical destination; across filesystems, that could become a long copy directly into the live filename.

cargo-dist 0.31.0 now:

1. creates staging directories inside destination directories;
2. moves complete bytes into that destination filesystem first;
3. performs final per-file renames only after staging.

This supersedes the strong historical cross-filesystem partial-byte mechanism. It does not make the group commit atomic. Interruption can still leave new `uv` with old `uvx`.

## Recovery contract

Avoid the unqualified word “atomic.” The required nested properties are:

### A. Canonical command availability

After handled failure or cancellation, a runnable `uv` exists at its normal path.

### B. Managed generation recoverability

After failure, interruption, or restart:

- every managed binary and receipt are old; or
- every managed binary and receipt are new; or
- a durable bounded journal identifies the authoritative state and an idempotent recovery action.

A filesystem cannot atomically rename the complete managed set. The correct stronger promise is recoverability.

## Code experiment

`teamleaderleo/uv#14` implements a Windows-only prototype finalizer that:

- validates and stages replacement bytes beside canonical while old `uv.exe` remains live;
- syncs the staged file;
- writes a prepared journal;
- waits for the updating parent PID to exit;
- renames old canonical to backup;
- renames stage to canonical;
- restores backup on ordinary injected commit failure;
- removes stage/backup/journal after completion.

The queued matrix checks deferred commit, missing-stage fail-closed behavior, and rollback after backup. The prototype is deliberately not a product candidate yet: sudden-power-loss recovery, uv CLI integration, multi-binary generation commit, and descendant ownership remain open.

## Selected continuation

1. Settle repaired runs `30754208709`, `30754251841`, `30754221525`, and `30754411464` at their exact heads.
2. Transfer exact job, artifact, and digest receipts into [`EXECUTION.md`](./EXECUTION.md).
3. Repair the finalizer experiment until all three hostile controls pass.
4. Add a next-run recovery executable that consumes prebuilt journal states and proves idempotence.
5. Add locked `uvx.exe` and failure-after-first-companion controls before proposing a multi-file patch.
6. Decide whether custom-route staging belongs in uv or axoupdater; do not silently broaden the official-route implementation.
7. Keep public PR 20855 read-only and do not create public review/comment/PR activity without separate authority.

## Clearing condition

This lane can leave `EXECUTE` when:

- old and candidate actual-executable controls complete at exact heads;
- self-replace failure is target-executed or its broad claim is explicitly removed;
- custom/GHE consequence completes without harness ambiguity;
- the selected single-file finalizer experiment has exact hostile-control receipts;
- multi-file/receipt work is explicitly routed as issue-first design rather than implied solved;
- complete internal diff review finds no unsupported evidence promotion.
