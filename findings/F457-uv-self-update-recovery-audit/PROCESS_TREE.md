# Windows installer process-tree ownership

## Question

Does cancelling `uv self update` terminate only the direct PowerShell installer process, or every descendant that can continue mutating staging or install state?

Public upstream contact authorized/performed: `false` / `false`.

## Current public source behavior

The public candidate uses Tokio `Command::kill_on_drop(true)`. That owns the direct child returned by Tokio.

uv also has `uv_windows::Job`, configured with:

- `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`;
- `JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK`.

The second flag is decisive. Microsoft documents that descendants are not automatically associated when silent breakaway is enabled and that a tool using that policy cannot monitor the complete process tree.

Primary source:

- <https://learn.microsoft.com/windows/win32/procthread/job-objects>

The existing Job helper therefore cannot support a whole-generated-installer-tree guarantee.

## Experiment 1 — strict versus silent breakaway

Owned draft: `teamleaderleo/uv#19`  
Exact source head: `6098dab64d959f9cf40fb44bbd8d4849c3aa9239`  
Exact base: public candidate `77e107dd2665f660c461998bc83174bf26ee7cf6`

Completed exact execution:

```text
run: 30755788490
job: 91517588607
conclusion: success
artifact: 8837070751
digest: sha256:ef0f8df1cae24898ad18abafef046d473b2fd3b47d72db96cebd212e18813998
```

The fixture spawns a PowerShell parent but prevents it from creating its delayed child until after Job assignment. This removes the ordinary spawn/assignment timing ambiguity from the policy comparison.

Observed result:

| Policy | Parent after Job close | Delayed descendant marker |
| --- | --- | --- |
| current silent breakaway | terminated | written; descendant survived |
| strict inherited tree | terminated | absent; descendant terminated |

This proves the policy distinction. It is not automatic product authorization. Preventing all breakaway can fail when a descendant requires an incompatible Job Object.

Later workflow generations on the stacked integration branch may retrigger the policy workflow with stale file-fence assumptions. Do not replace the successful exact receipt above with those harness failures.

## Experiment 2 — direct updater integration

Owned stacked draft: `teamleaderleo/uv#20`  
Exact base: experiment 1 head `6098dab64d959f9cf40fb44bbd8d4849c3aa9239`  
Current integration head: `792d787e8020498b905c317aa2bd714b601f2c7c`

Current focused workflow:

```text
run: 30852078064
state at this update: queued
ordinary CI: 30852078362 — pending at this update
```

The branch retains one inspectable source generator:

```text
.github/fieldwork/457-b2/inject_strict_installer_job.py
```

The generated updater experiment:

1. spawns PowerShell explicitly;
2. obtains Tokio's live Windows process handle;
3. creates a strict kill-on-close Job Object;
4. assigns PowerShell to the Job;
5. invokes a test callback after assignment;
6. waits for output while the updater future owns both Job and child.

The test fixture cannot spawn its delayed descendant until the post-assignment callback releases it. It then aborts and awaits the updater future and requires the delayed survival marker to remain absent.

Tokio documents `Child::raw_handle()` as returning the live Windows process handle while the child is running:

- <https://docs.rs/tokio/latest/tokio/process/struct.Child.html#method.raw_handle>

### Superseded first integration run

Run `30755883089` did not produce a process-tree result.

It established two carrier/source blockers:

- rustfmt was not installed on either execution path;
- the `Job` owner stored a raw `windows::HANDLE`, so the Job remained non-`Send` across `wait_with_output().await` and a `tokio::spawn` test could not compile.

The Windows job reached the concrete compiler diagnostic before the test ran. The Ubuntu cross-check stopped earlier at the missing formatter. Artifact `8837221189` retains the Windows receipt.

### Current ownership repair

The initial thought was an explicit `unsafe impl Send`. Complete review rejected that as the owner model.

The current branch instead uses conditional representation:

- under the `std` feature, `Job` stores `std::os::windows::io::OwnedHandle`;
- `OwnedHandle` supplies single ownership, automatic close, and standard-library thread mobility;
- under `no_std`, `Job` retains the existing raw `HANDLE` and explicit `Drop` implementation;
- no manual `Send` or `Sync` implementation is added.

The Ubuntu cross-check now requires both:

```text
cargo check -p uv-windows --no-default-features --target x86_64-pc-windows-msvc
cargo check -p uv --all-targets --features self-update --target x86_64-pc-windows-msvc
```

