# Gemini CLI tool execution and session recovery scout

## In simple words

Gemini CLI has several clear owners for tool work, but some cancellation and recovery boundaries lose the link between the tool call and the work it started.

The strongest deterministic findings are:

1. Project-discovered tool subprocesses discard the supplied abort signal, so a cancelled call can keep running until the subprocess exits.
2. Parallel approval modification uses the scheduler's first active call instead of the call identified by the approval correlation, so a response for one call can read modification state from another call.
3. Session recovery stores tool calls and results, but it does not store a durable execution lifecycle. An interrupted call is later repaired with a context-truncation explanation even when the real cause could be approval wait, cancellation, process interruption, completed side effect with lost output, or a still-running child.
4. The execution lifecycle can report an external process killed before asynchronous process-tree termination finishes.
5. An aborted approval wait can leave `onWaitingForConfirmation(true)` without the matching `false` transition.

These are code-path findings. Model output quality is outside this lane.

## Claim record

| Field | Value |
| --- | --- |
| Fieldwork issue | `#22` |
| Programme | `agent-cli-execution` (`#14`) |
| Target hub | Gemini CLI (`#5`) |
| Worker | `chatgpt:gpt-5.6-thinking` |
| Fieldwork branch | `scout/22-gemini-tool-session-recovery` |
| Owned path | `programmes/agent-cli-execution/scouts/gemini-tool-session-recovery/` |
| Target repository | `https://github.com/google-gemini/gemini-cli` |
| Target revision | `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e` |
| Fieldwork base | `09fe47ac92ec9c0c333b4979011f6321795deff2` |
| Retrieval date | `2026-07-29` |
| Upstream contact | Unauthorized; none performed |

## Question and boundary

Which deterministic code paths own tool registration, approval, execution, process or network work, cancellation, persistence, interruption cleanup, and session recovery? Which concrete implementation branches would reduce duplicate side effects, wrong-call approval handling, orphaned work, and false recovery state?

Included:

- registration and invocation ownership;
- approval correlation and modification;
- shell, project-discovered, and MCP execution;
- foreground and background process ownership;
- cancellation propagation and cleanup;
- JSONL session recording and resume conversion;
- recovery of incomplete tool calls;
- tests that define the current contracts.

Excluded:

- model answer quality;
- prompt quality;
- cosmetic terminal output;
- closed-service behaviour;
- claims that depend on probabilistic model choices.

## Evidence labels

- **source-confirmed**: directly established by the pinned implementation.
- **test-confirmed**: directly established by pinned tests.
- **probe-reproduced**: reproduced by the lane-owned minimized probe that mirrors the pinned control flow.
- **candidate**: proposed branch based on source-confirmed behaviour, with the exact target test still to be added.
- **open**: requires a target-native or platform-specific experiment.

## Deterministic lifecycle map

