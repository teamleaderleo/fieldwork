# cmux ssh-tmux large-paste candidate

Date: 2026-09-01  
Programme: high-leverage-open-source  
Worker: ChatGPT  
Claim scope: interface  
Upstream contact authorized: `false`

## In simple words

cmux's ssh-tmux path has a sharp reported paste cliff: 9,994 bytes arrive, while 9,995 bytes are discarded as a whole. The issue gives a byte-exact boundary and points to one small sender function. That makes this a strong contribution candidate because the symptom is consequential to the user and the responsible mechanism is unusually easy to prove.

An owned-fork candidate now preserves the existing binary-safe `send-keys -H` behavior while splitting the input into 4 KiB chunks and enqueueing the resulting tmux commands through the existing atomic batch path.

## Question

Can the reported 9,995-byte ssh-tmux paste loss be reduced to one bounded command-encoding defect and repaired without changing paste semantics?

## Assignment boundary

Expected deliverable: exact source/test map, red/green owned-fork candidate, fork CI, and recommendation.  
Owned output path: `programmes/high-leverage-open-source/scouts/cmux-ssh-tmux-large-paste/report.md`  
Dependencies: public upstream source/issue; owned cmux fork; GitHub-hosted macOS Actions.  
Target revision: `manaflow-ai/cmux` `342d3b5b9c94c8b1c524a8518a5dd356cf410bed`.  
Stop condition: candidate has a focused regression, bounded implementation, clean fork diff, and an executed fork verifier result; upstream remains read-only.

## Exact source state

Repository: https://github.com/manaflow-ai/cmux  
Reported issue: https://redirect.github.com/manaflow-ai/cmux/issues/10943  
Owned candidate PR: https://github.com/teamleaderleo/cmux/pull/2  
Candidate head: `416a2bb8c8f1ddc521119817d490973a236ee180`

The issue documents the exact observed boundary and root cause arithmetic: the current `sendKeys(paneId:data:)` hex-encodes all bytes into one control command. The command crosses the observed control-channel ceiling immediately after 9,994 input bytes.

## Code and test map

Production owner: `Sources/RemoteTmuxControlConnection+Commands.swift`

- `sendKeys(paneId:data:)` creates `send-keys -t %<pane> -H <hex...>`.
- `hexByteArguments` expands each byte to two hex digits plus a separator.
- `sendBatchInternal` already provides an all-at-once enqueue boundary for multiple commands.

Regression owner: `cmuxTests/RemoteTmuxAuthTests.swift`

- existing coverage already pins the hex encoding;
- the new focused test attaches the real test pipe, sends 9,995 bytes, and requires three `.other` command-result slots.

## Red / green candidate

1. `a26d0a5258842d51510935b99f2502ae677c5527` — test only. Pre-fix behavior enqueues one oversized command, so the new expectation is red.
2. `416a2bb8c8f1ddc521119817d490973a236ee180` — fix. Raw input is chunked as 4,096 + 4,096 + 1,803 bytes for the reported case and all commands are submitted through one batch enqueue.

Complete candidate diff: two files; no fork-main customization is included.

## Proofability / consequence

**Proofability: 5/5.** The reported boundary is byte-exact, the command-size arithmetic predicts it, the production owner is one function, and the regression can observe the existing command queue directly.

**Consequence: 4/5 at interface scope.** Documented symptom: a paste above the boundary delivers zero bytes in ssh-tmux. This report does not claim broader adoption or ecosystem impact.

**Cross score: excellent.** The issue combines an unambiguous user-visible failure with a tiny discriminating test and a narrow repair.

## Fork execution

Fork verifier workflow: https://github.com/teamleaderleo/cmux/actions/runs/33526441734

The verifier lives on the owned fork's default branch and explicitly checks out the candidate ref, so it does not enter the upstream-facing PR diff. It uses a GitHub-hosted macOS runner, upstream-style GhosttyKit/toolchain setup, runs `cmuxTests/RemoteTmuxAuthTests`, and then runs repository guards.

Status at initial record creation: running. Update this section with the final job result before treating execution as complete.

## Evidence labels

- Exact 9,994/9,995 symptom and reproduction: **Documented** in the public issue.
- Current source mechanism and candidate diff: **Observed** by source inspection on pinned revisions.
- Chunk sizes and generated command-length bounds: **Observed** by deterministic calculation against the candidate.
- Full macOS test execution: **Unknown** until the owned-fork verifier completes.
- Broader operational or ecosystem consequence: **Unknown** and outside this scout's supported scope.

## Recommendation

Retain as a high-priority contribution candidate. If the fork verifier passes, prepare an upstream packet for human review; do not mutate upstream without a fresh bounded greenlight.
