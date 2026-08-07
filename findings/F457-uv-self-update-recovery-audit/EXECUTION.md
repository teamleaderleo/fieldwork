# Execution ledger — uv self-update recovery audit

## Current state

Disposition: `REPAIR / EXECUTE`

This ledger separates completed target observations from queued reruns and source-only consequences. No queued, cancelled, or harness-failed run is treated as product evidence.

Public upstream contact authorized/performed: `false` / `false`.

## Exact source fence

| Surface | Exact identity |
| --- | --- |
| public uv head inspected | `astral-sh/uv@79bbface771210df216b738e9bdc7df95e5a9e6b` |
| public staged-Windows candidate | `astral-sh/uv@77e107dd2665f660c461998bc83174bf26ee7cf6` |
| candidate old-base control | `astral-sh/uv@ec8ad5b7c697b9cbbb8a65c8de00fdb461f2010b` |
| axoupdater | `axodotdev/axoupdater@122313e5b119f0f7f1aa02b95bd13d10b37637ff` / crate 0.10.0 |
| cargo-dist template | `axodotdev/cargo-dist@v0.31.0` |
| self-replace source inspected | `mitsuhiko/self-replace@d1356fdb346e191b90eec3a21b310c19ac24d2d9` / crate 1.5.0 |

## Completed observations

### Public candidate repository CI

- public run: `30616203874`
- conclusion: success
- Windows test shards and Windows clippy completed successfully.

Evidence boundary: this proves the repository accepted the exact public candidate under its existing suite. It does not prove that the added interruption test is a valid old-head negative control.

### First owned execution of the published regression

- owned PR: `teamleaderleo/uv#8`
- carrier head: `b78837bc4837cf6cf74ecc558fb90f81b8897538`
- run/job: `30692969073` / `91350907259`
- artifact: `8816406268`
- digest: `sha256:30943cc6afd6f943b9b5c64adcec6a0bc9e297b9875dea718500d4d9d02b0875`
- result: the candidate compiled, then the published test failed at `installer should have started` before cancellation or executable-state assertions.

Classification: `harness timing failure`. The test's one-second startup budget is not reliable on a clean hosted Windows build.

### Repaired candidate actual-executable control

- owned PR: `teamleaderleo/uv#9`
- historical carrier head: `e9249cae28746d44fcd2a84307923e50bf2f6041`
- run/job: `30693451279` / `91352168319`
- result: candidate-side control passed.

The control used `std::env::current_exe()`, waited up to 30 seconds, stopped if the task completed early, requested cancellation, awaited the join handle, and asserted cancellation completion. The actual current executable remained at its canonical path and no `.previous.exe` was created.

Supported claim: the public candidate protects canonical `uv.exe` during cancellation of the isolated official installer phase.

### Old public-fixture negative control

Same owned run `30693451279` executed the public test's fixture shape against exact old base `ec8ad5b...`.

Result: it passed on the known-broken old implementation.

Supported claim: asserting an unrelated `temp_dir/uv.exe` is non-discriminating and cannot prove the regression.

### Custom/GHE route characterization

- owned PR: `teamleaderleo/uv#8`
- historical head: `93aa1451bf283710c03d97b1e68a28f42184f859`
- run/job: `30693322755` / `91351841114`
- artifact: `8817348293`
- digest: `sha256:772e843c0d47f12de4ca36a4ea68ac45d01b0f120f50158359a03ce512b28a43`
- semantic result: the copied `uv.exe` entered the axoupdater custom route, the canonical path disappeared, and `.previous.exe` existed before interruption; the target test assertion passed.
- workflow result: the job remained alive for about 83 minutes because the deliberately blocked PowerShell descendant inherited output handles.

Evidence classification: the filesystem observation is target-executed; the long workflow tail is a harness-lifetime defect, not a contradictory product result.

## Preserved incomplete runs

### Old actual-current-executable control

