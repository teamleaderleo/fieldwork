## In simple words

Godot currently has two relevant matrix operations for scale: ordinary `Basis::scaled()` applies scale from the left (`S * R` for a rotation basis), while local scale applies from the right (`R * S`). With rotation plus non-uniform scale, those matrices differ substantially.

This experiment models only that mathematical distinction. It supports the first Godot scout probe but does not claim that a Godot binary was built or that the target-native regression test has run.

## Question

For the same rotation and non-uniform scale used by the prepared `AnimationPlayer` test, do left-applied and local right-applied scale produce the same basis?

## Command

```sh
python3 playgrounds/EXP-20260809-godot-trs-scale-order/run.py
```

## Result

For axis `(1, 2, 3)`, angle `0.7`, and scale `(2, 1, 3)`:

- maximum absolute matrix-element difference: `0.5501172307043584`
- Frobenius difference: `1.0471335212271937`

The two operations are clearly distinguishable for this fixture.

## Evidence boundary

- **Documented:** `Basis::scale()` left-multiplies by scale; `scale_local()` right-multiplies.
- **Observed:** `Node3D` retains rotation and scale separately and rebuilds a dirty local transform through `set_euler_scale()`.
- **Model-executed:** the pure Python matrix model distinguishes the two operations.
- **Target-test-prepared:** `teamleaderleo/godot` PR #1 carries a Godot-native `AnimationPlayer` regression probe.
- **Unknown:** target-native test outcome, because the new fork has not produced a PR workflow run yet.

## Disposition

Retain. The mechanism distinction is strong enough to justify target-native execution and continued source analysis around `AnimationMixer::_blend_apply()`.
