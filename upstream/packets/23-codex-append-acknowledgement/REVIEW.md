# Review record

## Review state

Current disposition at packet creation: `MATERIALIZE / HOLD`.

The bounded prerequisite has independent acceptance on prior exact source heads. Current public-source acceptance remains pending run `30674601315`, source-only ordinary gates, and complete-diff review of the resulting clean source commit.

## Prior accepted review

Selected predecessor:

- source PR: `teamleaderleo/codex#84`
- source head: `d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2`
- source parent: `a01a2d91461a57809e944de7758477b92617ab01`
- carrier: `teamleaderleo/codex#80@401c2e5e6a37730aae3e8da95591cc6f56655cfc`
- run: `30583967538`
- review: `4823945751`

Accepted findings:

- the return value preserves conversation updates and raw-item emission;
- an absent live thread returns success under ephemeral-session authority;
- pre-write failure returns false and leaves the tested durable item absent;
- commit-then-error returns false while the tested durable item is present;
- existing callers ignore the return value and retain prior behavior;
- one-shot test-store controls leave normal behavior unchanged;
- the boolean remains acknowledgement only and supplies no retry authority.

Later validated predecessor:

- source PR: `teamleaderleo/codex#97`
- source head: `926e0bc5a32b136f31b9eaae75e2de4abc20fa95`
- source parent: `4642370542739d5dd080b0c87a9de06a6435d3db`
- carrier PR: `teamleaderleo/codex#98`
- carrier head: `8161e9ee3423d78768263e8838bd6e4800178902`
- run: `30598744048`
- exact controls: 4/4
- complete thread-store package: passed

## Current public-source review fence

- public base: `openai/codex@670f69416bf91c5dfd8b58669e78050b584ff053`
- clean branch: `teamleaderleo/codex:fix/session-durable-append-acknowledgement`
- current clean branch head before publication: `670f69416bf91c5dfd8b58669e78050b584ff053`
- conflict diagnostic: `teamleaderleo/codex#131`
- semantic materializer: `teamleaderleo/codex#132@4bd35b35dee5649c6ba5af4c3535af2081c58bfc`
- materialization run: `30674601315`

Expected source fence:

- `codex-rs/core/src/session/mod.rs`
- `codex-rs/core/src/session/turn_tests.rs`
- `codex-rs/thread-store/src/in_memory.rs`

Expected parent relation: exactly one source commit directly parented by `670f6941...`.

## Current code observations

At public `670f6941...`:

- `record_conversation_items` returns unit;
- current image-preparation analytics run before persistence;
- `persist_rollout_response_items` returns unit;
- `persist_rollout_items` logs `append_items` errors and returns unit;
- current in-memory thread store lacks the two deterministic append fault modes;
- current turn tests lack the four append-outcome controls.

The old source does not merge cleanly into current `session/mod.rs`. The semantic reconstruction preserves the newer analytics and modifies only the acknowledgement seam.

## Duplicate and prior-art check

Public repository searches performed against `openai/codex`:

- exact phrase `append acknowledgement`: no open issue match;
- code/prior-art query for `append acknowledgement`, `append outcome`, or `persist_rollout_response_items`: no repository code-search result;
- `append_items error`: one open issue about rollout files missing from the state DB, issue #31433; related persistence inventory concern, separate from returning a session append acknowledgement;
- `record_conversation_items`: open issues concern conversation-history content handling, separate from append acknowledgement.

No public duplicate implementing this bounded three-file interface change was found in the inspected current source or search results.

## Current acceptance checklist

- [x] exact current public base identified
- [x] repository and contribution instructions read
- [x] historical source, carriers, runs, reviews, and failure receipts recorded
- [x] exact three-file source fence retained
- [x] direct transplant conflict recorded
- [x] semantic current-source approach published as owned carrier
- [ ] current materialization run passes
- [ ] clean direct-child source head recorded
- [ ] current four exact controls pass
- [ ] current complete thread-store package passes
- [ ] source-only ordinary gates pass
- [ ] complete current diff review accepts source head
- [ ] upstream invitation exists
- [ ] public-contact authorization exists

## Review boundary

A successful current run can establish source readiness in the owned fork. Public delivery remains held by contribution policy and authorization. Typed persistence certainty and every retry/replay/compaction consumer remain separate units.
