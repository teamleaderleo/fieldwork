# Upstream pull request draft — confirmation waiting ownership

**Status: DRAFT — requires an approved upstream issue and explicit authorization before posting.**

## Proposed title

fix(core): balance confirmation waiting ownership

## Draft body

## Summary

Guarantee balanced waiting-state cleanup for tool confirmations and keep the scheduler's external waiting callback active until the final overlapping confirmation completes.

This prevents a cancelled confirmation from leaving a caller paused and prevents one completed wait from reporting idle while another wait remains active.

## Details

- Add a confirmation-wait helper that always attempts the matching leave transition after the existing bus/IDE wait settles.
- Preserve the primary confirmation error when the leave callback also throws, while retaining the cleanup failure in logs.
- Add a scheduler-owned counter that emits the existing boolean callback only on `0 -> 1` and `1 -> 0` transitions.
- Use the counted callback at both scheduler confirmation call sites.
- Keep confirmation policy, message formats, IDE fallback behavior, queue ordering, and the public callback type unchanged.

Changed production files:

- `packages/core/src/scheduler/confirmation-wait-tracker.ts`
- `packages/core/src/scheduler/confirmation.ts`
- `packages/core/src/scheduler/scheduler.ts`

Changed tests:

- `packages/core/src/scheduler/confirmation-wait-tracker.test.ts`
- `packages/core/src/scheduler/confirmation.waiting-state.repair.test.ts`
- `packages/core/src/scheduler/confirmation.waiting-state.test.ts`

## Related Issues

Closes #<approved-issue-number>

## How to Validate

Run the focused scheduler confirmation tests and core typecheck:

```bash
npm run test --workspace @google/gemini-cli-core -- \
  src/scheduler/confirmation.waiting-state.test.ts \
  src/scheduler/confirmation.waiting-state.repair.test.ts \
  src/scheduler/confirmation-wait-tracker.test.ts \
  src/scheduler/confirmation.test.ts
npm run typecheck --workspace @google/gemini-cli-core
```

Expected result:

```text
Test Files  4 passed (4)
Tests       16 passed (16)
```

Then run the repository submission gate:

```bash
npm run preflight
```

Key cases covered:

1. cancellation after entering a confirmation wait produces balanced `[true, false]` transitions;
2. overlapping waits keep the external state active until the final leave;
3. IDE rejection preserves the current bus-wait fallback behavior;
4. a primary wait error stays authoritative when cleanup also fails;
5. a cleanup failure remains visible after a successful wait;
6. an unmatched leave is rejected.

## Pre-Merge Checklist

- [x] Updated relevant documentation and README (if needed) — no user-facing documentation change required for the internal lifecycle correction.
- [x] Added/updated tests (if needed)
- [x] Noted breaking changes (if any) — no callback type or confirmation-policy change.
- [ ] Validated on required platforms/methods:
  - [ ] MacOS
    - [ ] npm run
    - [ ] npx
    - [ ] Docker
    - [ ] Podman
    - [ ] Seatbelt
  - [ ] Windows
    - [ ] npm run
    - [ ] npx
    - [ ] Docker
  - [x] Linux
    - [x] npm run
    - [ ] npx
    - [ ] Docker

## AI-assisted development disclosure

This change was developed with AI assistance. The submitter should verify and use any additional disclosure wording required by the repository at submission time.

## Internal publication notes

- Replace the issue placeholder only after maintainers accept the issue scope.
- Refresh exact test results from the final rebased source head.
- Mark `npm run preflight` complete only after it executes on that exact head.
- Public upstream interaction requires explicit human authorization.
