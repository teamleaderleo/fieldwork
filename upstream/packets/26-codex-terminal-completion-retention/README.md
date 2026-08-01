# Unit 26 — Codex terminal completion retention

## Current disposition

**REPAIR**

The producer-retention change has authoritative historical execution evidence, and the current four-file source remains clean against current public Codex main. A unit-owned restack now exists at the current public revision. That restack has no execution receipt yet, and the latest retained-head carrier passed its nine exact controls before failing the broader `codex-core` gate. Independent review is also outstanding.

## Objective

Preserve terminal stdout and stderr bytes at the producer so a completed unified-exec process can return authoritative output even when:

- output arrived before the completion subscriber attached;
- a best-effort broadcast receiver lagged or closed;
- output contained invalid UTF-8;
- streamed output and the retained transcript overlap.

The change keeps normal completion authoritative while preserving prompt hard-termination behavior.

## Non-goals

- No public-upstream contact.
- No work on other Wave B units or shared-carrier neighbors.
- No changes to public Codex branches.
- No workflow-only result presented as product evidence.
- No claim that the current-main restack is ready before current-head execution and review.

## Assigned packet

- Packet path: `upstream/packets/26-codex-terminal-completion-retention/`
- Packet branch: `p0/435-unit-26-codex-terminal-completion-retention`
- Packet head: pinned in the completion handoff on [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)

## Current clean target-source branch

