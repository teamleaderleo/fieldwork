# NodeSDK current-main and prior-art check

## Status

- Checked: 2026-07-30
- Upstream contact: read-only retrieval and search only
- Upstream notifications created: none

## Current-main verification

The current default branch version of:

`experimental/packages/opentelemetry-sdk-node/src/sdk.ts`

has blob SHA:

`0eda59e7d6ea377447a930eca7f5a8851e18462f`

That is the same blob SHA reviewed at pinned revision:

`7b06368b7362a30ca69c178f43bd94dfbb36f85d`

Therefore the following behavior remains present on current upstream `main` at the time of this check:

- no instance start-state guard;
- instrumentation unload function discarded;
- context and propagation registration results ignored;
- trace and metric global-registration booleans ignored;
- logger global-registration return value ignored;
- shutdown limited to provider fields held by the SDK object.

## Prior-art searches

Read-only issue and pull-request searches were run for:

- `NodeSDK start twice`
- `NodeSDK repeated start`
- `MetricReader can not be bound to a MeterProvider again NodeSDK`
- `NodeSDK start idempotent`

No direct issue or PR matching the same repeated-start ownership split was returned.

This is not proof that no related discussion exists under different wording. It is enough to say that the obvious prior-art searches did not reveal an existing direct report or fix.

## Related but distinct report

A previous duplicate-registration report, `open-telemetry/opentelemetry-js#4804`, concerned application double initialization through separate setup paths. It was attributed to application startup duplication.

The current finding is narrower and mechanically different:

- the same `NodeSDK` object is started twice;
- private provider ownership moves while global ownership does not;
- shutdown can then target the non-global provider;
- metrics fail differently after preceding startup work.

Use a redirect link when citing that prior report from Fieldwork:

https://redirect.github.com/open-telemetry/opentelemetry-js/issues/4804

## Decision impact

The issue draft is current enough to retain. The minimal start-state guard remains the first patch candidate. The broader registration-transaction and shutdown/disposal questions remain separate follow-ups.

No upstream issue, pull request, comment, review, reaction, or direct backlink was created.