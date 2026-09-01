# cmux ssh-tmux paste current-main refresh

Date: 2026-09-01  
Programme: high-leverage-open-source  
Upstream contact authorized: `false`

## In simple words

A golden candidate clears the consequence/proofability bar: ssh-tmux silently drops an entire paste at a deterministic byte boundary. The upstream report gives an exact discriminator: 9,994 bytes arrive, while 9,995 bytes yield zero bytes. Current `main` still encodes one logical input event as one hex-expanded `tmux send-keys -H` control command, so the failing path remains live.

There is already strong active upstream work for this lane. The contribution target is therefore a **current-main refresh/extraction of the paste slice from the existing PR**, plus an independent writer-level regression, instead of a competing rewrite.

## Question

Can the active ssh-tmux send-key batching fix be isolated onto exact current `main` with a deterministic red/green proof for the reported 9,995-byte silent-loss boundary?

## Exact upstream state

Repository: `manaflow-ai/cmux`  
Issue: https://redirect.github.com/manaflow-ai/cmux/issues/10943  
Existing active candidate: https://redirect.github.com/manaflow-ai/cmux/pull/11219  
Current-main revision pinned for this scout: `244adb38efdb8dea6fde624b079a0083738049d5`  
Existing candidate base: `aafe92ec5864ac21cf60860f3cbf97045b60c8de`  
Existing candidate head: `6405524991a5d7d03a73ca60cb495eb2f5e30ba5`

At inspection time:

- the issue remained open;
- the existing PR remained open;
- current `main` was 90 commits ahead of that PR's base;
- the selected paste owners on current `main` still matched the pre-PR versions, so this lane is drifted by branch age rather than a conflicting rewrite in those owners;
- current `main` still sends literal ssh-tmux input through one unchunked hex-expanded `send-keys -H` command.

## Candidate ranking

| Candidate | Consequence | Proofability | Decision |
| --- | ---: | ---: | --- |
| ssh-tmux paste silently drops at 9,995 bytes — https://redirect.github.com/manaflow-ai/cmux/issues/10943 | 5/5 | 5/5 | **Selected.** Exact byte boundary, current source owner, active serious PR to refresh. |
| deep process-tree recursion crash — https://redirect.github.com/manaflow-ai/cmux/issues/7848 | 5/5 | 5/5 | Near-miss. Strong deterministic crash proof, but the lane already has multiple focused implementations: https://redirect.github.com/manaflow-ai/cmux/pull/7892 and https://redirect.github.com/manaflow-ai/cmux/pull/8802. |
| duplicate autoresumed agents share one session/transcript identity — https://redirect.github.com/manaflow-ai/cmux/issues/11043 | 5/5 | 4/5 | Near-miss. Dedicated recent work is already active at https://redirect.github.com/manaflow-ai/cmux/pull/11358. Transcript corruption after concurrent writes is **Unknown** from the retained report evidence. |
| config rewrite drops socket password and locks clients out — https://redirect.github.com/manaflow-ai/cmux/issues/8372 | 4/5 | 4/5 | Near-miss. Consequential and deterministic, with a broader persistence/config write owner and a less compact single behavior seam than the selected byte-boundary lane. |

## Source-confirmed boundary

Current `Sources/RemoteTmuxControlConnection+Commands.swift` takes all bytes from one logical send, expands every byte to lowercase hex arguments, and calls `sendInternal` once with one `send-keys -H` command. The issue's exact 9,994/9,995-byte observation therefore maps directly onto a single production owner.

The active PR introduces `RemoteTmuxSendKeysBatchBuilder` with an 8 KiB raw-byte command chunk, a 256 KiB logical-input admission limit, and a writer budget sized for the fully encoded logical event. Its app adapter sends the generated command list through the existing atomic batch enqueue path.

The ownership map for this refresh is:

- framing policy: `Packages/macOS/CmuxRemoteSession/Sources/CmuxRemoteSession/RemoteTmux/RemoteTmuxSendKeysBatchBuilder.swift`;
- app send-key adapter: `Sources/RemoteTmuxControlConnection+Commands.swift`;
- writer pending-byte budget: `Sources/RemoteTmuxControlConnection.swift`;
- pre-MainActor input admission budget: `Sources/RemoteTmuxPaneInputForwarder.swift`;
- existing paste/backpressure tests: `cmuxTests/RemoteTmuxAuthTests.swift`;
- independent exact-boundary regression: `cmuxTests/RemoteTmuxSendKeysBoundaryTests.swift`.