| Boundary | Entrypoint | Owner | Durable or live state | Cancellation and cleanup | Recovery behaviour |
| --- | --- | --- | --- | --- | --- |
| Tool registration | `ToolRegistry.registerTool`, discovery and MCP registration | `ToolRegistry` | In-memory map of known tools; cloned registries for subagents | Registry removal for MCP server tools; tool-specific execution owns resources | Registry is rebuilt on startup |
| Tool build | `tool.build(request.args)` | Declarative tool and invocation | Invocation and request are stored in scheduler state | Build errors become terminal tool errors | Rebuilt from stored tool-call metadata on resume only at history level |
| Policy and approval | `Scheduler._processToolCall` → `checkPolicy` → `resolveConfirmation` | Scheduler, policy engine, confirmation bus | Active-call map, correlation ID, confirmation details, approval outcome | Abort signal closes the bus iterator; user cancel cancels the active call and queued batch | Approval waits are live only; no durable approval receipt was found |
| Tool execution | `ToolExecutor.execute` → `executeToolWithHooks` → invocation | Tool executor and the invocation adapter | Live output, execution ID, terminal response | Abort signal is passed to invocation adapters; actual ownership varies by adapter | Terminal results are recorded into conversation tool-call metadata |
| Built-in shell process | `ShellExecutionService.execute` | Shell execution service plus execution lifecycle service | Static maps of active PTYs, child processes, listeners, background logs, and per-session background history | Abort handler calls `killProcessGroup`; PTY and stream cleanup runs on exit | Background logs survive in the global temp directory; active maps and history are process memory |
| Project-discovered subprocess | `DiscoveredToolInvocation.execute` | Invocation inside `tool-registry.ts` | Local child process and buffered stdout/stderr | The supplied abort signal is named `_signal` and unused; listeners are removed on `close` | No execution receipt beyond eventual tool result |
| MCP network call | `DiscoveredMCPToolInvocation.execute` | MCP callable tool and local invocation wrapper | Local promise plus transport-owned request | Local wait rejects on abort and removes its listener; `callTool` receives no abort signal in this path | Late remote completion is ignored by the local promise; remote side-effect cancellation remains transport-dependent |
| Background execution | `ExecutionLifecycleService.background` | Execution lifecycle service | Active execution remains in memory; foreground promise resolves as backgrounded | Later completion can inject or notify; kill resolves an aborted result | No cross-process reattachment for active executions was found |
| Session persistence | `ChatRecordingService.appendRecord` | Chat recording service | Synchronous JSONL append, with full message updates keyed by message ID | ENOSPC disables further recording; malformed individual lines are skipped by loader | Resume replays metadata, rewinds, and latest message records |
| Session resume | `loadConversationRecord` → `convertSessionToClientHistory` → history hardening | Recording loader, resume hook, history conversion and context manager | Rebuilt history of user/model turns and tool calls/results | Missing tool result becomes an unmatched function call | History hardening inserts a synthetic lost-result response |
| Scheduler disposal | `Scheduler.dispose` | Scheduler | Message-bus subscriptions and state-manager updates | Unsubscribes from the confirmation bus; caller owns aborting current work | No durable scheduler-state restore |

## Runnable probe

Artifacts:

- `artifacts/lifecycle_probe.mjs`
- `artifacts/lifecycle_probe-output.json`

Command:

```sh
node programmes/agent-cli-execution/scouts/gemini-tool-session-recovery/artifacts/lifecycle_probe.mjs
```

The probe uses Node built-ins and fixed inputs. It mirrors five pinned control-flow fragments without invoking a model or external service.

Observed results:

| Case | Observation | Label |
| --- | --- | --- |
| Discovered-tool abort ownership | Abort remains unobserved by the invocation while the child remains alive | probe-reproduced |
| Parallel confirmation affinity | Target `call-b` selects `call-a` through first-active lookup | probe-reproduced |
| Approval wait abort | Callback sequence is `[true]` | probe-reproduced |
| External kill acknowledgement | Lifecycle state becomes inactive while the simulated OS child remains alive | probe-reproduced |
| Interrupted session recovery | Trailing partial JSONL is skipped; unresolved call receives the context-truncation sentinel | probe-reproduced |

This is a source-equivalent control-flow probe. A target-native test suite run remains part of each candidate branch.

## Findings

### 1. Project-discovered tool cancellation does not terminate its subprocess

**Labels:** source-confirmed, test-confirmed gap, probe-reproduced.

`DiscoveredToolInvocation.execute` receives `abortSignal` as `_signal`, then starts a child process and waits for `close`. The signal is never checked, subscribed, or forwarded. Cleanup removes event listeners and disconnects IPC after the process closes; it does not terminate the child on cancellation.

The scheduler and tool executor pass an abort signal into invocation execution. This adapter breaks that ownership chain. A user interruption can therefore produce a cancelled scheduler call while the project tool command keeps running and may still perform filesystem, network, or service side effects.

The existing project-discovered tool execution test covers a non-zero exit and passes a live signal, but it contains no aborted-child case.

**Consequence:** orphaned work, side effects after cancellation, delayed scheduler completion, and overlap if a user retries the operation.

### 2. Parallel approval modification can use another call's tool and arguments

**Labels:** source-confirmed, test-confirmed gap, probe-reproduced.

The scheduler validates parallel active calls with `Promise.all`. Each approval has its own call ID and correlation ID. `resolveConfirmation` retrieves the current target by call ID before asking for confirmation, which is the correct affinity.

Both modification paths then pass `state.firstActiveCall` into `ToolModificationHandler`:

- external editor modification;
- inline content modification.

