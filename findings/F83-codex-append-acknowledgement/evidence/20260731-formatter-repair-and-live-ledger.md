# Formatter repair, current execution, and live receipt ledger

Date: 2026-07-31  
Canonical campaign: Fieldwork #83  
Related worker: #197  
Read-only public Codex pin: `4642370542739d5dd080b0c87a9de06a6435d3db`  
Public upstream interaction: none

## In simple words

Three current-source lanes were queued from the earlier reconciliation packet. The append-acknowledgement lane passed. The receipt-wire and runtime-effect lanes stopped at source formatting after their ancestry and file-fence checks, before any target test executed.

The repair keeps those failed heads immutable, uses pinned Rust formatting through narrow publisher carriers, publishes clean source-only successors, and gives each successor a fresh execution carrier. The next bounded source slice adds one session-scoped live receipt ledger keyed by protocol-owned `ToolOperationId`.

## Exact execution reconciliation

| Lane | Source | Carrier/run | Result | Evidence class |
| --- | --- | --- | --- | --- |
| Append acknowledgement | Codex #97 `926e0bc5a32b136f31b9eaae75e2de4abc20fa95` | #98 `8161e9ee3423d78768263e8838bd6e4800178902`, run `30598744048` | exact source/carrier fences, formatting, exact `4/4`, complete `codex-thread-store` package passed | `target-executed` |
| Receipt wire predecessor | #95 `15414d7e5da8109e03dca24111664b272e4a5717` | #96 `5873af57e20cfa70b471539520e7d8649257919c`, run `30598182882`, job `91055038170` | ancestry and fences passed; formatting failed; zero target tests | `carrier-diagnostic` |
| Tool effect predecessor | #99 `860f6babd420587dccc9e0d414f18ed157690958` | #100 `d835c7966cc86d54838e4ecc4860905874f77057`, run `30599039767` | ancestry and fences passed; formatting failed; zero target tests | `carrier-diagnostic` |

Append source #97 is ready for independent complete-diff review at its executed head.

## Formatter successors

### Receipt wire

- formatter publisher #102 head `0239f6fc3b39264f971498ce4a333fd740d29b9f`;
- formatter run `30623218584`: passed;
- clean source #104 head `8b31601977ccedce8a1c79c81b1b055d733402a9`;
- exact public-base diff: `protocol/src/lib.rs` and `protocol/src/tool_operation.rs`;
- renewed carrier #105 head `f0cd2db176c1436cf669f32b18eed00161fb76b0`;
- renewed run `30623383624`: in progress at record creation.

### Runtime effect

- formatter publisher #103 head `33ae3bec35da74b3b99c60019207db6a949b8185`;
- formatter run `30623278602`: passed;
- clean source #106 head `b76d46832f8426cb8acb4031b00f41069c7d7014`;
- direct parent: formatted wire head `8b316019...`;
- exact stacked diff: `tools/src/lib.rs`, `tools/src/tool_executor.rs`, and `tools/src/tool_executor_tests.rs`;
- renewed carrier #107 head `f4ba705107a142767421322901b2d3cf731ee960`;
- renewed run `30623517422`: in progress at record creation.

The selected ownership remains:

- `codex-protocol` owns durable receipt types and serialization;
- `codex-tools` re-exports only `ToolOperationEffect` and owns runtime effect declaration;
- `codex-core` owns the live session ledger.

## Live session ledger slice

Publisher PR #108 is stacked on source #106.

- publisher head: `ec08dcba9ace50b2f233ccda89de5ffc87562645`;
- run: `30623693696`, queued at record creation;
- output branch: `fieldwork/83-live-receipt-ledger-464237`;
- source fence: five core files only.

The proposed ledger:

- uses one `HashMap<ToolOperationId, ToolOperationReceipt>`;
- stores Direct and Code Mode identities together;
- defaults late observations to potential mutation;
- turns repeated identity, duplicate persistence, and conflicting terminal observations into ambiguity;
- caps retained receipts at 1,024;
- caps each operation-identity component at 512 bytes;
- marks invalid identity and overflow as permanent coverage loss;
- preserves existing entries when overflow occurs;
- keeps read-only receipts outside mutation preflight blocking.

Nine exact controls plus a `codex-core` library compile gate must pass before the source-only output branch is accepted.

## Boundary

The live-ledger slice adds no dispatch wiring, direct-result persistence wiring, rollout envelope, replay, checkpoint installation, compaction enforcement, retry policy, or retirement. Those remain independently reviewable successors.

No merge, deployment, credentials, production mutation, or public upstream interaction occurred.
