# TypeScript compatibility model — unit 10

## In simple words

Explicit TypeScript `this` parameters improve direct call diagnostics without forcing user implementations or subclass overrides to write their own `this` parameter. Ordinary receiver-free callback types and `OmitThisParameter` continue to work.

The main intentional sharp edge is a partial holder such as `Pick<Owner, "method">`: calling the copied native method through that partial object is rejected because the property-call receiver is not the full owner. Structural typing also remains an unavoidable limit: a fake object that structurally satisfies the owner interface can still be accepted even when the runtime would reject its identity.

## Exact environment

```text
TypeScript 5.8.3
Node v22.16.0
--strict --noEmit --lib es2022
```

Executed command:

```console
tsc --strict --noEmit --pretty false --lib es2022 /tmp/unit10-compat-model.ts
```

Result: exit code `0`.

Evidence label: **Model-executed**.

## Model

```ts
interface Owner {
  readonly brand: string;
  method(this: Owner, value: string): number;
}

class ImplementsOwner implements Owner {
  readonly brand = "impl";
  method(value: string) {
    return value.length;
  }
}

class Base {
  readonly brand = "base";
  method(this: Base, value: string): number {
    return value.length;
  }
}
class Sub extends Base {
  override method(value: string): number {
    return value.length + 1;
  }
}

const literal: Owner = {
  brand: "literal",
  method(value) {
    return value.length;
  },
};
literal.method("ok");

const owner = new ImplementsOwner();
const receiverFree: (value: string) => number = owner.method;
receiverFree("ok");

const omitted: OmitThisParameter<Owner["method"]> = owner.method;
omitted("ok");

const picked: Pick<Owner, "method"> = { method: owner.method };
// @ts-expect-error Pick does not supply the full owner as the call receiver.
picked.method("no");

const extracted: Owner["method"] = owner.method;
extracted.call(owner, "ok");
// @ts-expect-error unrelated receiver
extracted.call({}, "no");

const structuralFake: Owner = {
  brand: "fake",
  method: owner.method,
};
structuralFake.method("type-system-false-negative");
```

## Established compatibility behavior

### User implementations remain ergonomic

A class implementing an interface whose method has `this: Owner` may implement the method without writing an explicit receiver parameter. The same is true for an object literal assigned to the interface.

This matters for generated binding interfaces that users mock or implement in tests: the declaration change does not force a new source parameter or runtime argument.

### Subclass overrides remain ergonomic

A subclass may override a base method that has `this: Base` without repeating the receiver parameter. The override remains assignable and ordinary method syntax is unchanged.

### Callback widening remains available

A receiver-aware method value remains assignable to an ordinary receiver-free callback type. `OmitThisParameter<Owner["method"]>` also produces an explicit supported escape hatch.

This is consistent with the retained `fetch` fixture: direct exact-type use gets receiver diagnostics, while callback APIs can intentionally widen away that information.

### Partial holders are intentionally rejected

`Pick<Owner, "method">` contains the method property but not the full owner shape. Calling `picked.method()` supplies the partial object as `this`, so TypeScript rejects it.

For a native JSG method this is the correct early warning: copying the method onto an unrelated holder and invoking it as a property is the failure mode this unit targets.

Consumers that genuinely need a receiver-free callback can extract and widen the value or use `OmitThisParameter` rather than invoking it through a partial holder.

## Remaining structural-typing limit

TypeScript owner interfaces are structural, not nominal. A fake object that satisfies the complete owner shape can be accepted as the receiver even though V8 validates hidden native identity rather than TypeScript structure.

The current approach therefore improves common direct and accidental rebinding cases but cannot prove native object identity. A nominal brand across all generated JSG resource interfaces would be a much larger compatibility design and remains outside this unit.

Evidence label: **Observed type-system limit**.

## Publication implications

The upstream compatibility section should state:

- implementations and subclass overrides do not need source changes merely because generated methods gain `this` parameters;
- receiver-free callback assignment remains supported;
- partial-holder property calls may now fail compilation when they would fail at runtime;
- structural fakes remain a known false-negative boundary;
- no claim of nominal receiver safety should be made.
