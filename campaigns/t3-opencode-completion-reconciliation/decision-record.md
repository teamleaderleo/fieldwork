# Decision record: T3/OpenCode lifecycle repair sequence

Date: 2026-07-30

State: active

## What this campaign is trying to do

Produce an executable lifecycle contract for the T3/OpenCode boundary and land the smallest independently safe repairs.

The campaign is not primarily an issue-writing exercise. Issues and reports are evidence and coordination records. The target outcome is code that survives restart, steering, interruption, delayed provider events, pending approvals, and reaper concurrency without settling or blocking the wrong run.

## Current owning boundaries

### Adapter-local

The OpenCode adapter owns:

- provider event/session affinity;
- active provider turn state;
- interpretation of busy, idle, error, abort, permission, and question events;
- provider-native request handles;
- exact provider abort coalescing;
- suppression of stale provider events.

### Shared ProviderService/orchestration

Shared orchestration owns:

- durable active T3 run/turn identity;
- persistence of provider recovery metadata;
- conditional lifecycle transitions;
- projection cleanup;
- durable request expiration and response capability;
- reaper serialization or compare-and-set behavior.

A repair is misplaced when an adapter is asked to mutate projected app truth without an exact identity, or when shared orchestration guesses provider outcome from a generic session state.

## Executable baseline

Focused hosted CI has established direct failures for:

- resumed status/outcome reconciliation;
- exact interrupt validation and settlement;
- abort/idle and duplicate-caller races;
- delayed idle against a newer turn;
- pending skill visibility;
- pending permission/question cleanup;
- reaper check-then-stop ordering.

The former caller-generated message-ID specification was withdrawn after protocol review showed it could violate OpenCode's monotonic identifier ordering.

## Repair sequence

### 1. Exact interruption settlement

Proceed now.

Required properties:

- reject a stale explicit turn ID before provider abort;
- one caller owns the abort operation;
- duplicate callers await the same result;
- idle cannot classify an interruption as ordinary completion;
- successful abort clears adapter-local active state;
- abort failure preserves the active turn;
- a delayed idle with no provider activity evidence cannot close a newer turn.

Candidate: `candidates/0002-opencode-interrupt-settlement.patch`.

### 2. Pending request visibility and cleanup

Proceed independently.

Required properties:

- OpenCode `skill` permission maps to visible `dynamic_tool_call` approval;
- terminal cancellation/error expires pending permission and question handles;
- canonical resolution events clear projected pending state;
- stale responses fail before invoking the provider.

Candidate: `candidates/0003-opencode-pending-request-cleanup.patch`.

### 3. Reaper concurrency

Do not land a read-twice workaround.

The current persistence API has read/list/upsert but no compare-and-set or lease. A second projection read only shrinks the race window. The repair needs one of:

- a conditional stop operation tied to an expected provider-session revision;
- per-thread serialization shared with send/start/stop;
- a durable lease/state transition that cannot overwrite a newly active session.

Recent stopped-session reconciliation work already uses optimistic concurrency, which is the preferred precedent.

### 4. Restart reconciliation

Blocked on safe provider correlation.

Status snapshots can establish busy/idle activity but not terminal outcome. Bounded history can classify outcome only when T3 can identify the exact provider user messages belonging to the persisted run/turn.

Rejected approach:

- arbitrary caller-generated `msg...` IDs. OpenCode's private monotonic ID format is semantically significant and is not exported by the public SDK.

Replacement must use a supported provider-generated correlation path or an explicit provider API. It must close the crash window between prompt acceptance and durable correlation persistence.

### 5. Orchestration V2 compatibility

Keep repairs reusable under `RunId`.

Orchestration V2 strengthens durable effects, request expiration, idempotency, and startup repair, but it does not remove adapter protocol races. Adapter-local interruption and provider request mapping should avoid V1-only projection assumptions. Durable recovery metadata should be designed around a generic run identity rather than permanently embedding the current `TurnId` shape.

## Stop condition

Do not call this campaign complete until:

- focused tests execute without harness timeouts;
- at least the interruption and pending-request slices pass existing adapter tests and server typecheck;
- reaper safety has a truly conditional boundary;
- restart recovery has a version-tolerant provider correlation mechanism;
- Fieldwork records observed results separately from inferred design conclusions.

No upstream contact is authorized or performed.
