# cmux cross-generation identity scout

Date: 2026-09-01  
Programme: high-leverage-open-source  
Target: `manaflow-ai/cmux`  
Worker: automated code-first scout  
Upstream contact authorized: `false`

## In simple words

cmux deliberately lets some logical identities survive when the physical thing underneath them is replaced. Most of the dangerous seams I checked carry a second token for the physical generation: cloud machines have an active generation/current VM pairing, terminal hosts have `terminal_id + incarnation`, PTY attachments have exact attachment tokens/objects, and remote bridge ownership has lifecycle/transport generations.

The strongest current mismatch is in Computer Use hook completion. An agent's native session id is intentionally reused when cmux resumes that agent into a new process. `ComputerUseLiveSessionProjection.driverSessionID(...)` nevertheless accepted a hook immediately when that durable session id matched the current record, before checking the hook's process identity. A delayed `Stop` or `SessionEnd` from retired process A could therefore resolve to successor process B when A and B shared the same resumed agent session id.

The owned fork now carries an exact-base red regression and a two-commit repair candidate. The repair makes a supplied hook PID authoritative: when `ppid` exists, cmux must prove that exact current `AgentPIDProcessIdentity` belongs to the current live process tree. The logical-session-id shortcut remains only for hook sources that carry no process id.

## Assignment

Question: find a boundary where one cmux identity layer survives while a lower physical generation is recreated, and determine whether stale generation A can mutate or retire current generation B through the old logical identity.

Expected deliverable: exact upstream revision, identity map, intended persistence boundary, A→B sequence, distinguishing stale/current operations, negative control, durable consequence, smallest generation fence, fork candidate, and executable regression evidence.

Owned output path: `programmes/high-leverage-open-source/scouts/cmux-cross-generation-identity/`  
Stop condition: exact-base red regression, bounded repair, clean candidate diff, red→green execution result or explicit execution blocker, and upstream kept read-only.

## Exact upstream state

Repository: `manaflow-ai/cmux`  
Pinned upstream `main`: `eaa899cb20bd411019744fbd2bdedeb397f3070b`  
Pinned date: 2026-09-01

Automated upstream writes, issues, comments, reviews, pull requests, and maintainer contact: **none**.

## Identity map

| Layer | Durable / reconnect identity | Physical-generation identity | Replacement rule / owner | Result |
| --- | --- | --- | --- | --- |
| account / user | account/auth principal | outside this scout's useful lower-generation seam | auth layer | no candidate promoted |
| machine / cloud VM | logical machine/base record | active generation + current physical VM id | cloud repository decides whether an observation belongs to the current machine generation | fenced in inspected paths |
| daemon | durable registry/resource state | daemon generation / live process generation | daemon handshake and registry ownership | fenced in inspected paths |
| session | durable session/resource ids where specified | daemon/resource child generations | registry | no violating sequence established |
| workspace | durable workspace/resource identity | live pane/surface/runtime owners | workspace registry | no violating sequence established |
| terminal | stable `terminal_id` | `terminal_incarnation` | terminal registry + host protocol | explicitly fenced |
| terminal incarnation | none; this is the generation token | host incarnation | exact-incarnation comparisons | explicitly fenced |
| PTY | persistent logical `sessionID` | exact in-memory `wsPTYSession` object / process session | PTY hub | object-identity cleanup fences; `pty.close` is intentionally logical-session-wide |
| attachment | attachment id | client attachment token + exact attachment object | PTY hub | explicitly fenced |
| local bridge | logical lifecycle id | bridge/transport ownership generation | proxy broker/tunnel lifecycle registry | explicitly fenced |
| agent session | native agent `sessionId`, intentionally reused by resume | `AgentPIDProcessIdentity(pid,startSeconds,startMicroseconds)` | live agent index + process scanner | **mismatch in Computer Use hook resolution** |

## Intended agent persistence boundary

cmux's resume path treats the native agent session id as durable state. `SessionEntry` stores the native CLI session identifier and constructs resume commands using that same id, including Codex `resume <sessionId>`, Claude `--resume <sessionId>`, Grok `-r <sessionId>`, OpenCode `--session <sessionId>`, and equivalent exact-session restore paths.

