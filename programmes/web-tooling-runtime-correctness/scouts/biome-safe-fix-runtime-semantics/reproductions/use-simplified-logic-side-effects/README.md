# `useSimplifiedLogicExpression` side-effect reproduction

Biome 2.5.6 classifies `complexity/useSimplifiedLogicExpression` as a safe fix.

Run:

```sh
bash reproduce.sh
```

The fixture covers two right-hand absorbing literals:

```js
effect(false) || true;
effect(true) && false;
```

Both original expressions evaluate `effect(...)` before producing their final boolean result. Replacing them with `true` and `false` preserves only the result and deletes the calls.

Expected semantic difference:

```text
before: calls = 2
 after: calls = 0
```

Real left-hand expressions can perform writes, validation, telemetry, queue consumption, locking, cleanup, or throw exceptions. The safe rewrite must not remove those evaluations.

No upstream interaction is authorized by this reproduction.
