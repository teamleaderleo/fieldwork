# Unit 23 — Codex durable append acknowledgement

## Current disposition

`MATERIALIZE / HOLD`

The bounded source change is proven on prior exact public pins and is being reconciled onto current public Codex `670f69416bf91c5dfd8b58669e78050b584ff053`. Public submission remains held because `openai/codex` accepts external code contributions by invitation and no invitation or public-contact authorization exists.

## Scope

Return the authoritative rollout append acknowledgement from `Session::record_conversation_items` while preserving current behavior for callers that ignore the return value.

Exact intended source fence:

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

The boolean exposes acknowledgement only. It does not distinguish definite absence from ambiguous commit/acknowledgement loss and authorizes no retry, duplicate reconciliation, compaction decision, replay, or remote-effect settlement.

## Current branches and execution

- Packet branch: `teamleaderleo/fieldwork:p0/435-unit-23-codex-append-acknowledgement`
- Packet base: `920f87cb25dd0cc7901d59ea2019cd4b4a193b94`
- Clean target source branch: `teamleaderleo/codex:fix/session-durable-append-acknowledgement`
- Current public source base: `openai/codex@670f69416bf91c5dfd8b58669e78050b584ff053`
- Current execution carrier: `teamleaderleo/codex#132@4bd35b35dee5649c6ba5af4c3535af2081c58bfc`
- Current materialization run: `30674601315`
- Direct-transplant diagnostic: `teamleaderleo/codex#131`; GitHub reports a conflict in `session/mod.rs`.

The clean source branch currently points at the exact public base. Carrier #132 publishes one direct-child source commit only after formatting, four exact controls, and the complete thread-store package pass.

## Authoritative record chain

1. Fieldwork campaign and selected prerequisite: `teamleaderleo/fieldwork#83`.
2. Canonical finding and delivery record: `teamleaderleo/fieldwork#292` and `teamleaderleo/fieldwork#239`.
3. Historical current-pin source: `teamleaderleo/codex#51@30a0a9b50da5fd2f7d58ee81315e0311e84e221e`; run `30550323542`; retired.
4. Historical exact-pin carrier: `teamleaderleo/codex#52@324ddccba14b2b0934e2c56cc0cda7ca04a56e6d`; includes failed run `30560746088` and later exact-pin execution `30582576317`; retired.
5. Selected source generation: `teamleaderleo/codex#84@d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2`, parent `a01a2d91461a57809e944de7758477b92617ab01`.
6. Selected execution carrier: `teamleaderleo/codex#80@401c2e5e6a37730aae3e8da95591cc6f56655cfc`; run `30583967538`; success.
7. Later direct-current source: `teamleaderleo/codex#97@926e0bc5a32b136f31b9eaae75e2de4abc20fa95`, parent `4642370542739d5dd080b0c87a9de06a6435d3db`.
8. Later execution carrier: `teamleaderleo/codex#98@8161e9ee3423d78768263e8838bd6e4800178902`; run `30598744048`; success.
9. Current direct-transplant diagnostic: `teamleaderleo/codex#131`; conflict against public `670f6941...`.
10. Current semantic materializer: `teamleaderleo/codex#132@4bd35b35dee5649c6ba5af4c3535af2081c58bfc`; run `30674601315`.

## Governance and contact

Repository instructions read for this unit include root Fieldwork instructions, `START_HERE.md`, `CHARTER.md`, `CODE_FIRST.md`, `PLAIN_LANGUAGE.md`, `METHOD.md`, `REFERENCE_POLICY.md`, `PROGRAMMES.md`, `TARGET_HUBS.md`, `EXPERIMENTS.md`, `TESTBEDS.md`, `INTEGRATION_CONTEXT.md`, `COORDINATION.md`, `REVIEWING.md`, `BATCHES.md`, `upstream/README.md`, `upstream/INDEX.md`, and `upstream/packets/README.md`.

Current public Codex instructions read at `670f6941...`: root `AGENTS.md`, `README.md`, and `docs/contributing.md`. There is no `codex-rs/core/AGENTS.md` at that revision.

Public upstream contact authorized: `false`.
Public upstream interaction performed: `none`.
