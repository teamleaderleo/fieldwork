# Review — unit 24 Responses Lite first request after prewarm

## In simple words

The proposal makes startup prewarm transport setup only. The first generated Responses Lite turn sends the complete current request, later turns remain incremental, and a failed first generation retries the complete request.

The source is small and clean. Historical focused evidence supports the selected behavior. Final promotion depends on exact execution against the current source head and independent review of the complete three-file diff.

## Review subject

- Work class: `upstream-fork research`
- Target repository: `openai/codex`
- Proposed upstream base: `main`, inspected at `670f69416bf91c5dfd8b58669e78050b584ff053`
- Canonical source branch: [`teamleaderleo/codex:fix/responses-lite-first-request`](https://github.com/teamleaderleo/codex/tree/fix/responses-lite-first-request)
- Exact source head: [`2c3f21d38056d2d77215cd9dce820a680d11cfe8`](https://github.com/teamleaderleo/codex/commit/2c3f21d38056d2d77215cd9dce820a680d11cfe8)
- Canonical source PR: [`teamleaderleo/codex#130`](https://github.com/teamleaderleo/codex/pull/130)
- Fieldwork packet branch: [`p0/435-unit-24-codex-responses-lite-first-request`](https://github.com/teamleaderleo/fieldwork/tree/p0/435-unit-24-codex-responses-lite-first-request/upstream/packets/24-codex-responses-lite-first-request)
- Exact packet head: recorded in the latest unit-24 handoff on [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)
- Complete changed-file fence:
  - `codex-rs/core/src/client.rs`
  - `codex-rs/core/tests/suite/agent_websocket.rs`
  - `codex-rs/core/tests/suite/client_websockets.rs`
- Upstream-contact authority: `none`

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. [complete source compare](https://github.com/teamleaderleo/codex/compare/670f69416bf91c5dfd8b58669e78050b584ff053...2c3f21d38056d2d77215cd9dce820a680d11cfe8)
6. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
7. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact diff links

- complete compare: [`670f694...2c3f21d`](https://github.com/teamleaderleo/codex/compare/670f69416bf91c5dfd8b58669e78050b584ff053...2c3f21d38056d2d77215cd9dce820a680d11cfe8)
- production file: [`client.rs`](https://github.com/teamleaderleo/codex/blob/2c3f21d38056d2d77215cd9dce820a680d11cfe8/codex-rs/core/src/client.rs#L1609-L1631)
- full-agent test file: [`agent_websocket.rs`](https://github.com/teamleaderleo/codex/blob/2c3f21d38056d2d77215cd9dce820a680d11cfe8/codex-rs/core/tests/suite/agent_websocket.rs)
- client test file: [`client_websockets.rs`](https://github.com/teamleaderleo/codex/blob/2c3f21d38056d2d77215cd9dce820a680d11cfe8/codex-rs/core/tests/suite/client_websockets.rs)
- generated or dependency files: `none`

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| Warmup response must never own first generated Lite history | lifecycle invariant and outbound JSON tests | Does current provider/client contract define any valid reason to chain first generation to `generate=false` warmup? |
| `ModelClientSession::stream` is the correct boundary | exact production hunk | Does another layer already own response provenance more precisely? |
| Clearing `last_response_rx` is sufficient | continuation and failed-first retry tests | Can any other session field retain warmup authority after the receiver is cleared? |
| One full first request is an acceptable compatibility cost | existing full-request path; later continuation control | Could the one-time retransmission violate a documented Lite size or cache contract? |
| Stack overflow is separate runner evidence | 2/2 client controls and default-versus-16-MiB agent result | Does current head reproduce the same discriminator, and does the assertion reach the intended request capture before any unrelated failure? |

## Known risks

- Warmup-chain clearing could discard useful server-side prefix caching; later continuation coverage limits the discard to one transition, while a live provider check remains absent.
- Exact line links can drift as upstream moves; all review links are pinned to `2c3f21d...`.
- Current ordinary CI has several red or incomplete jobs. One inspected manifest failure is outside the unit fence; other red jobs remain unclassified.
- The historical execution source differs from the current source head, even though the three candidate files were unchanged across the public drift.
- Production prevalence and user-visible impact remain unmeasured.

## Evidence limits

- Historical focused execution only for `e520da008366cd720ef58fa0b489efc0a2867e97`.
- Current exact focused execution pending for `2c3f21d38056d2d77215cd9dce820a680d11cfe8`.
- No live provider, proxy, or long-running soak result.
- Default-stack full-agent execution aborts; 16 MiB passes.
- Independent reviewer acceptance absent.

## Staleness check

- Current upstream head checked: `670f69416bf91c5dfd8b58669e78050b584ff053` on `2026-08-01`
- Candidate base relationship: direct one-commit child
- Relevant source paths changed upstream between historical base `e6cfd40...` and current inspected base: `no`
- Duplicate/overlap search date: `2026-08-01`
- Open replacement work found: `none` for searched Responses Lite/prewarm/`previous_response_id` terms
- Packet and target PR descriptions synchronized: `yes` at packet creation; both state current exact execution pending

## Source cleanliness

- [x] No Fieldwork-only files in target source diff.
- [x] No temporary workflows or publishers in target source diff.
- [x] No execution artifacts in target source diff.
- [x] No unrelated formatting or generated churn.
- [x] Required snapshots or lock changes are absent and unnecessary.
- [x] Commit-pinned links resolve to the reviewed head.

## Test review

- [x] Historical intended client assertions ran exactly.
- [ ] Current baseline/candidate execution relationship is renewed.
- [x] Setup, stack, and product evidence are separated.
- [x] Failed first-generation retry is covered.
- [x] Post-generation continuation compatibility is covered.
- [x] Platform and integration limits are explicit.
- [x] Ordinary target gates are named accurately as mixed/incomplete.

## Draft review

- [x] Issue draft stays within measured impact.
- [x] PR draft describes the current three-file diff.
- [x] Target terminology is used.
- [x] Internal process vocabulary and private context are absent from the public draft sections.
- [ ] AI disclosure requirement checked at filing time.

## Reviewer disposition

`REPAIR`

Reviewed source head: `2c3f21d38056d2d77215cd9dce820a680d11cfe8`  
Reviewed packet head: latest packet-branch head recorded on issue `#435`  
Reason: the source boundary and tests are coherent, while promotion still needs exact current-head execution, current CI failure classification, and independent complete-diff review.  
Clearing condition: run all three exact controls on `2c3f21d...`, preserve the stack discriminator, classify any source-relevant current CI failure, and obtain independent review.  
Reviewer eligibility: `self-review only`

## Human deep-dive guide

The final human reviewer should focus on:

1. whether a `generate=false` warmup response may ever be a valid predecessor for first generation;
2. whether clearing `last_response_rx` fully severs warmup response authority;
3. whether the one-time full request has any undocumented Lite size/cache consequence;
4. whether the historical-to-current source equivalence plus renewed tests is sufficient for direct PR preparation.

Suggested response:

`Unit 24 looks ready for current-head execution and independent review`  
—or—  
`Unit 24 concern: <specific source, test, compatibility, or framing issue>`
