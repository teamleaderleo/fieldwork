# `useArrayLiterals` spread-argument reproduction

Biome 2.5.6 classifies `style/useArrayLiterals` as a safe fix and explicitly targets `Array(...args)`.

Run:

```sh
bash reproduce.sh
```

The fixture sets `args` to `[3]`.

Before the fix, `Array(...args)` is equivalent to `Array(3)`: it creates a sparse array with length three and no own index properties.

After the fix, `[...args]` creates a dense one-element array containing the number `3`.

Expected semantic difference:

```text
before: length 3, no index 0
 after: length 1, index 0 contains 3
```

This represents realistic code that forwards a runtime argument list into the `Array` constructor—for example, a helper that conditionally receives either a requested capacity or a list of initial elements.

No upstream interaction is authorized by this reproduction.
