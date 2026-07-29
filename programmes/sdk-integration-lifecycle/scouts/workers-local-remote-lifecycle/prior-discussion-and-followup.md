# Workers SDK follow-up: prior discussion and deeper branch findings

- Fieldwork issue: `#18`
- Fieldwork PR: `#41`
- Target fork: `teamleaderleo/workers-sdk`
- Runtime fork already available if needed: `teamleaderleo/workerd`
- Original source pin: `cloudflare/workers-sdk@69ef8228fd96b4df192195d93c33e56ae665500a`
- Fork base explored: `teamleaderleo/workers-sdk@e09da32b58bc3f6808bce9696e80af0d5f8652b8`
- Follow-up date: `2026-07-30`
- Upstream contact authorized: `false`
- Upstream contact performed: `false`

## Fork coverage

No additional fork is needed for the current campaign. `workers-sdk` owns the Wrangler, Miniflare, Vite-plugin, Vitest-pool, remote-binding, and deploy-helper paths under examination. The existing `workerd` fork is sufficient if a reproduced failure crosses into runtime process termination, Durable Object behavior, or compatibility implementation.

Two existing experiment branches were extended:

- `fieldwork/config-discovery-parity`
  - added `config-redirect-parity.mjs`
  - branch head: `0497e9e30e191f2b7e337b01e32855c4cb6cf5fe`
- `fieldwork/teardown-error-visibility`
  - added `teardown-ownership.mjs`
  - branch head: `161443215fba3ac77407ba30f6996aa9963a0276`

Both new dependency-free probes passed in the Fieldwork runtime.

## New finding 1: cleanup ownership can skip runtime termination

The earlier scout established that the Workers Vitest pool catches Miniflare disposal failures and sends them only to `NODE_DEBUG`. The deeper trace found a more consequential path below that catch.

`Miniflare.dispose()` awaits cleanup operations sequentially. Browser-process cleanup and proxy-client disposal occur before `Runtime.dispose()`. Those operations are not independently isolated. If either rejects, JavaScript leaves the `finally` block at that point and skips `Runtime.dispose()` plus later cleanup.

`Runtime.dispose()` is the operation that destroys the child-process streams, sends `SIGKILL` to `workerd`, and waits for the child to exit. Therefore, an earlier cleanup rejection can leave `workerd` alive. The outer Vitest-pool catch then hides the rejection in debug output and returns from `stop()`.

The retained `teardown-ownership.mjs` probe models this exact control flow:

1. an early proxy cleanup rejection stops sequential cleanup;
2. the modeled runtime-kill step is never called;
3. the outer test-pool catch suppresses the rejection;
4. failure-isolated cleanup reaches runtime termination and collects the earlier failure for a secondary diagnostic.

This does not prove that every reported hang follows this rejection path. A disposal promise that never settles is another plausible path. It does prove that current cleanup ordering has a sufficient path to a hidden live child process.

### Repair direction

- Treat runtime child termination as must-run cleanup.
- Isolate independent cleanup steps so one rejection does not skip the remainder.
- Aggregate component failures into one visible secondary warning while retaining full debug details.
- Add a bounded diagnostic for disposal that never settles and identify the last completed cleanup phase.
- Add tests that inject failures both before and after runtime termination and assert the child-kill path still runs.

## New finding 2: config redirection adds another Wrangler/Vite split

The first probe showed different file-format precedence and search boundaries. The follow-up found another split involving framework-generated deploy configuration.

Wrangler development reads configuration with `useRedirectIfAvailable: true`. A `.wrangler/deploy/config.json` file can therefore redirect `wrangler dev` from a source `wrangler.jsonc` to a generated configuration such as `dist/server/wrangler.json`.

The Vite plugin first resolves a concrete source config path and passes that explicit path to `wrangler.unstable_readConfig()`. An explicit path bypasses Wrangler's redirect discovery. In the modeled fixture:

- `wrangler dev` selects `/app/dist/server/wrangler.json`;
- Vite development selects `/app/wrangler.jsonc`.

This difference may be intentional for some framework build flows. Its contract is implicit, and the two files may contain different environments, bindings, compatibility flags, entry points, or generated assets settings.

### Repair direction

Expose a shared config-selection policy API with explicit options for:

- search boundary;
- format precedence;
- deploy-config redirection;
- consistent reporting of the selected source and generated config relationship.

Wrangler and Vite can then choose different policies deliberately and test those differences, rather than inheriting them from separate helper implementations.

# Prior discussion review

## A. Config selection and redirected configuration

### Exact result

No issue or pull request was found that reports the exact combined discrepancy demonstrated by the branch probes: JSON versus JSONC precedence, upward versus root-only discovery, and Wrangler-dev versus Vite-dev redirect handling.

### Nearby prior discussion

