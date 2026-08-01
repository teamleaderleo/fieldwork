# Tests — unit 10

## Exact clean source

- base: `7cdc8c0e089287c8f3643f3a6f668ecdc221722a`
- head: `f167a283fc9f792c427eeded306c38602e60261d`
- compare: https://github.com/teamleaderleo/workerd/compare/7cdc8c0e089287c8f3643f3a6f668ecdc221722a...f167a283fc9f792c427eeded306c38602e60261d
- owned draft PR: https://github.com/teamleaderleo/workerd/pull/5

## Test inventory in the clean diff

- `types/test/index.spec.ts`
  - generator snapshot and end-to-end transform ordering;
  - ordinary, explicit, generic, static, inherited, and global receiver output.
- `types/test/transforms/globals.spec.ts`
  - context-global widening;
  - static exclusion;
  - lexical superclass selection when another namespace contains the same unqualified name.
- `types/test/transforms/overrides/index.spec.ts`
  - partial and full override behavior;
  - explicit receiver preservation and overload handling.
- `types/test/transforms/overrides/replacement-receiver-generics.spec.ts`
  - generic generated owner → nongeneric replacement;
  - generic generated owner → generic replacement;
  - nongeneric generated owner → generic replacement.
- `types/test/types/fetch-receiver.ts`
  - legal bare, detached, nullish, `globalThis`, `self`, `call`, `apply`, and `bind` forms;
  - expected diagnostics for unrelated holders and unrelated explicit receivers;
  - raw host function stored on an unrelated client.

Exact test links:

- https://github.com/teamleaderleo/workerd/blob/f167a283fc9f792c427eeded306c38602e60261d/types/test/index.spec.ts
- https://github.com/teamleaderleo/workerd/blob/f167a283fc9f792c427eeded306c38602e60261d/types/test/transforms/globals.spec.ts
- https://github.com/teamleaderleo/workerd/blob/f167a283fc9f792c427eeded306c38602e60261d/types/test/transforms/overrides/index.spec.ts
- https://github.com/teamleaderleo/workerd/blob/f167a283fc9f792c427eeded306c38602e60261d/types/test/transforms/overrides/replacement-receiver-generics.spec.ts
- https://github.com/teamleaderleo/workerd/blob/f167a283fc9f792c427eeded306c38602e60261d/types/test/types/fetch-receiver.ts

## Executed runtime/application gate

Stensibly PR https://github.com/teamleaderleo/stensibly/pull/482 at exact head `2c42d8041b0cbe5fbccbe87202381361da2bc6ef`:

```console
bun install
bun run typecheck
bun run test
bun run test:convex
bun run worker:check
bun run test:runtime-parity
```

Exact-head validation run `30449733862`: all passed.

Final restored PR-head workflow `30449840120`: ordinary `test` and `runtime-parity` passed.

Versions printed by the retained exact-head run:

```text
Bun 1.3.14
Node v26.5.0
workerd 2026-07-22
```

The native matrix accepted bare, detached, nullish, `globalThis`, and `self` receiver forms and rejected unrelated holder, `call`, `apply`, and `bind` forms. The production `HttpGitHubOAuthClient` default wrapper completed through a local outbound Worker.

Merged revision: `f19c2c7aa09fc4d4fdb7e7ae2d4d727d0eedd091`.

## Executed TypeScript/tooling model

Environment:

- TypeScript `5.8.3`
- ESLint `10.7.0`
- typescript-eslint `8.65.0`
- Node `22.23.1`

Commands retained in issue https://github.com/teamleaderleo/stensibly/issues/474:

```console
tsc --strict --noEmit --pretty false --lib es2022 lane-b-exact.ts
tsc --strict --noEmit --pretty false --lib es2022 lane-b-mechanisms.ts
tsc --strict --noEmit --pretty false --lib es2022 lane-b-erasure.ts
tsc --strict --noEmit --pretty false --lib es2022 lane-b-negative-brand.ts
```

Observed result: one `this: void | null | Owner` receiver accepts the intended direct set and rejects unrelated receivers while the precise function type is retained. Assignment to a plain callback type erases the check.

## Executed workerd carrier checks

Carrier head `0ecc0a6632747031a6650c49a401760e511c9f36`:

- Lint run `30625540316`: passed.
- Focused run `30625540359`: queued at last inspection.
- Tests `30625540450`: queued.
- Coverage `30625540424`: queued.
- CodSpeed `30625540301`: pending.

Earlier execution carriers and historical repairs are preserved in:

- https://github.com/teamleaderleo/stensibly/pull/483
- https://github.com/teamleaderleo/workerd/pull/1
- https://github.com/teamleaderleo/workerd/pull/2

## Clean-head workflow state

Owned PR #5 requested the repository's ordinary pull-request workflows for `f167a283fc9f792c427eeded306c38602e60261d`:

| Workflow | Run | State at packet creation |
| --- | --- | --- |
| Lint | `30674453451` | queued |
| New PR Review | `30674453474` | queued |
| CodSpeed | `30674453493` | queued |
| Tests | `30674453627` | queued |
| Coverage | `30674453672` | queued |

This state records an execution request only.

## Required focused command

```console
bazelisk test \
  //types:test/index.spec \
  //types:test/transforms/overrides/index.spec \
  //types:test/transforms/overrides/replacement-receiver-generics.spec \
  //types:test/transforms/globals.spec \
  //types:test/types/fetch-receiver \
  --test_output=errors
```

## Remaining test gate

1. Complete the focused command at exact clean head `f167a283…`.
2. Complete ordinary target tests and lint at the same head.
3. Inspect representative real generated declaration output for compatibility and recursion.
4. Retain commands, runner image/toolchain, run/job URLs, logs, exact head, result, and runtime.
5. Obtain independent complete-diff review after execution.
