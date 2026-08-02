# Windows installer process-tree ownership

## Question

Does cancelling `uv self update` terminate only the direct PowerShell installer process, or every descendant that can continue mutating the staging/install state?

Public upstream contact authorized/performed: `false` / `false`.

## Current source behavior

The public candidate sets Tokio `Command::kill_on_drop(true)`. That owns the direct child returned by Tokio.

uv also has `uv_windows::Job`, configured with:

- `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`;
- `JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK`.

The second flag is decisive. Microsoft documents that child processes of an associated process are not automatically associated when silent breakaway is enabled, and states that a tool using this policy cannot monitor the entire process tree.

Primary source:

- <https://learn.microsoft.com/windows/win32/procthread/job-objects>

Therefore the existing Job helper cannot be cited as a full generated-installer tree guarantee without a different policy.

## Experiment 1 — strict versus silent breakaway

Owned draft: `teamleaderleo/uv#19`  
Exact head: `6098dab64d959f9cf40fb44bbd8d4849c3aa9239`  
Exact base: public candidate `77e107dd2665f660c461998bc83174bf26ee7cf6`  
Current workflow: `30755830232`, queued at latest review

Superseded execution head/run: `c9523e056abf72eeb073a93c4668e769d293f8a8` / `30755300973`.

The current head gates Windows-only imports so broad Linux all-target checks do not fail before the Windows experiment runs.

The experiment adds `Job::new_strict_tree`, retaining kill-on-close but omitting silent breakaway.

A PowerShell parent is spawned but cannot create its child until after job assignment. This removes the usual spawn/assignment timing ambiguity.

Expected result:

| Policy | Parent after job close | Delayed descendant marker |
| --- | --- | --- |
| current silent breakaway | terminated | written; descendant escaped |
| strict inherited tree | terminated | absent; descendant terminated |

This is a policy discriminator, not product authorization. Microsoft also documents that preventing all breakaway can cause failure when a descendant expects to associate itself or another child with an incompatible Job Object.

## Experiment 2 — direct updater integration

Owned stacked draft: `teamleaderleo/uv#20`  
Exact current head: `1e9fb3a337393ef72729877111455835f248bb1e`  
Exact base: experiment 1 head `6098dab64d959f9cf40fb44bbd8d4849c3aa9239`

Current workflow: `30755883089`, queued at latest review.  
Current broad CI: `30755883261`, pending.

Superseded integration heads/runs are retained in the PR history; they must not be used as current receipts.

The branch retains one inspectable source generator:

```text
.github/fieldwork/457-b2/inject_strict_installer_job.py
```

The generated updater experiment:

1. spawns PowerShell explicitly;
2. obtains Tokio's live Windows process handle;
3. creates strict kill-on-close Job Object;
4. assigns PowerShell to Job;
5. invokes test callback after assignment;
6. waits for output while updater future owns both Job and child.

Tokio documents `Child::raw_handle()` as returning live Windows process handle while child is running:

- <https://docs.rs/tokio/latest/tokio/process/struct.Child.html#method.raw_handle>

The test fixture cannot spawn its delayed descendant until post-assignment callback releases it. It then aborts and awaits updater future and requires delayed survival marker to remain absent.

Workflow has two gates:

- Ubuntu cross-target `cargo check` for generated Windows code;
- Windows target execution for real process-tree behavior.

### Static repairs before execution

- extracted source transform from workflow-only heredoc into committed patch generator;
- added Ubuntu cross-target compile lane;
- gated inherited Windows-only experiment imports;
- merged exact repaired base head into stack through maintenance PR `teamleaderleo/uv#21`;
- narrowed `unsafe_code` allowances to raw-handle adapter and generated assignment helper;
- removed unnecessary mutable binding;
- repaired malformed pinned receipt-uploader SHA found during diff review.

## Remaining creation race

The test eliminates race by using cooperative gate. Proposed generated production code does not: it calls `spawn()` and then assigns returned process handle.

