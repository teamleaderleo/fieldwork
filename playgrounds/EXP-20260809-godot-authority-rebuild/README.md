# EXP-20260809-godot-authority-rebuild

## In simple words

This experiment treats Godot's scene tree as a replaceable presentation of canonical application state. A tiny fixed action sequence updates application-owned objects with stable IDs. Godot rebuilds the entire presentation subtree during the run. Each fixed tick emits a canonical SHA-256 receipt after node physics processing through a deferred callback.

The same canonical receipts should be produced by the Python reference model, a headless Godot run, and a rendered Godot run. Presentation-node identity, frame cadence, and the rebuild itself are excluded from the canonical hash.

State: target-test-prepared. The Python reference is model-executed; Godot target execution remains open.

## Question

Can a Godot SceneTree be destroyed/rebuilt as presentation state while an external-style canonical state/action protocol produces the same fixed-tick receipts?

## Files

- `reference.py` — zero-dependency canonical-state model.
- `godot/project.godot` — minimal Godot project.
- `godot/main.tscn` — project entry scene.
- `godot/main.gd` — fixed-tick adapter and presentation rebuild.
- `results/reference.txt` — expected canonical receipts from the model.

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

Compare only lines beginning with `AUTH_RECEIPT`. The four tick/hash pairs should match `results/reference.txt` in both Godot modes. The third receipt is emitted after the presentation subtree has been synchronously destroyed and rebuilt.

## Claim boundary

A passing run would establish one small integration contract: application-owned deterministic state can survive complete presentation-tree replacement under the declared fixture. It would not establish deterministic Godot physics, cross-platform renderer equivalence, browser lifecycle behavior, or a general replay guarantee.

Automated upstream contact: prohibited.
