# cmux ssh-tmux paste current-main refresh

Date: 2026-09-01  
Programme: high-leverage-open-source  
Upstream contact authorized: `false`

## In simple words

A golden candidate clears the consequence/proofability bar: ssh-tmux silently drops an entire paste at a deterministic byte boundary. The upstream report gives an exact discriminator: 9,994 bytes arrive, while 9,995 bytes yield zero bytes. Current `main` still encodes one logical input event as one hex-expanded `tmux send-keys -H` control command, so the failing path remains live.

There is already strong active upstream work for this lane. The contribution target is a **current-main refresh/extraction of the paste slice from the existing PR**, plus an independent writer-level regression, instead of a competing rewrite.

## Question

Can the active ssh-tmux send-key batching fix be isolated onto exact current `main` with a deterministic red/green proof for the reported 9,995-byte silent-loss boundary?

## Exact upstream state

Repository: `manaflow-ai/cmux`  
Issue: https://redirect.github.com/manaflow-ai/cmux/issues/10943  
Existing active candidate: https://redirect.github.com/manaflow-ai/cmux/pull/11219  
Current-main revision pinned for this scout: `6b425641ae4d474e77854da535442af2a0d0a475`  
Existing candidate base: `aafe92ec5864ac21cf60860f3cbf97045b60c8de`  
Existing candidate head: `6405524991a5d7d03a73ca60cb495eb2f5e30ba5`

At the final implementation refresh point:

- issue 10943 remained open;
- PR 11219 remained open;
- current `main` still used the same unchunked `sendKeys` production owner as the existing PR base;
- the upstream commits that landed during this scout changed docs, TUI, release, and related files, while the selected paste owners and wired test owner stayed unchanged;
- the selected implementation therefore represents branch-age refresh work, with no competing rewrite discovered in the current paste owners.

## Candidate ranking

| Candidate | Consequence | Proofability | Decision |
| --- | ---: | ---: | --- |
| ssh-tmux paste silently drops at 9,995 bytes — https://redirect.github.com/manaflow-ai/cmux/issues/10943 | 5/5 | 5/5 | **Selected.** Exact byte boundary, live current source owner, active serious PR to refresh. |
| deep process-tree recursion crash — https://redirect.github.com/manaflow-ai/cmux/issues/7848 | 5/5 | 5/5 | Near-miss. Strong deterministic crash proof, with multiple focused implementations already active: https://redirect.github.com/manaflow-ai/cmux/pull/7892 and https://redirect.github.com/manaflow-ai/cmux/pull/8802. |
| duplicate autoresumed agents share one session/transcript identity — https://redirect.github.com/manaflow-ai/cmux/issues/11043 | 5/5 | 4/5 | Near-miss. Dedicated recent work is already active at https://redirect.github.com/manaflow-ai/cmux/pull/11358. Transcript corruption after concurrent writes is **Unknown** from retained evidence. |
| config rewrite drops socket password and locks clients out — https://redirect.github.com/manaflow-ai/cmux/issues/8372 | 4/5 | 4/5 | Near-miss. Consequential and deterministic, with a broader persistence/config write owner and a less compact single behavior seam than the selected byte-boundary lane. |

## Source-confirmed boundary

Current `Sources/RemoteTmuxControlConnection+Commands.swift` takes all bytes from one logical send, expands every byte to lowercase hex arguments, and calls `sendInternal` once with one `send-keys -H` command. The issue's exact 9,994/9,995-byte observation maps directly onto that production owner.

The issue records the wire math for a single-digit pane identifier:

- 9,994 raw bytes expand to a 30,000-character command and arrive intact;
- 9,995 raw bytes expand to a 30,003-character command and the remote receives zero bytes.

The active PR introduces `RemoteTmuxSendKeysBatchBuilder` with an 8 KiB raw-byte command chunk, a 256 KiB logical-input admission limit, and a writer budget sized for the fully encoded logical event. Its app adapter sends the generated command list through the existing atomic batch enqueue path, avoiding a partial logical paste under writer backpressure.

## Production and test owners

The owned refresh changes six files:

- framing policy: `Packages/macOS/CmuxRemoteSession/Sources/CmuxRemoteSession/RemoteTmux/RemoteTmuxSendKeysBatchBuilder.swift`;
- framing policy tests: `Packages/macOS/CmuxRemoteSession/Tests/CmuxRemoteSessionTests/RemoteTmuxSendKeysBatchBuilderTests.swift`;
- app send-key adapter: `Sources/RemoteTmuxControlConnection+Commands.swift`;
- writer pending-byte budget: `Sources/RemoteTmuxControlConnection.swift`;
- pre-MainActor input admission budget: `Sources/RemoteTmuxPaneInputForwarder.swift`;
- real writer/admission/boundary tests: `cmuxTests/RemoteTmuxAuthTests.swift`.

