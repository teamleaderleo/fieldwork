# Ownership and contribution routing

## In simple words

The observed failures do not have one owner.

uv decides which updater route runs, supplies the official staged-install flow, commits companion binaries, and owns the public regression. self-replace implements the final running-executable swap used by that flow. axoupdater implements the older custom/GHE route that still renames the canonical executable before launching the installer. cargo-dist generates the multi-file installer and receipt logic.

Trying to fix all of this in one uv pull request would blur distinct contracts and compatibility risks. The work should be routed as a small uv repair, a self-replace recovery primitive, and an axoupdater staging/capability change, with cargo-dist involved only if installation-wide journal recovery is selected.

## Ranked contribution units

### 1. uv — repair public Windows staged-update evidence and claims

**State:** `READY TO MATERIALIZE AFTER RECEIPTS`

**Scope:**

- retain the staged official-Windows installer direction from public PR 20855;
- replace the non-discriminating regression with an actual-current-executable test;
- use a robust bounded wait and await cancellation completion;
- add a final-replacement failure test;
- state explicitly that custom/GHE routes are not changed;
- avoid claiming installation-wide atomicity or coherence.

**Why uv owns it:** the routing, child process, temporary install, companion commit, and test live in `crates/uv/src/commands/self_update.rs`.

**Proposed title:**

```text
fix(self-update): validate Windows staged replacement at the real executable boundary
```

**Proposed changed-file fence:**

```text
crates/uv/src/commands/self_update.rs
```

Potential integration test additions should remain separate unless they exercise the custom route.

### 2. self-replace — restore or recover after failed Windows replacement

**State:** `ISSUE FIRST / SOURCE CANDIDATE AFTER EXACT FAILURE RECEIPT`

**Scope:**

- copy and validate the replacement into a destination-side temporary path before moving the old executable;
- preserve a backup until the new canonical path is durable;
- roll back ordinary errors;
- use a surviving helper or durable marker to restore after parent death between renames;
- schedule old-backup deletion only after commit;
- add exact missing-source, access-denied, final-rename, and interrupted-parent controls.

**Why self-replace owns it:** uv calls the library specifically to obtain a Windows-safe final replacement primitive. The library currently renames the canonical executable before later fallible operations and provides no rollback.

**Proposed issue title:**

```text
Windows self_replace can leave the canonical executable missing after a later error
```

**Issue draft:**

```text
On Windows, self_replace currently renames the running executable to a relocated path, schedules deletion of that path, and only then copies the replacement to a destination-side temporary file and renames it to the canonical path.

Any failure after the initial rename—cleanup-helper setup, replacement copy, final rename, or process termination—can return or exit with the canonical executable absent. The old executable may also already be scheduled for deletion.

A safer contract would fully stage the replacement beside the destination before moving the old executable, retain a backup until commit, restore on ordinary error, and use a surviving helper or durable recovery marker for process death between renames.

A minimal regression can run a copied helper executable, call self_replace with a nonexistent replacement source, and assert that an error does not remove the helper's canonical path.
```

### 3. axoupdater — add a staged Windows installer capability

**State:** `ISSUE FIRST`

**Scope:**

- do not rename the current executable before executing a potentially long generated installer;
- where the installer supports destination override, install into an isolated staging prefix;
- return a staged-install result or call a caller-supplied finalizer;
- preserve receipt and PATH semantics;
- make cancellation/process death recoverable;
- expose capability/opt-in rather than assuming every arbitrary installer supports staging.

**Why axoupdater owns it:** uv custom-source and GHE/base-URL routes still call axoupdater 0.10.0, and other consumers may share the same pre-rename failure window.

**Proposed issue title:**

```text
Support staged Windows updates without pre-renaming the running executable
```

**Issue draft:**

```text
The Windows run path renames std::env::current_exe() to .previous.exe before launching the generated installer. It restores that file only when installer execution returns an ordinary failure.

Cancellation, parent termination, power loss, or a dropped execution can bypass restoration and leave the canonical command absent while the previous executable remains under a noncanonical name.

Generated cargo-dist installers already accept a forced install prefix. A capability-gated Windows flow could install into an isolated prefix first and defer live replacement to a finalizer after staging succeeds. The finalizer still needs a recoverable replacement primitive and receipt handling.

The change should be opt-in or capability-based because axoupdater can execute arbitrary installers whose staging behavior is unknown.
```

### 4. cargo-dist — installation-wide recoverability

**State:** `HOLD UNLESS MULTI-FILE COHERENCE IS SELECTED`

**Scope:**

- destination-side stage all binaries and receipt on Windows as well as Unix;
- use a durable prepared/committed journal;
- recover or finish after interruption;
- make recovery idempotent;
- retain bounded cleanup records.

**Why this is optional:** the immediate uv issue only requires canonical `uv.exe` availability. Installation-wide old/new generation coherence is a stronger contract. It should not silently expand the first repair.

The Unix generator already includes the v0.31.0 destination-filesystem staging improvement from cargo-dist PR 2261. That work should be treated as prior art, not duplicated.

## Rejected routing

### One giant uv patch

Rejected because it would combine:

- public PR review repair;
- generic replacement-library behavior;
- generic updater capability;
- generated installer transaction semantics;
- receipt compatibility.

Those surfaces have different owners and release cadences.

### Only patch the public test

Insufficient. The test is defective, but exact source inspection independently establishes final self-replace and custom-route gaps.

### Only patch self-replace

Insufficient. It would not fix direct companion copies, receipt handling, or axoupdater's long pre-installer rename window.

### Only detect running uvx/uvw processes

Rejected by both mechanism and maintainer guidance. Detection is incomplete, races immediately, and does not cover interruption, disk errors, receipt state, or non-process locks.

## Authority

These are internal drafts and routing decisions. No public issue, comment, review, reaction, pull request, or message has been created. Public upstream interaction requires explicit user authorization for the exact destination and text.
