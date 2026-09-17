# Public PR audit — staged Windows uv self-update

## Review result

Disposition: `REPAIR`, while retaining the implementation direction.

Public target: `astral-sh/uv#20855`  
Exact head: `77e107dd2665f660c461998bc83174bf26ee7cf6`  
Exact base: `ec8ad5b7c697b9cbbb8a65c8de00fdb461f2010b`  
Last current uv head inspected: `79bbface771210df216b738e9bdc7df95e5a9e6b`  
Public upstream contact authorized/performed: `false` / `false`

The public change correctly isolates the ordinary official Windows installer. Exact repaired execution supports the narrow guarantee that cancelling during that staged installer phase keeps the actual current executable at its canonical path.

The public regression does not prove that result: it asserts an unrelated fixture, passes on exact broken old code, has a brittle one-second startup wait, and drops rather than awaits the cancelled task. The implementation also retains final self-replace, companion-file, receipt, custom-route, and process-tree limits.

## Claim review

| Public or implied claim | Review | Exact basis |
| --- | --- | --- |
| isolate official Windows installer before changing live `uv.exe` | `ACCEPT` | source ordering and repaired candidate actual-executable pass |
| proposed test proves old failure and candidate repair | `REPAIR` | exact old base passes the unrelated fixture assertion |
| interruption during staged installer keeps actual candidate executable canonical | `ACCEPT, NARROW` | repaired candidate control passed and awaited cancellation |
| every failed official update leaves canonical `uv.exe` available | `NOT ESTABLISHED` | self-replace renames old canonical before later fallible operations |
| companion executables switch as one generation | `NOT ESTABLISHED` | direct live copies are sequential and unjournaled |
| existing receipt is necessarily valid for staged release | `NOT ESTABLISHED` | temporary new receipt is discarded; old receipt retained without comparison |
| custom/GHE/base-URL routes are fixed | `FALSE` | those routes still delegate to axoupdater 0.10.0 pre-rename flow |
| direct child cancellation terminates complete installer process tree | `NOT ESTABLISHED` | `kill_on_drop` owns direct PowerShell child only |
| historical Linux cross-filesystem partial-copy mechanism remains current | `SUPERSEDED` | cargo-dist 0.31.0 destination-filesystem staging |

## Implementation direction that should remain

The candidate:

1. resolves the exact release;
2. downloads the generated installer;
3. creates temporary install and configuration prefixes;
4. runs the generated installer there with PATH modification disabled;
5. waits for success before touching the live installation.

This is the right boundary. It removes network, archive extraction, and most installer work from the live canonical executable window.

The public diff should not be rejected wholesale or duplicated by another PR.

## Test defect

The proposed test creates and asserts:

```text
temp_dir/uv.exe
```

The old code renames:

```text
std::env::current_exe()
```

The fixture is not connected to the destructive production operation. Exact old-base execution passed that assertion.

The test also uses:

```text
100 * 10 ms startup polling
task.abort()
drop(task)
release installer
```

Exact owned execution on a clean Windows runner compiled the candidate but failed at the startup assertion before cancellation. A later repaired control used a 30-second bound, checked early task completion, awaited the cancelled `JoinHandle`, and inspected the actual current executable; that control passed.

Required replacement test:

- exercise `std::env::current_exe()` or an explicitly injectable canonical path;
- give PowerShell a realistic bounded startup window;
- stop and report early task completion;
- await cancellation and assert the cancelled join result;
- run the exact same control on old base and candidate;
- avoid inherited handles that keep deliberately blocked descendants alive.

## Final replacement defect

The exact self-replace 1.5.0 Windows implementation:

1. canonicalizes current executable;
2. renames it to a relocated path;
3. schedules deletion of the relocated file;
4. copies replacement into a destination-side temporary file;
5. renames the temporary file to canonical.

Every step after the destructive old rename can fail. No rollback restores the old canonical name.

Therefore the PR body should either:

- narrow its guarantee to the staged installer phase; or
- add a safer finalizer with ordinary-error rollback and abrupt-exit recovery authority.