- `cloudflare/workers-sdk#8701` reported a redirected generated config that lacked the requested environment. Wrangler warned that the environment was absent, then still deployed the Worker using the generated config without the requested environment values. This demonstrates that source/generated config disagreement has already produced surprising successful deployments.
- `cloudflare/workers-sdk#13587` added `CLOUDFLARE_VITE_WRANGLER_CONFIG_PATH` so frameworks can explicitly direct the Vite plugin to a generated Wrangler config. This confirms that framework-owned config selection is an established use case and an explicit-path escape hatch already exists.

### Interpretation

The surrounding problem is known, while the exact precedence/search/redirect matrix appears unreported in the reviewed history. This remains a strong fresh regression-test candidate.

## B. Deployment failure after Worker activation

### Prior reports

- `cloudflare/workers-sdk#1585` in 2022 showed Wrangler uploading a Worker successfully and then failing while attaching a route. The reporter described the command as failing even though the Worker was deployed correctly. Discussion focused on route overlap rather than explaining the resulting partial state.
- `cloudflare/workers-sdk#12483` reported a Worker script upload succeeding before a later container operation returned `401 Unauthorized`. Maintainers later questioned the registry configuration in that specific report, so it is not clean proof of an SDK defect. It still documents the user-visible sequence: Worker changed, later deployment phase failed.
- The current deploy helper already checks for Docker before upload with a source comment explaining that this avoids a disjointed state where the Worker updates and the container fails. This shows maintainers recognize the failure class. API-side container rollout and trigger failures still occur after activation and are outside that preflight check.

### Interpretation

This is a long-running problem class rather than a newly discovered possibility. The fresh contribution is a bounded state-reporting design: retain the activated version ID, name the failed phase, and provide inspection, retry, and rollback commands.

## C. Vitest teardown and lingering runtimes

### Prior reports

- Open issue `cloudflare/workers-sdk#14903` reports `@cloudflare/vitest-pool-workers@0.18.8` leaving a live `workerd` child after parallel test files finish. All tests pass, Vitest never exits, serialization avoids the hang, and `NODE_DEBUG=vitest-pool-workers` reports no teardown error.
- Closed issue `cloudflare/workers-sdk#14180` reports a test-pool-specific teardown hang involving a Durable Object whose `blockConcurrencyWhile()` callback both logs and rejects. The same deployed Worker behaves normally.
- Issue `cloudflare/workers-sdk#12764` discussed teardown-related `outputGateBroken` error noise and the runtime-message suppression list.

### Interpretation

There is active and repeated community evidence around teardown. The new source trace supplies a concrete ownership hazard that can be tested independently of any one application reproduction. This candidate should move from warning visibility to lifecycle correctness.

## D. Vitest runtime versus deployed runtime

### Prior reports and maintainer discussion

- `cloudflare/workers-sdk#8988` discussed the pool forcing `nodejs_compat_v2` even when the application disables it. A maintainer described the requirement as intentional because the runner needs Node APIs. Contributors raised the concern that compatibility-driven application branches can then differ between tests and deployment and suggested a clear startup warning.
- `cloudflare/workers-sdk#12925` reported injected test capabilities masking deployment incompatibilities. Maintainer and reporter discussion disagreed over the precise cause, but both sides acknowledged that the pool adds capabilities needed by the runner.
- Maintainer discussion in `#8988` stated that exact production parity is unattainable because Vitest itself runs inside workerd, execution is hosted through a Durable Object, and local resources simulate hosted services.

### Interpretation

The core concern has already received substantial discussion. Strict parity is not a productive campaign target. A more useful contribution is an inspectable effective-runtime manifest and a deployability check that distinguishes application-declared capabilities from runner-supplied capabilities.

# Revised campaign ranking

1. **Vitest/Miniflare teardown lifecycle ownership**
   - Active external report, repeated historical reports, and a source-demonstrated path that can skip child termination.
   - First experiment: inject a failure before runtime disposal and assert `workerd` termination still occurs.

2. **Config selection policy across Wrangler and Vite**
   - Four demonstrated divergence cases, including generated-config redirection.
   - Exact combined discrepancy appears fresh and has a bounded test surface.

3. **Post-activation deployment state reporting**
   - Highest production consequence, with historical reports and explicit source recognition of disjointed state.
   - Start with accurate phase/state reporting rather than automatic rollback.

4. **Vitest effective-runtime disclosure and deployability checks**
   - Real and repeatedly discussed, while several differences are intentional requirements of the runner.
   - Focus on disclosure and application-code compatibility checks rather than runtime identity.

# Validation limits

- The new probes were executed and passed.
- The Workers SDK package and integration suites were not run because the current runtime could not clone from GitHub or install the monorepo dependencies.
- No live Cloudflare deployment, route update, container rollout, or rollback was performed.
- Historical review covered public issues, pull requests, commit history, release notes surfaced by search, and linked discussions available without contacting participants.
- No issue, pull request, review, comment, reaction, or other contact was made in `cloudflare/workers-sdk` or `cloudflare/workerd`.
