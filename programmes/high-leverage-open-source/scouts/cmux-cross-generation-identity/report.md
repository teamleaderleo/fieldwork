# cmux cross-generation identity scout

Date: 2026-09-01  
Programme: high-leverage-open-source  
Target: `manaflow-ai/cmux`  
Owned fork: `teamleaderleo/cmux`  
Upstream contact authorized: `false`

## Current result

The strongest cross-generation seam remains Computer Use hook completion across an agent-process replacement. The durable native agent session id can survive a resume, while the physical process generation changes. A delayed completion from retired process A must never complete successor B simply because both use the same surface and native session id.

The owned fork now carries the full fence, not the earlier PID-only draft:

- exact upstream/base: `6044a8b3f43152d2e6fc17f771fd4b277b393118`;
- test-only red: `d13e9a7cb3a3712f9f7a7f507c13d3a312c41d20`;
- initial PID fence: `fbc7742dc04a5e7d14172a48aa43066296d24ac6`;
- full ingress-generation fence / current head: `1287e78a3a751e41d7fb23ca4157d57403fac1d2`;
- owned draft PR: `teamleaderleo/cmux#17`.

The full candidate captures the hook sender's exact kernel birth identity at trusted Feed ingress and carries it with the event. Later Computer Use handling uses that frozen identity instead of resolving a bare PID after it may have been recycled. The projection-gap completion fallback is fenced by the same exact generation.

Third-party upstream remains read-only: no automated upstream issues, comments, reviews, pull requests, or maintainer contact.

## Identity map

| Layer | Durable identity | Physical-generation identity | Result in inspected paths |
| --- | --- | --- | --- |
| machine / cloud VM | logical machine/base | active/current physical VM generation | fenced |
| daemon | durable registry/resource state | daemon/live runtime generation | fenced in inspected recovery paths |
| workspace | workspace/resource id | live surface/runtime owner | no violating sequence established |
| terminal | `terminal_id` | `terminal_incarnation` | explicitly fenced |
| PTY | persistent `sessionID` | exact `wsPTYSession` object/process | exact-object cleanup/input fences |
| attachment | attachment id | token + exact attachment object | fenced |
| local bridge | logical lifecycle id | bridge/transport owner generation | fenced |
| agent session | native CLI session id, intentionally reused by resume | `AgentPIDProcessIdentity(pid,startSeconds,startMicroseconds)` | failing seam found in Computer Use |

## Persistence boundary

CMUX's resume paths intentionally reuse native agent session identifiers. A valid lifetime transition is:

```text
logical session L / process A
A exits
resume L
logical session L / process B
```

That makes `L` a logical identity, not proof that a hook came from the current OS process generation.

CMUX already models the lower generation with `AgentPIDProcessIdentity`, whose identity is PID plus process start seconds and microseconds. Related current upstream lifecycle work uses the same PID-birth identity because PID alone is recyclable.

## Upstream review performed

Relevant upstream work was reviewed read-only before extending the candidate.

### PR #9586 — agent lifecycle/process liveness

`manaflow-ai/cmux#9586` is still open and large. It moves multiple lifecycle paths toward exact process generations and requires PID start timestamps in several control paths. Its Cursor `generation_id` is explicitly a per-turn identifier, not the kernel process generation needed here. The current PR does not remove the Computer Use `WorkstreamEvent` `_ppid` seam on upstream `main`.

### Other lifecycle/resume work

Recent CMUX work around managed-agent liveness and Codex resume similarly treats process birth identity as the physical-generation discriminator. The fork candidate follows that convention rather than introducing a parallel logical token.

## Original failure

On upstream `6044a8b3`, `ComputerUseLiveSessionProjection.driverSessionID(...)` resolves a current surface and then accepts immediately if the current record's logical agent session id equals the hook session id. The process check is only the fallback for differing agent ids.

Therefore this sequence can cross generations:

