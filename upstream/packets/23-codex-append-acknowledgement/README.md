# Unit 23 — Codex durable append acknowledgement

## Current disposition

`MATERIALIZE: COMPLETE / OWNED-FORK REVIEW: COMPLETE / PUBLIC DELIVERY: HOLD`

The bounded source change is materialized and reviewed on current public Codex base `670f69416bf91c5dfd8b58669e78050b584ff053`. The only remaining hold is public-process authorization: `openai/codex` accepts external code contributions by invitation, and no invitation or public-contact authorization exists.

## Scope

Return the authoritative rollout append acknowledgement from `Session::record_conversation_items` while preserving current behavior for callers that ignore the return value.

Exact source fence:

- `codex-rs/core/src/session/mod.rs`
- `codex-rs/core/src/session/turn_tests.rs`
- `codex-rs/thread-store/src/in_memory.rs`

Behavior matrix:

| case | returned acknowledgement | durable item |
| --- | --- | --- |
| ephemeral session | `true` | no live store; in-memory session history remains authoritative |
| successful live append | `true` | present |
| pre-write failure | `false` | absent |
| commit-then-error acknowledgement loss | `false` | present |

The boolean is acknowledgement only. `false` intentionally combines definite pre-write failure with ambiguous commit/acknowledgement loss and therefore authorizes no retry, duplicate reconciliation, replay, compaction decision, or remote-effect settlement.

## Current source and review

- Public base and direct parent: `670f69416bf91c5dfd8b58669e78050b584ff053`
- Clean source branch: `teamleaderleo/codex:fix/session-durable-append-acknowledgement`
- Clean source head: `16cb14688dac752a5a13c180e94355b199f240a7`
- Source review PR: `teamleaderleo/codex#136`
- Review submission: `4841949952`
- Source shape: one commit, three files, 190 additions, 7 deletions
- Merge state in the owned mirror: clean and mergeable

All four production call sites currently discard the new result. That is the explicit unit boundary: unit 23 exposes the seam but does not change caller policy.

## Validation receipt

Semantic materializer:

- Carrier PR: `teamleaderleo/codex#132`
- Carrier head: `4bd35b35dee5649c6ba5af4c3535af2081c58bfc`
- Workflow run: `30674601315`
- Job: `91299123673`
- Generated and tested source head: `06971a3a2b95d70a809472bfbd6fe7884063a563`
- Exact append controls: `4/4`
- Full `codex-thread-store` package: `163 passed; 0 failed`
- Formatting: passed

The source branch was later rewritten to `16cb1468...` from the same parent. The tested and current heads contain identical blobs for all three changed files:

- `session/mod.rs`: `6a35b541245007424fd8f268a408225e9e262009`
- `turn_tests.rs`: `cd78a86704d6fe152fde0b522c8f8bc2927c36c5`
- `in_memory.rs`: `bbf69a3c7fb85076eaf0ebcd1d5799433caae9a4`

Current-head owned CI also passed v8-canary, formatting, cargo-deny, codespell, cargo-shear, changed-area detection, and blob-size policy. `blocking-ci` fails outside this three-file fence at a stale `codex-rs/code-mode/Cargo.toml` manifest exception; downstream matrix jobs fail or cancel after that repository gate.

## Authoritative record chain

1. Fieldwork campaign and prerequisite: `teamleaderleo/fieldwork#83`.
2. Canonical finding and delivery record: `teamleaderleo/fieldwork#292` and `teamleaderleo/fieldwork#239`.
3. Historical source/carrier pairs: `teamleaderleo/codex#51/#52`, `#84/#80`, and `#97/#98`.
4. Direct-transplant conflict diagnostic: `teamleaderleo/codex#131`.
5. Current semantic materializer and exact execution receipt: `teamleaderleo/codex#132`, run `30674601315`, job `91299123673`.
6. Current clean source review: `teamleaderleo/codex#136@16cb14688dac752a5a13c180e94355b199f240a7`.
7. Packet review: `teamleaderleo/fieldwork#449`.

## Governance and contact

Repository and target instructions were read and applied, including Fieldwork coordination, reviewing, batching, upstream packet, and public-contact rules, plus Codex root `AGENTS.md`, `README.md`, and `docs/contributing.md` at the source base.

Public upstream contact authorized: `false`.
Public upstream interaction performed: `none`.

Exact next action: preserve the owned source and packet until an OpenAI contribution invitation and explicit public-contact authorization both exist; then rebase/revalidate against the authorized delivery base before any public contact.