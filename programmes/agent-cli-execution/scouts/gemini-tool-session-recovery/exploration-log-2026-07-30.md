# Exploration log: Gemini CLI deterministic lifecycle follow-up

Date: 2026-07-30  
Parent scout: #22  
Programme: #14  
Target hub: #5  
Target revision: `teamleaderleo/gemini-cli@3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`  
Upstream contact authorized: `false`

## Purpose

Turn the strongest source findings from the first scout into isolated fork-only case packs, probe incomplete repair ideas, preserve rejected approaches, and identify the next deterministic questions without mixing unrelated lifecycle contracts.

The owned fork remains an implementation workspace rather than independent evidence. Its `main` branch exactly matches the scout pin.

## Execution boundary

Two attempts to obtain target-native execution evidence remained blocked:

- the fork pull-request commits produced no GitHub Actions workflow runs;
- the available local runner could not resolve `github.com`, so it could not clone the fork or install the repository dependencies.

Therefore none of the fork tests below are labelled test-confirmed. They are prepared target-native case packs backed by source-confirmed expected failures. The retained Node probes are source-equivalent deterministic probes, not substitutes for the target suite.

## Fork case-pack inventory

### Fork PR 1: discovered subprocess abort ownership

- Pull request: `teamleaderleo/gemini-cli#1`
- Branch: `fieldwork/discovered-tool-abort-process-tree`
- File: `packages/core/src/tools/tool-registry.abort.test.ts`
- Expected current failure: abort does not call `killProcessGroup` because `DiscoveredToolInvocation.execute` accepts the signal as `_signal` and never observes it.
- Repair boundary: no spawn for an already-aborted signal; parent and descendants terminated after spawn; ownership retained until exit or bounded escalation; listeners removed; partial output retained.

### Fork PR 2: confirmation modification call affinity

- Pull request: `teamleaderleo/gemini-cli#2`
- Branch: `fieldwork/confirmation-call-affinity`
- File: `packages/core/src/scheduler/confirmation.affinity.test.ts`
- Expected current failure: a response correlated to `call-b` passes `call-a` to the inline modifier because both modification paths use `state.firstActiveCall`.
- Repair boundary: retrieve and validate the exact call ID already owned by the confirmation loop; never derive modification authority from map insertion order.

### Fork PR 3: approval waiting-state cleanup

- Pull request: `teamleaderleo/gemini-cli#3`
- Branch: `fieldwork/confirmation-waiting-finally`
- File: `packages/core/src/scheduler/confirmation.waiting-state.test.ts`
- Expected current failure: abort yields callback transitions `[true]` rather than `[true, false]` because the clearing callback sits after the rejecting `await`.
- Repair boundary: every entered wait leaves through balanced cleanup, including bus abort, IDE rejection, lost state, and callback exceptions.

### Fork PR 4: asynchronous kill acknowledgement

- Pull request: `teamleaderleo/gemini-cli#4`
- Branch: `fieldwork/execution-lifecycle-await-termination`
- File: `packages/core/src/services/executionLifecycleService.async-kill.test.ts`
- Expected current failure: lifecycle ownership and the result promise settle immediately while the controlled asynchronous kill hook remains pending.
- Repair boundary: represent `terminating`, retain ownership, await termination or a bounded timeout, and preserve real exit details when they arrive.

All four pull requests are drafts, target the owned fork only, contain tests rather than production fixes, and explicitly exclude upstream submission.

## Expanded deterministic probe

Artifacts:

- `artifacts/expanded_lifecycle_probe.mjs`
- `artifacts/expanded_lifecycle_probe-output.json`

Command:

```sh
node programmes/agent-cli-execution/scouts/gemini-tool-session-recovery/artifacts/expanded_lifecycle_probe.mjs
```

The probe passed fixed assertions for five additional control-flow questions.

### 1. Abort during asynchronous sandbox preparation

A cancellation repair that checks the signal only before `sandboxManager.prepareCommand(...)` remains incomplete. Abort can occur while preparation is awaiting, after which the current flow can still spawn the command.

Required distinguishing cases:

1. signal already aborted before preparation;
2. abort while preparation is pending;
3. abort after preparation and before listener registration;
4. abort after spawn;
5. preparation cleanup after each path.

A correct adapter needs a post-preparation check and race-safe listener installation, not merely an early guard.

### 2. Parallel approval waits make a shared boolean ambiguous

Putting the clearing callback in `finally` fixes the single-call leak but does not fully define parallel behaviour. Two calls can emit `true, true`; when the first finishes it emits `false` even though the second is still waiting.

Possible contracts:

- callback receives a pending count;
- callback is call-scoped and the consumer aggregates;
- scheduler maintains a reference count and emits only on zero-to-one and one-to-zero transitions.

The narrow PR 3 test retains the single-call invariant. A separate parallel test should choose the global contract before the callback type is changed.

### 3. Synthetic cancellation suppresses later real exit details

`ExecutionLifecycleService.kill` currently records an aborted result and deletes active ownership immediately. A later process exit cannot replace that synthetic result because `completeWithResult` finds no active execution.

Consequences include:

- reported completion before process-tree exit;
- loss of the actual terminating signal or exit code;
- inability to distinguish successful termination from timeout or failed kill;
- overlap when a retry starts before the previous process exits.

The repair should decide whether the synthetic result is provisional, whether a timeout becomes terminal, and which late exit details are retained.

### 4. MCP local abort does not prove remote cancellation

The MCP adapter rejects its local promise on abort, but the underlying `CallableTool.callTool(functionCalls)` call receives no cancellation handle in this path. A deterministic source-equivalent case shows local rejection followed by later remote completion.

This does not prove that every MCP transport continues work. It proves only that this adapter does not own or evidence remote cancellation.

