# Upstream issue draft — Confirmation modification can use another active tool call

Draft status: `ready — filing authority required`  
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

The prepared candidate uses waiting-call object identity as the generation fence because the state manager replaces the call object on transitions. An explicit generation token or guarded state-manager update remains a viable wider design.

## Candidate evidence

- public base: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- candidate: `b6d8e8bb6160aec16555647d81d46a694e44b58b`
- one commit, four scheduler source/test files
- six focused controls: inline, editor, removal, status loss, same-ID generation replacement, missing call
- eight adjacent confirmation controls
- one scheduler control with two real scheduler calls awaiting approval simultaneously and call 2's modified response delivered before call 1's
- final result: 15/15 tests, posttest build, core typecheck, formatting, staged lint, four-file ESLint, exact fence, clean tree, and publication passed

Full repository preflight reaches shellcheck `SC2031` in `.github/workflows/pr-size-labeler-batch-run.yml`. The unchanged base reproduces the same workflow path and warning; the candidate changes no workflow.

## Compatibility and risks

- Public APIs and message formats remain unchanged.
- Stale modification results become explicit errors before state publication.
- The candidate adds two map lookups and one identity comparison per successful modification.
- Object identity is an implicit generation token; an explicit token may be clearer.
- External editor effects may occur before stale authority is detected; the candidate prevents publication, not editor-side rollback.

## Evidence limits

- Executor and modifier are controlled in the scheduler ordering test.
- Production frequency and impact are unmeasured.
- macOS, Windows, and a real external editor process are untested.
- Eligible independent review remains pending.

## Versions and environment

- baseline reproduced: `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`
- current public base: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- candidate: `b6d8e8bb6160aec16555647d81d46a694e44b58b`
- final runner: Ubuntu 22.04, Node `v20.19.0`, npm `10.8.2`, Vitest `3.2.4`
- model/external service: none

## Additional context

No equivalent public issue, pull request, branch, or commit was found in searches repeated on 2026-08-01. Repeat the search immediately before filing and use the repository's current issue template.

---

## Filing checklist

- [ ] Current upstream issue and PR search repeated immediately before filing.
- [x] Exact current candidate execution receipt completed.
- [x] Reproduction is source-current and candidate is rebased on current public main.
- [x] Severity and prevalence wording stays within evidence.
- [x] Private/internal links omitted from the public draft body.
- [ ] Eligible independent review completed.
- [ ] Target issue template and contribution policy checked at filing time.
- [ ] AI disclosure handled according to current project policy.
- [ ] Exact user authorization to file recorded.
