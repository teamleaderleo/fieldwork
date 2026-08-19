# Two-slot journal direction

## Problem

Recovery v2 preserves the journal when rollback fails, but each phase transition still rewrites one
journal file in place. `File::create()` truncates the previous record before the replacement record
is complete and durable. A crash during that rewrite can therefore destroy both the old phase and
the new phase.

This is a durability defect in the recovery mechanism itself. It is separate from ordinary returned
errors, which v2 handles.

## Proposed publication rule

Use two fixed journal slots and a monotonically increasing generation:

| Generation | Slot | Phase |
| ---: | ---: | --- |
| 0 | 0 | `prepared` |
| 1 | 1 | `old-backed-up` |
| 2 | 0 | `new-live` |
| 3 | 1 | `committed` |

For each transition:

1. serialize the complete record for the next generation;
2. include the generation, phase, transaction paths, encoded length, and checksum;
3. truncate and rewrite only `generation % 2`;
4. flush and sync that slot;
5. do not modify the other slot during publication.

Recovery reads both slots, rejects malformed or checksum-invalid records, and chooses the highest
valid generation. A torn write can invalidate its target slot, but the preceding generation remains
in the other slot.

A non-cryptographic checksum is sufficient for torn-write detection in this local transaction
protocol; it is not an authenticity boundary. A later production design may choose a cryptographic
hash if the journal is also expected to detect hostile modification.

## Recovery policy

- No valid slots: no discovered transaction, or explicit corruption if transaction debris exists.
- `prepared`: keep/restore old canonical and remove stage.
- `old-backed-up`: restore backup.
- `new-live`: conservatively restore backup.
- `committed`: keep new canonical and clean backup/stage.

The file state remains the final authority. A journal must never cause recovery to invent old or new
bytes when neither canonical nor backup supplies them.

## Cleanup ordering

Cleanup order is part of the correctness protocol:

1. remove the older uncommitted slot;
2. remove old backup;
3. remove stale stage;
4. remove the committed slot last.

Removing committed evidence first is unsafe. A crash after the old backup is removed could leave
only a `new-live` record, new canonical bytes, and no old authority. Recovery would then have to
guess whether to retain new bytes or report corruption.

The committed slot must therefore remain durable until every destructive cleanup operation is
complete.

## Model result

`models/dual_slot_journal.py` checks all intended publication and cleanup crash boundaries:

- torn `prepared` publication;
- crash after old canonical moves but before `old-backed-up` publication;
- torn `old-backed-up` publication;
- crash after new canonical becomes live but before `new-live` publication;
- torn `new-live` publication;
- torn `committed` publication;
- each committed cleanup boundary with committed evidence retained;
- final removal of committed evidence;
- the counterexample where committed evidence is removed before the old backup.

The intended ordering recovers the old generation at every non-committed boundary and the new
generation at every committed/cleanup boundary. The bad cleanup ordering is rejected as
unrecoverable.

## Remaining implementation requirements

A Rust prototype still needs:

- lossless Windows path encoding rather than `Path::display()` text;
- slot discovery and grouping by transaction nonce;
- checksum and generation validation;
- durable directory metadata handling where Windows semantics require it;
- explicit behavior when both slots are invalid but transaction files exist;
- reparse-point and path-identity validation;
- extension from one executable to the complete managed uv generation.

This model does not replace Windows filesystem execution. It constrains the next implementation so
that the recovery journal does not become a new single point of failure.
