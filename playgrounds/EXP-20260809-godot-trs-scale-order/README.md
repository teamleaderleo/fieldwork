## In simple words

Godot currently has two relevant matrix operations for scale: ordinary `Basis::scaled()` applies scale from the left (`S * R` for a rotation basis), while local scale applies from the right (`R * S`). With rotation plus non-uniform scale, those matrices differ substantially.

This experiment models that mathematical distinction and now includes negative controls plus negative-scale cases. It supports the first Godot scout probe but does not claim that a Godot binary was built or that the target-native regression test has run.

## Question

Across ordinary, uniform, identity-rotation, and negative-scale fixtures, when do left-applied and local right-applied scale diverge?

## Command

```sh
python3 playgrounds/EXP-20260809-godot-trs-scale-order/run.py
```

## Result

All fixtures use rotation axis `(1, 2, 3)`.

| case | angle | scale | max element diff | Frobenius diff |
|---|---:|---|---:|---:|
| nonuniform positive | `0.7` | `(2, 1, 3)` | `0.5501172307043584` | `1.0471335212271937` |
| uniform positive | `0.7` | `(2, 2, 2)` | `0` | `0` |
| identity rotation | `0` | `(2, 1, 3)` | `0` | `0` |
| nonuniform negative X | `0.7` | `(-2, 1, 3)` | `1.9736989908689988` | `3.3461655250801945` |
| mixed negative | `0.7` | `(-2, -1, 3)` | `1.9736989908689988` | `2.8045054921730266` |
| uniform negative | `0.7` | `(-2, -2, -2)` | `0` | `0` |

The controls behave exactly as the matrix-order hypothesis predicts: uniform scaling commutes with rotation, and any scaling commutes with identity rotation. Rotated non-uniform scaling distinguishes the two operations, with negative non-uniform cases widening the difference.

## Candidate construction

Godot already exposes `Basis(const Quaternion &, const Vector3 &)` backed by `set_quaternion_scale()`. `Basis::get_scale()` and related rotation extraction explicitly document their decomposition assumption as `M = R.S`.

If the target-native baseline test fails as predicted, the clearest one-line candidate in `AnimationMixer::_blend_apply()` is therefore:

```cpp
Transform3D transform(Basis(t->rot, t->scale), t->loc);
```

This expresses the semantic operation directly instead of reconstructing it through a generic scale modifier. Keep it candidate-only until the baseline failure and control matrix execute on Godot.

## Evidence boundary

- **Documented:** `Basis::scale()` left-multiplies by scale; `scale_local()` right-multiplies.
- **Documented:** Godot's rotation/scale decomposition assumes `M = R.S`; the Quaternion+scale constructor is available for this exact composition.
- **Observed:** `Node3D` retains rotation and scale separately and rebuilds a dirty local transform through the same local rotation/scale convention.
- **Model-executed:** positive, negative, uniform, and identity-rotation matrix controls behave as predicted.
- **Target-test-prepared:** `teamleaderleo/godot` PR #1 carries a Godot-native `AnimationPlayer` regression probe.
- **Unknown:** target-native test outcome, because the new fork has not produced a PR workflow run yet.

## Disposition

Retain at highest concrete priority. Current upstream issue #121158 independently identifies the same regression and source line; current overlap search found no matching repair PR.
