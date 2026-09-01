# cmux cross-generation identity scout

Date: 2026-09-01  
Programme: high-leverage-open-source  
Target: `manaflow-ai/cmux`  
Owned fork: `teamleaderleo/cmux`  
Upstream contact authorized: `false`

## Current result

The confirmed seam is Computer Use hook completion across an agent-process replacement. A native agent session id can survive resume while the OS process generation changes. A delayed completion from retired process A must never complete successor B merely because both use the same surface and logical session id.

Owned fork candidate:

- tested upstream/base: `544c0e0ff4f3aebb1a34eb8503c7ccc1f33a2de8`;
- regression-only RED: `5fa3df624315dad2e7bc3a31a1df572fe9cafe41`;
- full repair: `e43904d1db44a8b5fe752dcda3e1ade05325ddfb`;
- owned draft PR: `teamleaderleo/cmux#17`;
- exact ancestry: base -> RED -> repair.

Latest upstream checked after the test base advanced once to `2422b69c7c3555bd1efc5b37ffb32a7c619dc282`. That commit is TUI-only and does not touch any candidate file, so the running proof remains pinned to its immutable base.

Third-party upstream remains read-only: no automated upstream issue, comment, review, pull request, reaction, or maintainer contact has been made.

## Identity map

| Layer | Durable identity | Physical-generation identity | Result in inspected paths |
| --- | --- | --- | --- |
| machine / cloud VM | logical machine/base | active/current VM generation | fenced in inspected paths |
| daemon | durable registry/resource state | live daemon generation | fenced in inspected recovery paths |
| workspace | workspace/resource id | live surface/runtime owner | no violating sequence established |
| terminal | `terminal_id` | `terminal_incarnation` | explicitly fenced |
| PTY | persistent `sessionID` | exact `wsPTYSession` object/process | exact-object cleanup/input fences |
| attachment | attachment id | token + exact attachment object | fenced |
| local bridge | logical lifecycle id | bridge/transport owner generation | fenced |
| agent session | native CLI session id reused by resume | `AgentPIDProcessIdentity(pid,startSeconds,startMicroseconds)` | failing seam confirmed in Computer Use |

## Persistence boundary

A valid agent lifetime transition is:

```text
logical session L / process A
A exits
resume L
logical session L / process B
```

Therefore `L` is a logical identity, not proof of the current process generation. CMUX already represents one process lifetime with `AgentPIDProcessIdentity`, which combines PID with kernel process start seconds and microseconds.

## Original failure

On upstream, `ComputerUseLiveSessionProjection.driverSessionID(...)` resolves the current surface and then accepts immediately when the current record's logical agent session id equals the hook session id. The physical process check is only the fallback for differing agent ids.

A source-determined failure sequence is:

1. stable surface `S`, stable Computer Use driver `D`, logical agent session `L`;
2. process A invokes Computer Use;
3. A emits a delayed `Stop` or `SessionEnd` carrying `S`, `L`, and `pidA`;
4. A exits;
5. CMUX resumes `L` in process B;
6. B becomes the current live owner for `D`;
7. delayed A completion arrives;
8. logical-session equality resolves stale A to current `D` before A's physical generation is considered.

`ComputerUseUXCoordinator` then records completion for stable driver `D`, resolves the current proxy for `D`, retires current presentation/menu activity, cancels current cursor/focus/reassert work, and removes the accepted invocation record. The concrete consequence is stale A changing successor B's Computer Use presentation state.

No claim is made that this path kills B, rewrites authenticated Computer Use disk state, or crosses an authentication boundary.

## Why the first PID-only patch was incomplete

The earlier fork draft made a supplied PID authoritative in the live resolver. That closed the obvious dead-A-PID case but left two holes:

1. `ComputerUseUXCoordinator` also has a live-index refresh-gap completion fallback keyed by surface + logical session + time. Resume can preserve the same logical session id.
2. Reconstructing `AgentPIDProcessIdentity(pid:)` when the async consumer finally handles an event is too late. A recycled numeric PID can identify a later process generation.

The current candidate freezes the generation earlier and uses the same token in both admission paths.

## Repair

### Trusted internal ingress envelope

`Sources/Feed/WorkstreamEvent+FeedIngress.swift` defines `FeedIngressProcessGenerationEvent`, an app-internal Swift envelope. When a Feed event has `_ppid`, it snapshots `AgentPIDProcessIdentity` from the kernel at Feed ingress and carries that exact identity beside the event. If the PID is already gone, the envelope still exists with a nil identity so process-bound Computer Use handling fails closed instead of falling back to the logical session id.

The envelope is not part of the hook JSON schema, so an external hook payload cannot select the process generation later trusted by Computer Use.

`Sources/TerminalController+FeedAcknowledgment.swift` captures the envelope before accepted Feed delivery becomes asynchronous. When Feed re-homes or otherwise authoritatively rewrites the event, `replacingEvent(...)` keeps the original captured process identity. Both single-event and acknowledged/batch Feed paths publish the trusted envelope after acceptance.

The existing raw `.workstreamEventReceived` post still exists for compatibility. `ComputerUseUXCoordinator` ignores raw `WorkstreamEvent` notifications whenever `_ppid` is present and consumes only the trusted envelope for process-bound Computer Use events. Generationless events keep the old raw path.