## Overlap decision

The selected implementation is an extraction of the ssh-tmux paste/input slice from the active upstream PR, not a new competing design. The upstream PR bundles recovery and Codex-hook work alongside the paste fix; this owned-fork candidate carries only the paste production owners and paste tests needed on current `main`.

This honors the stronger contribution lane: refresh technically serious existing work whose production owners have survived branch drift, while supplying a current-main proof receipt.

## Owned-fork candidate

Owned repository: `teamleaderleo/cmux`  
Owned exact-base branch: `fieldwork/upstream-main-244adb38`  
Owned candidate branch: `fix/ssh-tmux-sendkeys-current-main`  
Owned draft PR: https://github.com/teamleaderleo/cmux/pull/3

Red commit: https://github.com/teamleaderleo/cmux/commit/00f86777f311f0bfe014b54c45bbac16624cb3cf  
Green commit: https://github.com/teamleaderleo/cmux/commit/779e8e3fefe38f4a839a287124101e42126e004e

Ancestry:

- red parent = exact upstream `244adb38efdb8dea6fde624b079a0083738049d5`;
- green parent = red `00f86777f311f0bfe014b54c45bbac16624cb3cf`;
- candidate is two commits ahead of the owned exact-base branch.

The red commit adds one test file. The green commit carries the four production paste owners plus the existing PR's paste test migration. The resulting owned PR has six changed files total.

## Discriminating proof

`RemoteTmuxSendKeysBoundaryTests.boundaryPasteIsSplitIntoControlSafeCommands` sends exactly 9,995 deterministic bytes through a real `RemoteTmuxControlConnection` wired to a real `RemoteTmuxControlPipeWriter`. It captures newline-delimited control commands and requires all of these properties:

1. the logical send is accepted;
2. at least two wire commands are emitted;
3. every emitted command is below 30,000 UTF-8 bytes;
4. decoding and concatenating all hex arguments reproduces the original 9,995 bytes exactly.

On the red commit, current-main production code emits one command for the whole logical event, so the command-count and command-size discriminator is expected to fail. On green, the extracted builder emits bounded ordered chunks and the existing batch writer enqueues them as one logical payload.

Fork verifier: https://github.com/teamleaderleo/cmux/actions/runs/33531328494  
CI result: **IN PROGRESS at scout-record creation; final status will be updated in this record.**

The verifier configuration lives on the owned default branch outside the candidate diff and checks the exact base/red/green ancestry before executing the focused red/green test, package tests, and repository guards.

## Claim-scoped evidence

- Current upstream revision and current production implementation: `source-read`.
- 9,994-byte success / 9,995-byte total-loss boundary: `upstream-report` from the issue; independent live remote-host reproduction in this scout is **Unknown**.
- Existing PR design, test claims, base/head, and active state: `upstream-pr-report` plus `source-read` of its changed paste files.
- Current-main candidate ancestry and six-file diff: `fork-authored` and GitHub compare evidence.
- Red/green focused regression execution: **Pending** until the retained fork verifier completes.
- Package tests and repository guards: **Pending** until the retained fork verifier completes.
- The precise tmux-internal implementation reason for the observed control-command ceiling: **Unknown**; the deterministic externally observed byte boundary and current one-command encoding are sufficient for the candidate proof.
- Maintainer preference for merging the extracted refresh versus the existing bundled PR: **Unknown**.
- Upstream submission, comment, label, push, review, or other mutation from this scout: absent.

## Current conclusion

**Golden candidate selected: refresh/extract the active ssh-tmux large-paste fix onto current main.**

Consequence: **5/5**. An entire paste can disappear silently in a remote terminal workflow at a deterministic boundary.  
Proofability: **5/5**. The exact 9,995-byte fixture can be discriminated at the real control writer by command count, maximum wire-command size, and byte-for-byte reconstruction.

The candidate is already isolated on the owned fork with an exact-base red/green split and a draft owned PR. Upstream contact authorization remains `false`.

## Stop condition

Implementation is complete on the owned fork. The scout stops after the retained verifier result is recorded here. No upstream mutation is authorized.
