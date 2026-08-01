# Upstream issue draft — Confirmation modification can use another active tool call

Draft status: `not ready — current-main reproduction and maintainer authorization required`  
Public interaction authorized: `no`

---

## Summary

When more than one tool call is active, a confirmation response can be correlated to one call while inline or external-editor modification receives the first active call. The modified arguments are then written under the correlated call ID.

This can mix one call's tool/arguments with another call's state update. Confirmation modification should remain owned by the same call and approval generation from response through publication.

## Reproduction

1. Keep `call-a` first in the active-call map and awaiting approval.
2. Run the confirmation loop for `call-b`, allowing it to enter `AwaitingApproval` with its own correlation ID.
3. Send modified inline content using `call-b`'s correlation ID.
4. Observe the call passed to the modification handler.

Minimal assertion:

```text
response.correlationId belongs to call-b
state.firstActiveCall is call-a
expect(modifierCall.request.callId).toBe('call-b')
```

## Observed behavior

At commit `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`, the focused Vitest case reached:

```text
expected 'call-a' to be 'call-b'
```

The same `firstActiveCall` selection remains in `confirmation.ts` at public main commit `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`.

## Expected behavior

The confirmation loop's call ID and approval generation should own:

- the confirmation response;
- the waiting call passed to inline or editor modification;
- the tool used to rebuild the invocation;
- the argument update.

If that call disappears, leaves approval, or enters another approval generation while modification is pending, the stale result should be rejected before state publication.

## Current source observation

`resolveConfirmation` captures `toolCall.request.callId` and waits for a matching correlation ID. Both modification helpers then use `state.firstActiveCall` as the modifier input, while `state.updateArgs` targets the captured call ID.

`firstActiveCall` reflects active-call insertion order. It does not establish ownership of the confirmation response.

## Candidate direction

A narrow repair can stay inside `confirmation.ts`:

1. fetch the active call using the captured call ID;
2. require `AwaitingApproval`;
3. pass that waiting call to the modifier;
4. after asynchronous modification, repeat the lookup and require the same approval generation;
5. rebuild and update only that call.

An explicit approval-generation token would also work, though it widens state types and transitions. The current candidate uses the waiting-call object identity as the generation fence because the state manager replaces the call object on status transitions.

## Compatibility and risks

- Public APIs and message formats remain unchanged.
- Stale modification results become explicit errors instead of silently publishing.
- A scheduler-level test with two simultaneous approval loops and out-of-order responses should define the integration contract.
- Maintainers may prefer an explicit generation token or a guarded state-manager update.

## Evidence limits

- The baseline focused reproduction covers inline modification; the editor path shares the same source mechanism and is covered on the repaired candidate.
- The current candidate tests use a stateful mock rather than two real scheduler loops.
- Production frequency and impact are unmeasured.
- Current-main rebase, full preflight, macOS, and Windows remain untested.

## Versions and environment

- project revision reproduced: `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`
- current public revision inspected: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- platform: Ubuntu 24.04 GitHub-hosted runner
- runtime/compiler: Node `v22.23.1`, npm `10.9.8`, TypeScript via core workspace typecheck, Vitest `3.2.4`
- relevant configuration: fixed-input unit harness; no model or external service

## Additional context

No equivalent public issue, pull request, or commit was found in searches repeated on 2026-08-01. Re-run the search immediately before filing and use the repository's current issue template.

---

## Filing checklist

- [ ] Current upstream issue and PR search repeated immediately before filing.
- [ ] Reproduction works on a current public revision.
- [x] Severity and prevalence wording stays within evidence.
- [x] Private, internal, and evidence-only links omitted from the public draft body.
- [ ] Target issue template and contribution policy followed.
- [ ] AI disclosure handled according to current project policy.
- [ ] Exact user authorization to file this issue recorded.
