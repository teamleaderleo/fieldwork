# cmux ssh-tmux paste current-main refresh

Date: 2026-09-01  
Programme: high-leverage-open-source  
Upstream contact authorized: `false`

## Verdict

**Golden candidate selected:** refresh/extract the active ssh-tmux large-paste fix onto current `main`.

The bug is silent total input loss at an exact byte boundary. The upstream report records 9,994 pasted bytes arriving intact and 9,995 yielding zero bytes. Current `main` still encodes one logical send as one hex-expanded `tmux send-keys -H` control command, so the reported failure path remains live.

There is already serious active upstream work. The contribution lane is a current-main extraction/refresh of that paste slice, plus an independent writer-level 9,995-byte discriminator, rather than a competing implementation.

## Exact upstream state

Repository: `manaflow-ai/cmux`  
Issue: https://redirect.github.com/manaflow-ai/cmux/issues/10943  
Existing active PR: https://redirect.github.com/manaflow-ai/cmux/pull/11219  
Current-main revision pinned for this handoff: `eaa899cb20bd411019744fbd2bdedeb397f3070b`  
Existing PR base: `aafe92ec5864ac21cf60860f3cbf97045b60c8de`  
Existing PR head: `6405524991a5d7d03a73ca60cb495eb2f5e30ba5`

At the final refresh point:

- issue 10943 remained open;
- PR 11219 remained open;
- current `main` still had the same unchunked `sendKeys` owner as the existing PR base;
- the final upstream move from `6b425641ae4d474e77854da535442af2a0d0a475` to `eaa899cb20bd411019744fbd2bdedeb397f3070b` changed only `cmux-tui/crates/cmux-tui-core/src/server.rs`;
- none of the six selected paste source/test owners changed in that move.

## Candidate ranking

| Candidate | Consequence | Proofability | Decision |
| --- | ---: | ---: | --- |
| ssh-tmux paste silently drops at 9,995 bytes — https://redirect.github.com/manaflow-ai/cmux/issues/10943 | 5/5 | 5/5 | **Selected.** Exact byte boundary, live current source owner, active serious PR to refresh. |
| deep process-tree recursion crash — https://redirect.github.com/manaflow-ai/cmux/issues/7848 | 5/5 | 5/5 | Near-miss. Strong deterministic crash proof, with multiple focused implementations already active: https://redirect.github.com/manaflow-ai/cmux/pull/7892 and https://redirect.github.com/manaflow-ai/cmux/pull/8802. |
| duplicate autoresumed agents share one session/transcript identity — https://redirect.github.com/manaflow-ai/cmux/issues/11043 | 5/5 | 4/5 | Near-miss. Dedicated recent work is already active at https://redirect.github.com/manaflow-ai/cmux/pull/11358. Transcript corruption after concurrent writes is **Unknown** from retained evidence. |
| config rewrite drops socket password and locks clients out — https://redirect.github.com/manaflow-ai/cmux/issues/8372 | 4/5 | 4/5 | Near-miss. Consequential and deterministic, with a broader persistence/config write owner and a less compact single behavior seam than the selected byte-boundary lane. |

## Source-confirmed boundary

Current `Sources/RemoteTmuxControlConnection+Commands.swift` takes all bytes from one logical send, expands every byte to lowercase hex arguments, and calls `sendInternal` once with one `send-keys -H` command.

The upstream issue records the exact command-length discriminator for a single-digit pane identifier:

- 9,994 raw bytes -> 30,000-character command -> 9,994 bytes received;
- 9,995 raw bytes -> 30,003-character command -> zero bytes received.

The selected paste slice introduces `RemoteTmuxSendKeysBatchBuilder` with an 8 KiB raw-byte command chunk, a 256 KiB logical-input admission limit, and a writer budget sized for the fully encoded logical event. Its app adapter sends the generated command list through the existing atomic batch enqueue path, preserving one logical admission decision under writer backpressure.

## Production and test owners

The owned refresh changes six files:

- framing policy: `Packages/macOS/CmuxRemoteSession/Sources/CmuxRemoteSession/RemoteTmux/RemoteTmuxSendKeysBatchBuilder.swift`;
- framing policy tests: `Packages/macOS/CmuxRemoteSession/Tests/CmuxRemoteSessionTests/RemoteTmuxSendKeysBatchBuilderTests.swift`;
- app send-key adapter: `Sources/RemoteTmuxControlConnection+Commands.swift`;
- writer pending-byte budget: `Sources/RemoteTmuxControlConnection.swift`;
- pre-MainActor input admission budget: `Sources/RemoteTmuxPaneInputForwarder.swift`;
- real writer/admission/boundary tests: `cmuxTests/RemoteTmuxAuthTests.swift`.

## Overlap decision

The selected implementation is an extraction of the ssh-tmux paste/input slice from active PR 11219, with one independent exact-boundary behavior test. The upstream PR bundles SSH recovery and Codex-hook work alongside the paste fix; the owned candidate carries only the paste production owners and paste tests needed for this lane.

The active upstream review also contains an unresolved CodeRabbit ownership finding against the new static-only `RemoteTmuxSendKeysBatchBuilder`. Current repository guidance in `.github/review-bot-rules/no-ambient-global-state.md` supports that concern: production behavior should live on a constructable/injectable/testable owner instead of a static-helper namespace. A repair was prepared on a superseded owned branch, but the final exact-current PR intentionally remains a faithful paste-slice extraction. Upstream acceptance of that static-only design is therefore **Unknown**, and the owned PR remains draft.

## Owned-fork state

Owned repository: `teamleaderleo/cmux`  
Owned exact-base branch: `fieldwork/upstream-main-eaa899cb`  
Owned candidate branch: `fix/ssh-tmux-sendkeys-eaa899cb`  
Owned draft PR: https://github.com/teamleaderleo/cmux/pull/4