A real installer can execute before assignment and could create descendant during this interval. Faster assignment is not correctness boundary.

## Race-free process creation options

### Preferred modern Windows route: job assignment at creation

Windows supports `PROC_THREAD_ATTRIBUTE_JOB_LIST` through `STARTUPINFOEX` and `UpdateProcThreadAttribute`. Job handles in this list are assigned to child as part of process creation. Supported on Windows 10+ and Windows Server 2016+.

Primary source:

- <https://learn.microsoft.com/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute>

This is strongest conceptual fit:

1. create strict update Job;
2. construct process attribute list containing Job handle;
3. call `CreateProcessW` with `EXTENDED_STARTUPINFO_PRESENT`;
4. child begins already associated;
5. wrap process/stdout/stderr handles for asynchronous collection;
6. close Job on cancellation.

Costs:

- custom Windows process launcher;
- correct command-line quoting and mutable buffer;
- explicit environment block handling;
- explicit pipe/handle inheritance allowlist;
- Windows version policy;
- integration with Tokio wait/output collection.

### Fallback: suspended creation, assign, resume

`CREATE_SUSPENDED` starts primary thread suspended; `ResumeThread` begins execution after assignment.

Primary sources:

- <https://learn.microsoft.com/windows/win32/procthread/process-creation-flags>
- <https://learn.microsoft.com/windows/win32/api/processthreadsapi/nf-processthreadsapi-resumethread>

Standard/Tokio `Command` exposes process handle but not primary thread handle needed to resume. Therefore this still requires custom launcher or additional native handle plumbing.

### Rejected: ordinary spawn then immediate assignment

Useful experiment and potentially acceptable optimization, but cannot support a race-free full-tree claim.

## Real cargo-dist installer subprocess surface

The pinned PowerShell template uses mostly in-process PowerShell/.NET operations:

- WebClient download;
- `Expand-Archive` for zip;
- `Copy-Item`, `Remove-Item`, receipt write, registry/PATH operations.

For tar archives it invokes external `tar xf`; under strict Job inheritance, that child should remain supervised unless it explicitly breaks away or joins incompatible Job.

No `Start-Process` occurrence was found in current cargo-dist installer template search. This reduces but does not eliminate compatibility risk: shell cmdlets and external tools can change, enterprise wrappers can differ, and custom/GHE routes may use arbitrary generated installers.

## Required compatibility matrix

Before strict Job ownership can become product source:

1. exact generated uv PowerShell installer with `.zip`/`Expand-Archive`;
2. tar path where applicable;
3. Windows PowerShell 5.1 and supported PowerShell Core behavior;
4. antivirus/indexer/file-lock environment;
5. nested outer Job environment such as CI and enterprise launchers;
6. custom/GHE installer paths separately;
7. descendant that deliberately tries own Job Object;
8. cancellation during download, extraction, copy, receipt write, and PATH mutation;
9. exact stdout/stderr capture and error propagation;
10. no orphan process after updater future cancellation.

## Product shape if compatible

A product implementation should avoid public test callback seam. Preferred internal abstraction:

```text
spawn_installer_in_update_job(command) -> SupervisedAsyncChild
```

Responsibilities:

- race-free assignment at creation;
- strict inherited-tree policy;
- explicit handle inheritance;
- asynchronous output collection;
- kill-on-drop cancellation;
- exact assignment/creation errors;
- no hidden detached descendant allowance.

`execute_official_installer` then owns one supervised child and waits for output.

## Current disposition

`EXECUTE / DESIGN`

- direct-child cancellation: present;
- whole-tree guarantee with current Job policy: false by construction;
- strict policy synthetic discriminator: queued at exact current head;
- strict updater integration with gated descendant: queued at exact current head;
- cross-target generated-source compile: queued in current integration workflow;
- race-free production launcher: design only;
- real generated-installer compatibility: unexecuted.

No public upstream issue, comment, review, reaction, branch, pull request, or message was created or modified by this work.
