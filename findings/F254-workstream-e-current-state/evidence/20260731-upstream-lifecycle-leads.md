# Upstream Gemini lifecycle leads — 2026-07-31

Evidence class: `upstream issue report`; independently unexecuted by Fieldwork  
Routing decision: absorb as controls and reopening triggers under existing owners  
New Fieldwork issue created: `no`  
Public upstream interaction performed: `no`

## Why these reports belong here

The updated decision protocol favors completing current technical owners over opening parallel backlog surfaces. Three current Gemini CLI reports intersect existing Workstream E invariants closely enough to strengthen their test matrices.

They remain reports until Fieldwork reads current source or executes the behavior. They do not establish defect frequency, current-main reproduction, or a production repair.

## Lead A — relaunch parent loses child signal ownership

Upstream issue: https://github.com/google-gemini/gemini-cli/issues/25590  
Reported area: `packages/cli/src/utils/relaunch.ts`, `relaunchAppInChildProcess`  
Reported environment: Linux under process-manager signalling  
Route: F22 process-tree and termination ownership

### Reported behavior

The memory-tuning bootstrap parent spawns the full CLI child with inherited stdio and IPC. Programmatic `SIGTERM` or `SIGHUP` reaches the bootstrap PID, while the child receives no forwarded signal and becomes reparented. Interactive Ctrl+C can hide the seam because the foreground terminal sends SIGINT to the process group.

### Why it is discriminating

The selected F22 termination receipt cannot treat bootstrap-parent exit as command termination when the real CLI child remains alive. A process receipt needs the identity of the execution owner it represents and a confirmed descendant-settlement rule.

### Controls to add

1. launch the real relaunch parent and full-memory child;
2. send `SIGTERM` to the supervised parent PID rather than the terminal process group;
3. require the child to receive the intended signal or a stronger explicit shutdown request;
4. require the parent receipt to remain pending until child settlement;
5. race signal delivery with natural child exit;
6. repeat relaunch cycles and prove precise listener removal;
7. preserve inherited stdin/stdout behavior;
8. classify SIGINT, SIGTERM, SIGHUP, and unsupported Windows signals separately.

### Ownership decision

Absorb into F22 and the discovered-tool process-tree lane. A separate finding is unnecessary unless current source shows bootstrap relaunch has an independent terminal-result owner from `ExecutionLifecycleService`.

## Lead B — Windows SEA turns a kill helper into another Gemini session

Upstream issue: https://github.com/google-gemini/gemini-cli/issues/26365  
Reported area: Windows SEA bootstrap plus `@lydell/node-pty` helper execution  
Reported environment: standalone `gemini.exe` on Windows  
Route: F22 adapter-specific termination matrix

### Reported behavior

Inside a Single Executable Application, `child_process.fork()` defaults to `process.execPath`, which is `gemini.exe`. A node-pty console-list helper used during terminal kill can therefore start a second full Gemini session instead of the intended helper script. The helper never sends its IPC reply, the original kill path times out, and console-handle reaping remains incomplete.

### Why it is discriminating

A successful call to the node-pty kill adapter does not prove the expected helper executed. F22 needs adapter evidence that binds the termination receipt to the intended child program, IPC response, and process tree.

The reported second session can also lose the original invocation's approval mode and inherit shared debug-log state, so the failure crosses authority, output, and cleanup boundaries.

### Controls to add

1. execute a fork-based helper inside the real Windows SEA artifact;
2. require helper IPC identity and exact argv normalization;
3. prove zero second Gemini bootstrap/session;
4. execute `WindowsTerminal.kill()` and require console-process enumeration;
5. verify original approval flags and debug-log ownership stay isolated;
6. classify node-pty timeout as request failure or outcome unknown, never confirmed termination;
7. execute the same matrix under npm/Node distribution as the control;
8. prove cleanup after helper load failure.

### Ownership decision

Absorb into F22's Windows adapter matrix. Reopen as a separate SEA execution finding only if the repair belongs exclusively to distribution bootstrap and changes helper execution beyond termination.

## Lead C — singleton external editor has no document-completion receipt

Upstream issue: https://github.com/google-gemini/gemini-cli/issues/24678  
Reported area: `Modify with external editor` using Zed on Windows  
Route: Gemini approval affinity / external modification integration after PR #6 focused gates

### Reported behavior

Closing the edited tab in Zed leaves Gemini waiting until the entire singleton editor process exits. VS Code's wait behavior completes when the document closes. The reported seam is process lifetime versus edit-session completion.

### Why it is discriminating

PR #6 repairs which tool call owns modification before and after the modifier await. It still needs an integration control proving that the await itself has a valid completion owner. Waiting for a singleton application process can hold approval indefinitely and lets cancellation or call replacement occur during the wait.

### Controls to add

1. model editor completion as an explicit document/session receipt;
2. compare VS Code, Zed, and a simple child editor fixture;
3. cancel or replace the tool call while the editor receipt is pending;
4. require post-await call/status revalidation before `updateArgs`;
5. require timeout and editor-process failure to leave the call in an explicit recoverable state;
6. remove editor listeners and temporary files exactly once;
7. avoid treating the entire singleton editor lifetime as document completion.

### Ownership decision

Add these controls to the affinity/external-modification successor. A new finding becomes useful only if current source reveals a shared editor-session abstraction used beyond approval modification.

## Ranked follow-up

1. **Windows SEA helper identity** — highest platform-specific risk because the termination helper can execute the wrong program and spawn another agent session.
2. **Relaunch signal forwarding** — highest process-supervision risk because the visible parent can exit while the real CLI child survives.
3. **External editor completion receipt** — strong approval-liveness lead; schedule after PR #6's focused authority gates settle.

## Stop rule

Keep these as routed hypotheses until one of these events:

- current-source read disproves the reported path;
- target execution reproduces the behavior;
- upstream source absorbs the issue;
- the repair requires a distinct owner and rollback boundary.

The portfolio map should reference the resulting exact finding or stopped record instead of growing a permanent lead list.