Red commit: https://github.com/teamleaderleo/cmux/commit/f87269d4f7e67ed3fa8fcea52c4fc375bc669ce5  
Green commit: https://github.com/teamleaderleo/cmux/commit/dd4c6bb4d8c61be2ce1356a86780e6821e940e42

Ancestry:

- red parent = exact upstream `eaa899cb20bd411019744fbd2bdedeb397f3070b`;
- green parent = red `f87269d4f7e67ed3fa8fcea52c4fc375bc669ce5`;
- candidate is exactly two commits ahead of the owned exact-base branch.

The red commit changes only the already-wired `cmuxTests/RemoteTmuxAuthTests.swift`. The green commit adds the four production paste owners, the active PR's package framing tests, and its app-level admission/backpressure test migration while retaining the independent 9,995-byte behavior check. No Xcode project-file edit is required.

Superseded owned PR https://github.com/teamleaderleo/cmux/pull/3 was closed. Its delayed repair workflow can only touch the obsolete branch and cannot alter final PR 4.

## Discriminating proof

The regression sends exactly 9,995 deterministic bytes through a real `RemoteTmuxControlConnection` wired to a real `RemoteTmuxControlPipeWriter`. It captures newline-delimited control commands and requires:

1. logical send accepted;
2. at least two wire commands emitted;
3. every emitted command below 30,000 UTF-8 bytes;
4. decoding and concatenating all hex arguments reproduces the original 9,995 bytes exactly.

On the red source, current production emits one 30,003-byte command for that logical event. On green, the extracted builder emits two bounded ordered commands.

A retained source-level execution probe using the exact current framing formula and extracted builder logic records:

- current 9,994-byte command = 30,000 bytes;
- current 9,995-byte command = 30,003 bytes;
- green 9,995-byte command count = 2;
- largest green command for that fixture = 24,594 bytes;
- green byte-for-byte reconstruction = true;
- maximum logical input = 262,144 bytes;
- maximum encoded writer payload observed by the probe = 787,040 bytes;
- production writer budget = 1,048,576 bytes;
- one byte above the logical input limit is rejected.

Retained probe: `programmes/high-leverage-open-source/scouts/cmux-ssh-tmux-paste-refresh/source-framing-probe.json`.

## CI result

### App-host verifier

Owned Fieldwork run: https://github.com/teamleaderleo/fieldwork/actions/runs/33536448895  
Job id: `99951817878`  
Evidence label: `target-executed-blocked`

The run successfully completed exact checkout/ancestry validation, Xcode selection, Bun/GhosttyKit/Zig/Rust setup, DerivedData setup, and Swift package resolution. The red regression then **did not execute** because the current app target failed compiling unrelated `Sources/TerminalController+Extensions.swift` code first.

Observed missing socket-routing symbols included:

- `SocketRequestTransactionContext`;
- `SocketResponseReadbackPolicy`;
- `requestContextRegistry`;
- `requestResponseRoutingRegistry`;
- `SocketResponseRoutingClient`.

The red commit touches only `cmuxTests/RemoteTmuxAuthTests.swift`, so this compile gate is outside the candidate diff. Current-main code search produced no defining result for the named missing socket-routing types/registries. Root cause of that upstream compile break is **Unknown**.

Retained diagnosis: `programmes/high-leverage-open-source/scouts/cmux-ssh-tmux-paste-refresh/ci-diagnosis.json`.

### Package tests and repository guards

Owned macOS package verifier: https://github.com/teamleaderleo/fieldwork/actions/runs/33537874789  
Owned Linux package verifier: https://github.com/teamleaderleo/fieldwork/actions/runs/33538090467

At handoff both remained queued without a runner. Their result is **Unknown**. No green package/guard claim is made.

### CI summary

- source-level framing discriminator: **PASS** (`source-model-executed`);
- exact candidate ancestry: **PASS** on the executed app-host verifier for the immediately preceding current-main pin; the final upstream delta touched only cmux-tui and final PR 4 was rebuilt directly on `eaa899cb20bd411019744fbd2bdedeb397f3070b`;
- macOS app-host red/green regression: **BLOCKED before test execution** by unrelated current-main compile errors;
- package framing/full package tests: **Unknown / queued**;
- repository guards: **Unknown / queued**.

## Claim-scoped evidence

- current upstream revision and current production implementation: `source-read`;
- 9,994 success / 9,995 total-loss boundary: `upstream-report`; independent live remote-host reproduction in this scout is **Unknown**;
- existing PR design, base/head, tests, review state: `upstream-pr-report` plus `source-read`;
- current-main candidate ancestry and six-file diff: `fork-authored`;
- exact framing math and extracted builder round-trip: `source-model-executed`;
- app-host compilation attempt: `target-executed-blocked`;
- package tests and guards: **Unknown** at handoff because owned runs remained queued;
- precise tmux-internal origin of the observed 30,000-character control-command ceiling: **Unknown**;
- maintainer preference for the extracted refresh versus bundled PR 11219: **Unknown**;
- upstream submission, comment, label, push, review, or other mutation from this scout: absent.

## Scores

Consequence: **5/5**. An entire paste can disappear silently in a remote terminal workflow at a deterministic boundary.  
Proofability: **5/5**. The 9,995-byte fixture has a crisp wire-level discriminator: command count, maximum command size, and exact byte reconstruction.

## Stop condition

Satisfied for scouting and owned-fork implementation. A golden candidate exists and is isolated on exact current main. CI has a retained upstream compile blocker and queued package/guard runs, so those claims remain scoped accordingly. Upstream contact authorization stays `false`.