Therefore this is an intended transition:

```text
logical agent session L / process generation A
        A exits
cmux resumes logical session L
logical agent session L / process generation B
```

cmux already has a lower-level generation token for this transition: `AgentPIDProcessIdentity`, which includes process id plus process start time. Other agent recovery and Computer Use control paths use that identity to reject stale or recycled PIDs.

## Failing boundary

Owner: `Sources/App/ComputerUseLiveSessionProjection.swift`

Pre-fix resolution order:

```text
surface matches current projection
→ if current agentSessionID == hook agentSessionID: accept
→ otherwise, if hook ppid identifies a process in current root tree: accept
```

The first branch treats a durable logical id as proof of current process generation. That contradicts the resume contract above.

The method comment itself states the intended stronger invariant: a delayed `Stop` from a replaced process must not match the successor's live process tree.

## A → replacement B sequence

Use stable surface `S`, stable Computer Use driver identity `D = driverSessionID(S)`, and durable native agent session `L`.

1. Generation A runs on `S` with physical identity `PA` and logical session `L`.
2. A invokes Computer Use; the coordinator records the accepted invocation for stable driver `D`.
3. A emits `Stop` or `SessionEnd`, carrying `surfaceId=S`, `sessionId=L`, and `ppid=pidA`, but delivery/handling is delayed.
4. A exits.
5. cmux resumes the same logical session `L` into physical process generation B with identity `PB != PA`.
6. The live projection now maps `D` to `(S, L, PB)`.
7. B starts/currently owns Computer Use state.
8. Delayed A completion is resolved.

### Distinguishing stale-A operation

```text
surfaceId = S
sessionId = L
ppid = pidA
```

Before the candidate repair, equality of `L` returned `D` before `pidA` was checked against B's current root process identities.

### Current-B negative control

```text
surfaceId = S
sessionId = L
ppid = pidB
```

This must resolve to `D`.

A hook-protocol alias with a different logical id and `ppid=pidB` must also continue to resolve, because some agents expose different scanner and hook identifiers and the current process generation is the stronger authority.

A same-session hook with no process id retains the old logical-session compatibility fallback.

## Consequence

`ComputerUseUXCoordinator.handleWorkstreamEvent` treats accepted `Stop` / `SessionEnd` as completion of stable driver `D`. It records a completion cutoff, asks the current menu snapshot for the proxy session associated with `D`, tells the watch-target/presentation controllers that `D` completed, removes the menu row, and removes the accepted invocation record.

The presentation controller moves the current stable driver state to `hiddenReusable`, resets focus mode, cancels current focus/cursor/reassert tasks, and schedules cursor hiding against the resolved current proxy session.

So the cross-generation consequence is:

```text
retired A completion
→ stable driver D
→ current B proxy/session presentation state
→ B cursor/activity can be retired as though B completed
```

This scout does not claim stale A can rewrite B's authenticated disk state, kill B's process, or cross an auth boundary through this seam.

## Smallest generation fence

Candidate policy:

1. if `hookProcessID` is supplied, construct its current `AgentPIDProcessIdentity`;
2. require that exact identity to belong to the current projected root process tree;
3. if the process check succeeds, accept regardless of scanner-vs-hook session-id spelling;
4. if no process id is supplied, retain exact logical agent-session-id matching as compatibility fallback.

This uses an existing generation token and changes only the admission order.

## Owned-fork candidate

Owned fork: `teamleaderleo/cmux`

Exact red branch: `fieldwork/cmux-computer-use-generation-red-20260901`  
Red test-only commit: `e41f91cc7f99bb0c405893bf206f38b7c6d32ac5`

Candidate branch: `fieldwork/cmux-computer-use-generation-fence-20260901`  
Production repair: `a447598ef3fb26a8b288c740b1e3f9435446c53f`  
Green test commit / candidate head: `8330732cc2dc5c7d045afa15e9e63f928e500146`

Candidate diff versus upstream is exactly:

```text
Sources/App/ComputerUseLiveSessionProjection.swift
cmuxTests/ComputerUseCrossGenerationIdentityTests.swift
```

