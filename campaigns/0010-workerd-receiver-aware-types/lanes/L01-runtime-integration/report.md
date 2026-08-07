# L01 — Runtime and owned-integration evidence

## In simple words

A Worker-global `fetch` function can be detached and called normally, with `undefined`, `null`, `globalThis`, or `self`. It is not permanently bound when read from `self.fetch`. workerd rejects unrelated objects used as the receiver. Bun and Node deliberately accept them. Stensibly now wraps the host function and runs a native-workerd regression, so the original production failure is protected locally.

## Ownership

- Worker: Bunyan lane, materialized by campaign coordinator
- Parent: #230
- Claim scope: integration
- Target source pins:
  - workerd package `1.20260728.1` / runtime `2026-07-28` for the cross-runtime matrix
  - pinned native workerd `2026-07-22` for the extended `self.fetch` matrix
- Testbed candidate head: `teamleaderleo/stensibly#482` head `2c42d8041b0cbe5fbccbe87202381361da2bc6ef`
- Merged testbed revision: merge commit `f19c2c7aa09fc4d4fdb7e7ae2d4d727d0eedd091`
- Upstream contact authorized: no new contact

## Observed receiver matrix

Given:

```js
const fromSelf = self.fetch;
```

Pinned native workerd returned HTTP 200 with body `receiver-ok` for:

```js
fromSelf(url);
fromSelf.call(undefined, url);
fromSelf.call(null, url);
fromSelf.call(globalThis, url);
fromSelf.apply(undefined, [url]);
fromSelf.apply(null, [url]);
fromSelf.apply(globalThis, [url]);
fromSelf.bind(undefined)(url);
fromSelf.bind(null)(url);
fromSelf.bind(globalThis)(url);
```

It rejected:

```js
fromSelf.call({}, url);
({ fetch: fromSelf }).fetch(url);
fromSelf.apply({}, [url]);
fromSelf.bind({})(url);
```

Every rejection produced:

```text
TypeError: Illegal invocation: function called with incorrect `this` reference. See https://developers.cloudflare.com/workers/observability/errors/#illegal-invocation-errors for details.
```

The same receiver rule applies across direct invocation, `call`, `apply`, and `bind`.

## Cross-runtime boundary

| Runtime | Unrelated receiver | Interpretation |
| --- | --- | --- |
| workerd | rejected | JSG/V8 host-operation receiver enforcement |
| Chromium | rejected | browser/Web IDL-compatible receiver enforcement |
| Bun | accepted | intentionally follows Node server-global behaviour |
| Node | accepted | plain server-global wrapper delegates without receiver brand check |

Observed versions in the retained compatibility packet:

- Bun `1.3.14`
- Node `26.5.0`
- workerd package `1.20260728.1`
- Chromium `144.0.7559.96`

The [Bun issue](https://redirect.github.com/oven-sh/bun/issues/36268) was closed as intentional Node compatibility. No Bun or Node runtime change is recommended.

## Owned testbed result

Stensibly's `HttpGitHubOAuthClient` now stores an application-owned arrow wrapper rather than raw host `fetch`:

```ts
this.fetchImpl = fetchImpl
  ? (input, init) => fetchImpl(input, init)
  : (input, init) => globalThis.fetch(input, init);
```

The merged parity check:

- runs Bun and Node receiver matrices;
- runs the corresponding native-workerd matrix;
- bundles the real default-fetch OAuth client path;
- routes outbound workerd requests to a local service;
- confirms the wrapper reaches the local service instead of failing at receiver validation.

Primary owned records:

- `teamleaderleo/stensibly#474`
- `teamleaderleo/stensibly#482`

## Evidence labels

- **Observed:** exact receiver results under the named runtimes.
- **Observed:** the production wrapper path completed under native workerd.
- **Documented:** Bun's maintainers treat Node-compatible global `fetch` receiver behaviour as intentional.
- **Inferred:** declaration diagnostics would prevent a subset of mistakes before runtime.

## Boundaries

- One pinned workerd configuration does not establish every compatibility date or platform.
- The runtime result establishes behaviour, not the correct generator architecture.
- The owned testbed proves Stensibly's path and does not establish ecosystem frequency.
- Chromium was not rerun for every extended `self.fetch` case because workerd was the required integration target.

## Disposition

Complete. Keep the merged Stensibly runtime regression regardless of the upstream declaration decision.
