# Tests — Vite `watchChange` error isolation

## Exact revisions

| Purpose | Revision |
| --- | --- |
| Public Vite base and current main | `e6b6b167afa0a80548829d1f24a0712f9194389a` |
| Retained negative reproduction | `882e62169e2cc4a8ac91d63aca2337fda4f69e1e` |
| Superseded environment-only source | `a2ab7ca6183ad74d64066d6706e57a546e355224` |
| Superseded plugin-settlement source | `79fa097750158790ec9bf03d74e6f83d702dd4c2` |
| Final canonical source | `ba8ac979ee91c77fdd91304ccde38942e9752133` |

## Negative behavior

At the public base, a rejected `watchChange` hook exits the watcher transaction before Vite-owned invalidation and HMR. The retained virtual-module reproduction proves:

- control: backing state changes from `alpha` to `beta`, cache invalidates, and the next transform contains `beta`;
- rejecting hook: the error is logged, HMR is skipped, cache remains populated, and the next transform still contains `alpha`.

The later adversarial control proved that environment-level settle-all was insufficient: a fast sibling rejection could let HMR continue while a slower sibling hook remained pending, and later sequential hooks could be skipped.

## Final target-native regression

Exact file:

`packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js`

Coverage:

1. **Change**
   - initial virtual transform contains `alpha`;
   - exact hook error reaches the configured logger;
   - HMR runs;
   - transform cache clears;
   - refreshed transform contains `beta`.
2. **Add**
   - watcher add maps to Rollup event `create`;
   - rejection is reported;
   - HMR receives type `create`.
3. **Unlink**
   - watcher unlink maps to Rollup event `delete`;
   - rejection is reported;
   - HMR receives type `delete`.
4. **Sibling settlement and barriers**
   - fast and slow failing hooks both start;
   - the fast failure is reported while the slow hook remains blocked;
   - HMR does not run early;
   - after release, the slow failure is reported;
   - a sequential hook runs only after the preceding group settles;
   - the later parallel hook and HMR retain order.
5. **Synchronous throw**
   - a direct throw is reported;
   - a later hook still runs;
   - HMR still runs.

The focused product-content carrier passed installation, formatting, full build/type generation, generated-declaration leak checks, all focused cases, ESLint across the exact three files, and clean three-file packaging.

## Final ordinary workflows

### Zizmor

- Run `30753769710`
- Result: **success**

### CI

- Run `30753769684`
- Result: **success**

Job results:

| Job | Result |
| --- | --- |
| Changed-file discovery | success |
| Lint / build / format / typecheck / docs / workflow checks | success |
| Ubuntu Node 20 Build&Test | success |
| Ubuntu Node 22 Build&Test | success |
| Ubuntu Node 24 Build&Test | success |
| Ubuntu Node 26 Build&Test | success |
| macOS Node 24 Build&Test | success |
| Windows Node 24.15.0 Build&Test | success |
| Build & Test Passed or Skipped aggregate | success |
| Build & Test Failed aggregate | skipped |

Every Build&Test job completed:

- dependency installation;
- Vite build;
- unit tests;
- ordinary serve tests;
- bundled-development serve tests;
- build tests.

Preview run `30753769692` skipped as expected for the internal source PR and carries no product claim.

## Source-gate repairs

The first final-source attempt failed ordinary type checking because:

- `plugin[hookName]` remained optional at the `getHookHandler` call;
- `shouldRunWatchChange()` could return `undefined` while declaring `boolean`.

Final head `ba8ac979...` fixes those exact type defects. The complete ordinary matrix above controls the final source.

## Classification summary

| Claim | Result | Evidence |
| --- | --- | --- |
| Public-base watcher transaction aborts after hook failure | confirmed | source read + target reproduction |
| Change cache invalidation and HMR continue after rejection | passed | final target-native test |
| Add/unlink event mapping and HMR continue after rejection | passed | final target-native test |
| Every applicable sibling hook settles | passed | blocked-sibling control |
| Every plugin failure is reported | passed | dual-failure assertions |
| Sequential barriers remain effective | passed | ordering assertion |
| Sync throws cannot skip later hooks/HMR | passed | final target-native test |
| Specialized method stays out of generated declarations | passed | generated-declaration check |
| Lint, formatting, typing, docs, and workflow checks | passed | final CI |
| Linux, macOS, and Windows ordinary Build&Test | passed | final CI |
| Public direct `watchChange()` remains fail-fast | source-confirmed | exact diff review |

## Evidence limits

- Simultaneous logger call ordering is not a public promise.
- A custom logger that throws can interrupt reporting; logger-failure policy is separate.
- Separate filesystem events remain independently concurrent.
- The repair does not roll back arbitrary plugin-owned partial state.
- Add/unlink controls prove event mapping and continuation rather than every platform-specific downstream mutation.
- Any source-head or material public-base movement requires renewed reconciliation.
