# Oxc parity matrix — `unicorn/no-impossible-length-comparison`

Reference: `sindresorhus/eslint-plugin-unicorn@v72.0.0`.

This matrix separates required parity from Oxc-specific structural probes. Each row must become a native `Tester` case or a documented exclusion before the finding can move beyond research.

## Must report

| Case | Expected proof |
| --- | --- |
| `array.length < 0` | always `false` |
| `array.length <= -1` | always `false` |
| `array.length === -1` | always `false` |
| `array.length == -1` | always `false` |
| `array.length !== -1` | always `true` |
| `array.length != -1` | always `true` |
| `array.length > -1` | always `true` |
| `array.length >= 0` | always `true` |
| `(array.length) >= 0` | always `true` |
| `array.length < -Number.EPSILON` | always `false` |
| `array.length > -Number.EPSILON` | always `true` |
| `0 > array.length` | always `false` |
| `0 <= array.length` | always `true` |
| `-1 >= array.length` | always `false` |
| `-1 !== array.length` | always `true` |
| `string.length === -1` | always `false` |
| `set.size <= -1` | always `false` |
| `set.size >= 0` | always `true` |
| `-1 === set.size` | always `false` |
| `const negativeOne = -1; array.length === negativeOne` | always `false` |
| `array.length! < 0` | always `false`; TypeScript wrapper unwrapped |
| `(array.length as number) < 0` | always `false`; TypeScript wrapper unwrapped |
| `<number>array.length < 0` | always `false`; TypeScript wrapper unwrapped |
| `(array.length satisfies number) === -1` | always `false`; TypeScript wrapper unwrapped |
| `array.length >= 0 && isArray(array)` | report cardinality comparison |
| `dimensions.width && (dimensions.length < 0 || fallback)` | report; shape guard is not in same flattened `&&` chain |

## Must not report

| Case | Reason |
| --- | --- |
| `array.length === 0` | possible |
| `array.length <= 0` | possible at zero |
| `array.length > 0` | possible |
| `array.length >= 1` | possible |
| `array.length < minimumLength` | dynamic bound |
| `array.length < Number.POSITIVE_INFINITY` | not an impossible finite bound |
| `array?.length >= 0` | optional subject |
| `(array?.items).length >= 0` | optional receiver chain |
| `(array?.items).metadata.length >= 0` | optional receiver chain at depth |
| `array["length"] < 0` | computed property excluded |
| `this.length < 0` | custom class receiver |
| `this.size < 0` | custom class receiver |
| `super.length < 0` | custom class receiver |
| `super.size < 0` | custom class receiver |
| `(this as Foo).length < 0` | wrapped custom receiver |
| `(<Foo>this).size === -1` | wrapped custom receiver |
| `(array?.length as number) >= 0` | wrapped optional subject |
| `(array?.items as Items).length >= 0` | wrapped optional receiver |
| `const value = {length: -1}; value.length < 0` | statically custom negative property |
| `const value = {size: "small"}; value.size < 0` | statically nonnumeric property |
| `const value = {length: NaN}; value.length < 0` | statically non-cardinality value |
| `const value = {length: Infinity}; value.length < 0` | statically non-cardinality value |
| `dimensions.width && dimensions.length < 0` | same-object shape guard |
| `(dimensions.width && dimensions.length < 0) || fallback` | same-object shape guard remains in flattened `&&` root |
| `dimensions.height && dimensions.size === -1` | same-object shape guard |
| `dimensions.depth && -1 < dimensions.length` | same-object shape guard with reversed operands |
| `array.length !== 0` | possible |

## Additional Oxc structural probes

### Optional and wrapper handling

- `foo?.bar.length < 0`
- `(foo?.bar).length < 0`
- `(foo?.bar as Bar).length < 0`
- `foo.bar?.length < 0`
- `(foo.bar.length as const) < 0`
- `foo.bar.length! >= 0`

Expected: suppress every case whose receiver or member access is optional; report non-optional TypeScript wrappers.

### Comparison-value safety

- `array.length < (sideEffect(), 0)`
- `array.length < +0`
- `array.length < -0`
- `array.length < (1 - 1)`
- `array.length < NaN`
- `array.length < Infinity`
- `array.length < -Infinity`
- `array.length < 0n`
- `array.length < "0"`

Expected: only side-effect-free finite numeric results participate. BigInt and strings must not be coerced into rule proofs unless the reference implementation does so for the exact AST.

### Receiver identity for shape guards

- `dimensions.width && dimensions.length < 0` — suppress
- `other.width && dimensions.length < 0` — report
- `dimensions["width"] && dimensions.length < 0` — report; reference requires static non-computed guard
- `dimensions.width && dimensions["length"] < 0` — suppress by computed subject exclusion before guard logic
- `dimensions.meta.width && dimensions.meta.length < 0` — suppress when structural receiver identity matches
- `getDimensions().width && getDimensions().length < 0` — confirm reference identity behavior; do not assume repeated calls are the same reference

### Property/value exclusions

- `({length: -1}).length < 0`
- `({length: 1.5}).length < 0`
- `({length: Number.MAX_SAFE_INTEGER + 1}).length < 0`
- `({length: 0}).length < 0`
- `({size: -1}).size >= 0`

Expected: known negative, fractional, non-finite, or unsafe-integer member values prove a custom property and suppress. Known non-negative safe integers retain cardinality semantics.

### Operator fence

Do not report arithmetic, bitwise, membership, or instance relations involving `.length`/`.size`. The visitor should early-return unless the binary operator is one of:

```text
< <= > >= === !== == !=
```

## Diagnostics

For every failing case verify:

- one diagnostic only;
- span covers the complete binary expression;
- message names `.length` or `.size`;
- message states the exact constant result (`true` or `false`);
- no fix or suggestion is offered.

## Execution receipt template

```text
Target base:
Source head:
Generated-file fence:
Focused command:
Focused result:
Format command/result:
Lintgen command/result:
Lint timings command/result:
Full test command/result:
Ready command/result:
Reviewer:
Review result:
```