## Overlap decision

The selected implementation is an extraction of the ssh-tmux paste/input slice from the active upstream PR, with one independent exact-boundary behavior test. The upstream PR bundles recovery and Codex-hook work alongside the paste fix; this owned-fork candidate carries only the paste production owners and paste tests needed on current `main`.

This keeps priority on technically serious existing work while supplying a current-main proof receipt.

## Owned-fork candidate

Owned repository: `teamleaderleo/cmux`  
Owned exact-base branch: `fieldwork/upstream-main-6b425641`  
Owned candidate branch: `fix/ssh-tmux-sendkeys-current-main`  
Owned draft PR: https://github.com/teamleaderleo/cmux/pull/3

Red commit: https://github.com/teamleaderleo/cmux/commit/4719143f4a21ab2442397efe70643435c1f604f6  
Green commit: https://github.com/teamleaderleo/cmux/commit/a732c5994bb2a698a7330bb0516210411d9ca298

Ancestry:

- red parent = exact upstream `6b425641ae4d474e77854da535442af2a0d0a475`;
- green parent = red `4719143f4a21ab2442397efe70643435c1f604f6`;
- candidate is exactly two commits ahead of the owned exact-base branch.

The red commit changes only the already-wired `cmuxTests/RemoteTmuxAuthTests.swift`. The green commit adds the four production paste owners, the active PR's package framing tests, and its app-level admission/backpressure test migration while retaining the independent 9,995-byte behavior check. No Xcode project-file edit is required.

## Discriminating proof

The red regression sends exactly 9,995 deterministic bytes through a real `RemoteTmuxControlConnection` wired to a real `RemoteTmuxControlPipeWriter`. It captures newline-delimited control commands and requires all of these properties:

1. the logical send is accepted;
2. at least two wire commands are emitted;
3. every emitted command is below 30,000 UTF-8 bytes;
4. decoding and concatenating all hex arguments reproduces the original 9,995 bytes exactly.

On red, current-main production code emits one oversized command for the logical event, so command count and maximum command size discriminate the failure. On green, the extracted builder emits bounded ordered chunks and the existing batch writer enqueues them as one logical payload.

The active PR's retained package tests independently cover empty input, lowercase hex framing, nonzero-based `Data` slices, maximum-input writer budgeting including terminators, and rejection one byte above the logical input limit.

Fork verifier: https://github.com/teamleaderleo/cmux/actions/runs/33535960544  
CI result: **Queued at this record update.** The owned runner is occupied by a superseded earlier scout verifier; only run `33535960544` is authoritative for this exact-current candidate.

Verifier configuration lives on the owned default branch outside the candidate diff. It checks exact ancestry, requires the red test to fail at a Swift Testing expectation, runs the focused green writer tests, runs the package framing suite and full package tests, then executes repository guards.

## Claim-scoped evidence

- Current upstream revision and current production implementation: `source-read`.
- 9,994-byte success / 9,995-byte total-loss boundary: `upstream-report`; an independent live remote-host reproduction in this scout is **Unknown**.
- Existing PR design, test claims, base/head, and active state: `upstream-pr-report` plus `source-read` of its paste files.
- Current-main candidate ancestry and six-file diff: `fork-authored` plus GitHub compare evidence.
- Red/green focused regression execution: **Pending** until authoritative fork run `33535960544` completes.
- Package framing/full package tests and repository guards: **Pending** until authoritative fork run `33535960544` completes.
- The precise tmux-internal implementation source of the observed 30,000-character control-command ceiling: **Unknown**. The exact externally observed boundary and current one-command encoding provide the required discriminator.
- Maintainer preference for the extracted refresh versus the existing bundled PR: **Unknown**.
- Upstream submission, comment, label, push, review, or other mutation from this scout: absent.

## Current conclusion

**Golden candidate selected: refresh/extract the active ssh-tmux large-paste fix onto current main.**

Consequence: **5/5**. An entire paste can disappear silently in a remote terminal workflow at a deterministic boundary.  
Proofability: **5/5**. The exact 9,995-byte fixture discriminates the real control writer by command count, maximum wire-command size, and byte-for-byte reconstruction.

The candidate is isolated on the owned fork with an exact-base red/green split and a draft owned PR. Upstream contact authorization remains `false`.

## Stop condition

Implementation is complete on the owned fork. The remaining execution gate is the authoritative fork verifier. No upstream mutation is authorized.
