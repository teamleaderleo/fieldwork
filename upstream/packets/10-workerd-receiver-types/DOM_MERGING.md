# DOM declaration merging — unit 10

## In simple words

The receiver-aware declarations work in the supported Workers typing environment, which recommends `lib: ["esnext"]` plus Workers types. A project that also includes TypeScript's `lib.dom` can merge receiver-free DOM overloads into the same globals and interfaces. Overload resolution may then select the DOM overload and accept an unrelated holder again.

This is an effectiveness limit in mixed browser/Worker ambient environments. It is not a reason to weaken the workerd declarations, and it does not affect importable types used under aliases in the same way.

## Supported package configuration

Current `npm/workers-types/README.md` recommends the minimal ambient setup:

```json
{
  "compilerOptions": {
    "target": "esnext",
    "module": "esnext",
    "lib": ["esnext"],
    "types": ["@cloudflare/workers-types"]
  }
}
```

The package now recommends `wrangler types` for compatibility-date and flag-specific output, but the same principle applies: the Workers declaration environment supplies its own Web API surface rather than layering on `lib.dom`.

Evidence label: **Documented configuration**.

## Executed merged-overload model

Environment:

```text
TypeScript 5.8.3
Node v22.16.0
--strict --noEmit --lib es2022,dom
```

Model:

```ts
declare function fetch(
  this: Window | typeof globalThis | null | void,
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<Response>;

interface EventTarget {
  addEventListener(
    this: EventTarget | typeof globalThis | null | void,
    type: string,
    callback: EventListenerOrEventListenerObject | null,
    options?: AddEventListenerOptions | boolean,
  ): void;
}

const fetchHolder = { fetch };
fetchHolder.fetch("data:text/plain,ok");

const nativeTarget = new EventTarget();
const eventHolder = { addEventListener: nativeTarget.addEventListener };
eventHolder.addEventListener("probe", () => {});
```

Command:

```console
tsc --strict --noEmit --pretty false --lib es2022,dom /tmp/unit10-dom-merge-model.ts
```

Result: exit code `0`.

Why it compiles:

- `lib.dom` already declares a receiver-free global `fetch` overload;
- `lib.dom` already declares receiver-free `EventTarget.addEventListener` overloads;
- the receiver-aware declarations merge into those overload sets rather than deleting the receiver-free forms;
- an unrelated property-call receiver can therefore match a receiver-free DOM overload.

Evidence label: **Model-executed**.

## Claim boundary

The contribution can claim improved diagnostics in a Workers-native declaration environment while the exact receiver-aware overload remains authoritative.

It must not claim:

- nominal native receiver safety;
- protection when a receiver-free overload from another library is merged into the same symbol;
- protection after assignment to a receiver-free callback type;
- protection through `Reflect.apply()`'s `any` receiver.

## Publication wording

Suggested compatibility note:

> The diagnostics rely on the receiver-aware Workers overload remaining in the selected declaration environment. Projects that merge browser DOM libraries or other receiver-free overloads into the same globals may retain a permissive overload. The recommended Workers TypeScript configuration uses Workers-generated Web API declarations without `lib.dom`.

## Out of scope

- detecting or rejecting incompatible ambient library combinations;
- changing TypeScript overload-merging rules;
- nominal branding of every generated JSG resource;
- modifying `lib.dom` declarations;
- making importable aliases affect unrelated global DOM declarations.
