# Upstream issue draft — Confirmation modification can use another active tool call

Draft status: `not ready — exact-head execution and filing authority required`  
Public interaction authorized: `no`

---

## Summary

When more than one tool call is awaiting approval, a confirmation response can be correlated to one call while inline or external-editor modification receives the first active call. Modified arguments are then written under the correlated call ID.

This can combine one call's tool and arguments with another call's state update. Confirmation modification should stay owned by the same call and approval generation from response through publication.

## Reproduction

1. Keep `call-a` first in active order and awaiting approval.
2. Run the confirmation loop for `call-b`, allowing it to enter `AwaitingApproval` with its own correlation ID.
3. Send modified inline content using call B's correlation ID.
4. Observe the call passed to the modification handler.

Minimal assertion:

```text
response.correlationId belongs to call-b
state.firstActiveCall is call-a
expect(modifierCall.request.callId).toBe('call-b')
```

## Observed behavior

At commit `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`, the focused Vitest reproduction reached:

```text
expected 'call-a' to be 'call-b'
```

The same `firstActiveCall` selection remained in `confirmation.ts` at public main commit `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`.

## Expected behavior

The confirmation loop's call ID and approval generation should own:

- the confirmation response;
- the waiting call passed to inline or editor modification;
- the tool used to rebuild the invocation;
- the argument update.

If that call disappears, leaves approval, or enters another approval generation while modification is pending, the stale result should be rejected before state publication.

## Current source observation

`resolveConfirmation` captures `toolCall.request.callId` and waits for a matching correlation ID. The baseline modification helpers use `state.firstActiveCall` as modifier input, while `state.updateArgs` targets the captured call ID.

`firstActiveCall` reflects insertion order. It carries no confirmation-response authority.

## Candidate direction

A narrow repair can stay inside `confirmation.ts`:

1. fetch the active call using the captured call ID;
2. require `AwaitingApproval`;
3. pass that waiting call to the modifier;
4. after asynchronous modification, repeat the lookup and require the same approval generation;
5. rebuild and update only that call.

The current candidate uses waiting-call object identity as the generation fence because the state manager replaces the call object on transitions. An explicit generation token or guarded state-manager update remains a viable wider design.

## Current candidate evidence

- current base: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- candidate head: `0c3a86b0555e152b50ca55fd5f8dc53608571cbe`
- one commit, four scheduler source/test files
- focused controls: inline, editor, removal, status loss, same-ID generation replacement, missing call
- adjacent confirmation controls: eight
- scheduler control: two real scheduler calls awaiting approval simultaneously, with call 2's modified response delivered before call 1's
- predecessor result: 14/14 focused and adjacent tests plus core build/typecheck passed
- current exact-head focused/typecheck/preflight run: pending in the owned fork

## Compatibility and risks

- Public APIs and message formats remain unchanged.
- Stale modification results become explicit errors instead of silently publishing.
- The candidate adds two map lookups and one identity comparison per successful modification.
- Object identity is an implicit generation token; maintainers may prefer an explicit token.
- External editor effects may occur before stale authority is detected; the candidate prevents state publication, not editor-side rollback.

## Evidence limits

- Current exact-head test and full preflight receipt are pending.
- Executor and modifier are controlled in the scheduler ordering test.
- Production frequency and impact are unmeasured.
- macOS, Windows, and a real external editor process are untested.

## Versions and environment

- baseline reproduced: `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`
- current public base: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- candidate: `0c3a86b0555e152b50ca55fd5f8dc53608571cbe`
- predecessor runner: Ubuntu 24.04, Node `v22.23.1`, npm `10.9.8`, Vitest `3.2.4`
- current requested runner: Linux, Node `20.19.0`, locked npm dependencies
- model/external service: none

## Additional context

No equivalent public issue, pull request, branch, or commit was found in searches repeated on 2026-08-01. Repeat the search immediately before filing and use the repository's current issue template.

---

## Filing checklist

- [ ] Current upstream issue and PR search repeated immediately before filing.
- [ ] Exact current candidate execution receipt completed.
- [x] Reproduction is source-current and candidate is rebased on current public main.
- [x] Severity and prevalence wording stays within evidence.
- [x] Private/internal links omitted from the public draft body.
- [ ] Target issue template and contribution policy checked at filing time.
- [ ] AI disclosure handled according to current project policy.
- [ ] Exact user authorization to file recorded.
