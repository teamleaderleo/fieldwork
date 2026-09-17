# Target execution follow-up — remote auth stale deletion

Date: 2026-09-01  
Fieldwork issue: #929  
Fieldwork PR: #932  
Target: `manaflow-ai/cmux`  
Exact tested target base: `8ef183f1e5de765b183aec9d1799f17a0848ae84`  
Regression-only head: `15210b38244e289ad750fe65ee07fc51f8854a56`  
Owned execution run: `33548418699`  
Job: `99991571843`  
Evidence class: `target-executed` for the stale-delete invariant and its settled-owner control  
Upstream contact authorized: `false`

## In simple words

The smallest lease-rotation defect now reproduces inside cmux's own Go package using the production `consumeWebSocketLease` function and the real `/admin/leases` handler.

The control consumes A completely before publishing B and passes. The overlapping test lets consumer A finish reading A, publishes B through `/admin/leases`, then lets A complete its single-use cleanup. Current source deletes B while finishing A.

This upgrades the stale-delete claim from the copied-function model to target execution. The torn-read and three-artifact mixing claims remain `model-executed` until separate target-native probes run.

## Exact execution

Runner: Ubuntu 24.04 / `ubuntu-latest`  
Go: `go1.22.12 linux/amd64`, selected from `daemon/remote/go.mod`

The carrier first proved its diff fence:

```text
merge-base(target, red) == target
changed file == daemon/remote/cmd/cmuxd-remote/ws_lease_generation_test.go
```

Negative control:

```text
go test ./cmd/cmuxd-remote \
  -run '^TestLeaseInstallAfterSingleUseConsumptionSurvives$' \
  -count=1 -v
```

Observed: PASS.

Discriminator:

```text
go test ./cmd/cmuxd-remote \
  -run '^TestSingleUseLeaseConsumptionDoesNotDeleteReplacementGeneration$' \
  -count=1 -v
```

Observed product-path failure:

```text
single-use cleanup for lease A deleted replacement lease B
```

The carrier treats that exact failure as the expected red result and completed successfully.

## Evidence update

The original `report.md` and `review.md` predate this hosted execution. Their statements that target-native Go execution was unexecuted are superseded for the stale-delete claim by this follow-up.

Current evidence split:

- stale A deletion of B: `target-executed`;
- settled-A then B publication control: `target-executed`;
- in-place torn JSON read: `model-executed`;
- first/second-artifact interruption: `model-executed`;
- concurrent X/Y mixed set: `model-executed`;
- actual daemon-process restart: `Unknown / unexecuted`;
- live Freestyle timing and production frequency: `Unknown`.

Current upstream has advanced to `manaflow-ai/cmux@2ead47750ab2f47c13972d0709d99cdcbaa8ad73`. The relevant lease/publication owners are source-continuous from the tested base: the intervening changes through `8ef183f1...` are cmux-tui sidebar UI, and `8ef183f1...` to `2ead4775...` changes CLA-policy CI files.

## Repair gate

The next bounded candidate should preserve two already distinguished properties without pretending to solve the whole generation transaction:

1. serialize daemon-admin publication with `consumeWebSocketLease` so A either settles before B publishes or B becomes current before a consumer reads it;
2. replace in-place JSON publication with temporary-file + atomic rename so readers outside the Go mutex cannot observe the truncate window.

The target-native stale-delete test is now the required red half for candidate work. A repair should turn it green while preserving the settled-owner control and existing daemon package tests.

PTY/RPC/RPC-client all-or-one publication remains a separate decision-bearing branch. Per-file locking or rename alone cannot provide that wider invariant.

## Remaining boundary

No actual `cmuxd-remote` restart or live Freestyle VM interleaving executed here. No third-party upstream mutation occurred.