1. stable surface `S`, stable driver `D`, durable agent session `L`;
2. process A with generation `PA` invokes Computer Use;
3. A emits a delayed `Stop` or `SessionEnd` carrying `S`, `L`, and `pidA`;
4. A exits;
5. CMUX resumes `L` into process B with `PB != PA`;
6. B becomes current for `D`;
7. delayed A completion is handled;
8. equality on `L` can resolve the stale event to current `D` before A's physical generation is considered.

`ComputerUseUXCoordinator` then records completion for stable driver `D`, resolves the current proxy associated with `D`, retires current presentation/menu activity, cancels current cursor/focus/reassert work, and removes the accepted invocation record. The consequence is a stale-A completion acting on successor-B Computer Use presentation state.

No claim is made here that this seam kills B's process, rewrites authenticated Computer Use disk state, or crosses an authentication boundary.

## Why the first fork patch was incomplete

The initial fork repair `fbc7742d` made a supplied PID authoritative in the live resolver. That closed the obvious A-PID-vs-B-tree case, but two holes remained:

1. `ComputerUseUXCoordinator` has a projection-gap completion fallback keyed by surface + logical agent session + time. A resumed B can keep the same logical session id, so stale A could still match there.
2. Reconstructing `AgentPIDProcessIdentity(pid:)` only when the async consumer handles the event is too late. If A exited and the OS recycled its numeric PID for B, the later lookup can silently identify B.

The final fence moves generation capture earlier.

## Full fence

### 1. Capture exact generation at trusted Feed ingress

`Sources/TerminalController+FeedAcknowledgment.swift` now snapshots `AgentPIDProcessIdentity` for each event's `_ppid` before accepted Feed delivery becomes asynchronous.

The tuple is stored in a reserved opaque event field:

```text
_cmux_agent_process_generation = {
  pid,
  start_seconds,
  start_microseconds
}
```

Ingress removes and replaces any value supplied under that reserved key, so a sender cannot select the generation later trusted by Computer Use. If the live process identity cannot be captured, the reserved generation is removed and generation-bound consumers fail closed.

`WorkstreamEvent` already preserves unknown fields through `extraFieldsJSON`, and target rehoming copies that bag, so the generation survives the existing internal event path without extending every external agent hook protocol.

### 2. Never re-resolve a bare PID later

`ComputerUseLiveSessionProjection.driverSessionID(...)` now takes the captured generation alongside `_ppid`. When `_ppid` exists it requires:

- a captured generation exists;
- captured generation PID equals `_ppid`;
- the exact captured `(pid,startSeconds,startMicroseconds)` belongs to the current root process tree.

The resolver does not call `AgentPIDProcessIdentity(pid:)` at this late boundary, so PID reuse cannot retarget the event.

No-PID hook sources retain the existing logical-session compatibility path.

### 3. Fence the projection-gap completion fallback

`ComputerUseUXCoordinator` now stores the accepted invocation's exact generation. A `Stop`/`SessionEnd` can use the projection-gap fallback only when surface, logical session, ordering, PID, and exact captured generation all match the accepted invocation.

Even if live projection resolves a completion, an active accepted invocation for that driver requires the same generation before completion side effects run.

## Current fork diff

GitHub compare from upstream `6044a8b3` to head `1287e78a` is exactly four files and three linear commits:

```text
Sources/App/ComputerUseLiveSessionProjection.swift
Sources/App/ComputerUseUXCoordinator.swift
Sources/TerminalController+FeedAcknowledgment.swift
cmuxTests/HostSettingsShortcutNotificationTests.swift
```

The regression was placed in an already-wired test source to avoid Xcode target-membership ambiguity.

## Regression coverage

### Exact current vs retired vs PID-recycled generation

`exactGenerationRejectsRetiredAndRecycledProcesses` checks:

- B PID + exact B birth identity + stable logical session → accepted;
- B PID + exact B birth identity + alternate hook-protocol session id → accepted;
- retired A exact generation + stable logical session → rejected;
- B numeric PID + different birth timestamp → rejected;
- bare B PID without ingress generation → rejected;
- no PID + stable logical session → compatibility fallback accepted.

