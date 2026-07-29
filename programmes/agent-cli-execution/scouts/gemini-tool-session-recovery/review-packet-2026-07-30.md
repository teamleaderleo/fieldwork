# Review packet: Gemini CLI deterministic lifecycle findings

Date: 2026-07-30  
Parent lane: #22  
Fieldwork PR: #45  
Owned fork: `teamleaderleo/gemini-cli`  
Pinned target: `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`  
Upstream contact authorized: `false`

## Purpose

This packet is the reviewer-facing index for the Gemini CLI scout and fork case packs. It tightens evidence language, separates direct defects from proposed contracts, and states exactly what has and has not executed.

Earlier report shorthand such as **test-confirmed gap** means that existing pinned tests establish surrounding behaviour while omitting the distinguishing regression case. It does **not** mean that a newly added fork test has run and failed.

## Evidence vocabulary

- **source-confirmed defect**: the undesirable control flow is directly present in the pinned implementation.
- **existing-test coverage gap**: pinned tests exercise nearby behaviour but omit the distinguishing failure case.
- **probe-reproduced**: a fixed-input Node probe mirrors the pinned control flow and reproduced the result.
- **prepared target-native test**: a Vitest case exists in the owned fork, but no retained target-suite run is available.
- **candidate contract**: the current behaviour is source-confirmed, but the preferred replacement semantics require an explicit design decision.
- **open transport/platform question**: the inspected adapter does not establish the lower-level outcome.

No fork case is currently labelled target-test-confirmed. GitHub started no workflow runs for the fork heads, and the available local runner could not resolve GitHub to install the repository.

## Finding matrix

| Finding | Classification | Direct evidence | Fork case | Missing evidence | Reviewer decision |
| --- | --- | --- | --- | --- | --- |
| Project-discovered invocation ignores abort | Source-confirmed defect; existing-test coverage gap; probe-reproduced | `DiscoveredToolInvocation.execute` names the signal `_signal`, spawns, and waits for `close` without observing cancellation | `teamleaderleo/gemini-cli#1` | Focused Vitest receipt; real parent/descendant case; sandbox-preparation race matrix | Accept narrow helper-wiring case, then require real process ownership before calling the full repair verified |
| Inline approval modification can use another call | Source-confirmed defect; existing-test coverage gap; probe-reproduced | Confirmation owns `callId`, then inline modification receives `state.firstActiveCall`; updated arguments are written under the owned call ID | `teamleaderleo/gemini-cli#2` | Focused Vitest receipt; external-editor case; two-active-call scheduler case with out-of-order responses | Accept as high-confidence inline mechanism defect; keep broader affinity acceptance tests separate |
| Approval waiting callback remains true after abort | Source-confirmed defect; existing-test coverage gap; probe-reproduced | `true` runs before the rejecting await; `false` runs after it and outside `finally` | `teamleaderleo/gemini-cli#3` | Focused Vitest receipt; IDE failure and callback-exception cases | Accept narrow single-call cleanup fix; do not treat it as the parallel waiting-state design |
| Lifecycle kill settles before asynchronous termination | Source-confirmed current behaviour; probe-reproduced; candidate contract | External kill hook is typed `() => void`; lifecycle immediately resolves, emits exit, and deletes ownership; shell hooks start asynchronous process-group termination | `teamleaderleo/gemini-cli#4` | Focused Vitest receipt; caller inventory; terminating/timeout/rejection/repeated-kill contract | Review as a proposed lifecycle contract, not as an already-promised API guarantee |
| Interrupted sessions lack durable tool lifecycle receipts | Source-confirmed design gap; probe-reproduced | Persistence records message/tool metadata but not approval, execution, background, termination, or uncertain side-effect phase; unmatched calls receive a context-truncation cause | none | Phase-specific target fixtures; schema and reconciliation design | Do not patch wording alone; require durable receipts and evidence-limited recovery states |
| MCP abort proves local rejection only | Source-confirmed locally; open remotely | Local wrapper rejects and removes its listener; `CallableTool.callTool(functionCalls)` receives no cancellation handle in this path | none | Controlled MCP server and transport-frame observation | Keep as a spike; do not invent a cancellation API |
| Discovered execution buffers output without a local bound | Source-confirmed implementation difference; exploration candidate | Discovery enforces 10 MB stream limits; execution concatenates stdout/stderr until close and ignores live update | none | Intended output contract and controlled pressure run | Explore before classifying as a bug or choosing a threshold |

## Refined fork case-pack scope

### Fork PR 1 — missing abort handoff

Title: `test(discovered-tools): reproduce missing abort handoff`

The current test mocks both process creation and process-tree termination. It proves that abort should hand the spawned PID to the shared termination helper. It does not prove actual descendant exit.

Reviewer acceptance criteria:

1. current-year license header;
2. deterministic cleanup when the assertion fails;
3. no claim of real operating-system termination;
4. exact expected pinned-base failure stated;
5. later integration case requires parent and descendant exit before settlement.

