# Upstream pull-request draft

## In simple words

This is the polished public-facing draft for the two-file Vite change. It deliberately omits Fieldwork workflow terms and private branch names. It remains unposted until the user authorizes the exact public upstream interaction.

## Title

`fix(dev): continue invalidation after watchChange errors`

## Body

### Description

A rejected plugin `watchChange` hook currently exits the dev-server file-event handler before Vite performs its own module-graph invalidation and HMR work.

The watcher listener logs the rejection, so the error is visible, but a previously transformed virtual module can remain cached after its watched backing file changes.

This follows the error-reporting work in #22188. That change handles escaped watcher promises; this change isolates a hook failure from the later file-event work Vite owns.

### Change

- add one server-level helper for environment `watchChange` notifications;
- wait for every environment notification to settle;
- report each rejection through the configured logger;
- continue the existing invalidation and HMR path;
- use the same helper for change, add, and unlink events;
- keep generic plugin hook ordering and success-path behavior unchanged.

### Regression coverage

The focused server test covers all watcher event kinds.

For a change event with a rejecting hook, it verifies that:

- the exact error reaches the configured logger;
- the plugin `hotUpdate` hook runs;
- the virtual-module transform cache is invalidated;
- the next transform reads updated content.

For add and unlink events, it verifies that:

- the exact error reaches the logger;
- `watchChange` receives `create` or `delete` respectively;
- `hotUpdate` still runs with the matching event type.

### Compatibility

The behavior change is limited to rejected `watchChange` hooks. Their errors remain visible, while Vite continues cache and HMR work for the filesystem event. When several environments reject, each rejection is logged.

No public API, configuration option, dependency, generated output, or lockfile changes.

### Tests

```text
pnpm run build
pnpm exec vitest run packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js
pnpm exec oxfmt --check packages/vite/src/node/server/index.ts packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js
pnpm exec eslint packages/vite/src/node/server/index.ts packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js
```

The focused three-case regression passed in Vite CI. Repository build, lint, formatting, typecheck, documentation tests, workflow checks, Linux Node 20/22/24/26 Build&Test, and macOS Node 24 Build&Test passed. Windows build, unit, focused regression, and ordinary serve also passed; later Windows HMR/SSR playground runs were flaky in existing tests outside this change.

## Private validation note — remove before public use

- Canonical source head: `a2ab7ca6183ad74d64066d6706e57a546e355224`
- Inspected public base: `e6b6b167afa0a80548829d1f24a0712f9194389a`
- Complete source diff: exactly two files
- Source self-review disposition: `ACCEPT` for independent final review
- Public upstream contact: unauthorized; interactions zero

## Finalization checklist

Before public use:

1. obtain independent complete-diff acceptance;
2. re-read the then-current Vite `main` and rebase if materially needed;
3. repeat duplicate search and contribution/AI-disclosure policy checks;
4. rerun the focused regression and ordinary gates if the source or base moves;
5. replace the test paragraph with the final accepted receipts;
6. remove the private validation note, this checklist, and every internal reference;
7. obtain explicit authority for the exact public pull request.

Public upstream contact remains unauthorized.