The handler reads that selected call's tool, confirmation details, file content, path, and arguments. With two active approvals, the first inserted call can differ from the call whose correlation ID received the modification response. The returned parameters are then rebuilt and written under the target call ID, mixing two calls.

The single-call confirmation tests explicitly mock `firstActiveCall` to the same call under test. The parallel scheduler tests establish multiple active calls but do not combine that state with approval modification.

**Consequence:** the user can approve or edit one operation while the modification logic reads another operation's file or arguments. This crosses an approval boundary and can also produce invalid arguments or wrong-file writes.

### 3. Interrupted-session recovery has no durable tool-lifecycle receipt

**Labels:** source-confirmed, probe-reproduced, candidate.

Chat persistence is synchronous append-only JSONL. Tool calls and their eventual results are stored inside Gemini message records. The loader tolerates an interrupted trailing line by skipping malformed records, which is useful crash resilience.

A process interruption after the call is recorded and before its result is durably recorded leaves a tool call without a result. Resume conversion rebuilds the model function call and creates a function-response turn only when a result exists. History hardening then detects the unmatched call and inserts this error:

> The tool execution result was lost due to context management truncation.

The persisted record has no durable status that identifies:

- awaiting approval;
- denied or cancelled;
- executing with an owned process ID;
- completed side effect with result loss;
- backgrounded and still running;
- terminated during shutdown;
- actual context-management truncation.

**Consequence:** the resumed session receives a specific cause unsupported by the stored evidence. A later retry can duplicate an already-completed side effect, while a still-running child has no reattachment path.

### 4. External process kill is acknowledged before asynchronous termination completes

**Labels:** source-confirmed, test-confirmed contract, probe-reproduced.

`ExecutionLifecycleService` defines external `kill` hooks as synchronous `() => void`. Its `kill` method invokes the hook and immediately settles the execution with exit code 130, emits an exit event, removes listeners, and deletes the active execution.

Shell execution registers a kill hook that calls asynchronous `killProcessGroup(...).catch(...)` and returns immediately. `ShellExecutionService.kill` therefore can resolve after lifecycle cleanup while process-tree termination is still in progress.

Current lifecycle tests use synchronous mock termination and assert immediate completion. They do not hold termination open and check active ownership during the terminating phase.

**Consequence:** UI and callers can observe cleanup completion while the process tree still exists. A retry can overlap with the previous process, and a later real exit cannot replace the already-settled aborted result.

### 5. Aborted approval waits can leave waiting state enabled

**Labels:** source-confirmed, test-confirmed gap, probe-reproduced.

`resolveConfirmation` calls `onWaitingForConfirmation(true)`, awaits the bus/IDE result, and then calls `false`. The second call sits after the `await`, outside a `finally` block. Abort and other rejection paths skip it.

The dedicated scheduler callback test only verifies that the callback is passed into `resolveConfirmation`. Confirmation tests cover successful response, editor modification, inline modification, IDE success, and lost call state. They do not assert callback balance after abort or rejection.

**Consequence:** subagent or UI state can remain in a waiting mode after cancellation, which can block subsequent lifecycle decisions or report the wrong activity state.

### 6. MCP abort ends the local wait without proven remote cancellation

**Labels:** source-confirmed locally, open remotely.

The MCP invocation races `callTool` against the abort signal and rejects locally on abort. The underlying `callTool(functionCalls)` receives no signal in this path. The wrapper removes its local listener and ignores late resolution through normal Promise settlement rules.

This establishes local cancellation semantics. Remote execution cancellation depends on the MCP client and transport outside this call. The lane did not find a cancellation handle passed from this invocation to that owner.

**Consequence:** local state can say cancelled while a remote side effect continues. A branch needs transport/API confirmation before implementation.

## Resilience and negative results

1. **JSONL crash tolerance:** each complete record is appended synchronously, and malformed individual lines are ignored during loading. A partial final line does not invalidate earlier records.
2. **Shell cancellation preserves partial output:** scheduler state conversion and `ToolExecutor` cancellation responses retain live or returned output where available.
3. **Shell abort path attempts process-tree cleanup:** child and PTY abort handlers call `killProcessGroup` with escalation. Unix handling targets the process group and enumerated descendants; Windows uses PTY termination plus `taskkill /f /t`.
4. **Confirmation bus listener cleanup is mostly explicit:** the bus-versus-IDE race removes its parent abort listener and aborts the losing iterator in `finally`.
5. **Queued cancellation is explicit:** scheduler cancellation converts queued calls to terminal cancelled responses, and a user denial cascades across the current batch. This appears intentional in the pinned implementation.
6. **MCP local listener cleanup is explicit:** abort listeners are removed after abort, resolve, or reject.
7. **No model-quality dependency:** every finding comes from fixed control flow, persistence format, or ownership contracts.

