# Workers SDK fork experiments

- Fieldwork issue: `#18`
- Fork: `teamleaderleo/workers-sdk`
- Fork base revision explored: `e09da32b58bc3f6808bce9696e80af0d5f8652b8`
- Original scout pin: `69ef8228fd96b4df192195d93c33e56ae665500a`
- Retrieval and experiment date: `2026-07-29`
- Upstream contact authorized: `false`
- Upstream contact performed: `false`

The fork base was four commits ahead of the original scout pin and zero commits behind. Those intervening changes did not modify the two config-discovery implementations examined here.

## Validation method

The environment could access GitHub through repository APIs but could not clone from `github.com` or install the monorepo dependencies. Each branch therefore contains a dependency-free Node probe that models the exact source ordering or mutation policy under study, plus a README tying the probe to source files. All four probes were also executed in the Fieldwork runtime and passed their assertions.

These are source-backed controlled experiments. They are stronger than inspection alone and remain below package-suite, mocked integration, or live Cloudflare deployment evidence.

## Branch 1: config discovery parity

- Branch: `fieldwork/config-discovery-parity`
- Branch head after experiment notes: `0cc03615cd602f582c402b2fa7383ab44d1a9baa`
- Probe: `fieldwork-experiments/config-discovery-parity/config-discovery-parity.mjs`

Wrangler searches upward for `wrangler.json`, then repeats the upward search for `wrangler.jsonc`, then for `wrangler.toml`. The Vite plugin checks only the Vite root and tries `jsonc`, `json`, then `toml`.

The retained probe demonstrates three divergent layouts and one control:

1. Same directory with JSON and JSONC: Wrangler selects JSON; Vite selects JSONC.
2. Parent JSON with child JSONC: Wrangler selects the parent JSON; Vite selects the child JSONC. Wrangler's format priority beats proximity.
3. Parent JSONC only: Wrangler finds the parent config; Vite finds no config.
4. TOML only in the same root: both select the TOML file.

### Campaign consequence

This candidate is ready for an upstream-style regression test and a design decision. A shared discovery helper with an explicit search boundary and precedence policy is more coherent than a warning-only repair, because warnings would leave commands reading different files.

## Branch 2: post-activation deployment failure

- Branch: `fieldwork/deploy-post-activation-failure`
- Branch head after experiment notes: `609623ba8552a016f3c67cee7259e38d8431bd91`
- Probe: `fieldwork-experiments/deploy-post-activation-failure/deploy-post-activation-failure.mjs`

The deployment source activates code before later container and trigger operations:

- the versions path uploads a version and creates a 100% deployment before container rollout and trigger deployment;
- the legacy path performs the script `PUT` before trigger deployment;
- later container and trigger errors escape the deployment function.

The source-order model passes three cases. A container failure, a new-API trigger failure, and a legacy-path trigger failure each produce a failed command while the model keeps the new Worker active.

### Campaign consequence

Start with state visibility rather than automatic rollback. Track whether activation completed, retain the activated version ID, name the failed phase, and print inspection, retry, and rollback commands. Automatic rollback can add another deployment and may be wrong when the failed later step is safely retryable.

## Branch 3: teardown error visibility

- Branch: `fieldwork/teardown-error-visibility`
- Branch head after experiment notes: `fc640d21069ef4bb4f61d167b5562f76cf30c06d`
- Probe: `fieldwork-experiments/teardown-error-visibility/teardown-error-visibility.mjs`

The Workers Vitest pool catches Miniflare and remote-proxy disposal failures and sends them to `util.debuglog`. The Vite plugin catches Miniflare disposal failure during server close and sends it to its debug logger.

The model demonstrates that two Vitest teardown failures and one Vite teardown failure produce zero ordinary visible errors while stop or close returns successfully.

### Campaign consequence

Preserve the primary test or server result and emit one visible secondary warning that names failed cleanup components. Keep full errors in debug output. This would aid diagnosis of locked state directories, occupied ports, live child processes, and stale remote sessions without turning a passed test suite into a failure solely because teardown rejected.

## Branch 4: Vitest runtime capability delta

- Branch: `fieldwork/vitest-runtime-delta`
- Branch head after experiment notes: `846daede3b77c1f798755351b1cb343cb13a37e0`
- Probe: `fieldwork-experiments/vitest-runtime-delta/vitest-runtime-delta.mjs`

The Workers Vitest pool intentionally adds runner capabilities: cross-request promise handling changes, `nodejs_compat_v2`, `unsafe_module`, six Node feature flags, unsafe eval, module fallback, injected `node:console` and `node:vm`, and an ephemeral runner Durable Object. It also uses the current date when the test configuration omits a compatibility date.

The model shows a deployment declaration containing only `nodejs_compat` becoming a test runtime with nine added flags plus helper capabilities and injected modules.

### Campaign consequence

Strict parity is the wrong target because several additions are necessary runner machinery. Reframe this candidate around an inspectable effective-runtime manifest and a deployability check that distinguishes application-declared capabilities from capabilities supplied only by the test runner.

## Revised campaign ranking

1. **Config discovery parity** — strongest demonstrated discrepancy, small reproducer, bounded patch and test surface.
2. **Post-activation deployment state visibility** — highest operational consequence, source-order model confirms the ambiguity, requires careful error design.
3. **Teardown failure visibility** — clear diagnostic gap with a low-risk secondary-warning direction.
4. **Vitest effective-runtime disclosure** — real and measurable delta, reframed from strict parity because the runner additions are intentional.

## Recommended sequence

Begin with the config-discovery regression tests and shared-policy decision. Follow with post-activation deployment error enrichment. Treat teardown warnings as a focused reliability patch. Pursue the Vitest runtime manifest after defining which test-only capabilities can be attributed to user application code.

## Remaining evidence limits

- The Workers SDK package and integration suites were not run.
- No live Cloudflare deployment, container rollout, route update, or rollback was performed.
- The probes model source-selected behaviour; they do not replace mocked API tests or disposable-account end-to-end tests.
- No issue, pull request, comment, or other contact was made in `cloudflare/workers-sdk`.
