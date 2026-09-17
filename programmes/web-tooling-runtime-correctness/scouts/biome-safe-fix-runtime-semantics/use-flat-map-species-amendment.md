# `useFlatMap` Array-species amendment

Date: 2026-07-30

Fieldwork lane: #89  
Fieldwork PR: #97  
Released package: `@biomejs/biome@2.5.6`  
Workflow: `30492976711`  
Job: `90715101021`  
Upstream contact authorized: `false`

## In simple words

Biome's recommended `complexity/useFlatMap` rule classifies its rewrite as safe and changes:

```js
source.map(callback).flat()
```

to:

```js
source.flatMap(callback)
```

For ordinary arrays, the flattened values are normally the same. For native Array subclasses that customize `Symbol.species`, the two expressions can construct different result classes and execute a different number of observable species getters.

## Released-package result

The fixture uses only built-in Array subclassing and `Symbol.species`.

Before:

```json
{"constructor":"FinalArray","speciesReads":["SourceArray","IntermediateArray"],"values":[1,2]}
```

After Biome 2.5.6 rewrote the chain to `flatMap()`:

```json
{"constructor":"IntermediateArray","speciesReads":["SourceArray"],"values":[1,2]}
```

The values remain `[1, 2]`, but the result's constructor changes and one species getter no longer executes.

## Mechanism

`map()` performs Array-species construction for the source and returns the selected intermediate subclass. Calling `flat()` on that intermediate result performs a second species construction.

`flatMap()` performs one species construction directly from the source. It does not construct and then flatten the intermediate mapped array.

The rewrite therefore cannot preserve all subclass/species semantics in general.

## Source and ecosystem comparison

Biome's implementation is syntactic. It checks method names and argument counts but does not establish that the receiver is a plain built-in Array whose species behavior is unobservable.

The corresponding `eslint-plugin-unicorn` rule also performs a broad autofix and has receiver heuristics rather than full species analysis. Targeted issue and pull-request searches did not surface an exact Array-species report in Biome or Unicorn.

This ecosystem precedent lowers surprise and may influence desired policy. It does not make the two JavaScript expressions semantically identical.

## Severity and exposure

- The rule is recommended and the fix is classified safe.
- The trigger uses standard language features, but customized Array species is uncommon.
- The result class can matter to downstream methods, branding checks, serialization, allocation policy, or application-specific subclass invariants.
- A species getter may itself be observable or have side effects, although side-effectful species accessors are fragile design.

Characterization: **confirmed semantics change with low expected prevalence, broader default exposure, and no simple syntax-only guard**.

## Correction boundary

Possible dispositions require maintainer policy rather than one obvious narrow patch:

1. classify the rewrite unsafe unless type information proves a plain Array-like receiver;
2. use typed analysis to restrict the safe fix to receivers whose Array/species behavior is known;
3. keep the current behavior but document that the safe classification does not preserve Array subclass/species identity;
4. decline promotion if Biome's safe-fix policy intentionally accepts this ecosystem-standard optimization boundary.

A custom-receiver-only example would be too weak. This retained fixture deliberately uses native Array semantics.

## Current disposition

Retain as a separate, lower-priority candidate for safety-policy review. Do not rank it above the accessor, dynamic-Array-arity, or numeric-string findings, all of which have narrower corrections and more ordinary destructive consequences.

No upstream contact occurred.
