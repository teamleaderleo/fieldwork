# Proposal directions — recoverable uv self-update commit

## Decision frame

The work separates four properties that are easy to blur together:

1. **Download integrity:** complete release bytes were obtained and verified.
2. **Installer isolation:** the generated installer completed away from the live installation.
3. **Canonical command availability:** a runnable `uv` remains at the normal path after failure or cancellation.
4. **Installation generation recovery:** `uv`, `uvx`, `uvw`, aliases, and receipt are coherently old, coherently new, or covered by a durable idempotent recovery record.

The public candidate materially improves properties 2 and 3 during the official installer phase. It does not establish property 4 and does not cover property 3 for custom/GHE axoupdater routing or every final self-replace failure.

## Near-term repair to the occupied public direction

This is the smallest non-competing improvement and should be preferred before proposing a broad updater redesign.

### Test repair

- inspect the actual canonical executable boundary, not an arbitrary fixture;
- use a realistic bounded installer-start wait;
- stop early and report if the task completed before the marker;
- request cancellation, await the join handle, and assert cancellation completion;
- run the same control against exact old base and candidate;
- keep the public fixture as an explicit negative control only if it is useful to show why it is insufficient.

### Claim repair

Narrow the immediate statement to:

> On the official Windows route, cancellation while the generated installer runs in the isolated staging prefix does not pre-rename the running `uv.exe`.

Do not claim all failed installations leave `uv.exe` available until final replacement failure is covered.

### Final replacement repair

At minimum:

- copy the proposed new `uv.exe` completely beside the canonical destination before moving the old file;
- create recovery authority before the destructive rename;
- roll back ordinary errors;
- add a missing-source/copy-failure control and a final-rename failure control.

An in-process rollback alone does not cover abrupt process death after the old rename. A helper or next-run recovery journal is necessary for that stronger claim.

## Experiment A — deferred single-file finalizer

Exact experiment: `teamleaderleo/uv#14@ef509a215af602cbc904aed467b4ac5edd66f827`.

### Selected ordering

1. validate old canonical and staged replacement;
2. copy and sync replacement into a temporary file in the canonical directory;
3. write and sync a prepared journal;
4. wait for the updating uv process to exit;
5. rename old canonical to a unique backup;
6. rename complete stage to canonical;
7. on ordinary failure, restore backup;
8. after success, remove backup and journal.

### Why wait for parent exit

Windows permits renaming a running executable but not arbitrary overwrite/delete operations. The existing primitives exploit the rename ability early. The safer ownership split is the opposite: the running process prepares all fallible bytes and metadata, then delegates the tiny destructive commit to another process that acts only after the parent releases its image lock.

### What the journal buys

A journal cannot make several filesystem operations atomic. It can make the interrupted state interpretable and recovery idempotent.

Minimum fields:

- schema version;
- transaction ID;
- canonical path;
- stage path;
- backup path;
- expected old/new hashes or sizes;
- phase (`prepared`, `old-backed-up`, `new-live`, `committed`);
- managed generation identifier.

The prototype currently records paths only. Hashes, phase transitions, directory syncing, and next-run recovery remain design work.

### Recovery table

| Observed state | Authority | Recovery action |
| --- | --- | --- |
| canonical old, stage present, no backup | old | discard or resume prepared stage |
| canonical absent, backup old, stage new | old until commit | restore backup, then retry later |
| canonical new, backup old, journal uncommitted | inspect hashes/phase | finish commit if new matches, otherwise roll back |
| canonical new, backup old, journal committed | new | delete backup and journal |
| canonical missing and no valid backup | unknown/corrupt | fail loudly; never invent success |

### Stop condition

Do not promote this experiment as the product solution unless its workflow passes and a separate recovery invocation proves every listed interrupted state is idempotent.

## Experiment B — recoverable managed-file generation

The complete installation includes multiple binaries and a receipt. Ordinary filesystems do not provide one atomic rename for that set, so the correct promise is recoverability.

### Prepared generation

Create a destination-local transaction directory containing:

- staged `uv.exe`;
- staged `uvx.exe`;
- staged `uvw.exe` where applicable;
- staged aliases/libraries;
- staged receipt;
- manifest with old/new file hashes, modes, and intended destinations.

No live name changes before every staged file and manifest has been validated and synced.

### Commit

For each managed file:

1. record phase before mutation;
2. rename old live file to a transaction-owned backup;
3. rename new staged file to live;
4. record completion.

Commit receipt last, then mark the transaction committed. Cleanup is separate and retryable.

### Recovery policy

A non-committed transaction restores the complete old generation. A committed transaction retains the complete new generation and removes backups. Recovery must be safe to repeat after interruption at any statement.

### Compatibility questions

- What if the new release adds or removes a managed binary?
- What if an old companion is locked by a running process?
- Are aliases symlinks, hard links, copied files, or trampolines on each platform?
- Can the receipt schema or install layout change between releases?
- How should antivirus/indexer locks be retried and bounded?
- Is rollback of a new binary that has already been launched safe?

These questions make this an issue-first architecture proposal unless maintainers explicitly choose the policy.

## Experiment C — custom/GHE route safety

The exact custom route still delegates to axoupdater 0.10.0 and pre-renames the running executable. There are three plausible ownership decisions.

### C1. uv owns a staged path for every generated uv installer

Use uv's known cargo-dist installer contract for public, mirror, GHE, and custom GitHub sources. Resolve/download into a temporary prefix, then use one uv-owned finalizer.

Advantage: one behavior across uv routes.

Risk: custom receipts or installers may not be cargo-dist-compatible despite reaching the same command path.

### C2. axoupdater exposes a staged-install capability

Add a capability/API that returns a prepared installation rather than mutating live paths, leaving finalization to the caller.

Advantage: reusable by other consumers.

Risk: axoupdater supports arbitrary generated installers and may not be able to promise a universal staging contract.

### C3. fail closed on unsafe Windows custom updates

Until a staged capability exists, refuse self-update on Windows routes that would pre-rename the current executable, with a diagnostic directing users to the relevant installer/package process.

Advantage: immediately prevents command disappearance.

Risk: behavior regression for enterprise/custom users; requires explicit maintainer policy.

Current recommendation: characterize exact supported custom receipt/installer types before selecting C1 or C2. C3 is a safety fallback, not an automatic choice.

## Installer descendant ownership

`tokio::process::Command::kill_on_drop(true)` owns the direct PowerShell process. A real generated installer can launch archive tools and other descendants. A robust cancellation claim requires one of:

- a Windows Job Object configured to terminate the process tree;
- a generated-installer contract that forbids detached descendants;
- explicit descendant process handles and shutdown acknowledgements.

A PowerShell loop test proves only direct-child cancellation. It must not be generalized to the process tree.

## Receipt policy

The public candidate directs the staged installer to a temporary configuration root, then discards the new receipt and keeps the old one.

Possible policies:

1. prove the old receipt is unchanged in every semantically relevant field and deliberately retain it;
2. treat the staged receipt as part of the new managed generation and commit it last;
3. synthesize a canonical receipt from validated old policy plus new managed-file metadata.

The second is the clearest transaction model. The first is acceptable only with explicit field comparison and tests for add/remove binary and layout changes.

## Selected continuation

1. Complete and inspect the four queued Windows runs.
2. Repair the experiment until the three hostile finalizer controls pass at one exact head.
3. Add a second experiment that invokes recovery from prebuilt journal/file states without relying on the original finalizer process.
4. Add a deterministic locked-companion/mid-sequence model before attempting a multi-file source patch.
5. Keep public PR 20855 occupied and read-only; prepare review notes internally only.
6. Decide uv-versus-axoupdater ownership for the custom route before writing a competing product patch.

## Rejected shortcuts

- calling the operation atomic because `uv.exe` survives installer cancellation;
- process enumeration to check whether `uvx` is running;
- restoring `.previous.exe` only in Rust error handling;
- writing new bytes directly to canonical companion names;
- deleting recovery artifacts eagerly before a durable committed phase;
- treating a successful public CI run as proof that a regression fails on old code;
- promising complete rollback after sudden power loss without an executable recovery path.