Both runner paths install rustfmt before formatting.

This is still experiment infrastructure. It does not establish strict Job compatibility with the real installer or a race-free production launch boundary.

## Remaining creation race

The test eliminates the race through a cooperative post-assignment gate. The proposed generated production code does not: it calls `spawn()` and then assigns the returned process handle.

A real installer can execute before assignment and can create a descendant during that interval. Faster assignment is not a correctness boundary.

## Race-free process creation options

### Preferred modern Windows route: Job assignment at creation

Windows supports `PROC_THREAD_ATTRIBUTE_JOB_LIST` through `STARTUPINFOEX` and `UpdateProcThreadAttribute`. Job handles in this list are assigned as part of process creation. Supported on Windows 10+ and Windows Server 2016+.

Primary source:

- <https://learn.microsoft.com/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute>

Conceptual sequence:

1. create the strict update Job;
2. construct a process attribute list containing the Job handle;
3. call `CreateProcessW` with `EXTENDED_STARTUPINFO_PRESENT`;
4. child begins already associated;
5. wrap process and pipe handles for asynchronous collection;
6. close the Job on cancellation.

Costs:

- custom Windows process launcher;
- exact Windows command-line quoting and mutable buffer ownership;
- explicit environment-block construction;
- explicit pipe and handle-inheritance allowlist;
- Windows version policy;
- integration with Tokio wait and output collection.

### Fallback: suspended creation, assign, resume

`CREATE_SUSPENDED` starts the primary thread suspended. `ResumeThread` begins execution after assignment.

Primary sources:

- <https://learn.microsoft.com/windows/win32/procthread/process-creation-flags>
- <https://learn.microsoft.com/windows/win32/api/processthreadsapi/nf-processthreadsapi-resumethread>

Standard and Tokio `Command` expose the process handle but not the primary thread handle needed to resume. This route also requires a custom launcher or additional native handle plumbing.

### Rejected as a race-free guarantee: ordinary spawn then immediate assignment

This remains useful for the controlled experiment and may reduce orphan risk, but it cannot support a race-free full-tree claim.

## Real cargo-dist installer subprocess surface

The pinned PowerShell template primarily uses in-process PowerShell and .NET operations:

- WebClient download;
- `Expand-Archive` for zip;
- `Copy-Item`, `Remove-Item`, receipt write, registry and PATH operations.

For tar archives it invokes external `tar xf`; under strict inherited membership that child should remain supervised unless it explicitly breaks away or attempts an incompatible Job.

No `Start-Process` occurrence was found in the inspected cargo-dist installer template. This reduces but does not eliminate compatibility risk: generated templates can change, enterprise wrappers can differ, and custom or GHE routes may use different installers.

## Required compatibility matrix

Before strict Job ownership can become product source:

1. exact generated uv PowerShell installer using zip and `Expand-Archive`;
2. tar path where applicable;
3. Windows PowerShell 5.1 and supported PowerShell Core;
4. antivirus, indexer, and file-lock environments;
5. nested outer Job environments such as CI and enterprise launchers;
6. custom and GHE installer routes separately;
7. descendant that deliberately attempts its own Job Object;
8. cancellation during download, extraction, copy, receipt write, and PATH mutation;
9. exact stdout/stderr capture and error propagation;
10. no orphan process after updater-future cancellation.

## Product shape if compatible

A product implementation should not expose the test callback seam. Preferred internal abstraction:

```text
spawn_installer_in_update_job(command) -> SupervisedAsyncChild
```

Responsibilities:

- race-free Job assignment during process creation;
- strict inherited-tree policy;
- explicit handle inheritance;
- asynchronous output collection;
- kill-on-drop cancellation;
- exact creation and assignment errors;
- no hidden detached-descendant allowance.

`execute_official_installer` would own one supervised child and wait for output.

## Current disposition

`EXECUTE / DESIGN`

- direct-child cancellation: present;
- whole-tree guarantee with current silent-breakaway Job: false by construction and execution;
- strict policy synthetic discriminator: complete and positive;
- strict updater integration with gated descendant: queued at exact current head `792d787e...`;
- `std` handle ownership: represented by `OwnedHandle`, execution pending;
- `no_std` compatibility: explicit Windows cross-check queued;
- race-free production launcher: design only;
- real generated-installer compatibility: unexecuted.

No public upstream issue, comment, review, reaction, branch, pull request, or message was created or modified by this work.
