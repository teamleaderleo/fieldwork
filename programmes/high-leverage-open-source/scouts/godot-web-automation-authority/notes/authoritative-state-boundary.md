# Godot external-authority and replay boundary

## In simple words

Godot's SceneTree gives a usable boundary for an application whose canonical state lives outside scene-node identity. `physics_frame` is emitted before node physics processing. Physics process groups then run, including sub-thread groups; Godot explicitly waits for those worker groups to complete before the processing pass returns. The global deferred-message queue is flushed afterward, then timers/tweens run, transforms flush again, and queued deletion is near the end of the tick.

That supports a client adapter where an external core supplies a validated action batch at the beginning of a fixed tick and Godot consumes it for presentation. The authoritative receipt should name its own tick/action sequence and state hash; frame count, transient node IDs, physics internals, and renderer state stay outside canonical identity.

State: source-read + reference-model-executed + Godot integration fixture prepared.

## Exact source

Development revision: `godotengine/godot@4173760fdf6c2c722e82e08cb58e55f34c9efd80`.
Retrieved: 2026-08-09.

Key paths:

- `scene/main/scene_tree.cpp`
- `scene/main/node.h`
- `core/object/message_queue.*`

## Physics tick ordering

At the pinned revision, `SceneTree::physics_process()` performs this relevant sequence:

```text
increment current_frame
flush transform notifications
MainLoop::physics_process
emit physics_frame
process picking
run SceneTree node physics processing
  - process groups by order
  - submit sub-thread groups to WorkerThreadPool
  - wait for each submitted group batch to complete
flush unique deferred group calls
flush global MessageQueue
process physics timers
process physics tweens
flush transforms
flush queued deletions
run idle callbacks
```

`physics_frame` therefore provides a pre-node-processing hook for a validated external action batch. The explicit worker-group join means the post-processing MessageQueue flush occurs after ordinary and sub-thread node physics callbacks have completed for that pass.

Node process ordering has explicit physics/process priority fields plus tree-order tie-breaking. Sub-thread process groups are sorted by process-thread-group order; threaded batches at one ordering boundary are joined before SceneTree proceeds.

## Deferred-call nuance

A receipt queued with `call_deferred()` from the `physics_frame` hook will execute at the global MessageQueue flush after node processing completes. Because it entered the queue before deferred calls created later by node physics callbacks, it may execute before those later deferred side effects.

That is useful if the receipt contract intentionally ends at **completed physics callbacks**. It is insufficient if canonical state can be changed by node-owned deferred calls. The safest adapter therefore keeps canonical mutation synchronous in the authority callback/core and treats node-deferred work as presentation work. A stricter experiment can add a second sentinel deferred from node processing to make this ordering visible.

## Idle-frame ordering differs

`SceneTree::process()` polls multiplayer before `process_frame`, emits `process_frame`, flushes the MessageQueue, runs node idle processing, flushes unique group calls and the MessageQueue again, handles pending scene changes, timers/tweens, transforms, queued deletion, accessibility updates, and idle callbacks.

For deterministic domain state, physics ticks are the cleaner authority boundary. Idle frames are useful for rendering/input presentation and asynchronous UI work.

## Proposed adapter contract

### Inputs

Each external action batch carries:

- application-owned tick or sequence number;
- validated action IDs and payloads;
- source-state hash or generation;
- explicit content/resource identity where needed.

### Tick start

At `physics_frame`, verify the expected generation and apply the batch to a dedicated adapter object. Convert external state into Godot presentation state. Avoid deriving canonical IDs from `Node` instance IDs, scene-generated names, or physics body IDs.

### Tick-end receipt

Queue a receipt from the `physics_frame` authority hook. At the current SceneTree ordering, that receipt runs only after all node physics process groups—including joined sub-thread groups—have completed. Hash only application-owned canonical state.

Keep canonical mutation out of node-owned `call_deferred()` work if this receipt is the boundary. Physics timers/tweens and the deletion queue also run later, so include them in canonical state only when the application explicitly models those semantics. A cleaner design keeps authoritative timing/tween state outside Godot and treats Godot timers/tweens as presentation helpers.

### Restart/rebuild

Given one canonical snapshot plus content identities, rebuild Godot nodes/resources from scratch and compare the next action/result receipt. This is the important test: the scene is a replaceable projection, not the database.

## Active integration fixture

`playgrounds/EXP-20260809-godot-authority-rebuild/` now contains:

- a Python reference model with four retained canonical SHA-256 receipts;
- a minimal Godot project applying the same four actions;
- full presentation-subtree destruction/rebuild on tick 3;
- a `PROCESS_THREAD_GROUP_SUB_THREAD` sentinel node whose physics counter must equal the canonical tick when each deferred receipt runs;
- headless and rendered execution controls.

The sub-thread sentinel stays outside the canonical hash. It tests only whether the chosen receipt boundary observes worker-group completion.

Expected reference hashes:

```text
tick 1  9951d38a40ac3b6fa83c957187d45a071041d8a4d542e633deff8a31ffae06ab
tick 2  8c94b59a1d901607e320eb86c781c0817021293375cc2bb8faab9064ce967943
tick 3  7114ca26cd8ee5c248efe3134ac86e340344b62ef48945ee5970bd3552441b05
tick 4  96be96804eeda51642fc6645fd203bae1be38689fef2eebe57e2cf5e5ecb8eb8
```

Target execution remains open.

## Failure classes to probe

1. **Ordering drift** — same action sequence produces different application hash because presentation feedback enters canonical state at a different point in the tick.
2. **Deferred side effects** — a node-owned `call_deferred()` changes domain state after the chosen receipt boundary.
3. **Process-group feedback** — sub-thread presentation processing feeds data into canonical state despite the worker join being complete.
4. **Scene replacement** — pending scene change swaps presentation nodes while an action references stale node identity.
5. **Focus/pause** — browser or OS lifecycle interrupts presentation cadence while canonical tick/sequence continuity remains explicit.
6. **Resource reimport** — presentation content changes path/version while canonical content identity remains stable or produces a deliberate generation change.
7. **Physics divergence** — engine physics result is useful for visuals but should be treated as an observation unless the application deliberately makes Godot physics authoritative.

## Current conclusion

Godot's main-loop ordering is compatible with an externally authoritative client as long as the adapter owns its tick protocol explicitly. The explicit wait for sub-thread process groups is particularly useful: presentation work can fan out across Godot's process groups while a main-thread deferred receipt still observes completion of the physics callbacks.

The cleanest canonical boundary excludes node-deferred mutations, SceneTree timers/tweens, queued deletion timing, transient node identity, and renderer state. Those remain replaceable runtime behavior unless a narrower contract proves otherwise.

## Evidence boundary

Supported: source-level ordering, explicit sub-thread group join, API hook placement, and model-executed reference receipts.

Prepared: presentation-rebuild and sub-thread-completion Godot fixture.

Unknown: target Godot receipt equivalence, cross-platform behavior, browser event ordering, physics determinism, and ergonomic cost in an owned project. Those require execution.

Automated upstream contact: prohibited.
