# Unit 24 independent review and execution classification

Date: `2026-08-01`  
Reviewer: `GPT-5.6 Thinking`  
Public upstream interaction: `none`

## Exact source

- Public-source parent: `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`
- Candidate head: `9fd4ba575de8dd77bc411362256591ce9e7d8c82`
- Source PR: `teamleaderleo/codex#130`
- Complete source fence: exactly three files

## Independent source judgment

Disposition: `ACCEPT — subject to exact-head execution`.

Independent complete-diff review found no source, test, compatibility, or packaging defect inside the unit boundary.

The selected transition is limited to the first non-warmup Responses Lite request after untraced warmup. It discards the warmup response receiver before request preparation, causing the established full serializer to emit the complete first generated Lite request without a warmup `previous_response_id`. A successful generated response becomes the next incremental base through the existing state assignment. Transport failure, stream failure, caller cancellation, and reconnect leave no generated response ID to reuse, so the next attempt remains full. Generic non-Lite warmup compression remains unchanged.

The three target controls cover:

1. full first generated request after warmup;
2. later continuation from the first generated response;
3. failed first generation retrying the complete request.

Source review receipt: `teamleaderleo/codex#130`, review `4834383404`.

## Current execution classification

Execution disposition: `REPAIR`.

Execution-only PR: `teamleaderleo/codex#135`  
Carrier head: `fb77d59b2f5d07cebee889851a476ebab57c9e45`  
Workflow run: `30690825055`  
Job: `91345120846`

The job completed with failure before any Codex target test ran. Setup, checkout, Rust installation, source-fence checks, dependency fetch, and fixture build completed. The selected-test step then failed because the carrier invoked a missing path:

```text
python3: can't open file '/home/runner/work/codex/codex/.fieldwork-carrier/programmes/ai-cli-labs/scouts/codex-responses-lite-poisoning/run_experiment.py': [Errno 2] No such file or directory
```

This run supplies zero current-head behavioral coverage. It must not be cited as a target-test pass or as a completed exact-head receipt.

The direct workflows associated with source head `9fd4ba575de8dd77bc411362256591ce9e7d8c82` skipped every substantive product job on the fork pull request. Summary-only success is not product execution evidence.

Historical run `30584165709` / job `91011486628` remains predecessor evidence for historical source `e520da008366cd720ef58fa0b489efc0a2867e97`. It does not close the execution gate for the current source head.

## Superseded packet statements

Any statement in this packet that run `30690825055` / job `91345120846` is queued is superseded by this receipt. The run is complete and failed during carrier setup before target execution.

Any statement that independent source acceptance is absent is superseded by source review `4834383404`.

## Remaining gate

Repair the execution carrier so it runs against immutable source head `9fd4ba575de8dd77bc411362256591ce9e7d8c82`, then record:

- exact source parent/head and three-file fence;
- formatting;
- both exact client controls;
- full-agent default/raised-stack discriminator;
- raised-stack `codex-core` suite;
- fix gate;
- clean worktree and diff.

A source-attributable failure returns the unit to source repair. A passing exact-head receipt permits packet promotion from execution `REPAIR` to the next review state.
