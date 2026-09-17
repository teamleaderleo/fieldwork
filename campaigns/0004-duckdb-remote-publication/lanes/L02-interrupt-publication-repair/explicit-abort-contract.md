# Explicit COPY Abort Contract

State: `design candidate`

Lane: #103  
Campaign: #96  
Upstream contact authorized: `false`

## Problem with destructor-only repair

A destructor can suppress exceptions but cannot reliably report abort failure to the query result. It also has incomplete failure context: active exception and interrupt state cover the observed cases, but do not encode every possible failed operator teardown.

## Candidate ownership

### Core copy function

Add an optional `copy_to_abort` callback to `CopyFunction`.

When `CopyToFileGlobalState` is destroyed with `finalized == false`, invoke the callback for each initialized global file state before ordinary path cleanup and before format-writer members are released.

### Buffered writer

Add `BufferedFileWriter::Abort()` that:

1. discards its unwritten 4 KiB buffer;
2. calls an abort operation on the owned file handle;
3. releases the handle without calling normal close.

### File handle

Add an optional/default abort operation distinct from `Close()`.

- local/default implementation can close without flushing the discarded `BufferedFileWriter` buffer, after which existing failed-path removal runs;
- S3 implementation aborts the multipart upload;
- other side-effecting filesystems can override when close is commit-like.

### Format implementations

CSV, Parquet, BLOB, and other file-producing copy functions wire their global writer state to `copy_to_abort`.

## Advantages

- failure ownership is explicit;
- all query failures can use the same path, not only interrupts;
- abort errors can be logged or attached before final query cleanup;
- successful `Close()` remains a commit operation;
- destructor behavior becomes a safety net rather than the publication decision.

## Costs and questions

- requires coordinated core and extension changes;
- every built-in copy writer needs an audit;
- partitioned, per-thread, rotated, and nested writers need recursive abort behavior;
- error precedence needs a rule when query failure and abort failure coexist;
- generic `FileHandle::Abort()` default semantics require care for local files and out-of-tree filesystems;
- successful implicit-close users still need an explicit-close migration plan before destructor completion can be removed.

## Current ranking

1. Use the extension-level containment and native-abort experiments to prove the available signals and S3 operation.
2. Prefer an explicit copy abort callback for a complete repair if the narrower experiments pass.
3. Retain destructor checks as defense in depth.
4. Avoid core teardown-before-delete as the primary fix because it completes and publishes partial data before deletion.

No upstream contact occurred.
