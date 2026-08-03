# Strict updater Job integration — target-native receipt

Date: 2026-08-03  
Disposition: `TARGET-NATIVE CONTROL PASSED; CROSS-CHECK AND PRODUCT DESIGN REMAIN OPEN`  
External contact authorized/performed: `false` / `false`

## Exact identities

```text
controlled repository: teamleaderleo/uv
controlled PR: #20
branch: experiment/457-b2-official-installer-job
requested source head: 792d787e8020498b905c317aa2bd714b601f2c7c
generated PR merge tested: 9865b4f46ed0cc4fb66d39aaa195d3651cbccd75
strict policy base: 6098dab64d959f9cf40fb44bbd8d4849c3aa9239
public candidate base: 77e107dd2665f660c461998bc83174bf26ee7cf6
workflow run: 30852078064
Windows job: 91814229144
job conclusion: success
artifact: 8871457657
artifact digest: sha256:aa81a5dfafb179f882a210e7da474515d6cdf46d051b82940b62a248f30bf7b2
```

Artifact files:

```text
identity.txt
receipt.json
injected-source.diff
test.log
rust-version.txt
cargo-version.txt
```

## Executed boundary

The generated updater experiment:

1. spawned PowerShell;
2. obtained Tokio's live process handle;
3. created a strict kill-on-close Job Object without silent breakaway;
4. assigned PowerShell to the Job;
5. invoked a test callback after assignment;
6. released the fixture so PowerShell could spawn a delayed descendant;
7. aborted and awaited the updater future;
8. required the descendant's delayed survival marker to remain absent.

The fixture's post-assignment gate removes the ordinary spawn/assignment race from this control.

## Result

The target-native test compiled and passed:

```text
commands::self_update::tests::fieldwork_strict_installer_job_terminates_spawned_descendant_on_cancellation ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 43 filtered out
```

Observed contract:

```text
assignment boundary: release descendant only after strict Job assignment callback
cancellation boundary: abort updater future; Job and direct child drop together
expected observation: spawned PowerShell descendant cannot write delayed survival marker
result: passed
```

This establishes that the strict Job integration can retain the Job across the asynchronous wait and terminate the gated inherited descendant when the updater future is cancelled.

## Ownership representation

The tested `std` representation used `std::os::windows::io::OwnedHandle`:

- single ownership;
- automatic close;
- standard-library thread mobility;
- no manual `Send` or `Sync` implementation.

The `no_std` representation remains the existing raw `HANDLE` plus explicit `Drop`.

The successful receipt contained one unused import and three locally explainable unsafe-code warnings. Current controlled head `d93f31c8deba64a52a2e8e49f8e70e3c29bb4167` cfg-gates the no-std closer and locally documents/allows only the constructor and standard-child assignment blocks. Behavior is unchanged.

Fresh warning-clean runs:

```text
focused strict integration: 30853540708 — queued at last check
lower-level ownership workflow: 30853540671 — queued at last check
ordinary fork CI: 30853541009 — pending at last check
```

The focused cross-check now requires both:

```text
cargo check -p uv-windows --no-default-features --target x86_64-pc-windows-msvc
cargo check -p uv --all-targets --features self-update --target x86_64-pc-windows-msvc
```

No result is claimed from those fresh runs yet.

## What this does not prove

This result does not close the production process-creation race. The generated production experiment still performs ordinary `spawn()` followed by Job assignment. An installer can execute or spawn a descendant before assignment.

A product whole-tree guarantee requires a race-free launcher, such as:

- `CreateProcessW` with `STARTUPINFOEX` and `PROC_THREAD_ATTRIBUTE_JOB_LIST`; or
- suspended creation with retained primary-thread handle, Job assignment, and explicit resume.

The result also does not prove compatibility with:

- the exact generated cargo-dist installer across all supported routes;
- tar extraction subprocesses;
- nested CI or enterprise Job Objects;
- descendants that deliberately create incompatible Job Objects;
- cancellation at each installer mutation phase.

## Next action

1. classify the warning-clean no-std/full cross-check;
2. retain its artifact/log identity;
3. keep the target-native passing receipt even if a later carrier generation fails;
4. design a race-free process creation abstraction before proposing product source;
5. run the real generated-installer compatibility matrix before any public routing.

No canonical upstream issue, pull request, review, comment, reaction, email, or message was created or modified.
