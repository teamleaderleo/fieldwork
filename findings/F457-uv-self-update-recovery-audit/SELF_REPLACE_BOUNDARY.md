# `self-replace` boundary

## Exact Windows ordering

The inspected `self-replace` Windows implementation defines three random private suffixes:

- `.__relocated__.exe`;
- `.__selfdelete__.exe`;
- `.__temp__.exe`.

Its `self_replace` path performs:

1. resolve current executable;
2. rename canonical executable to a random same-directory relocated path;
3. schedule that relocated executable for deletion;
4. copy the replacement to a random same-directory temp path;
5. rename the temp replacement to canonical.

The deletion scheduler may itself move the relocated executable to the system temporary directory, copy a self-delete helper, and spawn that helper. Every step after the first canonical rename is fallible.

## Consequence for the immediate uv repair

The current-head generation rollback candidate in `teamleaderleo/uv#31` takes an independent snapshot of canonical `uv.exe` before invoking `self_replace`. That snapshot can restore the managed command path even when `self_replace` has already renamed canonical away.

Together with companion and receipt snapshots, this is sufficient for the bounded managed-generation guarantee:

> if the update returns an ordinary error, `uv.exe`, companion destinations, and the receipt are restored to their pre-update contents or the rollback failure retains named recovery snapshots.

It is not sufficient to promise a byte-for-byte identical directory or temp-directory state. Depending on the exact internal failure point, `self-replace` may leave a private relocated, self-delete, or temp executable. Their names are random and the scheduler may have moved them outside the installation directory.

Blindly deleting newly observed matching suffixes is not safe enough for production: another concurrent process could legitimately own them, and system-temp cleanup would require authority beyond the managed installation directory.

## Ownership options

### Immediate bounded uv repair

Keep PR #31's independent canonical snapshot and narrow the guarantee to managed installation coherence on ordinary returned errors. Treat private `self-replace` leftovers as an explicit cleanup caveat.

Advantages:

- based directly on the current public candidate;
- small enough to review;
- closes the experimentally proven old-uv/new-companion/new-receipt state;
- does not require a dependency release first.

### `self-replace` repair

Move ordinary-error rollback into the primitive itself. A correct implementation must stage replacement bytes before destructive canonical rename and explicitly restore canonical after every later failure. Wrapping the existing function after it returns is too late.

Advantages:

- fixes the primitive for every caller;
- can own and clean all private paths it creates.

Cost:

- requires upstream dependency work and a new release before uv can consume it.

### Deferred external finalizer

Use a separate helper that stages everything first, opens a handle to the actual updating parent, waits for parent exit, and then commits through known paths with a journal and rollback.

Advantages:

- the running canonical executable is never renamed by its own process;
- private commit paths and recovery phases remain under uv's control;
- provides a path toward process-death recovery.

Cost:

- more architecture, CLI integration, multi-file generation handling, and compatibility testing.

## Current recommendation

Use the current-head ordinary-error rollback candidate as the smallest repair if its exact Windows matrix passes. Continue the deferred-finalizer experiment as the cleaner crash-recovery direction. Do not describe the immediate wrapper as eliminating every private temporary artifact created by `self-replace`.
