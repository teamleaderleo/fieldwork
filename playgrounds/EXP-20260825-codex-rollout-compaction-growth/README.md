# Experiment: Codex rollout compaction storage growth

Experiment ID: `EXP-20260825-codex-rollout-compaction-growth`

State: `complete — retained for human review`

Target label: `target:codex`

Target hub: Fieldwork #8

Claim scope: `operational` for one directly measured local session store; `source-read` for the public implementation boundary

Related finding: [Fieldwork #776](https://github.com/teamleaderleo/fieldwork/issues/776)

Owner: `codex:gpt-5.6-sol`

Date: 2026-08-25

## In simple words

Codex deliberately writes a `compacted` checkpoint containing a full `replacement_history` whenever it starts a new context window. In this observed local snapshot, those checkpoints grew without a rollout byte budget: **all 6,246 compacted records contain the `replacement_history` field and occupy 28.32 GB, or 83.1% of all retained session bytes**. The eight files above 1 GiB are 91.4–94.8% compacted checkpoints.

The checkpoint mechanism is intentional; this scale is not ordinary chat text. Current public source appends each full replacement history to the rollout, keeps prior checkpoints in the journal, and reconstructs from persisted compacted records. The documented `history.max_bytes` setting applies to `history.jsonl`, not these rollout files. This packet extends the existing oversized-rollout finding with a content-safe attribution of the on-disk producer.

## Question

Do persisted compacted replacement-history records account for most of the bytes in one observed multi-gigabyte Codex session store?

## Change thesis

- **Current behaviour — Documented:** each compaction persists `replacement_history: Some(items.clone())` as a new append-only rollout item.
- **Current behaviour — Observed:** compacted records account for 28,319,667,945 of 34,059,784,421 bytes in the measured snapshot.
- **Consequence — Observed and linked:** the stable snapshot alone occupied 31.72 GiB on a machine that had only 6.2 GiB free before cleanup. Fieldwork #776 separately observed app-server hydrating multi-GB rollouts into a 16 GB physical-footprint peak.
- **Candidate improvement — Inferred:** add a rollout persistence budget and a recovery-compatible checkpoint compaction, deduplication, or rewrite policy; do not rely only on read-time hydration limits.
- **Boundary:** this experiment does not select a safe deletion or rewrite algorithm, prove ecosystem prevalence, or map the exact public-source commit bundled in Desktop.

## Sources and environment

### Current public source pin

Source: [OpenAI Codex `c3953649156e15b67e572cb9e38bc825a811c24e`](https://github.com/openai/codex/commit/c3953649156e15b67e572cb9e38bc825a811c24e), retrieved 2026-08-25.

The relevant source boundaries are:

1. `codex-rs/history/src/lib.rs:94-155` defines `RolloutItem::Compacted` and its optional full `replacement_history`.
2. `codex-rs/core/src/session/mod.rs:3451-3485` clones the current annotated history into every new compacted item and persists it.
3. `codex-rs/core/src/session/rollout_reconstruction.rs:155-186` scans compacted records in reverse and selects the newest surviving replacement history as the replay base.
4. `codex-rs/rollout/src/recorder.rs:1009-1059` parses every rollout line and pushes every item into a `Vec` when full history is loaded.
5. `codex-rs/config/src/types.rs:192-212` limits `history.max_bytes` to `~/.codex/history.jsonl`; [the official configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) documents the same boundary and no equivalent rollout-session cap.

The existing public owner for oversized-rollout hydration is [OpenAI Codex issue 29510](https://redirect.github.com/openai/codex/issues/29510). No new public issue is proposed.

The upstream duplicate and fix-route review recommends one human-reviewed corroboration on [the existing replacement-history issue](https://redirect.github.com/openai/codex/issues/31198). Seven of the eight ≥1 GiB outliers are subagent rollouts; the 13.26 GB largest outlier is a root/VS Code rollout, which shows the producer is not limited to child histories. See `upstream-landscape.md` for the route decision and current partial mitigations.

### Measured environment

```text
ChatGPT Desktop: 26.818.61809 build 7019
bundled codex-cli: 0.149.0-alpha.4.3
macOS: 26.6.1 (25G76)
architecture: arm64
Python: standard library only
network during measurement: disabled/not used
```

The exact public-source commit corresponding to the bundled Desktop binary is unknown. The public source pin establishes the current persistence design, not binary identity.

## Inputs and privacy boundary

The analyzer scanned 368 local rollout JSONL files whose modification time was no later than `2026-08-25T14:10:00Z`. This fence is after the 13 GB outlier's final observed write and before this investigation's live rollout activity. It makes the retained input set stable while excluding eight active or newer files.

The analyzer did not JSON-decode transcript payloads and retained none of the following:

- paths or filenames;
- thread IDs;
- timestamps;
- prompts, messages, reasoning, or tool output;
- repository names or working directories.

It read each line as bytes, classified only the current top-level record type and optional payload type from a bounded prefix, and accumulated byte and record counts. For the ranked files it decoded the canonical session-metadata line, retained only the allow-listed coarse classes `vscode` or `subagent`, and discarded every other metadata field; unrecognized source values become `other`. The raw rollouts remain local and are not part of Fieldwork.

## Command

```text
python3 analyze_rollouts.py \
  --root <redacted-codex-sessions-root> \
  --modified-before 2026-08-25T14:10:00Z \
  --largest 12
```

## Actual result

| Measure | Observed value |
| --- | ---: |
| rollout files | 368 |
| total records | 2,231,479 |
| total bytes | 34,059,784,421 (31.72 GiB) |
| compacted records | 6,246 |
| compacted bytes | 28,319,667,945 (26.37 GiB) |
| compacted share | 83.1% |
| compacted records containing `replacement_history` | 6,246 (100%) |
| non-compacted bytes | 5.35 GiB |
| files at least 1 GiB | 8 |
| compacted record p90 | 9,248,165 bytes |
| compacted record p99 | 42,309,563 bytes |
| largest compacted record | 63,397,531 bytes |

The eight files above 1 GiB total 27.72 GiB. Compacted records account for 91.4%, 92.0%, 92.0%, 92.0%, 94.6%, 94.8%, 94.8%, and 94.8% of those files respectively.

The largest file is 13,260,971,182 bytes. Its 399 compacted records occupy 12,124,666,631 bytes, or 91.4% of that file.

### Negative control inside the same store

The tenth-largest rollout is 202,386,991 bytes and only 1.4% compacted records by byte size. The analyzer therefore does not mechanically classify every active rollout as checkpoint-dominated; the extreme concentration is specific to the pathological outliers.

## Interpretation

The result supports the second distinguishing outcome: repeated replacement-history checkpoints are the primary on-disk amplification mechanism in this incident. All 6,246 compacted records contained the literal `replacement_history` field; this attribution does not depend only on the public source shape.

The source design has a legitimate recovery purpose. Resume and fork reconstruction need a durable checkpoint plus its later suffix. A repair cannot simply delete every old `compacted` line without proving rollback, window-chain, fork, world-state, and late-result semantics. Plausible boundaries include:

- content-addressing or deduplicating checkpoint payloads;
- rewriting or compressing superseded windows while retaining the recovery graph;
- a per-thread byte budget with explicit quarantine/safe-mode behavior;
- bounded pagination instead of full-history hydration;
- size telemetry that triggers before one rollout consumes gigabytes.

Read-time hydration limits address the memory crash documented by Fieldwork #776 and the existing public issue. They do not prevent the append-only session store from exhausting disk. Both owners need guardrails.

## Uncertainty and threats to validity

- The analyzer depends on the current compact JSONL field order to classify the first top-level `type` from a 4 KiB prefix. The retained totals matched independent shell attribution on the largest records, but the script is not a general JSON parser.
- The modification-time fence excludes files still active after the observation boundary; it is a stable snapshot, not a claim about every byte currently under the sessions directory.
- The experiment measures one heavy local installation and does not establish frequency across users.
- It does not distinguish which tasks, tools, compaction modes, or context contents caused replacement histories to become large.
- The source pin is current public source on the observation date, but the exact bundled Desktop source revision is unavailable.
- Older compacted checkpoints may participate in rollback, fork, window-chain, world-state, or diagnostic behavior. The safe retention boundary remains a source-and-test question.

## Reproduction status

- [x] Plain-language block updated
- [x] Target label and hub recorded
- [x] Exact local command shape recorded with private path redacted
- [x] Source revision recorded
- [x] Evidence labels used
- [x] Deterministic on the declared snapshot
- [x] Negative control retained
- [ ] Independent reproduction available
- [ ] Cross-platform result available

## Disposition

Retain as a completed operational experiment and attach it to Fieldwork #776 after human review. The human owner gave a bounded greenlight for one corroborating comment on the exact replacement-history issue. That comment was submitted at `2026-08-25T15:44:38Z`; `upstream-submission.json` records its URL and the SHA-256 of the exact body. The duplicate review found enough evidence to corroborate, but no newly isolated producer that warrants another upstream issue.

## Boundaries

- Standing automated third-party upstream authority remains prohibited, so `upstream_contact_authorized` remains `false`.
- One bounded human greenlight authorized the recorded corroborating comment and was consumed by that interaction.
- No follow-up reply, edit, reaction, label, closure, or other upstream action is authorized.
- No transcript content, path, identifier, secret, production payload, or private repository material was retained.
- The human owner remains the final gate for any Fieldwork issue update or further upstream interaction.
