# Recovery state-machine result

## In simple words

The current public candidate materially improves one phase: the external installer can finish in isolation before the live installation changes. That does not make the final commit recoverable.

At the commit boundary, companion binaries are copied directly into their live names, the current `uv.exe` is renamed away before the replacement copy, and the existing receipt remains old. Interrupting those primitives can therefore leave a partial companion, mixed old/new binaries, a missing canonical `uv.exe`, or a new binary set described by the old receipt.

A destination-side staging plus durable rollback journal can recover every modeled interruption point to a coherent old generation until an explicit commit marker is durable, then retain the coherent new generation. The model does not claim this protocol is already implemented or target-executed.

## Exact execution

- Script: [`recovery_state_machine.py`](./recovery_state_machine.py)
- Runtime: Python 3 in the Fieldwork worker environment
- Dependencies: standard library only
- Evidence class: `model-executed`
- Scope: operation ordering and recoverability; no Windows filesystem or uv package runtime

## Current-candidate states

The modeled sequence follows the inspected candidate and self-replace ordering:

1. stage a complete release outside the live installation;
2. directly copy `uvx` into its live name;
3. directly copy `uvw` into its live name;
4. rename canonical `uv` to a backup/relocated name;
5. copy the new `uv` to a destination-side temporary file;
6. rename the new file to canonical `uv`;
7. leave the old receipt in place.

Observed distinguishing states:

| Interruption point | Canonical `uv` available? | Coherent generation? | Partial live file possible? |
| --- | --- | --- | --- |
| staged release only | yes | yes, old | no |
| during direct `uvx` copy | yes | no | yes |
| after `uvx` copy | yes | no | no |
| during direct `uvw` copy | yes | no | yes |
| after companion copies | yes | no | no |
| after canonical `uv` rename | no | no | no |
| during replacement temp copy | no | no | replacement temp may be partial |
| after new `uv` becomes canonical | yes | no | no; receipt remains old |

The exact source also schedules old-executable deletion after renaming it and before copying the replacement. That operation does not improve any modeled invariant and can reduce the remaining recovery surface.

## Journaled rollback protocol

The comparison protocol assumes:

1. every new file, including the receipt, is completely staged on the destination filesystem;
2. one durable journal records the old generation, staged paths, backups, and state `prepared`;
3. each old live file is renamed to a backup and each staged file is renamed to its live name;
4. the journal is atomically changed to `committed` only after every file and receipt has its new live name;
5. recovery before `committed` rolls every backed-up file back to the old generation;
6. recovery after `committed` retains the new generation and removes backups.

The script exhaustively interrupts after every modeled rename and commit marker. Recovery satisfies all three invariants at every point:

```text
canonical uv available: true
all managed binaries and receipt one generation: true
no partial live file: true
```

## Meaning

This does **not** prove that a journal is the only acceptable design. It proves a narrower point: multi-file atomicity is unavailable, but installation-wide recoverability is still a concrete, testable property. A proposal should state whether it guarantees only canonical `uv` availability or a coherent managed installation; those are different claims.

## Required target controls

Before retaining a journal implementation:

- kill the updater after every actual filesystem primitive;
- repeat recovery after a second interruption;
- inject disk-full, access-denied, and locked-companion failures;
- verify old and new binaries actually execute after recovery;
- include receipt/provider/managed-file evolution;
- cover Windows rename and deletion semantics directly;
- bound and clean stale journals, backups, and staged files;
- prove cleanup failure cannot erase the primary update result.
