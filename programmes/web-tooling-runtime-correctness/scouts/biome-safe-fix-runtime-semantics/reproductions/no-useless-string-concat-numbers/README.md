# `noUselessStringConcat` numeric-formatting reproduction

Biome 2.5.6 classifies `complexity/noUselessStringConcat` as a safe fix and extends the source ESLint rule by folding string-plus-number expressions.

Run:

```sh
bash reproduce.sh
```

The fixture uses numeric values whose JavaScript string representation uses exponent notation:

```js
"large:" + 1e21;
"small:" + 1e-7;
```

JavaScript evaluates those as:

```text
large:1e+21
small:1e-7
```

Biome parses the number as a host floating-point value and formats it with Rust's `to_string()` before building the replacement string literal. The released fix produces:

```text
large:1000000000000000000000
small:0.0000001
```

The numeric values are equal, but the resulting strings are not. That matters for serialized fields, URLs, cache keys, signatures, filenames, snapshots, protocol values, and any code comparing the exact string representation.

No upstream interaction is authorized by this reproduction.
