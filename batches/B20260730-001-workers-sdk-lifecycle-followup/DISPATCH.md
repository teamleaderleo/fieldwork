# Workers SDK lifecycle follow-up dispatch

- Batch: `B20260730-001`
- Batch issue: `#88`
- Programme: `#13`
- Target hub: `#3`
- Source scout: `#18`
- Source scout PR: `#41`
- Coordinator: `teamleaderleo`
- Maximum parallel workers: `4`
- Upstream contact authorized: `false`

These assignment packets are immutable for the initial dispatch. A worker may report a proposed scope change to issue #88, but must not silently expand into another assignment, repository, or upstream interaction.

## Rules shared by every assignment

1. Read Fieldwork issue #18, PR #41, issue #88, this dispatch, and the batch manifest before beginning.
2. Work in a dedicated Workers SDK branch and a dedicated Fieldwork branch. Do not edit another worker's branch.
3. Write only the assigned result path. Do not edit `manifest.json`, `STATUS.md`, `synthesis.md`, or another worker's result.
4. Pin source claims to exact commits and paths.
5. Prefer package-level failing tests and runnable reproductions. A source-backed model is acceptable only when the real suite cannot be run, and the limitation must be explicit.
6. Record rejected hypotheses, negative controls, and plausible alternative causes.
7. Search prior issues, pull requests, commits, changelogs, and linked discussions, but do not interact with upstream.
8. Do not open, comment on, review, react to, or otherwise contact `cloudflare/workers-sdk` or `cloudflare/workerd`.
9. Report completion on Fieldwork issue #88 with the Fieldwork PR, Workers SDK branch, exact tested revisions, commands, strongest finding, and final state.
10. Final assignment state must be one of `complete`, `blocked`, `negative-result`, or `needs-decision`.

---

# A001 — Teardown lifecycle ownership

## Role

Own the teardown mechanism investigation. Determine whether cleanup ordering can leave `workerd` alive and whether that mechanism explains any reported Vitest hangs.

## Starting point

- Repository: `teamleaderleo/workers-sdk`
- Starting revision: `161443215fba3ac77407ba30f6996aa9963a0276`
- Existing experiment branch: `fieldwork/teardown-error-visibility`
- New suggested branch: `fieldwork/teardown-lifecycle-hardening`
- Owned result: `batches/B20260730-001-workers-sdk-lifecycle-followup/results/A001.md`

## Question

Can an early rejection or cleanup operation that never settles prevent `Runtime.dispose()` from terminating `workerd`, especially when Vitest runs files or projects in parallel?

## Work

- Trace every awaited step in `Miniflare.dispose()` and the Vitest pool stop path.
- Identify which pre-runtime cleanup operations can reject or remain pending.
- Build a package-level failure-injection regression test when possible.
- Inject failures before and after runtime termination and assert whether the child-kill path still runs.
- Inspect lifecycle ownership under parallel files, projects, remote sessions, assets watchers, and shared state.
- Compare against upstream issues #14903, #14180, and #12764 as quiet references.
- Test a bounded repair that makes runtime termination must-run, isolates independent cleanup, aggregates errors, and preserves the primary test result.
- Consider a bounded diagnostic for a disposal operation that never settles.

## Required caution

Do not claim that all teardown hangs have this cause. Establish whether the mechanism is sufficient, whether it is actually exercised, and what remains unproven.

## Completion

Return a failing regression test or a precise feasibility boundary, a source trace, alternative explanations, and a patch direction. Also review A002's final behaviour matrix after completing the primary work.

---

# A002 — Configuration selection contract

## Role

Own the configuration contract investigation. Produce the authoritative matrix for which config each tool selects and why.

## Starting point

- Repository: `teamleaderleo/workers-sdk`
- Starting revision: `0497e9e30e191f2b7e337b01e32855c4cb6cf5fe`
- Existing experiment branch: `fieldwork/config-discovery-parity`
- New suggested branch: `fieldwork/config-selection-contract`
- Owned result: `batches/B20260730-001-workers-sdk-lifecycle-followup/results/A002.md`

## Question

Under which layouts and invocation modes do Wrangler, `wrangler dev`, the Cloudflare Vite plugin, explicit config paths, and redirected deployment configuration select different files?

## Work

