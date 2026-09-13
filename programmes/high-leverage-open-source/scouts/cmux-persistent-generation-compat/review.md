# Review — cmux persistent-generation compatibility

Date: 2026-09-01  
Work class: upstream-fork research + evidence/documentation; owned-fork workflow is an execution carrier  
Scout: #927  
Upstream contact authorized: `false`

## Reviewed inputs

- assignment-time target pin: `manaflow-ai/cmux@8ef183f1e5de765b183aec9d1799f17a0848ae84`;
- exact dynamically executed artifact: `eaa899cb20bd411019744fbd2bdedeb397f3070b`;
- released comparison: `v0.64.22@ddd4a01bc5d8ebac19643930f5fd7d40e85f1534`;
- protocol-only comparison: `ae830c381bb846609230fc155a7fcdcd5e06b4d0` -> `a23c328f58738e58f692ef7e0e23ec5c194cf383`;
- additive-column comparison: `c4d7ee75205b01ddac887e5cd0c80bda83972281` -> `c5e2c64b704ae4ed0ebdc5140a4a4e003da8bcff`;
- canonical result files: `report.md`, `binary-generation-map.md`, and retained `artifacts/` receipts;
- owned-fork execution carrier: `teamleaderleo/cmux@40013d90654d86f9561ad3bf00272655525f467b`, run `33544120861`.

## Decision-bearing claims and evidence class

1. **Interrupted generic terminal input cannot be reconciled to one external delivery reality after daemon replacement.** `target-executed` at `eaa899cb...`. Two executions with identical durable `executing` state recover to `indeterminate` while the child consumed zero bytes in one branch and one byte in the other.
2. **Correlated terminal creation can reconcile a surviving host across the same daemon-generation replacement.** `target-executed` positive control at `eaa899cb...`; same host PID/incarnation/shell survives and replay converges to one creation.
3. **Current workspace migrations have a typed newer-schema preflight and transactional schema-number advancement.** `source-read` at assignment pin `8ef183f1...`.
4. **The no-schema-bump `terminal_hosts.on_exit` change preserves B-only `keep` across an A-style old update and defaults an A insert to `close`.** `model-executed` with exact source SQL.
5. **Released v0.64.22 schema-8 -> current schema-14 rollback and protocol-3 -> protocol-4 live-host rollback have exact target-native probes prepared.** `target-test-prepared`; workflow jobs remain queued at review time.
6. **Remote auth, daemon key pinning, protocol compatibility, cloud persistent-home bootstrap, and macOS restore fences are mapped from current source.** `source-read` only where dynamic provider/app execution is absent.

## Negative controls preserved

- same-binary clean reopen;
- completed terminal input exact replay;
- correlated creation survivor adoption;
- short-lived child exit reconciliation;
- additive-column old-writer compatibility model;
- current newer-workspace-schema refusal regression in source;
- fresh-B / A->A / A->B / B->A byte comparisons encoded in the queued carrier.

## Evidence that remains missing

- target execution of the prepared cross-binary jobs;
- macOS A/B restore execution;
- real cloud compute destruction/resurrection on one retained home volume;
- executable auth-v1 -> auth-v2 -> v1 rollback pair;
- interruption during SQLite + pepper sidecar cleanup;
- independently installed remote daemon versus older bundled client end-to-end.

## Self-review result

**ACCEPT for synthesis** of the proven daemon-generation finding and the current persistent-state/version map.

**EXECUTE** remains the disposition for the cross-binary carrier. A queued workflow is platform admission only. Any later result that changes the binary-transition interpretation must update the canonical scout files before promotion.

No source patch is proposed. The proven terminal-input ambiguity points to the persistent terminal-host / PTY-input owner as the smallest place capable of adding a per-operation delivery witness. The binary rollback branches remain evidence gathering until execution distinguishes clean refusal from mutation, hidden fresh-state fallback, or terminal identity loss.

Third-party upstream remained read-only throughout this scout.
