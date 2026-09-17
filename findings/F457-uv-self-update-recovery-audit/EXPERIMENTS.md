# Fork experiment ledger — uv self-update recovery

## Purpose

These are fork-local probes, not public proposals. Each experiment isolates one authority boundary that the occupied public Windows candidate does not settle.

Public upstream contact authorized/performed: `false` / `false`.

## A. Deferred single-file finalizer

Owned draft: `teamleaderleo/uv#14`  
Exact current head: `94f7229d88fa0a8a81c1b946d3fce1f214b5ac7d`  
Exact base: public candidate `77e107dd2665f660c461998bc83174bf26ee7cf6`

Current workflow runs at this exact head:

- deferred finalizer matrix: `30755910004`, queued;
- recovery workflow selected by changed paths: `30755909988`, queued;
- repository CI: `30755910166`, queued.

Superseded source head/run: `ef509a215af602cbc904aed467b4ac5edd66f827` / `30754411464`.

### Hypothesis

The updating process should finish all slow/fallible staging while old canonical `uv.exe` remains runnable. A separate finalizer should acquire parent-exit authority and touch canonical only after the parent releases the executable lock.

### Prototype ordering

1. validate canonical and replacement;
2. copy replacement beside canonical;
3. sync staged replacement;
4. write prepared journal;
5. wait for parent process exit;
6. rename old canonical to backup;
7. rename staged new file to canonical;
8. restore backup on ordinary commit failure;
9. clean transaction files after committed success.

### Hostile matrix

- canonical remains old while parent is alive;
- successful replacement occurs only after parent exit;
- missing replacement fails before waiting or canonical mutation;
- injected failure after backup restores old canonical;
- success and rollback clean stage, backup, and journal.

### Static repair after broad-CI review

The experiment driver now gates Windows-only `env` and `PathBuf` imports with `#[cfg(windows)]`. This prevents Linux all-target checks from reporting unused imports before the Windows behavior runs.

### Limits

- no next-run recovery in this base experiment;
- parent is identified initially by PID rather than a passed process handle;
- one file only;
- no CLI integration;
- no hashes or directory durability proof;
- no complete installer process-tree ownership.

## B. Idempotent journal recovery stack

Owned stacked draft: `teamleaderleo/uv#16`  
Exact current head: `12d3341759f97d79fd7bb6b3f43edfaa8394aa6d`  
Exact base: experiment A head `94f7229d88fa0a8a81c1b946d3fce1f214b5ac7d`

Maintenance merge: `teamleaderleo/uv#22`, merged solely to preserve exact ancestry after the platform-import repair.

Current workflow runs:

- recovery matrix: `30755930465`, queued;
- deferred finalizer matrix: `30755930463`, queued;
- repository CI: `30755930556`, pending.

Superseded stack head/runs:

- `a135d36334ef07a1386a48e7ce48e39d8975e9d9`;
- finalizer `30755118098`;
- recovery `30755118069`;
- CI `30755118191`.

### Additional source behavior

The stack adds explicit phases:

- `prepared`;
- `old-backed-up`;
- `new-live`;
- `committed`.

Recovery policy is conservative:

- every non-committed state chooses the old generation;
- committed state keeps new canonical and cleans stale transaction files;
- repeated recovery after cleanup is a no-op success;
- missing canonical and backup is corruption and retains the journal;
- journal paths outside the transaction directory are rejected before mutation.

### Static repairs made during review

The first stack opened the parent process by PID only after staging. If staging were slow and the parent exited, that PID could disappear or be reused before `OpenProcess`.

The current stack now opens and owns a synchronization handle before staging. The handle remains bound to that exact process even if it exits while bytes are copied.

The current stack also:

- cleans stage/journal if the first prepared journal cannot be written;
- rolls back if `old-backed-up`, `new-live`, or `committed` phase recording fails;
- closes the process handle through RAII;
- platform-gates Windows-only experiment imports.

### Recovery matrix

- `prepared`: retain old canonical, discard stage;
- `old-backed-up`: restore backup to canonical;
- `new-live` without commit: replace new canonical with old backup;
- `committed`: retain new canonical, remove backup/stage/journal;
- repeated invocation: success after cleanup;
- missing authority: fail and preserve diagnostic journal;
- escaping path: reject and preserve external file.

### Remaining design faults

- helper can still lose the parent-identity race before it opens the handle; a duplicated/inherited process handle is stronger than a PID argument;
- journal phase updates rewrite the same file in place and can themselves tear;
- journal paths have no hashes, sizes, transaction nonce verification, or canonicalization defense against path aliases/reparse points;
- directory metadata is not explicitly synced;
- recovery covers one file, not the managed installation generation.

## C. Mixed generation after finalizer failure

Owned execution-only PR: `teamleaderleo/uv#17`  
Exact head: `e8b7a3ae5bbdc2d70832985a709e9a5c97a4baf1`  
Exact base: public candidate `77e107dd2665f660c461998bc83174bf26ee7cf6`

Current runs:

- mixed-generation workflow: `30754972997`, queued;
- repository CI: `30754973056`, queued.

### Hypothesis

The candidate copies companions into live names before invoking final `uv.exe` replacement. Therefore an error at the finalizer boundary can leave old `uv.exe` with new `uvx.exe`.

### Control

The execution workflow temporarily injects an explicit current-executable path and finalizer callback into the exact candidate helper, then:

1. creates old live `uv.exe` and `uvx.exe`;
2. creates new staged `uv.exe` and `uvx.exe`;
3. runs the exact companion-copy loop;
4. injects an error at current-executable finalization;
5. asserts old live `uv.exe` plus new live `uvx.exe`.

The seam exists only in the execution workspace. The PR carries no product source and must close without merge after receipt transfer.

### Consequence

Even a perfect single-file finalizer cannot make the candidate installation coherent if companions commit first without a shared journal and rollback policy.

## D. Installer Job Object policy

Owned draft: `teamleaderleo/uv#19`  
Exact current head: `6098dab64d959f9cf40fb44bbd8d4849c3aa9239`  
Exact base: public candidate `77e107dd2665f660c461998bc83174bf26ee7cf6`

Current runs:

- strict-versus-silent policy matrix: `30755830232`, queued;
- repository CI: `30755830304`, queued.

Superseded head/run: `c9523e056abf72eeb073a93c4668e769d293f8a8` / `30755300973`.

### Source finding

uv already has a Windows `Job` abstraction with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, but `Job::new` also enables `JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK`.

Windows documentation states that under silent breakaway, descendants of associated processes are not automatically associated with the job. Microsoft explicitly notes that this policy cannot monitor the entire process tree.

Primary source:

- <https://learn.microsoft.com/windows/win32/procthread/job-objects>

### Experiment design

The experiment adds a strict job policy with kill-on-close and no breakaway flag. A gated PowerShell parent cannot spawn its child until after job assignment, eliminating the assignment race in the policy measurement.

It compares:

- existing silent-breakaway policy: assigned parent dies on job close, delayed child survives and writes marker;
- strict policy: assigned parent and inherited child die before delayed marker.

### Static repair

The current head gates Windows-only imports in the experiment binary so broad Linux all-target checks do not fail on unused imports.

### Compatibility boundary

Strict membership can break a descendant that expects to create or join an incompatible Job Object. Therefore a strict result is not automatic product authorization. The real cargo-dist PowerShell installer and its archive tools need a compatibility matrix.

## E. Strict Job integration into the official updater

Owned stacked draft: `teamleaderleo/uv#20`  
Exact current head: `1e9fb3a337393ef72729877111455835f248bb1e`  
Exact base: experiment D head `6098dab64d959f9cf40fb44bbd8d4849c3aa9239`

Maintenance merge: `teamleaderleo/uv#21`, merged solely to preserve exact ancestry after the base experiment's platform-import repair.

Current runs:

- strict updater integration: `30755883089`, queued;
- inherited Job policy workflow: `30755883092`, queued;
- repository CI: `30755883261`, pending.

The branch retains one inspectable source generator:

```text
.github/fieldwork/457-b2/inject_strict_installer_job.py
```

### Generated updater experiment

1. spawn PowerShell explicitly;
2. obtain Tokio's live Windows process handle;
3. create strict kill-on-close Job Object;
4. assign PowerShell to the job;
5. invoke a test callback after assignment;
6. wait for output while updater future owns both job and child.

The test fixture cannot spawn its delayed descendant until the post-assignment callback releases it. It then aborts and awaits the updater future and requires the delayed survival marker to remain absent.

### Workflow gates

- Ubuntu cross-target `cargo check` for the generated Windows source;
- Windows target execution for actual descendant cancellation.

### Static repairs before execution

- extracted the source transform from a workflow-only heredoc into a committed generator;
- added the Ubuntu cross-target compile lane;
- narrowed `unsafe_code` allowances to the raw-handle adapter and generated assignment helper;
- removed an unnecessary mutable child binding;
- merged the exact repaired base head;
- repaired a malformed pinned upload-action SHA found during diff review.

### Remaining production race

The gated test proves the behavior after assignment. The generated production shape still calls ordinary `spawn()` before `AssignProcessToJobObject`, leaving a small interval in which a real installer can execute and create a descendant before assignment.

A race-free product launcher should assign the Job Object during `CreateProcess` with `STARTUPINFOEX` and `PROC_THREAD_ATTRIBUTE_JOB_LIST`, or create the process suspended while retaining and resuming the primary thread handle. Ordinary spawn-then-assign cannot support an unqualified whole-tree guarantee.

See [`PROCESS_TREE.md`](./PROCESS_TREE.md) for the complete design and compatibility boundary.

## F. Repaired destructive-path carriers

These remain queued because Windows runner capacity has not started them:

| Purpose | PR | Exact head | Run |
| --- | --- | --- | --- |
| custom/GHE clean bounded completion | `teamleaderleo/uv#8` | `41fc6d53e2a2c5065743657302c4255acffa0db5` | `30754208709` |
| old exact-base actual-executable displacement | `teamleaderleo/uv#9` | `614df9998cd043a8a20547fd4ce7efb0aaf6a051` | `30754251841` |
| self-replace missing-source failure | `teamleaderleo/uv#10` | `34031835cbfe8b84edaf8e3ce5d6d846bc50d59e` | `30754221525` |

Queued means no new target conclusion.

## Promotion rules

No experiment becomes a proposal merely because it compiles or passes one synthetic control.

Promotion requires:

1. exact-head workflow completion and artifact receipt;
2. complete source diff review;
3. negative controls against old behavior;
4. ordinary-error and abrupt-exit boundaries;
5. explicit compatibility scope;
6. owner selection;
7. independent review;
8. separate authorization before any public contact.
