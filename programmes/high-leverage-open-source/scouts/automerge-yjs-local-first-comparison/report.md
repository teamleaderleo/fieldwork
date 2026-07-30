# Automerge and Yjs local-first identity and recovery corpus

## In simple words

This pass compares two released CRDT engines with the same application-level cases. The question is broader than convergence: after offline edits, duplicate delivery, restart, deletion, malformed input, or writer-identity reuse, can the application still explain what happened and apply its own authority rules?

The corpus deliberately keeps provider identity, authorization, schema migration, deletion policy, backup acceptance, and user-visible recovery outside the CRDT engine.

## Exact target pins

- Automerge JavaScript package: `@automerge/automerge@3.3.2`.
- Automerge release commit: `b4a1bbe9fc17d26c4d3f1819f9ee3b318de3a516`.
- Yjs stable package: `yjs@13.6.31`.
- Yjs release tag/commit: `v13.6.31` / `271330889b13eae102873bb417d6747a0ddd8b4a`.
- Runner: Node 22 and Node 24 on Ubuntu.

Yjs `main` currently identifies itself as a 14.0 release candidate, so this first compatibility corpus uses the latest stable 13.x package and records 14.x as a later migration lane.

## Source map

### Automerge

The released JavaScript entry point documents these relevant contracts:

- `getChanges` / `applyChanges` for change delivery;
- `save` / `load` and incremental save/load for persistence;
- stateful per-peer sync;
- concurrent same-key assignments expose conflicts through `getConflicts` while one deterministic value is presented;
- actor IDs represent sequential writers and must not be used concurrently;
- cursors can preserve a position through edits and can be resolved after later document states.

The clone API creates a fresh actor ID by default specifically to avoid duplicate sequence numbers.

### Yjs

The stable source exposes:

- state vectors and idempotent update application;
- relative positions that encode, decode, and resolve after a full update is loaded into a new document;
- per-client clocks, structs, delete sets, pending causal updates, and transaction cleanup;
- application-independent shared maps, arrays, and text.

`readUpdateV2()` integrates decoded structs before it reads and applies the delete set. `transact()` completes transaction cleanup in `finally`, including when update decoding throws. The truncation scan tests the resulting failure-atomicity boundary instead of assuming an exception leaves the destination unchanged.

## Shared executable cases

1. **Duplicate and reordered delivery**
   - independent writers add distinct keys;
   - updates arrive in reverse order;
   - one update is delivered twice;
   - the final value must contain both keys exactly once.

2. **Duplicate provider identity**
   - two offline writers create locally distinct calendar records with the same provider identity;
   - both records converge;
   - the result demonstrates why provider uniqueness remains application-owned.

3. **Delete versus edit**
   - one writer marks an event deleted;
   - another changes its start time;
   - both fields converge;
   - product policy still decides whether the edit is ignored, retained for restore, rejected, or surfaced as a conflict.

4. **Stable text position after restart**
   - create a position at index 2;
   - insert two leading characters;
   - serialize and load into a new document;
   - the position must resolve to index 4.

5. **Truncated second change or update**
   - create text and then delete its middle bytes;
   - truncate every possible suffix boundary;
   - record exceptions, silent partial results, and any destination mutation after an exception;
   - compare the full accepted result.

6. **Duplicate writer identity**
   - create two independent writers with the same Automerge actor ID or Yjs client ID;
   - deliver the conflicting first operations in both orders;
   - record rejection, loss, or order-dependent state.

## Evidence classes

- Source contracts and candidate mechanism: `source-read`.
- Node execution of released packages: `target-executed` once the exact workflow is green and its output is retained.
- Calendar and manuscript product conclusions: application-model evidence only. They describe ownership boundaries and do not establish a target defect by themselves.

## Promotion rules

A target-specific candidate requires all of:

- a minimized byte/update corpus;
- exact package and source revision;
- ordinary and negative controls;
- repeatability across the named Node matrix;
- a documented expectation or a clear recovery/API hazard;
- a likely owning subsystem;
- an explicit application consequence.

A difference between Automerge and Yjs remains comparative evidence until one engine violates its own stated contract or exposes an unsafe, unexplained recovery boundary.

## Contact boundary

This is owned Fieldwork research. No public upstream issue, pull request, comment, review, or message is authorized or included.
