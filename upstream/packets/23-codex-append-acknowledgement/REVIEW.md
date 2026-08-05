# Review record

## Review state

`MATERIALIZE: COMPLETE / OWNED-FORK REVIEW: COMPLETE / PUBLIC DELIVERY: HOLD`

The current public-base source is materialized, exactly tested, and completely reviewed within the three-file unit fence. Public delivery remains held only by contribution policy and authorization.

## Current source fence

- Public base and direct parent: `670f69416bf91c5dfd8b58669e78050b584ff053`
- Clean branch: `teamleaderleo/codex:fix/session-durable-append-acknowledgement`
- Clean source head: `16cb14688dac752a5a13c180e94355b199f240a7`
- Source PR: `teamleaderleo/codex#136`
- Source shape: one commit, three files
- Merge state in owned mirror: clean and mergeable
- Review submission: `4841949952`

Changed files:

- `codex-rs/core/src/session/mod.rs`
- `codex-rs/core/src/session/turn_tests.rs`
- `codex-rs/thread-store/src/in_memory.rs`

## Complete-diff findings

No code findings inside the unit fence.

Accepted observations:

- `record_conversation_items` returns the result of the authoritative live-thread append.
- An absent live thread returns `true` under ephemeral-session authority; this does not claim disk durability.
- An acknowledged live append returns `true` and the item is present in reloaded history.
- A pre-write failure returns `false` and the item is absent from reloaded history.
- A commit-then-error result returns `false` even though the item is present, preserving ambiguity and withholding retry authority.
- Current in-memory history updates, image analytics, and raw-response emission remain intact.
- Raw-response emission occurs after the persistence attempt regardless of the returned boolean; delivery is not durability.
- The two in-memory fault controls are one-shot and leave ordinary behavior unchanged when unarmed.

## Caller audit

Five references exist in current `session/mod.rs`: one definition and four production call sites.

The four call sites cover world-state context, changed turn context, response-item lifecycle emission, and user-message lifecycle emission. Every call site discards the new boolean.

This is accepted for unit 23 because the unit establishes the acknowledgement seam only. It does not implement caller gating, retry, replay, compaction, settlement, or typed certainty. Any successor must consume the return explicitly and must not infer persistence from scheduling or channel delivery.

## Test and tree receipt

Materializer run `30674601315`, job `91299123673`, generated and tested source head `06971a3a2b95d70a809472bfbd6fe7884063a563`:

- four unique exact append controls passed, `4/4`;
- full thread-store package passed, `163/163`;
- formatting passed;
- exact three-file fence and direct-parent assertion passed.

Current source head `16cb1468...` is a rewrite from the same parent. All three changed-file blob SHAs are identical between tested and current heads:

- `session/mod.rs`: `6a35b541245007424fd8f268a408225e9e262009`
- `turn_tests.rs`: `cd78a86704d6fe152fde0b522c8f8bc2927c36c5`
- `in_memory.rs`: `bbf69a3c7fb85076eaf0ebcd1d5799433caae9a4`

The test evidence therefore applies to the exact current product tree, while the receipt preserves the distinct tested commit ID.

## Current ordinary CI classification

Current-head v8-canary runs passed. Formatting, cargo-deny, codespell, cargo-shear, changed-area detection, and blob-size policy passed.

The blocking workflow fails at an unrelated repository gate: `verify_cargo_workspace_manifests.py` reports a stale exception for `codex-rs/code-mode/Cargo.toml`, outside the three-file source fence. Downstream SDK/Bazel jobs fail or cancel after that gate. This does not invalidate the exact unit tests or the current-tree review.

## Prior accepted review chain

- `teamleaderleo/codex#51@30a0a9b...`, run `30550323542`, review `4820933076`.
- `teamleaderleo/codex#84@d8299b7...`, carrier #80, run `30583967538`, review `4823945751`.
- `teamleaderleo/codex#97@926e0bc...`, carrier #98, run `30598744048`.
- Direct-transplant conflict diagnostic: `teamleaderleo/codex#131`.
- Current semantic materializer: `teamleaderleo/codex#132`.
- Current clean source review: `teamleaderleo/codex#136`, review `4841949952`.

## Duplicate and prior-art result

No inspected current public code or public issue/PR result implements this exact bounded three-file interface change. Public issue #31433 concerns a different persistence inventory problem.

## Acceptance checklist

- [x] exact current public base identified
- [x] repository and contribution instructions read
- [x] historical source, carrier, run, review, and failure receipts recorded
- [x] direct-transplant conflict recorded
- [x] semantic current-source materialization passed
- [x] clean direct-child source head recorded
- [x] exact four controls passed
- [x] complete thread-store package passed
- [x] tested/current tree identity proven
- [x] current ordinary CI classified
- [x] complete current diff review accepted
- [x] caller audit completed
- [ ] upstream invitation exists
- [ ] public-contact authorization exists

## Review boundary and next action

Technical preparation in the owned repositories is complete. Do not contact public upstream. Preserve source PR #136 and packet PR #449. Once both an OpenAI invitation and explicit public-contact authorization exist, rebase/revalidate against the authorized public base before delivery.