### Trusted ingress overwrite

`feedIngressOverwritesSpoofedGenerationWithLiveKernelIdentity` supplies a forged reserved generation field, captures at ingress using the current live PID, and verifies that the forged generation is replaced while unrelated opaque fields survive.

### Completion fallback

`completionFallbackRequiresExactAcceptedInvocationGeneration` verifies:

- exact accepted B generation → accepted;
- stale A generation → rejected;
- same PID with different birth timestamp → rejected;
- generationless completion → rejected.

## Executable verification

Temporary carrier: `.github/workflows/cmux-computer-use-generation.yml` on Fieldwork branch `fieldwork/cmux-cross-generation-identity-20260901`.

### Previous run

Run `33550591279` completed with failure. Checkout, immutable ancestry/diff checks, Xcode selection, Bun, GhosttyKit, Zig, Rust, DerivedData preparation, and Swift package resolution all succeeded. The failure occurred in the old red-proof step; green was therefore skipped. This is harness/partial evidence, not a green candidate result.

### Current run

Run `33561165354` was triggered by Fieldwork commit `87e736029ef8bd9769602a3b367debe2dd39ad41` and is currently executing.

The refreshed carrier pins:

```text
base    6044a8b3f43152d2e6fc17f771fd4b277b393118
red     d13e9a7cb3a3712f9f7a7f507c13d3a312c41d20
partial fbc7742dc04a5e7d14172a48aa43066296d24ac6
green   1287e78a3a751e41d7fb23ca4157d57403fac1d2
```

It first checks exact linear ancestry and the four-file diff fence. The red side runs the upstream-plus-regression suite and must fail after reaching the stale-A test rather than at build/compile setup. The green side runs the full `ComputerUseCrossGenerationIdentityTests` suite against the final ingress-generation candidate.

Until that run is terminal, evidence class remains `target-test-running`, not `target-executed-green`.

## Boundaries checked and ruled down

### Cloud machine resurrection

The inspected cloud-machine path carries a current physical generation/current VM association under the durable logical machine record. No stale-old-generation publication into the current VM owner was established.

### Daemon replacement

Inspected daemon/runtime recovery paths carry explicit generation/ownership checks while durable registry ids survive restart intentionally.

### Terminal host replacement

Stable `terminal_id` is paired with `terminal_incarnation`; host recovery/adoption and mutations compare incarnation before transferring ownership or acting on stale host state.

### Persistent PTY and attachment

Persistent PTY `sessionID` is logical by contract. Physical cleanup checks exact `wsPTYSession` object identity before removing the map entry. Input/resize/detach resolve exact current attachment id/token/object. The Swift close path intentionally closes the logical persistent session and gates known lifecycle generations before issuing the generation-blind daemon close.

### Local bridge / transport replacement

The proxy broker carries lifecycle/attachment/transport ownership tokens through tunnel replacement and claims exact owners during cleanup.

### Terminal public API candidate

Stable-terminal-id public effects still deserve separate execution work because public resource-v2 intentionally hides incarnation. This scout did not establish a legal production transition that preserves one public terminal id while crossing the native host-incarnation fences, so it remains a candidate rather than a confirmed failure.

## Evidence labels

- exact current upstream: GitHub read;
- resume and identity contracts: source read;
- upstream related-work review: PR/source read;
- original stale-A seam: source-determined;
- old decision-rule probe: model-executed, retained as historical discriminator;
- final repair: fork-authored;
- current fork ancestry/diff: GitHub compare;
- previous target-native carrier: setup-executed / red-step failure / green skipped;
- current target-native carrier: running;
- upstream contact: absent.

## Recommendation

Keep owned PR #17 draft until run `33561165354` reaches a terminal result. If green passes, the candidate has the desired source and target-native evidence for the full fence. If the run fails, classify the exact failing step and repair the owned candidate or verifier without posting anything upstream.