Required next evidence:

- inspect the exact `CallableTool` implementation produced by `mcpToTool`;
- identify request IDs and protocol cancellation support;
- test a controlled MCP server that delays a side effect and records cancellation frames;
- if cancellation is unsupported, expose a detached/unknown remote outcome rather than reporting full cancellation.

### 5. Project-discovered execution has no output bound

Tool discovery limits stdout and stderr to 10 MB and terminates discovery when the bound is exceeded. Project-discovered tool execution instead concatenates all stdout and stderr until close and ignores the output update callback.

The probe demonstrates the retention algorithm, not an agreed failure threshold. This is a new candidate rather than a promoted bug because the intended execution-output contract is not documented in the inspected path.

Questions to resolve:

- should execution use the same 10 MB per-stream limit as discovery;
- should output spill to a file while retaining a bounded tail;
- should partial output stream through `updateOutput`;
- should limit termination be treated as cancellation, tool error, or truncation;
- how should the limit interact with later scheduler-level output truncation, which occurs only after invocation completion.

## Rejected or deferred approaches

### Rejected: implement production fixes before target execution

The source findings are strong, but target-native tests have not run. Production patches were not added to the fork case-pack branches. This keeps the evidence boundary visible and avoids presenting source reasoning as a verified repair.

### Rejected: use `child.kill()` as the discovered-tool repair

Killing only the immediate child does not own descendants and can leave service, shell, or helper processes running. The existing shared `killProcessGroup` utility already expresses the stronger cross-platform ownership attempt.

### Rejected: add only an initial `abortSignal.aborted` check

That misses cancellation during sandbox preparation and the listener-registration race after spawn.

### Rejected: treat `try/finally` as the full waiting-state design

It repairs the single-call leak but a shared boolean still becomes false while another parallel approval remains pending. The minimal cleanup branch and the parallel-state contract should remain distinct.

### Rejected: make `ExecutionLifecycleService.kill` return a promise without mapping callers

Changing a central void API to an awaited API can create silent fire-and-forget call sites. The call-site inventory, background UI contract, repeated-kill semantics, and timeout behaviour need to be explicit before changing the signature.

### Rejected: pass an abort signal into `CallableTool.callTool` by assumption

The inspected `CallableTool` call surface in this path accepts function calls only. A patch should not invent a transport contract. First resolve the concrete MCP client and protocol cancellation mechanism.

### Rejected: replace the recovery sentinel alone

Changing “context management truncation” to “interrupted” would remove one unsupported cause but would not establish whether a side effect completed, remains active, or is safe to retry. Durable lifecycle receipts and reconciliation remain the substantive repair.

### Rejected: combine the four case packs

Subprocess cancellation, approval affinity, callback cleanup, and lifecycle termination have different owners and acceptance criteria. Separate branches allow each test to fail and each future patch to be reviewed independently.

## Negative results and resilience retained

- The owned fork pin exactly matches the scout target, so no drift explanation is needed for these case packs.
- JSONL loading continues to preserve complete earlier records when the trailing record is malformed.
- Shell execution already attempts process-group and descendant termination; the direct orphan finding is specific to project-discovered tools.
- Confirmation bus/IDE race cleanup removes the parent listener and aborts the losing iterator in `finally`; the new callback finding does not invalidate that cleanup.
- MCP abort listener cleanup is explicit locally; the open question is remote work ownership, not a local listener leak.
- No deterministic model-quality claim was needed.

## New areas worth exploring

### High priority

1. **Execute fork PRs 1-4** on a retained runner and capture exact commands, runtime versions, test output, and failure locations.
2. **Approval editor-path affinity** with two calls and an out-of-order `ModifyWithEditor` response; PR 2 currently exercises the inline path only.
3. **Discovered-tool cancellation race matrix**, including sandbox preparation, descendant processes, partial output, repeated abort, and close-before-kill completion.
4. **Lifecycle terminating state**, including natural exit during kill, kill timeout, repeated kill, backgrounded execution, and late real exit reconciliation.

### Medium priority

5. **Parallel approval waiting aggregation** to choose count, call-scoped, or reference-counted semantics.
6. **Discovered-tool output pressure** with controlled stdout/stderr generation and a separate observer for memory, spill, truncation, and cleanup.
7. **Interrupted-session phase fixtures** at approval, scheduled, executing, side-effect-complete/result-missing, backgrounded, and shutdown stages.
8. **MCP cancellation ownership server** that records whether cancellation reaches the transport and whether a delayed side effect still completes.

### Lower priority until contracts are settled

9. **Durable process reattachment** across CLI restart. This may be inappropriate for arbitrary child processes; explicit `interrupted_unknown` reconciliation may be safer.
10. **Automatic retry of incomplete calls.** Do not promote without idempotency evidence and an operator-visible warning for side-effecting unknown outcomes.
11. **Unified process supervisor.** Architecturally attractive, but too broad before the narrow ownership tests identify stable common contracts.

## Recommended continuation order

1. Obtain target-native execution for PRs 1-4.
2. Repair call affinity and single-call waiting cleanup first if their tests fail as predicted; both are narrow and low-risk.
3. Expand discovered-tool cancellation tests before implementing its process-tree repair.
4. Define the lifecycle `terminating` contract and caller migration before changing `kill`.
5. Run controlled output-pressure and MCP-server probes.
6. Design durable session receipts using the evidenced terminal states from the earlier branches.

## Interaction record

- Writes occurred only in `teamleaderleo/fieldwork` and `teamleaderleo/gemini-cli`.
- No issue, pull request, comment, review, reaction, email, or other interaction occurred in `google-gemini/gemini-cli`.
- No upstream packet was prepared for submission.
- Upstream contact remains blocked on explicit human authorization.
