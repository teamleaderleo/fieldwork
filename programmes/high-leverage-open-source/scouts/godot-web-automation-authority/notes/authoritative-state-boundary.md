# Godot external-authority and replay boundary

## In simple words

Godot's SceneTree gives a usable boundary for an application whose canonical state lives outside scene-node identity. `physics_frame` is emitted before node physics processing. Physics callbacks then run in priority/tree order, deferred calls are flushed afterward, timers/tweens run, transforms flush again, and queued deletion is near the end of the tick.

That supports a client adapter where an external core supplies a validated action batch at the beginning of a fixed tick and Godot consumes it for presentation. The authoritative receipt should name its own tick/action sequence and state hash; frame count, transient node IDs, physics internals, and renderer state stay outside canonical identity.

State: source-read; integration fixture still required.

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
flush unique deferred group calls
flush MessageQueue
process physics timers
process physics tweens
flush transforms
flush queued deletions
run idle callbacks
```

`physics_frame` therefore provides a pre-node-processing hook for a validated external action batch.

Node process ordering has explicit physics/process priority fields plus tree-order tie-breaking. The public Node documentation describes lower process-priority values as running earlier.

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

### Tick end receipt

A dedicated late physics processor can queue a deferred receipt after its own `_physics_process`. This places the receipt after ordinary node physics processing and earlier queued deferred calls. The receipt should hash only application-owned canonical state.

Because physics timers/tweens and the deletion queue run after the first MessageQueue flush, include them in canonical state only when the application explicitly models those semantics. A stricter design keeps authoritative timing/tween state outside Godot and treats Godot timers/tweens as presentation helpers.

### Restart/rebuild

Given one canonical snapshot plus content identities, rebuild Godot nodes/resources from scratch and compare the next action/result receipt. This is the important test: the scene is a replaceable projection, not the database.

## Failure classes to probe

1. **Ordering drift** — same action sequence produces different application hash because a presentation callback feeds back into canonical state at a different point in the frame.
2. **Deferred side effects** — a `call_deferred()` changes domain state after the receipt was taken.
3. **Scene replacement** — pending scene change swaps presentation nodes while an action references stale node identity.
4. **Focus/pause** — browser or OS lifecycle interrupts presentation cadence while canonical tick/sequence continuity remains explicit.
5. **Resource reimport** — presentation content changes path/version while canonical content identity remains stable or produces a deliberate generation change.
6. **Physics divergence** — engine physics result is useful for visuals but must be treated as an observation unless the application deliberately makes Godot physics authoritative.

## First integration fixture

A generated project can stay tiny:

- external state: `{tick, objects[{id, x, y, state}], rng_seed}`;
- action log: deterministic move/toggle actions;
- Godot adapter creates/updates presentation nodes keyed by application IDs;
- fixed-tick receipt records input action IDs plus canonical hash;
- rendering may be enabled or headless without changing the hash;
- destroy/rebuild the entire presentation tree halfway through and continue from the same snapshot;
- run with pause/focus gaps and compare receipts;
- on web, repeat across orderly quit/relaunch.

## Current conclusion

Godot's main-loop ordering is compatible with an externally authoritative client as long as the adapter owns its tick protocol explicitly. Godot gives useful deterministic hook points, while scene-node identity, deferred presentation work, idle-frame cadence, timers/tweens, renderer resources, and default physics state should be treated as replaceable runtime state unless a narrower contract proves otherwise.

## Evidence boundary

Supported: source-level ordering and API hook placement.

Unknown: cross-platform receipt equivalence, physics determinism, browser event ordering, and ergonomic cost in an owned project. Those require execution.

Automated upstream contact: prohibited.
