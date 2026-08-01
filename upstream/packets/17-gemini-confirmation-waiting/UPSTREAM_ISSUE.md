# Upstream issue draft — confirmation waiting ownership

**Status: DRAFT — do not post without explicit authorization.**

## Proposed title

Confirmation waiting state can remain active after cancellation and clear early during overlapping approvals

## Draft body

### Description

The scheduler exposes `onWaitingForConfirmation(waiting: boolean)` so callers can pause work such as an agent deadline while a tool confirmation is awaiting user input.

The current confirmation path sets the callback to `true`, awaits the confirmation race, and sets it to `false` afterward. When that wait rejects, such as during cancellation, the final clear can be skipped. A caller can then remain marked as waiting after the confirmation operation has already ended.

A second case appears when two confirmations overlap. Direct per-call boolean transitions can produce:

```text
true   # first wait enters
true   # second wait enters
false  # first wait exits
```

The second wait remains active while the global callback reports `false`.

### Expected behavior

- Every entered confirmation wait leaves the waiting state on success, cancellation, and failure.
- A global waiting callback stays `true` while at least one confirmation wait remains active.
- If the confirmation wait and waiting-state cleanup both fail, the original confirmation error remains the primary failure.
- Existing bus and IDE confirmation behavior remains unchanged.

### Reproduction

A focused unit case can:

1. start a confirmation operation with an abort signal;
2. observe `onWaitingForConfirmation(true)`;
3. abort the operation;
4. assert that the callback transitions are `[true, false]`.

Current behavior produces `[true]`.

A separate overlap case can enter two waits, leave one, and assert that the external state remains waiting until the final wait leaves.

### Proposed scope

A narrow repair could:

- guarantee one leave attempt for every entered wait;
- aggregate overlapping waits inside the scheduler while keeping the current boolean callback API;
- add focused regression coverage for cancellation, callback errors, and overlapping waits.

This would avoid changes to confirmation policy, message formats, queue ordering, IDE fallback behavior, and the deadline timer itself.

### Validation

Suggested focused commands:

```sh
npm run test --workspace @google/gemini-cli-core -- \
  src/scheduler/confirmation.waiting-state.test.ts \
  src/scheduler/confirmation.waiting-state.repair.test.ts \
  src/scheduler/confirmation-wait-tracker.test.ts \
  src/scheduler/confirmation.test.ts
npm run typecheck --workspace @google/gemini-cli-core
npm run preflight
```

### Additional context

The waiting callback was introduced to pause subagent timeout budgets during human approval. This issue concerns balanced and aggregate ownership of that callback only.

## Internal publication notes

- Target contribution policy asks contributors to link pull requests to an existing issue and recommends issue-first discussion.
- Refresh current source and duplicate search before posting.
- Replace any internal test names if the final source branch differs.
- Public upstream interaction requires explicit human authorization.
