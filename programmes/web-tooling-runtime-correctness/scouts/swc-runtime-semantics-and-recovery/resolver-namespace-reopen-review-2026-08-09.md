# SWC reopened-namespace resolver review

## In simple words

The active resolver fix for reopened TypeScript namespaces has a much broader regression matrix than the first source review suggested, but two narrow forward-reference questions remain distinct from the covered cases.

Upstream issue `swc-project/swc#11607` reports that a later declaration of one TypeScript namespace can resolve a reference to an outer binding instead of an exported member from an earlier declaration. Active upstream PR `swc-project/swc#11872` owns the repair.

Current reviewed upstream head: `bcd1935d38c763d7d755680a769abfcb7c421785`.

Evidence in this note is `source-read`, changed-test review, and upstream review-state inspection. No third-party upstream mutation was performed.

## What the current patch is doing

The resolver now maintains merged namespace tables keyed by a parent identity plus namespace name. It separately tracks exported value/type names, namespace declaration ids, erased namespaces, and per-instance binding marks. The intent is to share exported members across re-opened namespace bodies while keeping private names body-local.

That is the right ownership problem to solve, and earlier review rounds already corrected several over-broad variants that leaked non-exported names across bodies.

## Existing test coverage that narrows the review

The current PR already carries several important cases.

### Dotted reopen — backward reference is covered

`namespace_reopen_dotted_exports` contains:

```ts
namespace Outer.Inner {
    export class C {}
    export function f() {}
}

namespace Outer.Inner {
    export const c = new C();
    export const g = f();
}
```

So the later dotted body resolving exports from an earlier dotted body is covered.

### Later namespace export — value-space forward case is covered

`namespace_reopen_late_namespace_export` contains:

```ts
namespace N {
    export const x = C;
}
namespace N {
    export namespace C {
        export const a = 1;
    }
}
const C = "outer";
```

So a block-form namespace body referring in value space to an exported namespace introduced by a later reopen is covered.

### Interface + namespace type forward case is covered

`namespace_reopen_interface_namespace_forward` contains:

```ts
namespace Outer {
    export type U = Inner;
}

namespace Outer {
    export interface Inner {}
    export namespace Inner {
        export const a = 1;
    }
}
```

So a forward type reference whose later symbol is both an interface and a namespace is also covered.

These tests materially reduce the original review uncertainty. The remaining questions below are deliberately narrower than “dotted reopen is broken” or “forward namespace types are broken.”

## Remaining source seam A: dotted namespace forward seeding

`Resolver::seed_namespace_exports` explicitly says:

```text
Dotted bodies' inner members are not seeded; forward references across sibling re-opens therefore reach one nesting level deep.
```

The existing dotted regression exercises the later body referring backward to members already declared by the earlier body. It does not exercise the opposite direction:

```ts
namespace A.B {
    export var x = y;
}
namespace A.B {
    export var y = 1;
}
```

The source comment predicts exactly this boundary: the merged table can pre-seed namespace `B` at the outer level while the inner exported member `y` is not pre-seeded into `B` before the earlier dotted body resolves.

This remains a narrow source-backed question. Fieldwork has not executed this exact discriminator.

## Remaining source seam B: pure namespace qualifier in forward type space

The existing interface+namespace test proves a later merged declaration can be found when the type name is also introduced as an interface.

The unresolved source asymmetry is a qualifier introduced only as a namespace:

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

`seed_namespace_exports` deliberately keeps namespace ids out of its pre-scan type set. `bind_namespace_id` later registers namespace declarations in type space when their body is visited, but the earlier sibling body's lookup occurs before that later visit.

That makes this case distinct from `export type U = Inner` where `Inner` is simultaneously introduced as an interface.

Evidence remains `source-read` pending exact-head execution.

## Transform-side dotted-body seam

The TypeScript transform's `enter_current_namespace` intentionally does not push a namespace frame when the recorded member context equals the namespace id's own context, and its comment identifies dotted bodies as that case.

That makes the exact forward dotted case worth testing through resolver + transform together if the resolver-only discriminator fails: cross-body references in dotted forms cannot rely on the ordinary namespace-frame rewrite in the same way block-form bodies do.

## Review threads checked

The PR has repaired and resolved several earlier findings around private binding leakage, exported import aliases, nested namespace instance marks, forward value seeding, and later namespace exports. Some unresolved review comments are outdated against later commits; Fieldwork should version current-head source/tests rather than count raw thread totals.

## Disposition

**NARROW REVIEW HOLD / OBSERVE ACTIVE UPSTREAM.**

The changed-test audit eliminates several broad concerns. The remaining high-value exact-head discriminators are now only:

1. earlier dotted body -> inner export declared by a later dotted reopen;
2. type alias -> pure namespace qualifier introduced only by a later reopen.

If both pass on the exact current PR head, retire these seams as negative results. If either fails, preserve the exact target receipt and continue reviewing the active implementation rather than opening a competing repair.

Automated third-party upstream contact remains prohibited.
