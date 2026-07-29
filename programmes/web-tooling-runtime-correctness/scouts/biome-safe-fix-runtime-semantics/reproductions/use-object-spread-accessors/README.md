# `useObjectSpread` accessor-semantics reproduction

Biome 2.5.6 classifies `style/useObjectSpread` as a safe fix. The rule converts `Object.assign()` calls whose first argument is an object literal into a flattened object literal.

Run:

```sh
bash reproduce.sh
```

The fixture covers two ordinary accessor cases:

1. A setter on the target object literal. `Object.assign` invokes it when assigning the later source property. Flattening the literals overwrites it with a data property without invoking it.
2. A getter on a source object literal. `Object.assign` reads it and creates a data property. Flattening retains the getter as an accessor.

Expected released-binary result:

```text
before: target setter called, source getter eagerly read
after: target setter not called, source getter retained and read later
```

This is not a claim that object spread and `Object.assign` are always interchangeable. It tests whether Biome's automatic safe fix applies the guard needed for the cases where they are not.

No upstream interaction is authorized by this reproduction.