- Convert the retained probes into package-level regression tests.
- Cover JSON versus JSONC versus TOML precedence.
- Cover parent versus child configuration and Vite root versus working directory.
- Cover `.wrangler/deploy/config.json` redirects.
- Cover explicit `configPath`, environment selection, and framework-generated configs.
- Record which selected path is reported to the user and which file is watched for changes.
- Review upstream issue #8701, PR #13587, and related history as quiet references.
- Classify every difference as intentional, accidental, compatibility-sensitive, or unknown.
- Design the smallest shared selection-policy API that makes search boundary, extension priority, redirects, and reporting explicit.

## Required caution

Do not silently choose a new default or treat every difference as a bug. Include migration and compatibility consequences.

## Completion

Return an executable selection matrix, intentional-versus-accidental classification, negative controls, and a bounded implementation direction. Also review A003's final tests and state assumptions after completing the primary work.

---

# A003 — Partial deployment state

## Role

Own the deployment lifecycle investigation. Determine exactly what may have changed when the command reports failure.

## Starting point

- Repository: `teamleaderleo/workers-sdk`
- Starting revision: `609623ba8552a016f3c67cee7259e38d8431bd91`
- Existing experiment branch: `fieldwork/deploy-post-activation-failure`
- New suggested branch: `fieldwork/deploy-state-reporting`
- Owned result: `batches/B20260730-001-workers-sdk-lifecycle-followup/results/A003.md`

## Question

Which Worker, version, assets, settings, container, route, and trigger mutations can succeed before Wrangler reports a later failure, and what state can the command report safely afterward?

## Work

- Map mutation order for ordinary deploy, versions upload/deploy, assets, settings, containers, routes, triggers, and rollback.
- Mark each operation as pre-activation, activation, or post-activation.
- Record identifiers available after each operation, especially version IDs.
- Add failure injection at every meaningful post-activation boundary.
- Separate hosted API failures, user configuration, and SDK reporting behaviour.
- Review issue #1585 and relevant container reports as quiet references.
- Locate preflight checks intended to avoid partial state and document their limits.
- Prototype a deployment journal or error result that reports what changed, the failed phase, active version, uncertainty, and safe inspect/retry/rollback commands.

## Required caution

Do not implement general automatic rollback. Resource-specific rollback may be unsafe or impossible and requires separate evidence.

## Completion

Return a mutation table, tests or controlled models, historical evidence, and a bounded state-reporting proposal. Also review A001's final failure injection after completing the primary work.

---

# A004 — Independent reviewer and prior-art auditor

## Role

Act as the independent adversarial reviewer. Do not inherit the implementation assumptions of A001–A003.

## Starting point

- Fieldwork source: PR #41 at `e95d5cc36411fc4048728015235594b51afdde17`
- Workers SDK sources: the A001–A003 starting revisions above, followed by their delivered branch heads
- Suggested Workers SDK branch: `fieldwork/workers-sdk-independent-review`
- Owned result: `batches/B20260730-001-workers-sdk-lifecycle-followup/results/A004.md`

## Question

Which claims and proposed tests from A001–A003 survive independent reproduction, source review, compatibility analysis, and prior-art research?

## Work

- Begin prior-art research immediately; perform final branch review after A001–A003 deliver.
- Re-run every reproduction that does not require hosted credentials.
- Confirm proposed regression tests fail before a proposed fix and pass for the intended reason afterward.
- Search Workers SDK and workerd issues, pull requests, commits, changelogs, and linked discussions.
- Classify prior art as exact duplicate, same failure class, nearby but different, intentional behaviour, resolved, or apparently fresh.
- Challenge causal claims and identify alternate explanations.
- Check compatibility effects and missing negative controls.
- Flag conclusions based only on source reading, untested assumptions, or incomplete evidence.
- Rank each candidate's confidence and implementation readiness.

## Required caution

Do not absorb implementation ownership. Small independent harnesses are allowed only to verify or falsify claims.

## Completion

Return an independent acceptance review of A001–A003, including confidence, duplicates, contradictions, missing tests, and a recommendation on which implementation PRs should proceed.

---

# Review loop

- A001 reviews A002.
- A002 reviews A003.
- A003 reviews A001.
- A004 independently reviews all three.
- The coordinator accepts handoffs, updates shared status, and owns synthesis.