- Repository: [`teamleaderleo/codex`](https://github.com/teamleaderleo/codex)
- Branch: [`fieldwork/26-terminal-completion-retention-source`](https://github.com/teamleaderleo/codex/tree/fieldwork/26-terminal-completion-retention-source)
- Public base revision: [`670f69416bf91c5dfd8b58669e78050b584ff053`](https://redirect.github.com/https://github.com/openai/codex/commit/670f69416bf91c5dfd8b58669e78050b584ff053)
- Source head: [`a020d7bd3e7f6886c3fbc21d75b3110586df08f5`](https://github.com/teamleaderleo/codex/commit/a020d7bd3e7f6886c3fbc21d75b3110586df08f5)
- Source tree: `9a067c244d464e863a7b50978826ac9930df680b`
- Compare: [`670f694...a020d7b`](https://github.com/teamleaderleo/codex/compare/670f69416bf91c5dfd8b58669e78050b584ff053...a020d7bd3e7f6886c3fbc21d75b3110586df08f5)

The source head is a single commit over current public main and changes exactly four files:

- `codex-rs/core/src/unified_exec/async_watcher.rs`
- `codex-rs/core/src/unified_exec/async_watcher_tests.rs`
- `codex-rs/core/src/unified_exec/process.rs`
- `codex-rs/core/src/unified_exec/process_tests.rs`

The four source blobs are byte-identical to the reviewed live source in [Codex PR #125](https://github.com/teamleaderleo/codex/pull/125) at `ee605985012dc1b768f03f6b450db16dd5c0467e`:

| File | Blob |
|---|---|
| `async_watcher.rs` | `a0427969dec77d57f6bc3037108cd4be26125cd0` |
| `async_watcher_tests.rs` | `57002ea930169d2815aed51e42bbb37f27faedc8` |
| `process.rs` | `ca47e90159328921a3f469fd0dad72c91ef5f86a` |
| `process_tests.rs` | `b76c9151eb9b5a42e6e6cdfe4ef4b1c0c1686f58` |

## Evidence summary

### Strongest accepted execution

[Fieldwork PR #268](https://github.com/teamleaderleo/fieldwork/pull/268), run [`30587866332`](https://github.com/teamleaderleo/fieldwork/actions/runs/30587866332), passed:

- the nine named terminal-retention controls;
- the full `codex-core` library gate;
- integration-target compilation.

The executed source head/tree were:

- source head `8c7ea38419d790032db459816980e6b4dd38f574`
- source tree `563f90f55c0ebd9454171d24697d796cba1388d4`
- artifact `8777460316`
- artifact digest `sha256:9c6c4f6741ee2514e995849ca2bed9caf0f80b80fdbb3a9ea31565df3ebda2dd`

### Latest retained-head execution

[Codex PR #126](https://github.com/teamleaderleo/codex/pull/126), head `4c6352df86602b35e3ec9547530295a8cd9752c0`, guarded and tested source head `ee605985012dc1b768f03f6b450db16dd5c0467e` in run [`30651607704`](https://github.com/teamleaderleo/codex/actions/runs/30651607704), job [`91225943920`](https://github.com/teamleaderleo/codex/actions/runs/30651607704/job/91225943920).

Observed step result:

- checkout/setup/source guard: pass;
- baseline build: pass;
- exact nine controls: pass;
- broader focused `codex-core` gate: fail;
- integration compile: not reached.

The exact broader-gate failure text was unavailable through the retained connector log response, so it remains unclassified.

### Current-main restack

The unit-owned source head `a020d7bd3e7f6886c3fbc21d75b3110586df08f5` was created by reusing the four exact source blobs from PR #125 over current public main `670f69416bf91c5dfd8b58669e78050b584ff053`. It has no execution receipt yet.

## Direct history

- [Fieldwork issue #23](https://github.com/teamleaderleo/fieldwork/issues/23): original report, design, execution trail, and handoffs.
- [Fieldwork issue #239](https://github.com/teamleaderleo/fieldwork/issues/239): latest-head source/carrier chain.
- [Fieldwork PR #33](https://github.com/teamleaderleo/fieldwork/pull/33): original reproduction and design report.
- [Fieldwork PR #268](https://github.com/teamleaderleo/fieldwork/pull/268): authoritative execution export.
- [Fieldwork PR #292](https://github.com/teamleaderleo/fieldwork/pull/292): prior finding; its stale execution conclusion is superseded by run `30587866332` and later source heads.
- Codex source/carrier lineage: [#6](https://github.com/teamleaderleo/codex/pull/6), [#49](https://github.com/teamleaderleo/codex/pull/49), [#50](https://github.com/teamleaderleo/codex/pull/50), [#53](https://github.com/teamleaderleo/codex/pull/53), [#70](https://github.com/teamleaderleo/codex/pull/70), [#86](https://github.com/teamleaderleo/codex/pull/86), [#91](https://github.com/teamleaderleo/codex/pull/91), [#93](https://github.com/teamleaderleo/codex/pull/93), [#94](https://github.com/teamleaderleo/codex/pull/94), [#125](https://github.com/teamleaderleo/codex/pull/125), and [#126](https://github.com/teamleaderleo/codex/pull/126).

Shared-carrier records for unrelated units were read and excluded from this packet: Codex [#46](https://github.com/teamleaderleo/codex/pull/46), Codex [#48](https://github.com/teamleaderleo/codex/pull/48), and Fieldwork issue [#197](https://github.com/teamleaderleo/fieldwork/issues/197). Fieldwork issue #41 was also inspected after an ambiguous numeric reference and excluded as unrelated.

## Remaining blockers

1. Execute the current unit-owned source head `a020d7bd3e7f6886c3fbc21d75b3110586df08f5` with a clean carrier pinned to current public base `670f69416bf91c5dfd8b58669e78050b584ff053`.
2. Run the nine exact controls, full `codex-core` library gate, and integration-target compile.
3. Capture the full failure text if the broader gate fails again, then classify source, baseline, runner, or carrier behavior.
4. Obtain independent review of the four-file diff and the stream-semantics risks.
5. Keep public-upstream contact gated by invitation.

## Continuation action

Create a carrier branch from `a020d7bd3e7f6886c3fbc21d75b3110586df08f5`, copy the guarded paired baseline/source execution from PR #126, pin every source/base SHA, preserve full logs and artifacts, then update this packet and issue #435 with the exact run and resulting disposition.
