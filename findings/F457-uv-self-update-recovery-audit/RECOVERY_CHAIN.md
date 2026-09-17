# Current recovery successor chain

## Purpose

This file records the active owned-fork chain for Windows self-update recovery. It separates four guarantees that should not be collapsed into one broad claim:

1. rollback after an ordinary returned mutation error;
2. defer canonical replacement until the updater exits;
3. preserve valid recovery evidence when rollback itself fails;
4. publish phase journals without truncating the prior complete generation.

All runs must be re-queried before promotion. Public upstream contact authorized/performed: `false` / `false`.

## 1. Complete managed-generation rollback on returned errors

Owned draft: `teamleaderleo/uv#31`  
Exact base: `astral-sh/uv#20855@8d9324af47e1b52ec1f57f9232bd408281282cf5`  
Exact current head: `53b8b8c350eb25d3a7e20b765f9bb3f43a50206f`  
Current focused run: `30935014059`

Executed Windows evidence already passed twice at exact earlier source head `7098add2d9240eb8c95275f63fe5d544b3f6c4f3`:

- uv-fork run/job `30859708891` / `91838789116`;
- independent Fieldwork run/job `30860080826` / `91839926618`;
- destructive finalizer rollback passed;
- mid-companion-copy rollback passed;
- successful complete-generation commit passed;
- affected Windows all-target check passed.

Current authority split:

- Ubuntu runs the committed transforms twice and proves deterministic one-file output;
- Windows formats, compiles, executes, checks affected targets, and uploads the exact generated source;
- promotion downloads and commits that exact Windows-authoritative file instead of reconstructing it elsewhere.

Bounded guarantee: a returned ordinary mutation error restores canonical `uv.exe`, pre-existing companions, prior receipt, and absence of newly introduced companion paths.

Explicitly excluded: forced termination, power loss, concurrent atomic visibility, custom/GHE route, and private `self-replace` debris.

## 2. Deferred single-file finalization after real parent exit

Owned draft: `teamleaderleo/uv#14`  
Exact current head: `dfcc528fc2ef9b4d829da2a604e194c41342147e`  
Current focused run: `30932981482`

The current harness uses the production relationship:

1. a PowerShell updater parent starts the finalizer child with its own PID;
2. the child opens and owns a synchronization handle to that exact parent;
3. the child publishes readiness only after the handle is owned;
4. the parent remains alive until the outer control terminates it;
5. canonical must remain old before parent exit and change only afterward.

This replaced the invalid sibling-process blocker harness that returned `Access is denied` before proving semantics.

Bounded guarantee under test: slow staging happens while canonical remains runnable; final same-directory replacement occurs only after parent exit; ordinary post-backup failure restores old canonical.

Limits: one file, PID handoff before child readiness, no complete-generation transaction, no next-run discovery, and no directory durability proof.

## 3. Preserve recovery evidence when rollback fails

Owned stacked draft: `teamleaderleo/uv#33`  
Exact base: #14 at `dfcc528fc2ef9b4d829da2a604e194c41342147e`  
Exact current head: `4928f75fd075bf8cd34ccd635205983131ce79ed`  
Current focused run: `30943434536`

Historical recovery stack `teamleaderleo/uv#16` remains evidence only. Its rollback helper deleted stage and journal even when restoring canonical failed, which could erase the only durable recovery instructions.

Recovery v2 adds:

- `prepared`, `old-backed-up`, `new-live`, and `committed` phases;
- conservative old-generation recovery for every non-committed phase;
- committed new-generation retention and debris cleanup;
- repeated-recovery no-op success;
- missing-authority failure with journal retention;
- transaction-directory path containment;
- journal, backup, and stage preservation when rollback fails;
- error text naming the retained journal;
- later recovery after a live injected update-plus-rollback failure.

The live matrix uses a real updater parent that spawns the finalizer. This avoids reintroducing the disproved sibling-process authority model.

This PR intentionally keeps in-place line-journal writes so it answers one narrow question: when the current journal generation is readable, does rollback failure preserve enough evidence for later recovery?

## 4. Publish complete journal generations with one replace operation

Owned stacked draft: `teamleaderleo/uv#34`  
Exact base: #33 at `4928f75fd075bf8cd34ccd635205983131ce79ed`  
Exact current head: `a2869231f2fda2f9cfb45e69a3119941c8917837`  
Current focused run: `30943935274`

The remaining defect in #33 is in-place phase rewriting through `File::create()`. A failed phase write can truncate the retained journal, leaving recovery evidence present by name but unreadable.

The atomic-publication successor:

1. writes a complete journal generation to a same-directory `.write` file;
2. syncs that write-side file;
3. publishes it over the prior journal through one Unicode `MoveFileExW` replacement request with replace-existing and write-through flags;
4. removes an unpublished write-side file after ordinary publication failure;
5. leaves the prior complete journal authoritative;
6. can recover from a complete write-side journal when the first destination publication never appeared.

Hostile additions:

- write-side-only prepared journal recovery;
- post-backup phase publication failure plus rollback failure;
- proof that the prior `prepared` journal remains complete and parseable;
- proof that no unpublished `.write` journal remains;
- later recovery restoring old canonical.

Claim boundary: this removes the in-place truncation window and uses one same-directory replacement operation. It does not prove containing-directory flush durability. The line format still lacks lossless path encoding, content hashes, transaction authentication, and reparse-point defense.

## Current selection

The smallest production-shaped contribution remains #31 because it closes the already executed ordinary-error mixed-generation defect without requiring a new helper process or recovery protocol.

The stronger crash-recovery direction is the #14 → #33 → #34 chain. It should not displace #31 unless target-native execution passes and the owner accepts the larger helper/journal surface. If selected, it still needs:

- complete `uv`/`uvx`/`uvw`/receipt generation ownership;
- next-run journal discovery;
- lossless path encoding and content identity;
- directory durability analysis;
- stale/corrupt transaction policy;
- CLI integration and upgrade compatibility;
- complete-diff review.

## Clearing order

1. settle exact #31, #14, #33, and #34 runs;
2. transfer artifacts, digests, and failure classifications;
3. materialize #31 exact source from the Windows-authoritative artifact if its current gate passes;
4. retain or retire #14/#33/#34 based on target-native results and review cost;
5. keep custom/GHE staging and whole installer process-tree ownership as separate owner decisions;
6. obtain independent complete-diff review before any promotion claim.