Owned failure carrier `teamleaderleo/uv#10` is repaired at `34031835cbfe8b84edaf8e3ce5d6d846bc50d59e`; run `30754221525` was queued at the latest record. The previous run is harness-only because PowerShell rejected its invocation before the helper launched.

## Companion commit defect

After the isolated installer succeeds, `replace_from_temporary_install` copies every non-current entry directly into the live directory, then calls self-replace for `uv.exe`.

This allows:

- partial live companion bytes if interruption occurs during copy;
- one new companion followed by a later locked-file failure;
- new `uvx.exe` or `uvw.exe` with old `uv.exe`;
- final self-replace failure after companions already changed;
- no rollback and no record of changed files.

The repair must not depend on detecting whether `uvx` or `uvw` is running. File-state staging and recovery ownership are required.

A proper complete-generation design should stage every managed file and the receipt on the destination filesystem, record a prepared transaction, commit per-file renames, mark committed only after every live file is new, and recover any non-committed state to the old generation.

## Receipt defect

The candidate runs the staged installer with a temporary configuration root. The generated new receipt is discarded with that temporary directory. The existing receipt remains live.

That is safe only if all relevant fields are proven equivalent:

- install prefix and layout;
- managed binary/library set;
- aliases;
- source/provider;
- schema;
- PATH modification policy.

The clearer transaction model is to stage and commit the new receipt last. Retaining the old receipt is an optimization requiring explicit comparison, not an implicit guarantee.

## Custom/GHE route defect

The official staged path is bypassed for custom receipt sources and GitHub/GHE installer-base overrides. Those routes call axoupdater 0.10.0, which on Windows:

1. downloads the installer;
2. renames current executable to `.previous.exe`;
3. runs the installer against the live prefix;
4. restores only after an ordinary returning failure.

Process interruption can bypass restoration.

An exact copied-uv integration test observed canonical `uv.exe` absent and `.previous.exe` present on this route. Its workflow tail remained alive because the intentionally blocked descendant inherited output handles. The repaired head `41fc6d53e2a2c5065743657302c4255acffa0db5`, run `30754208709`, removes that harness leak and was queued at the latest record.

This route needs an explicit ownership decision:

- uv-owned staged behavior for every compatible uv installer;
- an axoupdater staged-install capability;
- or fail-closed Windows behavior for unsafe custom routes until staging exists.

## Direct-child versus process-tree cancellation

`Command::kill_on_drop(true)` is valuable, but it is a direct-child contract. The real PowerShell installer can invoke archive tools or other descendants.

A complete process-tree guarantee requires a Windows Job Object or an installer contract that prevents detached descendants. The simple loop test must not be described as proving real-installer descendant cleanup.

## Internal code experiment

`teamleaderleo/uv#14@ef509a215af602cbc904aed467b4ac5edd66f827` prototypes a deferred finalizer:

- stage and sync complete replacement bytes beside canonical while old executable remains live;
- write a prepared journal;
- wait for parent PID exit;
- rename old canonical to backup;
- rename stage to canonical;
- restore backup on ordinary injected failure;
- clean transaction files.

Its workflow matrix is run `30754411464`, queued at the latest record. It is an internal experiment, not a competing upstream PR.

It still lacks:

- next-run recovery after power loss;
- full managed-binary/receipt generation handling;
- uv CLI integration;
- real installer descendant ownership.

## Requested repair sequence

1. Replace the public regression with the exact actual-executable old/candidate control.
2. Retain the staged installer implementation.
3. Narrow the public claim to the installer phase unless final replacement is repaired.
4. Add final self-replace failure controls.
5. Stage companions beside their destinations rather than copying into live names.
6. Choose rollback or durable recovery policy for partial multi-file commit.
7. Reconcile the receipt explicitly.
8. State that custom/GHE routes are outside the current fix or repair them separately.
9. State the direct-child cancellation boundary.

## Current execution surfaces

See [`EXECUTION.md`](./EXECUTION.md) for exact historical artifacts, repaired heads, queued runs, and evidence promotion rules.

## Final audit disposition

`REPAIR — retain architecture, replace evidence, narrow claims, and route remaining transaction work explicitly.`

No public comment, review, reaction, branch, issue, or pull request was created or modified by this audit.