## Competing hypotheses and distinguishing tests

### Hypothesis A: approval modification is effectively serial in the product

The scheduler itself supports multiple active validating calls and runs validation concurrently. The distinguishing target test should schedule two modifiable tools, wait for two correlation IDs, answer the second first with modified content, and assert that only the second call's tool, file path, and arguments are read and updated.

### Hypothesis B: the context-truncation sentinel is only an API compatibility message

Even as an API compatibility message, it assigns a cause and becomes part of resumed history. The distinguishing test should interrupt a session at each lifecycle phase and inspect both UI history and client history. Each phase should recover to an explicit stored outcome or an evidence-limited `interrupted_unknown` response.

### Hypothesis C: process termination is intentionally fire-and-forget

The public `ShellExecutionService.kill` method is asynchronous and callers can reasonably treat resolution as completion. The distinguishing test should provide a deferred asynchronous external kill hook, invoke kill, and require lifecycle ownership to remain in `terminating` until the hook resolves or a bounded timeout expires.

### Hypothesis D: discovered tools finish quickly enough that abort ownership has little value

Project tool commands are arbitrary subprocesses. The distinguishing test should spawn a long-running command with a child process, abort the invocation, and assert both parent and descendant exit before the invocation settles.

## Ranked branch candidates

### 1. `fix/discovered-tool-abort-process-tree`

**Confidence:** high.  
**Owner:** `packages/core/src/tools/tool-registry.ts`.  
**Tests:** `packages/core/src/tools/tool-registry.test.ts`.

Implementation:

- consume `abortSignal` in `DiscoveredToolInvocation.execute`;
- reject before spawn when already aborted;
- register a one-shot abort listener after spawn;
- terminate the child and descendants through the shared process utility;
- remove the abort listener on close/error;
- settle only after child termination or a bounded escalation path;
- test parent and descendant cleanup, already-aborted signal, output-before-abort, and listener cleanup.

Payoff: closes a direct orphan-process path for project-configured tools.

### 2. `fix/scheduler-confirmation-call-affinity`

**Confidence:** high.  
**Owner:** `packages/core/src/scheduler/confirmation.ts` and `state-manager.ts`.  
**Tests:** `confirmation.test.ts` and `scheduler_parallel.test.ts`.

Implementation:

- replace `state.firstActiveCall` with `state.getToolCall(toolCall.request.callId)`;
- assert the retrieved call is still awaiting approval and has the expected correlation context;
- pass that exact call to both modification handlers;
- add two-call, out-of-order approval tests for external and inline modification;
- assert one call's payload never reads or updates the other call.

Payoff: restores call-level approval affinity and prevents wrong-file or wrong-argument modification.

### 3. `feat/session-interrupted-tool-reconciliation`

**Confidence:** high on the persistence gap; medium on final schema.  
**Owner:** chat recording types/service, scheduler terminal callbacks, session conversion, and history hardening.  
**Tests:** chat recording, session resume, history hardening, and one end-to-end interrupted-session fixture.

Implementation:

- append lifecycle records keyed by call ID for `awaiting_approval`, `scheduled`, `executing`, `backgrounded`, `success`, `error`, and `cancelled`;
- include execution ID, tool name, argument digest, timestamps, and terminal response reference where available;
- on startup, reconcile every nonterminal receipt into an explicit status such as `interrupted_unknown` or `cancelled_during_shutdown`;
- retain cause as `unknown` unless evidence names it;
- suppress the context-truncation sentinel for lifecycle-interrupted calls;
- add an idempotency marker or operator warning for side-effecting calls with unknown completion;
- test interruption after approval, after process spawn, after side effect, after backgrounding, and during result append.

Payoff: truthful recovery and fewer duplicate side effects.

### 4. `fix/execution-lifecycle-await-termination`