### Live resolver fence

`ComputerUseLiveSessionProjection.driverSessionID(...)` now receives both `_ppid` and the captured `AgentPIDProcessIdentity`.

When `_ppid` exists, production code requires:

- a captured process identity;
- captured identity PID equals `_ppid`;
- the exact captured `(pid,startSeconds,startMicroseconds)` belongs to the current live root process tree.

The production resolver never re-resolves a numeric PID at consumption time. A DEBUG-only overload retains the old convenience API for existing tests; release callers cannot use that PID-only overload.

When no PID exists, the existing logical-session compatibility path remains available.

### Completion refresh-gap fence

`ComputerUseUXCoordinator` now records `ComputerUseAcceptedInvocationIdentity`, containing surface, logical agent session, exact process identity, and acceptance time.

A completion using the projection-gap fallback must match the same surface, logical session, ordering, PID, and exact process birth identity. A same-PID/different-start-time completion is rejected.

Computer Use onboarding/helper reconciliation is also moved behind successful generation resolution, so a rejected stale invocation has no Computer Use onboarding side effect.

## Exact fork diff

GitHub compare from tested base `544c0e0f` to repair `e43904d1` contains exactly five files and two linear commits:

```text
Sources/App/ComputerUseLiveSessionProjection.swift
Sources/App/ComputerUseUXCoordinator.swift
Sources/Feed/WorkstreamEvent+FeedIngress.swift
Sources/TerminalController+FeedAcknowledgment.swift
cmuxTests/HostSettingsShortcutNotificationTests.swift
```

The RED commit changes only `cmuxTests/HostSettingsShortcutNotificationTests.swift`.

## Regression coverage

`ComputerUseCrossGenerationIdentityTests` first creates retired generation A and live generation B while holding the logical agent session id constant. The RED test expects stale A to be rejected; upstream accepts it through the logical-session shortcut.

The repair adds discriminators for:

- current B exact process generation -> accepted;
- current B with a different hook-protocol session alias -> accepted by process authority;
- retired A with the same logical session -> rejected;
- B numeric PID paired with a stale/different process-start token -> rejected;
- generationless stable logical session -> compatibility path accepted;
- completion refresh-gap fallback with current accepted generation -> accepted;
- completion refresh-gap fallback with stale start token -> rejected;
- ingress envelope capture of the current live B generation -> exact match.

## Related upstream work reviewed read-only

`manaflow-ai/cmux#9586` remains open and broad. It moves multiple lifecycle paths toward exact process generations and introduces other generation identifiers, but it does not remove the current Computer Use `_ppid`/logical-session seam on upstream `main`.

Other inspected CMUX work around Codex resume, managed-agent liveness, reconnect ownership, and terminal incarnation uses the same general rule: a persistent logical id is separate from one physical generation, and stale work is fenced by an incarnation/owner/process-generation token.

## Target-native verification

Verifier: `.github/workflows/cmux-computer-use-generation.yml` on Fieldwork branch `fieldwork/cmux-cross-generation-identity-20260901`.

Current run: `33567657260`.

The carrier pins the exact base/RED/repair SHAs, verifies linear ancestry and the five-file diff set, selects a supported Xcode with CMUX's `scripts/select-ci-xcode.sh`, prepares the repository build dependencies, then runs:

```text
RED  : cmuxTests/ComputerUseCrossGenerationIdentityTests
FIX  : cmuxTests/ComputerUseCrossGenerationIdentityTests
FIX  : cmuxTests/ComputerUseUXTests
```

The RED step must fail after reaching the stale-generation test rather than at compile/setup. The FIX steps must pass.

Earlier carrier failures are classified as verifier evidence only:

- run `33550591279` failed before testing because the runner remained on Command Line Tools instead of full Xcode;
- run `33561643140` selected Xcode and reached an app build, then hit unrelated current-source compiler failures in `LocalhostBrowserURLPolicy.swift` and `CmuxScriptWorkerPool.swift` under that runner/Xcode combination;
- run `33567439435` failed only because the verifier compared a sorted filename list against a locale-order-dependent literal; GitHub compare independently confirmed the candidate ancestry/diff was correct.

Run `33567657260` uses the corrected order-independent diff fence and had passed checkout, immutable ancestry/diff verification, Xcode selection, Bun, GhosttyKit, and Zig setup at the time of this report update. Evidence class remains `target-test-running` until the RED and FIX steps finish.

## Evidence limit

The current candidate closes the identified in-process stale-generation seam by freezing process birth identity when the Feed frame enters CMUX and carrying that identity through asynchronous handling. The uniform external hook wire still exposes `_ppid` rather than a sender-attested process-start tuple. A theoretical PID recycle before CMUX captures the incoming frame would require a broader hook-wire or peer-identity change across providers; this scout does not claim that broader protocol guarantee.

## Recommendation

Keep owned PR #17 draft until run `33567657260` reaches a terminal result. If it proves RED behavioral failure and FIX green, record that result and preserve the exact SHAs. If it exposes a candidate compile/test defect, repair only the owned fork/Fieldwork and rerun. Keep upstream read-only unless explicit authorization is given later.
