# Executed failure-boundary receipt — 2026-08-03

## Scope

This receipt consolidates completed Windows observations that materially change the uv self-update audit. It separates executed product behavior from prototype and harness failures.

Public upstream contact authorized/performed: `false` / `false`.

## 1. self-replace ordinary error removes canonical executable

- owned carrier: `teamleaderleo/uv#10` — closed without merge after transfer;
- exact head: `34031835cbfe8b84edaf8e3ce5d6d846bc50d59e`;
- run/job: `30754221525` / `91513487808`;
- workflow conclusion: success;
- platform: Windows Server 2025;
- helper result: expected error exit `42` for nonexistent replacement source;
- filesystem result: canonical copied helper executable absent;
- artifact: `8836256601`;
- digest: `sha256:2d4ab5cfa6649c86a8e67a4f774ddbcb16f5e634138f396e67223f67d185580b`.

Evidence class: `target-executed`.

Supported conclusion: self-replace 1.5.0 can return an ordinary error after the canonical executable has been renamed away. The public candidate's broad failed-installation guarantee cannot rely on this primitive without additional rollback or narrower wording.

## 2. public candidate leaves mixed binary generation after finalizer error

- owned execution-only carrier: `teamleaderleo/uv#17` — closed without merge after transfer;
- exact public candidate base: `77e107dd2665f660c461998bc83174bf26ee7cf6`;
- exact carrier head: `e8b7a3ae5bbdc2d70832985a709e9a5c97a4baf1`;
- run/job: `30754972997` / `91515482594`;
- workflow conclusion: success;
- focused test: `fieldwork_companion_copy_survives_finalizer_failure_as_mixed_generation`;
- test result: one passed, zero failed;
- filesystem result: old live `uv.exe`, new live `uvx.exe`;
- artifact: `8836688193`;
- digest: `sha256:8cce47b0ad3862fbb7f199b21276926ba980c9675af51b092fbf8ecef894e02c`.

Evidence class: `target-executed`.

Supported conclusion: preserving canonical `uv.exe` does not imply coherent installation generation. The candidate's companion-copy order commits live state before the final current-executable operation.

## 3. silent-breakaway Job policy permits descendant escape

- owned experiment: `teamleaderleo/uv#19`;
- exact head: `6098dab64d959f9cf40fb44bbd8d4849c3aa9239`;
- exact successful branch run/job: `30755788490` / `91517588607`;
- workflow conclusion: success;
- observed current policy: assigned parent terminated, delayed descendant survived and wrote marker;
- observed strict policy: assigned parent and inherited descendant terminated before marker;
- artifact: `8837070751`;
- digest: `sha256:ef0f8df1cae24898ad18abafef046d473b2fd3b47d72db96cebd212e18813998`.

Evidence class: `target-executed synthetic policy discriminator`.

Supported conclusion: uv's current Job Object policy is not a full process-tree ownership guarantee. Strict policy is mechanically stronger but requires real-installer compatibility review before product use.

A later workflow on a stack-maintenance merge failed the exact file fence and is not a contradictory product result.

## 4. strict updater integration did not reach target execution

- owned stacked experiment: `teamleaderleo/uv#20`;
- exact tested head: `1e9fb3a337393ef72729877111455835f248bb1e`;
- run: `30755883089`;
- Windows job: `91517832885`;
- cross-target job: `91517832890`;
- artifact: `8837221189`;
- digest: `sha256:d41dc65294ee45b08b8fcb974300620c62d0bb1949664e0d1ce5c6bd26372454`.

Classification: `proposal compile failure / harness dependency gap`, not target behavior.

Findings:

- the workflow omitted rustfmt installation;
- more importantly, holding `uv_windows::Job` across `wait_with_output().await` made the updater future non-`Send` because the current raw HANDLE representation is not `Send`;
- `tokio::spawn` correctly rejected the future before the descendant-cancellation control ran.

Design consequence: the Job/process owner needs a sound asynchronous ownership abstraction or a dedicated supervisor thread/task. An unreviewed `unsafe impl Send` is not an acceptable shortcut.

## 5. deferred-finalizer current result

- owned draft: `teamleaderleo/uv#14`;
- exact source head under this run: `ead4f6b9ce0e7dc398d75dee47c80695e9494ee5`;
- run/job: `30794558226` / `91625090584`;
- build and rustfmt component setup: completed;
- hostile matrix: failed before the first parent-wait assertion;
- helper stderr: `Access is denied. (os error 5)` while opening the unrelated blocker process for synchronization;
- artifact: `8848451432`;
- digest: `sha256:879ab5c65854c99766bdeeff55352dd714bf5bdd90ed1c10b145cb796b5442ad`.

Classification: `harness authority failure`, no finalizer semantic result.

The successor harness should have a short-lived parent launch its own finalizer and pass its own PID, then use an explicit release marker before parent exit. This tests the intended parent-child authority rather than asking a sibling helper to open an unrelated process.

## 6. current public head refresh

Public PR `astral-sh/uv#20855` remains open and mergeable at:

- current head: `8d9324af47e1b52ec1f57f9232bd408281282cf5`;
- current CI run: `30785105065` — success.

The new commit `Preserve receipt during staged Windows updates` adds this ordering:

1. copy companions into live names;
2. promote the staged receipt into the live receipt path;
3. call self-replace for current `uv.exe`.

This fixes the stale-receipt omission but extends the partial-commit boundary. It does not add rollback for companion copies, receipt promotion, or final replacement.

Exact-current-head execution-only carrier:

- owned PR: `teamleaderleo/uv#26`;
- base: `8d9324af47e1b52ec1f57f9232bd408281282cf5`;
- carrier head: `481c0ca18ec6e319abc9ffa3ee961e4b1e7b253f`;
- question: after injected final replacement failure, is live state old `uv.exe`, new `uvx.exe`, and a new receipt?
- state at receipt creation: queued/pending; no result claimed.

## Review disposition

The public staging direction remains useful and should not be discarded. The evidence supports a focused `REPAIR` disposition:

- replace the non-discriminating regression;
- narrow the broad failure guarantee;
- repair ordinary final replacement rollback;
- treat binaries and receipt as one recoverable generation or record the partial state;
- explicitly scope custom/GHE routes and process-tree cancellation.
