# Automerge and Yjs local-first identity and recovery corpus

State: `target-executed`

## In simple words

This pass compares released Automerge and Yjs packages with the same application-level recovery cases. Both engines converge ordinary duplicate/reordered delivery and preserve text positions through restart. Both also converge product states that still need application policy, such as duplicate provider records and delete-plus-edit.

The decisive recovery differences are malformed update handling and duplicate writer identity:

- Automerge rejected every truncated change without changing the public immutable document;
- Yjs threw after mutating the destination for nine suffix truncations;
- Automerge detected duplicate actor sequence after accepting the first writer;
- Yjs silently retained whichever colliding writer arrived first.

## Exact identity

- Fieldwork issue: #121
- Fieldwork carrier: PR #263
- Executed carrier head: `b9627c9a0a6fe1168e47272cad95b5e2ecb378fa`
- Automerge package: `@automerge/automerge@3.3.2`
- Automerge release source: `b4a1bbe9fc17d26c4d3f1819f9ee3b318de3a516`
- Yjs package: `yjs@13.6.31`
- Yjs release source: `271330889b13eae102873bb417d6747a0ddd8b4a`
- Execution: `30582556167`, Node 22 and Node 24 on Ubuntu
- Executed-head Fieldwork integrity: `30582555951`
- Upstream contact authorized: `false`

Yjs `main` identified itself as a 14.0 release candidate during the source pass, so this compatibility corpus uses the stable 13.x release. A 14.x comparison is a distinct migration lane.

## Source map

### Automerge

The released JavaScript entry point exposes:

- `getChanges` / `applyChanges` for change delivery;
- `save` / `load` and incremental save/load for persistence;
- stateful per-peer sync;
- deterministic presented values plus `getConflicts` for concurrent same-key assignments;
- actor IDs as sequential-writer identity;
- cursors that preserve positions through edits and later document states.

The clone API creates a fresh actor ID by default to avoid duplicate sequence numbers.

### Yjs

The stable source exposes:

- state vectors and idempotent update application;
- relative positions that encode, decode, and resolve after restart;
- per-client clocks, structs, delete sets, pending causal updates, and transaction cleanup;
- application-independent shared maps, arrays, and text.

`readUpdateV2()` decodes and integrates client structs before reading and applying the delete set. Transaction cleanup runs through `finally`. A suffix truncation can therefore throw after integrated state has become observable.

## Executed shared cases

### Duplicate and reordered delivery

Independent writers added distinct keys. Updates arrived in reverse order and one update was delivered twice.

Both engines retained both keys exactly once.

Disposition: ordinary idempotent delivery control passed.

### Duplicate provider identity

Two offline writers created locally distinct calendar records with provider ID `provider-42`.

Both engines converged two records sharing one provider identity.

Disposition: provider uniqueness remains application-owned. Convergence does not deduplicate product identity.

### Delete versus edit

One writer marked an event deleted while another changed its start time.

Both engines converged:

```text
deleted: true
start: 10:00
```

Disposition: application policy decides whether the edit is ignored, retained for restoration, rejected, or surfaced.

### Stable text position after restart

A position at index 2 was retained through a two-character leading insertion and a full save/load or update/load restart.

Both engines resolved the position to index 4.

Disposition: bounded stable-position controls passed.

## Malformed update boundary

### Automerge

The second change was 128 bytes. Every proper truncation, 127 cuts, threw. No returned immutable document showed mutation after the exception. The full change produced `abef`.

```text
bytes: 128
proper cuts: 127
throws: 127
public-state mutation after throw: none
full text: abef
```

Disposition: this public immutable-document corpus was failure-atomic.

### Yjs

The complete update was 45 bytes. Every proper truncation, 44 cuts, threw. Cuts 36 through 44 threw after the destination already exposed the complete visible text `abef` and a seven-byte state vector.

```text
bytes: 45
proper cuts: 44
throws: 44
silent partial cuts: 0
throws after observable mutation: 9
mutation cuts: 36–44
visible text after throw: abef
state-vector bytes after throw: 7
```

Disposition: an exception from `Y.applyUpdate` is not a rollback receipt. Apply untrusted, corrupted, or crash-recovered update bytes to a disposable candidate document or validate them under an equivalent complete framing contract before durable acceptance.

Canonical finding: `findings/F121-yjs-truncated-update-mutation/finding.md`.

## Duplicate writer identity boundary

### Automerge

Two independent documents reused actor ID `00000000000000000000000000000001` and each emitted sequence 1.

The first writer was retained; the second raised a duplicate-sequence error. Reversing delivery reversed which value remained.

Disposition: collision is detected, but recovery still requires application authority over source histories and arrival order.

### Yjs

Two independent documents reused client ID `424242` and each created its first map item.

The first delivered writer remained. The second value disappeared without an exception. Reversing delivery reversed the surviving value.

Disposition: writer identity collision can turn arrival order into silent authority.

Canonical finding: `findings/F121-crdt-duplicate-writer-identity/finding.md`.

## Application ownership boundary

The application must retain:

- account and authorization scope;
- provider and source identity;
- schema and migration policy;
- conflict semantics beyond pure convergence;
- backups and export acceptance;
- unique writer-history binding;
- user-visible recovery and rejection decisions.

The CRDT may own operation convergence. It does not own product truth, provider uniqueness, backup authority, or collision recovery.

## Deterministic corpus assertions

The retained script now asserts:

- duplicate/reordered delivery results;
- duplicate provider and delete-plus-edit controls;
- stable positions after restart;
- every Automerge proper truncation throws with no public immutable-document mutation;
- every Yjs proper truncation throws, no silent partial cut advances visible or state-vector state, and exact cuts 36–44 mutate before throwing;
- duplicate Automerge actor sequence rejects the second writer;
- duplicate Yjs client identity retains only the first delivered writer in both orders.

The exact executed receipt predates these assertion additions. The final source head requires ordinary repository checks or local Node execution before promotion; the accepted target observations remain tied to `b9627c9a...`.

## Evidence boundary

- source contracts and mechanisms: `source-read`;
- exact released-package outcomes: `target-executed` on Node 22 and Node 24;
- calendar and manuscript conclusions: application-model evidence;
- Automerge truncation result: public immutable-document boundary only;
- Yjs mutation-after-throw: exact stable v13 update and corpus only;
- Yjs 14 behavior: unmeasured;
- security/resource-limit conclusion: absent;
- public upstream interaction: absent.

## Current disposition

**ACCEPT the two recovery findings and retain the shared corpus.**

- Require disposable-candidate application or equivalent validation for untrusted Yjs update bytes.
- Require one unique writer identity per independent history and explicit collision recovery.
- Keep provider uniqueness, deletion policy, and schema authority application-owned.

The one-off execution workflow is retired after receipt transfer. A target-specific upstream candidate requires a documented contract mismatch or a narrower diagnostics/safety improvement.
