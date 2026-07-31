# F239 current-evidence reconciliation — 2026-07-31

## Purpose

This note preserves the exact portfolio reconciliation that moved Codex work from broad investigation into bounded findings and source candidates. It supersedes the stale snapshot on Fieldwork PR #297.

Upstream contact authorized: `no`.

## Current identity

- Canonical protocol review surface: Fieldwork PR #283.
- Current Codex adoption and F239 authoring surface: Fieldwork PR #292.
- Current read-only public Codex head inspected: `4642370542739d5dd080b0c87a9de06a6435d3db`.
- The public move from `413492cd6c3a4d4f8dff6f406247ccda5a9d88aa` to `4642370542739d5dd080b0c87a9de06a6435d3db` changes only precomputed app-server protocol export archives and has no file overlap with the active source fences below.

File-disjoint drift supports carry-forward review only. Every delivery candidate still needs an exact current-head diff, compatibility review, and renewed execution where required.

## Bounded packets

### Append acknowledgement — F83

- Source PR: owned Codex #84 at `d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2`.
- Authoritative execution: carrier #80 run `30583967538`, job `91010830120`, success.
- Independent review: `4823945751`.
- Accepted boundary: return a bounded append acknowledgement to the session caller.
- State: `delivery-gate-ready`.
- Remaining gate: direct-current-head packaging, renewed controls and complete-diff review, then carrier retirement.
- Outside scope: typed `Persisted/Ambiguous`, retry authority, duplicate reconciliation, compaction, replay, and remote-effect settlement.

### Producer-owned terminal retention — F23

- Authoritative execution: Fieldwork #268 run `30587866332`, job `91023382172`, success.
- Retained source commit: `8c7ea38419d790032db459816980e6b4dd38f574`.
- Retained source tree: `563f90f55c0ebd9454171d24697d796cba1388d4`.
- Artifact: `8777460316`.
- Artifact digest: `sha256:9c6c4f6741ee2514e995849ca2bed9caf0f80b80fdbb3a9ea31565df3ebda2dd`.
- Current materialization carrier: owned Codex #86 at `4779b0f376b21bb0fa8ed0fbb0e42728e0ecf9c1`, run `30590643470` queued at this reconciliation.
- Accepted boundary: normal-close completion uses the producer-owned bounded transcript rather than a best-effort subscriber.
- State: `delivery-gate-ready`.
- Remaining gate: materialize the verified tree in owned Git, open the exact four-file source PR, review current drift, and retire temporary carriers.
- Outside scope: hard termination, restart reattachment, Windows containment races, and remote-effect settlement.

### MCP publication generation — F84

- Source PR: owned Codex #75 at `c3373c717f3138ff5f0a979d12836f60800d2bcf`.
- Authoritative execution: carrier #77 run `30584055792`, job `91011123543`, exact controls `5/5`, success.
- Independent review: `4823972975`.
- Accepted boundary: a manager-owned generation and freshness ticket determines which completed candidate may publish.
- State: `delivery-gate-ready`.
- Remaining gate: one complete slow-older/fast-newer runtime fixture and current-head synchronization.
- Outside scope: active-call binding, reconnect route behavior, timeout certainty, and remote-effect settlement.

### MCP call authority

- The broad serialized-`ToolInfo` live-rebind direction was retired after source-precedent review and a carrier-only failure.
- Retained rule: ordinary calls keep their captured prepared binding; cached-only advertisements may wait for startup and must prove callable-authority equality before approval, hooks, rewriting, or dispatch.
- Canonical sibling surface: Fieldwork PR #290.
- Reopening trigger: current source removes captured prepared authority or an exact counterexample defeats the cached-only split.

### MCP reconnect

- Current source PR: owned Codex #76 at `7e9d80c4965a76b802f02d7bace17ea1c4a8931c`.
- App-server carrier: #82 at `feb0c46d3b88e03c94cb9f07d6ba903205e73f05`.
- Earlier run `30584136349` proved the two direct controls and then failed before handler execution because the fixture used obsolete method `mcpServer/refresh`.
- Current public method: `config/mcpServer/reload`.
- Repaired run `30589313367` remained queued at this reconciliation.
- Remaining proof: strict route-level behavior, including a bounded stability window and planning-failure/zero-reconnect control.

### Deferred runtime exposure

- Current source PR: owned Codex #88 at `9b6eab9b31f5b4c06c441773afb81bd808021971`.
- Authoritative execution: carrier #64 run `30584556260`, job `91012754932`, source fence `2/2`, exact planner controls `5/5`, focused planner package success.
- Independent review: `4824091314`.
- Accepted boundary: in an effective Direct request, a runtime may remain deferred only when that turn has an executable loader for it; otherwise it becomes directly exposed. Code Mode retains its separate catalogue path.
- State: `delivery-gate-ready`.
- Remaining gate: direct-current-head source child, renewed exact controls, complete-diff review, and carrier cleanup.
- Separate diagnostic: default Tokio worker stack overflowed while the 16 MiB discriminator passed. That does not alter the planner conclusion.

### Responses Lite first generated request — F85

- Source PR: owned Codex #87 at `e520da008366cd720ef58fa0b489efc0a2867e97`.
- Authoritative execution: carrier #58 run `30584165709`, job `91011486628`, source fence `3/3`, client controls `2/2`, success.
- Independent reviews: `4824079205` and `4824085183`.
- Accepted boundary: after startup prewarm, the first generated Lite request sends the complete current request; successful continuation may use the generated response identity; a failed first generation retries the same full request without inheriting the warmup response identity.
- State: `delivery-gate-ready`.
- Remaining gate: direct-current-head packaging and renewed complete-diff review.
- Separate diagnostic: full agent test classified `default:101;large:0`; stack pressure remains independently owned.

### Receipt replay and typed identity

- Receipt replay carrier #78 was repaired for a stale exhaustive-match anchor at `e2d796a17fd6aa0b1053ca80c6daa36f8e03de2f`; run `30590871322` remained queued at this reconciliation.
- Typed identity reached a real current-source conflict in `codex-rs/core/src/tools/registry_tests.rs`; no typed-identity behavior control ran.
- These remain independent from append acknowledgement. Persistence acknowledgement cannot by itself prove replay identity, rollback handling, compaction safety, or remote-effect certainty.

## Portfolio conclusion

The useful result is not a single Codex patch. It is a set of independently falsifiable ownership rules:

1. request planning owns model-visible executability;
2. runtime managers own publication freshness;
3. prepared calls own ordinary dispatch authority;
4. cancellation delivery and remote-effect certainty remain separate facts;
5. session code owns caller-visible append acknowledgement;
6. replay owns conservative reconstruction of durable operation facts;
7. terminal producers own the transcript used for completion;
8. carriers own execution receipts only until source and evidence transfer completes.

Issue #239 remains the portfolio synthesis. Existing technical issues remain the owners. A new issue is appropriate only when a bounded packet lacks an existing owner or presents an independent implementation or review decision that the current owner cannot carry cleanly.

## Supersession and reopening

- Fieldwork PR #297 is superseded as a canonical authoring surface by PR #292. Its useful reconciliation intent is retained here with corrected identities.
- Reopen a packet when current public source overlaps its fence, an exact control regresses, a materialized tree differs from the retained artifact, or a counterexample defeats its accepted ownership rule.
- Public upstream interaction remains prohibited without separate exact authorization.