### Fork PR 2 — inline approval call mismatch

Title: `test(scheduler): reproduce inline approval call mismatch`

The case intentionally covers inline modification only. The source shows the same lookup in the external-editor path, but that path and the higher-level two-approval scheduler test remain follow-ups.

Reviewer acceptance criteria:

1. response correlation belongs to `call-b`;
2. `call-a` remains first in active insertion order;
3. modifier is required to receive `call-b` and its original arguments;
4. rebuilt invocation and state update remain scoped to `call-b`;
5. title and description do not claim full editor-path coverage.

### Fork PR 3 — waiting-state leak on abort

Title: `test(scheduler): reproduce waiting-state leak on abort`

The case defines the single-call invariant `[true, false]` on abort. It deliberately leaves parallel aggregation unresolved.

Reviewer acceptance criteria:

1. listener attachment is used as the deterministic synchronization point;
2. abort rejects the confirmation wait;
3. cleanup callback is required before the rejection escapes;
4. follow-up design chooses counted, call-scoped, or reference-counted semantics for overlap.

### Fork PR 4 — asynchronous kill ownership contract

Title: `test(core): define async kill ownership contract`

The case proposes that lifecycle ownership and the result remain pending while asynchronous termination is outstanding. The pinned API does not currently promise that; this is a contract candidate.

Reviewer acceptance criteria:

1. test is self-cleaning through unconditional gate release;
2. body states that promise-aware kill is proposed, not existing API;
3. production work inventories callers before changing the signature;
4. timeout, rejection, natural exit, repeated kill, and background execution remain explicit follow-ups.

## Candidate repair sketches

These sketches are review aids, not verified patches.

### A. Confirmation call affinity

Inside each modification path:

1. resolve `state.getToolCall(toolCall.request.callId)`;
2. require the result to remain `AwaitingApproval` and to contain an invocation;
3. pass that exact call into the modifier;
4. fail closed if the call disappeared or changed state;
5. never use `firstActiveCall` for authority-sensitive modification.

This is the narrowest production candidate and should be reviewed first after the target test receipt exists.

### B. Single-call waiting cleanup

Wrap only the entered wait with balanced cleanup:

```text
onWaitingForConfirmation(true)
try:
    response = await waitForConfirmation(...)
finally:
    onWaitingForConfirmation(false)
```

Then separately decide how the scheduler represents multiple simultaneous waits. A per-call `finally` is necessary but not sufficient for a shared global boolean.

### C. Discovered subprocess cancellation

A complete branch needs more than an initial abort check:

1. reject before sandbox preparation when already aborted;
2. recheck after asynchronous preparation;
3. install the abort listener without a post-spawn race;
4. request process-tree termination using the spawned PID;
5. retain ownership until `close` or bounded escalation;
6. remove listeners exactly once;
7. preserve partial output and run sandbox cleanup after ownership release.

A direct `child.kill()` patch is insufficient because descendants may survive.

### D. Lifecycle termination acknowledgement

Before implementation, choose one explicit API:

- make `kill` asynchronous and require callers to await it; or
- return a termination receipt while retaining a synchronous request method.

Either design needs a live `terminating` state, a bounded timeout result, repeat-call semantics, and reconciliation with a natural exit that arrives during termination.

### E. Interrupted-session reconciliation

Do not merely replace the context-truncation sentence. Persist append-only lifecycle events keyed by call ID, fold them on resume, and report only the last evidenced phase. Nonterminal calls should recover to an evidence-limited state such as `interrupted_unknown`, with a visible warning before retrying side-effecting work.

## Rejected shortcuts

- Immediate production patches before a target-native failing receipt.
- `child.kill()` without descendant ownership.
- Only checking `abortSignal.aborted` before asynchronous preparation.
- Treating a per-call `try/finally` as a complete parallel waiting-state design.
- Making central `kill` async without mapping callers and timeout semantics.
- Passing an abort token to `CallableTool.callTool` by assumption.
- Renaming the recovery sentinel without adding durable lifecycle evidence.
- Combining unrelated findings into one implementation branch.

## Independent-review checklist

For each proposed finding or branch, verify:

1. the source and test refer to target revision `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`;
2. the claim follows from deterministic control flow rather than model output;
3. the fork test fails for the predicted assertion rather than setup, typing, or timing noise;
4. cleanup executes even when an intermediate assertion fails;
5. the PR title matches the exact path covered;
6. source-confirmed behaviour is not confused with a preferred future contract;
7. negative results and scope limits remain visible;
8. no result is labelled target-test-confirmed without retained command, versions, output, and head SHA;
9. no upstream interaction occurred;
10. any future upstream packet remains blocked on explicit human authorization.

## Recommended review order

1. PR 3: smallest direct cleanup defect.
2. PR 2: direct authority/call-affinity defect on the inline path.
3. PR 1: direct missing abort handoff, followed by real process ownership cases.
4. PR 4: contract review only after caller inventory.
5. Session receipt design and MCP cancellation spike after the narrow branches establish stable terminal states.