Production delta: 16 additions / 13 deletions in the resolver file.  
Regression: 97-line focused Swift Testing file.

## Regression design

`ComputerUseCrossGenerationIdentityTests.delayedGenerationACompletionCannotResolveGenerationBWithSameLogicalSession` uses real process generations:

- generation A: launches `/usr/bin/true`, records its PID, waits for A to exit;
- generation B: uses the live test process and captures its exact `AgentPIDProcessIdentity`;
- both are modeled as the same logical native agent session id;
- the live projection contains only B's current process identity.

Assertions:

1. current B PID + stable logical id → accepted;
2. current B PID + alternate hook-protocol id → accepted;
3. retired A PID + same stable logical id → rejected;
4. no PID + same stable logical id → compatibility fallback accepted.

The third assertion is the discriminator: upstream source accepts it through the logical-id shortcut; the candidate requires current process-generation membership.

## Executable verification

Temporary Fieldwork workflow: `.github/workflows/cmux-computer-use-generation.yml` on branch `fieldwork/cmux-cross-generation-identity-20260901`.

Run: `33549605183`

The workflow pins immutable SHAs and performs:

- ancestry/diff checks;
- exact upstream + test-only red execution;
- exact candidate green execution;
- one focused `cmux-unit` test on macOS 14.

Current state at initial report materialization: **queued**. Treat runtime proof as pending until the run has a terminal result. The temporary workflow is an execution carrier and must be removed from the final Fieldwork branch after evidence capture.

## Boundaries checked and ruled down

### Cloud machine resurrection

The cloud machine path carries an active physical generation/current VM association under the durable logical machine record. I found no source sequence where a stale old machine generation can silently publish itself as the current VM through the inspected owner path.

### Daemon replacement

The daemon/runtime layers inspected carry explicit generation/ownership checks. Durable registry identities surviving process restart are intentionally separate from live daemon process identity.

### Terminal host replacement

This is one of the strongest fences in the codebase. Stable `terminal_id` is paired with `terminal_incarnation`; recovery/adoption and mutations compare incarnation before transferring ownership or acting on stale host state.

### Persistent PTY and attachment

Persistent PTY `sessionID` is intentionally logical. Physical session cleanup uses exact `wsPTYSession` object identity before deleting the map entry, while input/resize/detach resolve an exact current attachment id/token/object. `pty.close(sessionID:)` is generation-blind at the daemon wire layer, but its Swift caller contract intentionally defines a logical-session-wide close and gates locally known lifecycle generations before issuing it. I did not establish a production interleaving that violates that contract.

### Local bridge / transport replacement

The remote proxy broker snapshots PTY lifecycle state through automatic tunnel replacement and carries lifecycle/attachment/transport ownership tokens. Wrapper-end cleanup claims the exact owner before retiring it.

### Terminal public API candidate

The resource-v2 terminal API still deserves a separate executable investigation because some public effects are addressed by stable terminal id while the durable model also knows `terminal_incarnation`. I did not establish a legal production A→B transition that preserves the exact public terminal id yet crosses the native host-incarnation fences, so this scout does not promote it as a finding.

## Evidence labels

- upstream revision: `github-read`;
- identity/resume contracts: `source-read`;
- failing resolver order: `source-read`;
- downstream completion consequence: `source-read`;
- red regression: `fork-authored / execution pending`;
- production repair: `fork-authored`;
- candidate ancestry/diff: `github-compare`;
- red→green runtime: `execution pending`;
- upstream contact: absent.

## Evidence limit

The source-level violating sequence is deterministic once a delayed A event reaches `driverSessionID` after B becomes current: pre-fix code accepts on logical-session equality before consulting A's physical generation. The exact scheduling/reachability of that sequence in an app-host run is being tested by the focused macOS regression.

No broader claim is made about frequency in production or affected-user prevalence.

## Recommendation

Retain this as a high-confidence cross-generation correctness candidate. If the pinned red→green run reaches the assertion and behaves as predicted, the owned fork has a narrow repair suitable for independent review or a human-prepared upstream packet. Keep third-party upstream read-only unless separately authorized.
