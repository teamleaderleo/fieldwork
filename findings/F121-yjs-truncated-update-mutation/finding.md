# Yjs truncated updates can mutate before throwing

Finding ID: `F121-yjs-truncated-update-mutation`  
State: `target-executed / recovery-rule-ready`  
Owning issue: #121  
Fieldwork carrier: PR #263  
Package: `yjs@13.6.31`  
Source: `271330889b13eae102873bb417d6747a0ddd8b4a`  
Execution: `30582556167` on Node 22 and Node 24  
Upstream contact authorized: `false`

## In simple words

Applying a damaged Yjs update can change the destination document and then throw an exception. Catching the exception does not prove the destination is unchanged.

An application that accepts updates from storage, synchronization, import, or another trust boundary should not apply unvalidated bytes directly to its only durable document and then continue after an error.

## Exact corpus

The source document performs two text operations whose complete encoded update is 45 bytes and yields `abef`.

Every proper truncation boundary, cuts 1 through 44, was applied to a fresh destination. The corpus recorded:

```text
proper cuts: 44
cuts that threw: 44
silent partial cuts: 0
cuts that threw after mutation: 9
mutation cuts: 36, 37, 38, 39, 40, 41, 42, 43, 44
visible text after those throws: abef
state-vector bytes after those throws: 7
```

The complete update also yields `abef`.

The result repeated on Node 22 and Node 24 at exact carrier head `b9627c9a0a6fe1168e47272cad95b5e2ecb378fa`.

## Source mechanism

Stable Yjs `readUpdateV2()`:

1. decodes client structs;
2. integrates those structs into the document store;
3. reads and applies the delete set afterward.

A suffix truncation can therefore occur after struct integration but before update decoding finishes. Transaction cleanup runs through `finally`, so the integrated state remains observable when the decoder throws.

## Governing recovery rule

> An exception from `Y.applyUpdate` is not a rollback receipt.

For untrusted, corrupted, or crash-recovered update bytes:

1. retain the accepted document or checkpoint unchanged;
2. load or clone a disposable candidate document;
3. apply the update to the candidate;
4. validate application-level identity, schema, resource, and authorization rules;
5. accept the candidate only after the whole operation succeeds;
6. discard or quarantine the candidate on any exception.

A provider may instead validate the complete update framing before application, but framing validation must cover the exact decoder contract rather than only a transport checksum.

## Main criticism

Yjs documents update application and convergence; it does not promise transactional rollback for malformed bytes. The observed behavior may be intentional for performance and streaming integration.

That limits the current disposition. This is an application recovery hazard and documentation boundary, not yet an upstream correctness defect.

## Edge cases still open

- update-v2 encoding;
- pending causal structs and delete sets;
- observers fired before the throw;
- undo manager state;
- garbage collection and subdocuments;
- provider persistence that retries the same damaged update;
- large hostile inputs and resource limits;
- Yjs 14 release-candidate behavior.

## Decision

**ACCEPT the recovery hazard. Require disposable-candidate application or equivalent validation before durable acceptance of untrusted update bytes.**

An upstream candidate requires a documented atomicity expectation, a safety-oriented API, or a diagnostics improvement with a minimized corpus. No public upstream interaction occurred.
