# Ownership and contribution routing

## Summary

The self-update failures span four owners:

- **uv** chooses the route, owns the official staged flow, copies companions, decides receipt handling, and owns the public regression;
- **self-replace** owns the final Windows running-executable swap used by the public candidate;
- **axoupdater** owns the custom/GHE path that still pre-renames the running executable;
- **cargo-dist** generates installer and receipt behavior for the managed file set.

Do not force these into one public patch. The immediate occupied uv direction should receive a focused evidence/claim repair. Final single-file recovery, generic updater staging, and managed-generation recovery should remain separately reviewable.

Public upstream contact authorized/performed: `false` / `false`.

## Route 1 — uv public candidate evidence and scope

State: `REPAIR EXISTING DIRECTION; DO NOT DUPLICATE`

Public lane: `astral-sh/uv#20855@77e107dd2665f660c461998bc83174bf26ee7cf6`.

uv owns:

- official/custom route selection;
- isolated temporary install/config prefixes;
- direct PowerShell child lifetime;
- companion copy loop;
- receipt policy;
- proposed regression.

Required bounded repair:

1. replace unrelated fixture assertion with actual-current-executable old/candidate controls;
2. use realistic bounded startup and await completed cancellation;
3. narrow claims to the official staged-installer phase unless final replacement is repaired;
4. state custom/GHE exclusion;
5. add final replacement failure characterization;
6. make companion/receipt limits visible rather than calling the installation atomic.

Possible title for an internal successor only if the public lane stops or maintainers ask for a revision:

```text
fix(self-update): validate staged Windows replacement at the canonical executable boundary
```

Expected primary file:

```text
crates/uv/src/commands/self_update.rs
```

No public successor should be created while PR 20855 remains active without explicit coordination authority.

## Route 2 — deferred Windows single-file finalizer

State: `INTERNAL EXPERIMENT / EXECUTE`

Owned experiment: `teamleaderleo/uv#14@ef509a215af602cbc904aed467b4ac5edd66f827`.

The experiment moves destructive authority out of the updating process:

- fully stage and sync replacement beside canonical while old executable remains runnable;
- write a prepared journal;
- wait for parent exit;
- commit with backup and same-directory renames;
- roll back ordinary errors.

This is currently implemented in `uv-windows` because the fork already has Windows process APIs and the experiment can be run end to end. That does not settle the eventual public owner.

Promotion conditions:

- hostile matrix passes at one exact head;
- a separate invocation recovers every prebuilt interrupted journal state idempotently;
- process wait/error semantics are reviewed;
- journal paths cannot escape the intended install directory;
- stage and canonical identity/hashes are verified;
- directory durability limitations are documented.

Potential eventual owner choices:

- **self-replace**, if this becomes a general safe replacement primitive;
- **uv/uv-windows**, if it depends on uv-specific installation and receipt policy.

Do not submit the experiment publicly as written.

## Route 3 — self-replace ordinary and abrupt failure recovery

State: `ISSUE FIRST AFTER EXACT FAILURE RECEIPT`

Source consequence: self-replace 1.5.0 renames canonical current executable before cleanup scheduling, replacement copy, and final rename. It has no rollback.

Exact failure carrier:

- owned PR `teamleaderleo/uv#10`;
- repaired head `34031835cbfe8b84edaf8e3ce5d6d846bc50d59e`;
- run `30754221525` queued at last record.

A clean target receipt should establish the missing-source case before any external issue draft is considered execution-backed.

Internal issue title:

```text
Windows self_replace can leave the canonical executable missing after a later error
```

Minimum desired contract:

- stage replacement before destructive rename;
- retain backup until commit;
- restore ordinary failures;
- expose or own abrupt-exit recovery;
- schedule deletion only after commit authority exists.

The missing-source control is necessary but not sufficient. Access-denied, cleanup-helper failure, final-rename failure, and process-death boundaries remain.

## Route 4 — axoupdater custom/GHE staging capability

State: `ISSUE FIRST / OWNER DECISION`

Exact source: `axodotdev/axoupdater@122313e5b119f0f7f1aa02b95bd13d10b37637ff`.

Exact owned uv characterization observed canonical absence and `.previous.exe` presence on the custom/GHE route. A repaired clean-completion run remains queued at `teamleaderleo/uv#8@41fc6d53e2a2c5065743657302c4255acffa0db5`, run `30754208709`.

Possible approaches:

### A. Capability-gated staged install in axoupdater

- installer declares forced-prefix/staging support;
- axoupdater runs it outside live installation;
- caller or library finalizer commits afterward;
- receipt/PATH behavior is preserved.

### B. uv owns staged behavior for compatible custom routes

- uv recognizes receipts/installers it can safely stage;
- all compatible uv routes use one uv finalizer;
- unknown installers retain current behavior or fail closed by policy.

### C. Fail closed on unsafe Windows custom self-update

- refuse routes that require destructive pre-rename;
- provide a clear alternative update instruction.

This is safest mechanically but can regress enterprise workflows and requires maintainer policy.

Do not assume every arbitrary axoupdater installer supports staging. A capability/API boundary is required.

## Route 5 — cargo-dist managed-generation recovery

State: `HOLD / ISSUE-FIRST ARCHITECTURE`

The immediate command-availability defect does not require a full multi-file protocol. The broader installation can still become mixed, and cargo-dist is the natural generator owner if a reusable solution is selected.

Desired properties:

- destination-local stage for every binary/library/alias/receipt;
- manifest with expected old/new identities;
- durable prepared and committed phases;
- per-file backup and live rename records;
- idempotent rollback or finish after interruption;
- receipt committed last;
- bounded cleanup independent of commit result.

Prior art:

- cargo-dist 0.31.0 already stages Unix bytes on the destination filesystem before final renames;
- do not reopen the historical cross-filesystem partial-copy patch;
- retain only multi-file generation coherence and Windows direct-copy behavior.

## Process-tree ownership

State: `RETAIN AS SEPARATE TEST/DESIGN BOUNDARY`

Tokio `kill_on_drop(true)` owns the direct PowerShell child. Real installers may launch descendants. A strong interruption guarantee needs:

- Windows Job Object ownership; or
- a generator contract forbidding detached descendants; or
- explicit descendant handles and completion receipts.

This should not be hidden inside a file-transaction patch.

## Ranked continuation

1. Complete the repaired old/candidate, custom-route, and self-replace executions.
2. Make the internal deferred finalizer matrix pass.
3. Add idempotent recovery-from-journal controls.
4. Review public PR 20855 internally with narrow accepted claim and explicit exclusions.
5. Decide self-replace versus uv ownership for final single-file recovery.
6. Decide uv versus axoupdater ownership for custom-route staging.
7. Open managed-generation design only after locked companion and partial-commit controls make the policy concrete.

## Rejected routing

### One giant uv patch

Rejected because it combines route selection, generic replacement, generic updater capability, generated installer semantics, receipt policy, and process-tree shutdown.

### Test-only repair as full closure

Rejected. The public test needs repair, but source and target evidence independently retain custom-route and final replacement windows.

### self-replace-only repair as full closure

Rejected. It cannot fix companions, receipt handling, or the long axoupdater installer window.

### Process enumeration for uvx/uvw

Rejected. It races, misses non-process locks, and does not solve interruption, disk failure, or receipt state.

### Unqualified “atomic update” claim

Rejected. Ordinary filesystems do not atomically switch the managed file set. The stronger implementable promise is deterministic recoverability.

## Authority

All titles and issue text are internal planning artifacts. No public issue, comment, review, reaction, pull request, branch, or message has been created or modified by this lane.
