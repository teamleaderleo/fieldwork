# Deep dive

## Problem

`Session::record_conversation_items` updates live conversation history, attempts to append rollout items through `LiveThread`, and emits raw response items. At public Codex base `670f69416bf91c5dfd8b58669e78050b584ff053`, the `LiveThread::append_items` result was logged and discarded before returning to the session caller.

A caller therefore could not distinguish an acknowledged authoritative append from an append error. Unit 23 creates that observability seam without changing caller policy.

## Selected interface change

The current source returns `bool` from `record_conversation_items`:

- `true` when no live thread exists, because the ephemeral session's in-memory history remains authoritative for that session;
- `true` when `LiveThread::append_items` returns success;
- `false` when the append returns an error.

`persist_rollout_response_items` returns the same acknowledgement. A private checked helper performs the append and returns the result. Existing `persist_rollout_items` callers retain fire-and-log behavior by discarding the checked helper's return value.

Current analytics, in-memory history updates, and raw-response emission remain in place. Raw-response delivery still occurs after the persistence attempt even when the returned acknowledgement is `false`.

## Persistence states

### Ephemeral session

There is no `LiveThread`. `record_conversation_items` returns `true` after updating live history. This claims session authority, not disk durability.

### Acknowledged live append

`LiveThread::append_items` returns success. The caller receives `true`, and the test reloads live-thread history and confirms the item is present.

### Pre-write failure

The in-memory test store consumes a one-shot fault before extending durable history. The caller receives `false`, and reloaded history lacks the item.

### Commit-then-error acknowledgement loss

The in-memory test store extends durable history and then returns a one-shot error. The caller receives `false`, while reloaded history contains the item.

This proves that a generic append error cannot authorize retry: the durable effect may already exist.

## Caller audit

The current source contains one definition and four production call sites of `record_conversation_items`:

1. world-state context recording;
2. changed turn-context recording;
3. response-item recording before lifecycle emission;
4. user-message recording before lifecycle emission.

All four call sites discard the new boolean. This is intentional for unit 23. The change exposes an authoritative input for later receipt work; it does not claim that current callers now gate lifecycle events, retries, replay, compaction, or settlement on persistence.

Any successor must consume the return explicitly. Channel delivery, raw-response emission, or task scheduling must not be treated as proof of durable append.

## Current-source reconciliation

The strongest predecessor was `926e0bc5a32b136f31b9eaae75e2de4abc20fa95`, a direct child of public `4642370542739d5dd080b0c87a9de06a6435d3db`.

Public Codex advanced to `670f69416bf91c5dfd8b58669e78050b584ff053`. A direct transplant conflicted in current `session/mod.rs`, which contains newer image-preparation analytics and session changes. The selected materializer therefore:

1. started from exact public `670f6941...`;
2. reused validated test-support blobs;
3. applied the acknowledgement change by exact semantic anchors to current `session/mod.rs`;
4. preserved current analytics and raw-response behavior;
5. asserted the exact three-file product fence;
6. listed tests and required one unique full-name match for each selector;
7. ran all four with `--exact` and required `4/4`;
8. ran formatting and the complete thread-store package;
9. published one direct-child clean source commit only after success.

Run `30674601315`, job `91299123673`, generated and tested `06971a3a2b95d70a809472bfbd6fe7884063a563`. The branch was later rewritten to current source head `16cb14688dac752a5a13c180e94355b199f240a7` from the same parent. The three product blob SHAs are identical across both heads, so the execution receipt applies to the current tree exactly.

## Test support

`InMemoryThreadStore` receives two one-shot test/debug controls:

- fail the next non-empty append before writing;
- write the next non-empty append and then return an error.

Ordinary behavior is unchanged when neither control is armed. Each control is consumed once.

## Review result

Source PR `teamleaderleo/codex#136` is clean and mergeable in the owned mirror. Review `4841949952` found no code defects inside the three-file unit fence.

Current-head CI passed v8-canary, formatting, cargo-deny, codespell, cargo-shear, changed-area detection, and blob-size policy. The blocking workflow stops at an unrelated repository-manifest check for a stale code-mode feature exception; that failure is outside the source fence and precedes many downstream matrix failures or cancellations.

## Risks and controls

- **False-green selectors:** list tests first, require one exact full-name match per declared suffix, run each with `--exact`, and require `FIELDWORK_APPEND_OUTCOME_EXACT=4/4`.
- **Receipt/head confusion:** record tested head and current head separately, then prove product-tree identity with all three blob SHAs.
- **Caller overclaim:** state explicitly that all current production callers ignore the return value.
- **Retry misuse:** preserve the commit-then-error case and state that `false` supplies no retry authority.
- **Carrier pollution:** execution-only files remain outside the clean source commit.
- **Public process violation:** no public upstream interaction occurs without invitation and explicit authorization.

## Successor boundary

Deferred work:

- typed `Absent/Persisted/Ambiguous` certainty;
- durable operation receipt ownership;
- stable direct and nested Code Mode identities;
- explicit caller policy;
- replay and duplicate reconciliation;
- retry authority;
- compaction, resume, fork, rollback, and remote settlement policy.