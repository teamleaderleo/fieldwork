# Exact-head self-review

## In simple words

This review covers the Fieldwork scout record for #929. The requested transition is to retain the source map, executable mechanism evidence, negative controls, and repair-boundary analysis as durable Fieldwork evidence. The strongest result is a deterministic stale-owner sequence where single-use consumer A authenticates A, replacement B becomes fully readable at the same pathname, and A then removes B while completing A.

The report is suitable for retention. Promotion of a cmux repair candidate still needs a target-native deterministic regression; actual daemon-process restart and live Freestyle execution remain outside this evidence class.

## Scope

- Repository: `teamleaderleo/fieldwork`
- Issue: #929
- Work class: evidence/documentation with upstream-fork research implications
- Canonical branch: `scout/cmux-remote-auth-publication-20260901`
- Reviewed head before this review file: `11ab42c5e93ef13aa3c51c6d8f6b4d20f4999084`
- Fieldwork assignment base: `ad3745069e186190a65f032bbccae7f91ac2f2f4`
- Current Fieldwork `main` during review: `eda248dc8a752241ae9359962a467c2bfd2dbb8a`
- Current-main relation: two unrelated Meson-report commits advanced `main`; no changed paths overlap this scout
- Changed-file fence before this review: `programmes/high-leverage-open-source/scouts/cmux-remote-auth-publication/` only
- Automated third-party upstream contact: prohibited
- Human-performed upstream interaction already exists: no interaction created by this scout

Pinned target source: `manaflow-ai/cmux@8ef183f1e5de765b183aec9d1799f17a0848ae84`, rechecked as current upstream `main` immediately before materialization.

## Claim-scoped evidence

| Claim or invariant | Evidence class | Exact receipt, source, or artifact | Coverage limits |
| --- | --- | --- | --- |
| Admin publication does not take `wsLeaseMu`; single-use consumption holds it across read/auth/remove | source-read | `report.md`; pinned `ws_pty.go` blob in `artifacts/EVIDENCE.txt` | current pinned source only |
| Old A can delete fully published B | model-executed | `TestOldSingleUseConsumerDeletesReplacement`; `harness-results.txt` | copied low-level source with one pre-remove pause hook |
| B survives when installed after A settles | model-executed | `TestNegativeControlInstallAfterConsumeSettles` | same harness |
| In-place publication can expose invalid/empty JSON | model-executed | `TestReadRacingInPlaceWriteSeesInvalidJSON` | retained Linux filesystem/runtime only |
| Atomic rename removes torn-read observation but leaves stale pathname deletion | model-executed | two atomic-rename controls | model scope |
| Interrupted or concurrent three-artifact installs can mix generations | source-read + model-executed | failure injection and X/Y tests | actual daemon crash/process restart unexecuted |
| Shared daemon locking serializes the demonstrated stale-delete interleaving | model-executed | `TestSharedLockSerializesOldConsumeBeforeReplacement` | daemon-process publisher only; external shell writer remains outside lock |
| Full authorization-generation atomicity needs a wider publication boundary | source-read + model-executed | report repair comparison | design conclusion; target contract decision still required |

Commands: `GO111MODULE=off go test -v -count=1 ./...`  
Runtime: `go1.23.2 linux/amd64`; upstream daemon module declares Go 1.22.  
Focused tests: ten retained tests, all passed in the recorded run.  
Full repository gate: not claimed.  
Retained artifacts: `artifacts/lease_race_test.go`, `artifacts/harness-results.txt`, `artifacts/EVIDENCE.txt`.

## Self-review before handoff

- Strongest claim traced to exact support: yes
- Intended assertion actually ran: yes
- Harness/setup failure separated from product mechanism: yes
- Negative control retained: yes
- Contradictory repair hypotheses retained: yes
- No automated third-party upstream mutation attempted: yes
- Current upstream pin rechecked after the first pin moved: yes
- Committed harness digest reconciled to committed bytes: yes

## Complete-diff review

Invariant under review: installing a new authorization generation must preserve the replacement as complete readable authorization, and older work must never consume or delete it.

Strongest positive evidence: B is inspected as complete JSON after A authenticates and before A resumes; after A resumes, the pathname is absent.

Negative/compatibility controls: settled-A control; atomic-rename torn-read control; atomic-rename stale-delete discriminator; shared-lock stale-delete control; per-artifact atomic-rename bundle discriminator.

Failure/recovery paths examined: first-artifact failure, second-artifact failure, concurrent install, fresh re-read of surviving files, RPC-client reuse mismatch, existing RPC connection revocation semantics by source read.

Unsupported or unexecuted claims are labeled in `report.md`: actual daemon-process restart, target-native upstream checkout test, live Freestyle VM timing, production frequency, and incident prevalence.

Diff-quality concern: none found. The branch owns only the scout report/review and retained artifacts. Current Fieldwork main advances unrelated Meson paths.

## Coordination state

- Programme: #114
- Adjacent scout: #927 owns broader persistent-generation compatibility
- This scout owns legacy WebSocket auth publication/rotation
- Issue `State:` and labels should move to `ready` at handoff
- Current-main relation: known
- Upstream remains read-only

## Disposition

Disposition: **ACCEPT** for durable Fieldwork retention and coordinator synthesis.

Accepted transition: merge/retain this scout record as evidence. A product repair candidate should next receive a target-native stale-delete regression. Transactional multi-artifact publication should remain a separate decision-bearing branch until the PTY/RPC/RPC-client generation contract is explicit.

## Uncertainty

The mechanism evidence is strong for the copied low-level behavior. It does not establish production frequency, a live provider interleaving, or crash consistency under a real daemon restart. Those are explicit next probes rather than prerequisites for retaining the demonstrated invariant violation.
