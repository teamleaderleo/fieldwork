# Vite build marker operation-scope follow-up

State: `candidate-created`

Batch: `B20260730-001`

Canonical candidate: #183

Sibling candidates: #165, #179

Parent review hub: #88

Synthesis PR: #112

Workers SDK branch: `fieldwork/teardown-lifecycle-hardening`

Reviewed Workers SDK head: `26556bcf7cda31009039b3aaf1527a8e4649e37f`

Upstream contact authorized: `false`

Upstream contact performed: `false`

## Finding

The Cloudflare Vite plugin sets `process.env.CLOUDFLARE_VITE_BUILD = "true"` from its build config hook. Preview configuration later uses that process-global marker to choose `prerenderWorkerConfigPath` instead of the ordinary entry `configPath`.

Production code never restores or deletes the value.

The package's own programmatic playground harness calls `createBuilder(...).buildApp()` and then `preview(...)` in the same process. It manually deletes `CLOUDFLARE_VITE_BUILD` after the build, with a comment explaining that the later independent preview must not be treated as a preview running during build.

This directly establishes operation-state leakage.

## Consequences

- successful programmatic build contaminates later independent preview;
- failed config resolution or build also leaves the marker set;
- unrelated concurrent preview observes the build marker;
- plugin internals overwrite any pre-existing value without restoration.

When the deploy-config record includes `prerenderWorkerConfigPath`, contaminated preview can select the prerender Worker instead of the normal entry Worker.

## Executed model

Executed:

```sh
node /tmp/vite-build-marker-scope.mjs
```

The executed content is identical to the committed Workers SDK artifact.

Output:

```text
PASS: a successful build leaves the process-wide marker sticky
PASS: a failed build also leaves the process-wide marker sticky
PASS: a concurrent unrelated preview observes the sticky marker
PASS: scoped build preview selects prerender only inside the build
PASS: concurrent unrelated preview stays outside scoped build state
PASS: scoped build failure preserves the error and clears the scope
```

Evidence class: `source-read` plus `model-executed`.

No Vite package, playground, or programmatic build/preview test executed.

## Draft repair

`vite-build-marker-scope.patch` replaces the internal process marker with an `AsyncLocalStorage` build context and wraps the selected `builder.buildApp` hook.

Desired contract:

- preview/prerender nested inside the build sees build context;
- later or concurrent independent preview does not;
- build failure preserves the exact error and ends the context;
- a custom `builder.buildApp` receives the same scope;
- process environment is unchanged.

The patch remains unapplied.

## Design boundary

The current draft begins the scope at `builder.buildApp()`.

Frameworks can create child Vite servers earlier during `configResolved()`; an existing React Router child-compiler regression confirms that pattern. That known child is a dev server and does not consume the preview marker, but a child `isPreview` server must be characterized before promotion.

If a configResolved child preview is supported and must select the prerender Worker, the scope needs a higher operation boundary without reintroducing process-global state.

## Required tests

1. Programmatic build followed by independent preview selects the entry Worker without manual env deletion.
2. Failed build followed by preview preserves the build error and selects the entry Worker.
3. Preview nested inside buildApp selects the prerender Worker.
4. Concurrent unrelated preview during a pending build selects the entry Worker.
5. Custom buildApp receives the scope.
6. Two concurrent builds keep nested preview state isolated.
7. Process environment is unchanged after success and failure.
8. Child preview created during configResolved is characterized on Vite 6, 7, and 8.
9. Actual deploy-config paths are asserted, not only helper booleans.

## Coordination placement

- #183 is the canonical review and disposition surface.
- #165 remains the container cleanup ownership candidate.
- #179 remains the logical runtime/tunnel ownership candidate.
- #88 remains the parent review hub.
- #112 retains the repository-backed synthesis.
- #87 and PR #105 own the generated review projection.

The established labels are sufficient:

- `state:ready`
- `type:lane`
- `parallel-safe`
- `target:workers-sdk`
- `programme:sdk-integration-lifecycle`

## Boundary

This candidate concerns operation-scoped build intent and preview config selection. It should not be merged into the container cleanup or logical runtime-owner changes.

No live build, preview, browser, deployment, or upstream interaction occurred.