- run: `30693451279`
- artifact: `8817700085`
- digest: `sha256:65a203dbaef26ad5f11f1d6802ec888a530c3178e0e4179631713a0a8b6acfde`
- result: the old actual-executable test did not complete before workflow cancellation.

The candidate pass and weak-fixture pass are retained. The old-base destructive result remains source-supported until the focused closure run completes.

### self-replace failure injection

- owned PR: `teamleaderleo/uv#10`
- historical head: `e5e3d2dcb047bfbaea61c1eb9675340183e9ac08`
- run/job: `30693674419` / `91352741319`
- artifact: `8816605390`
- digest: `sha256:062be24866326ecd204057024b0556db013fccd7c197b7351473a4f04d73a999`
- result: PowerShell rejected a literal backslash line continuation before the helper launched.

Classification: `harness parse failure`; no self-replace product result.

## Repaired continuation heads

| Purpose | Owned PR | Exact head | Run | State at 2026-08-02 review |
| --- | --- | --- | --- | --- |
| custom/GHE route without inherited output handles | `teamleaderleo/uv#8` | `41fc6d53e2a2c5065743657302c4255acffa0db5` | `30754208709` | queued |
| focused old-base actual-executable discriminator | `teamleaderleo/uv#9` | `614df9998cd043a8a20547fd4ce7efb0aaf6a051` | `30754251841` | queued |
| self-replace missing-source failure | `teamleaderleo/uv#10` | `34031835cbfe8b84edaf8e3ce5d6d846bc50d59e` | `30754221525` | queued |
| deferred finalize-after-exit prototype | `teamleaderleo/uv#14` | `ef509a215af602cbc904aed467b4ac5edd66f827` | `30754411464` | queued |

Queued means no target result. Each run must be inspected at its exact head before this table is promoted.

## Harness repairs made

### Custom/GHE route

- changed the copied updater process stdout/stderr from inherited handles to null;
- writes the finish marker immediately after interrupting the parent;
- waits for the parent only after releasing the deliberately blocked installer.

This preserves the filesystem assertion while allowing descendants to exit and the workflow to complete.

### Old-base discriminator

- removed already-settled candidate and weak-fixture controls from the successor run;
- executes only the missing old actual-executable boundary;
- records canonical absence and `.previous.exe` presence before releasing the installer;
- uses a bounded timeout instead of depending on normal victim completion;
- restores the renamed test executable only after Cargo's test process releases Windows file locks.

### self-replace primitive

- replaced invalid PowerShell backslash continuation with a splatted `Start-Process` argument map;
- keeps the helper under an external workflow supervisor;
- records exit code and exact directory contents after failure injection.

## Deferred finalizer experiment

Owned draft PR: `teamleaderleo/uv#14`

The experiment is not an upstream-ready uv patch. It prototypes one safer commit primitive:

1. validate canonical and replacement files;
2. copy and sync replacement bytes beside the installed executable while old canonical `uv.exe` remains runnable;
3. write a small prepared journal;
4. wait for the updating parent PID to exit;
5. rename old canonical to a backup;
6. rename the complete destination-side stage to canonical;
7. roll back ordinary commit failure;
8. remove backup and journal after success.

The workflow matrix covers:

- no canonical mutation while the parent is alive;
- successful commit after parent exit;
- missing replacement failing before waiting or canonical mutation;
- injected failure after backup restoring the old canonical file;
- cleanup of stage, backup, and journal files after success or ordinary rollback.

Known limits:

- sudden power loss between same-directory renames still requires startup/next-run journal recovery;
- the prototype does not integrate with uv CLI routing;
- it handles one canonical file, not an atomic `uv`/`uvx`/`uvw` generation;
- it does not yet prove descendant termination for the generated installer.

## Evidence promotion rules

A run can be called target-executed only after:

1. exact source/carrier identity and file fence pass;
2. the intended helper or target test launches;
3. the discriminating filesystem state is recorded;
4. workflow completion is inspected;
5. artifact identity and digest are retained when produced.

A red run caused by checkout, syntax, startup timing, inherited handles, or supervisor failure remains harness evidence only.
