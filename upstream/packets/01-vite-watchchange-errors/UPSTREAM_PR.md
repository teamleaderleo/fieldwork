# Upstream pull-request draft

## In simple words

This draft describes the two-file Vite change without Fieldwork workflow terms. It remains unposted until the user authorizes the exact public upstream interaction.

## Title

`fix(dev): continue invalidation after watchChange errors`

## Body

### Description

A rejected plugin `watchChange` hook currently exits the dev-server file-event handler before Vite performs its own module-graph invalidation and HMR work.

The watcher listener logs the rejection, so the error is visible, but a previously transformed virtual module can remain cached after its watched backing file changes.

This follows the error-reporting work in #22188. That change handles escaped watcher promises; this change isolates the hook failure from the later Vite-owned event processing.

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
- the virtual module transform cache is invalidated;
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

Ordinary CI and workflow-security checks should be listed here with their final exact-head results before submission.

## Finalization checklist

Before public use:

1. rebase onto the then-current Vite `main`;
2. run the focused regression and ordinary repository gates at the final exact head;
3. replace the test section with accepted final receipts;
4. confirm the complete diff contains only the implementation and test;
5. confirm current contribution and AI-disclosure policy;
6. remove this checklist and every internal branch reference;
7. obtain explicit authority for the exact public pull request.

Public upstream contact remains unauthorized.