**Confidence:** high.  
**Owner:** `executionLifecycleService.ts`, `shellExecutionService.ts`, and lifecycle tests.

Implementation:

- allow external kill hooks to return `void | Promise<void>`;
- introduce a `terminating` live state;
- await termination before emitting exit and deleting ownership;
- use a bounded timeout with an explicit timeout result;
- preserve late real exit details when available;
- test deferred termination, repeated kill, natural exit during kill, and process-group escalation.

Payoff: makes cleanup acknowledgement correspond to process ownership release.

### 5. `fix/confirmation-waiting-finally`

**Confidence:** high.  
**Owner:** `confirmation.ts`.  
**Tests:** `confirmation.test.ts` and `scheduler_waiting_callback.test.ts`.

Implementation:

- wrap the wait in `try/finally`;
- pair every `true` transition with `false`;
- cover bus abort, IDE rejection with later bus abort, lost call state, and callback exceptions;
- define whether nested or parallel waits require a counter instead of a boolean.

Payoff: reliable cancellation and activity reporting for approval waits.

### 6. `spike/mcp-call-cancellation-ownership`

**Confidence:** medium.  
**Owner:** MCP invocation/client transport.

Implementation question:

- determine whether the callable tool or transport supports request cancellation;
- pass a cancellation token when supported;
- otherwise record that the remote call is detached and expose that state to recovery;
- test late remote completion after local abort and side-effecting MCP calls.

Payoff: aligns local cancellation with remote execution ownership, or reports the ownership gap explicitly.

## Suggested campaign order

1. Land call-affinity and discovered-tool abort tests first; both are narrow and high-confidence.
2. Add deferred process-kill ownership tests and revise the lifecycle contract.
3. Design the durable lifecycle receipt with fixtures from the first two branches.
4. Add truthful resume reconciliation and idempotency warnings.
5. Resolve MCP transport cancellation as a focused spike.

## Alternative designs

### Call-scoped confirmation object

Create a confirmation session object containing call ID, correlation ID, invocation revision, tool, and modifier. Modification methods receive this object directly, avoiding global active-call lookup.

### Tool lifecycle write-ahead log

Append lifecycle events before and after every side-effect boundary. Resume folds events by call ID and reports the last evidenced phase. This fits the existing JSONL append model and preserves crash tolerance.

### Process supervisor ownership

Make every process-producing invocation register an execution handle with one supervisor. The handle owns abort, backgrounding, output, termination acknowledgement, and recovery metadata. Adapters stop implementing partial local lifecycle rules.

## Limitations

- Source was inspected at the pinned revision through repository retrieval. The full Gemini CLI test suite was not executed in this lane.
- The runnable probe is minimized and source-equivalent; each branch needs a target-native regression test.
- OS-specific descendant behaviour needs Linux, macOS, and Windows process-tree runs.
- Remote MCP cancellation support remains open until the callable-tool and transport contracts are exercised directly.
- No upstream issue, comment, pull request, email, or other contact was created.

## Handoff

- Worker: `chatgpt:gpt-5.6-thinking`
- State: ready for synthesis after Fieldwork review
- Programme: `agent-cli-execution` (`#14`)
- Target: Gemini CLI (`#5`)
- Parent issue: `#22`
- Question: deterministic tool approval, execution, process ownership, persistence, interruption, cancellation, cleanup, and recovery
- Deliverables:
  - `programmes/agent-cli-execution/scouts/gemini-tool-session-recovery/report.md`
  - `programmes/agent-cli-execution/scouts/gemini-tool-session-recovery/artifacts/lifecycle_probe.mjs`
  - `programmes/agent-cli-execution/scouts/gemini-tool-session-recovery/artifacts/lifecycle_probe-output.json`
- Owned path: `programmes/agent-cli-execution/scouts/gemini-tool-session-recovery/`
- Target revision: `google-gemini/gemini-cli@3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`
- Evidence: pinned source and tests plus five-case lane-owned probe
- Main result: concrete branches for subprocess abort ownership, approval call affinity, interrupted-session reconciliation, asynchronous process termination, and approval-wait cleanup
- Dependencies: programme hub `#14`, target hub `#5`, reusable process cases from sibling lane `#24`
- Remaining uncertainty: target-native and cross-platform execution; MCP remote cancellation contract
- Upstream contact authorized: `false`
