# EXP-20260809-godot-authority-rebuild

## In simple words

This experiment treats Godot's scene tree as a replaceable presentation of canonical application state. A tiny fixed action sequence updates application-owned objects with stable IDs. Godot rebuilds the presentation subtree during the first run, snapshots canonical state at tick 2, then restores that snapshot and replays ticks 3–4 after another complete presentation rebuild.

Each fixed tick emits a canonical SHA-256 receipt through a deferred callback after SceneTree has processed and joined a deliberately sub-threaded physics node. The replay receipts for ticks 3 and 4 must be byte-identical to the original receipts even though presentation-node identity and physical frame count differ.

The same canonical receipts should be produced by the Python reference model, a headless Godot run, and a rendered Godot run. Presentation-node identity, frame cadence, rebuild generation, and the sub-thread sentinel count are excluded from the canonical hash.

State: target-test-prepared. The Python reference is model-executed, including the snapshot/replay phase; Godot target execution remains open.

## Question

Can a Godot SceneTree act as replaceable presentation state while an external-style canonical state/action protocol survives presentation rebuild and snapshot/replay with identical fixed-tick receipts?

## Files

- `reference.py` — zero-dependency canonical-state + snapshot/replay model.
- `godot/project.godot` — minimal Godot project.
- `godot/main.tscn` — project entry scene.
- `godot/main.gd` — fixed-tick adapter, presentation rebuild, snapshot restore, replay receipt comparison, and sub-thread join sentinel.
- `godot/thread_probe.gd` — deliberately sub-threaded physics node used only to verify receipt ordering.
- `results/reference.txt` — expected original and replay canonical receipts from the model.

## Commands

Reference model:

```sh
python3 playgrounds/EXP-20260809-godot-authority-rebuild/reference.py
```

Godot headless, from the experiment directory:

```sh
godot --headless --path godot
```

Rendered control:

```sh
godot --path godot
```

## Expected trace

The original run produces ticks 1–4. At tick 2 it records `AUTH_SNAPSHOT`. The original tick-3 path synchronously destroys and rebuilds the presentation subtree. After original tick 4, the adapter restores the tick-2 canonical snapshot, destroys/rebuilds presentation again, and replays actions 3 and 4.

The important comparisons are:

```text
original tick 3 hash == replay tick 3 hash
original tick 4 hash == replay tick 4 hash
AUTH_REPLAY_RESULT matched=2 expected=2
```

The known canonical hashes remain:

```text
tick 1  9951d38a40ac3b6fa83c957187d45a071041d8a4d542e633deff8a31ffae06ab
tick 2  8c94b59a1d901607e320eb86c781c0817021293375cc2bb8faab9064ce967943
tick 3  7114ca26cd8ee5c248efe3134ac86e340344b62ef48945ee5970bd3552441b05
tick 4  96be96804eeda51642fc6645fd203bae1be38689fef2eebe57e2cf5e5ecb8eb8
```

Every Godot receipt also records:

- `projection_ok` — current presentation exactly projects canonical state;
- `thread_probe_count` and `expected_thread_probe_count` — the deferred receipt observed the next sub-thread physics step, proving SceneTree joined that process group before the global deferred-message receipt ran;
- `replay_hash_ok` — replay receipt matches its original canonical receipt.

## Claim boundary

A passing run would establish one bounded integration contract: application-owned deterministic state can survive complete presentation replacement and in-process canonical snapshot/replay under the declared fixture, while the receipt is taken after a sub-threaded physics group has completed.

It would **not** establish deterministic Godot physics, process-restart persistence, cross-platform renderer equivalence, browser lifecycle behavior, or a general rollback/replay guarantee. A later experiment should serialize the snapshot across an actual process restart before making a process-boundary claim.

Automated upstream contact: prohibited.
