# SWC reopened-namespace resolver review

## In simple words

The active resolver fix for reopened TypeScript namespaces is still carrying live correctness review debt on its current head. Fieldwork should observe and review this work rather than create a competing implementation.

Upstream issue `swc-project/swc#11607` reports that a later declaration of one TypeScript namespace can resolve a reference to an outer binding instead of an exported member from an earlier declaration. Active upstream PR `swc-project/swc#11872` owns the repair.

Current reviewed upstream head: `bcd1935d38c763d7d755680a769abfcb7c421785`.

Evidence in this note is `source-read` plus upstream review-state inspection. No third-party upstream mutation was performed.

## What the current patch is doing

The resolver now maintains merged namespace tables keyed by a parent identity plus namespace name. It separately tracks exported value/type names, namespace declaration ids, erased namespaces, and per-instance binding marks. The intent is to share exported members across re-opened namespace bodies while keeping private names body-local.

That is the right ownership problem to solve, and earlier review rounds already corrected several over-broad variants that leaked non-exported names across bodies.

## Current source-confirmed review seam A: dotted namespace forward seeding

`Resolver::seed_namespace_exports` explicitly says:

```text
Dotted bodies' inner members are not seeded; forward references across sibling re-opens therefore reach one nesting level deep.
```

That limitation aligns with an unresolved current review finding for dotted forms such as:

```ts
namespace A.B {
    export var x = y;
}
namespace A.B {
    export var y = 1;
}
```

The merged table can learn that `B` is an exported namespace of `A`, while the inner exported member `y` is not pre-seeded into `B` before the earlier body resolves `x = y`.

This is a narrow, source-backed gap in the current algorithm. Fieldwork has not run a target-native discriminator for it, so the evidence class remains `source-read`.

## Current source-confirmed review seam B: namespace ids are omitted from forward type seeding

The same function documents that namespace ids are deliberately kept out of the pre-scan type set, and the forward type seed inserts only `scan.types`.

An unresolved review branch asks about the corresponding forward type case:

```ts
namespace N {
    export type T = C.I;
}
namespace N {
    export namespace C {
        export interface I {}
    }
}
```

The current source has a real asymmetry here: `bind_namespace_id` eventually registers namespace declarations in type space when their body is visited, but the earlier sibling body's lookup happens before that registration and the forward seed does not add namespace ids to the merged type table.

Again, this is `source-read` evidence rather than target execution.

## Transform-side dotted-body seam

The TypeScript transform's `enter_current_namespace` intentionally does not push a namespace frame when the recorded member context equals the namespace id's own context, and its comment identifies dotted bodies as that case.

That makes the resolver's dotted-form correctness especially important: cross-body references to classes, functions, or other values cannot rely on the ordinary namespace-frame rewrite in the same way block-form bodies do. Current unresolved review comments include examples where a dotted reopen may leave a bare `C` instead of qualifying it through the namespace object.

This should be treated as a resolver/transform contract, not solely a resolver-local detail.

## Review threads checked

The PR has repaired and resolved several earlier findings around private binding leakage, exported import aliases, nested namespace instance marks, and forward value seeding. It still has unresolved current review branches, including dotted namespace reopens and type-space forward references. Some unresolved comments are outdated against later commits; Fieldwork should distinguish those from current-head findings rather than count raw thread totals.

## Disposition

**REVIEW HOLD / OBSERVE ACTIVE UPSTREAM.**

The current patch is substantial and already actively owned upstream. The highest-value Fieldwork contribution is a small current-head discriminator for the two source-confirmed seams above, after the active mapped-`arguments` execution carrier finishes:

1. dotted value-space forward reference across two `namespace A.B` declarations;
2. type-space forward reference to an exported namespace declared only by a later reopen.

If both pass on the exact current PR head, retire those review concerns as negative results. If either fails, preserve the exact target receipt and continue reviewing the active implementation rather than opening a competing repair.

Automated third-party upstream contact remains prohibited.
