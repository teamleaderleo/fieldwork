# `useFlatMap` Array species reproduction

This fixture checks whether Biome 2.5.6's recommended safe `complexity/useFlatMap` fix preserves built-in Array subclass construction semantics.

The source uses only native `Array`, subclassing, and `Symbol.species`:

- `SourceArray#map()` constructs `IntermediateArray`;
- calling `.flat()` on that result constructs `FinalArray`;
- `SourceArray#flatMap()` constructs only `IntermediateArray`.

Therefore replacing `source.map(callback).flat()` with `source.flatMap(callback)` changes the result constructor and the number/order of species getter evaluations while preserving the flattened values.

Run:

```bash
bash reproduce.sh
```

The script executes the original source, applies released `@biomejs/biome@2.5.6` with only `complexity/useFlatMap`, executes the rewritten source, and requires the runtime JSON to differ.

This is an exploration fixture. A runtime difference alone does not decide whether the behavior is a novel Biome defect, an accepted source-rule tradeoff, or too rare to promote.
