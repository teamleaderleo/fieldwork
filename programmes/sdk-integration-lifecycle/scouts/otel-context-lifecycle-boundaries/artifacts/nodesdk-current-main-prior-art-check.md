# OpenTelemetry JS current-main and prior-art check

## Status

- Checked: 2026-07-30
- Upstream contact: read-only retrieval and search only
- Upstream notifications created: none
- Current upstream default-branch head: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- User-owned fork default-branch head: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`

The upstream repository and owned fork are currently aligned at the exact revision used by the lifecycle work.

## Current-main verification

A fresh read-only commit query returned upstream `main` head:

`7b06368b7362a30ca69c178f43bd94dfbb36f85d`

That is the exact pinned revision used by the characterization and fix branches. The findings therefore do not currently depend on an outdated fork base.

### NodeSDK class helper

`experimental/packages/opentelemetry-sdk-node/src/sdk.ts` has blob SHA:

`0eda59e7d6ea377447a930eca7f5a8851e18462f`

The following behavior remains present on current upstream `main`:

- no instance start-state guard;
- instrumentation unload function discarded;
- context and propagation registration results ignored;
- trace and metric global-registration booleans ignored;
- logger global-registration return value ignored;
- shutdown limited to provider fields held by the SDK object;
- shutdown can observe an empty provider set before or during startup;
- provider shutdown calls are invoked eagerly while constructing the aggregate promise list.

### Experimental function helper

`experimental/packages/opentelemetry-sdk-node/src/start.ts` remains at the reviewed pinned implementation.

The current path still:

- registers instrumentation before component creation;
- can return `NOOP_SDK` after partial helper-created state;
- publishes globals without ownership tokens;
- returns a shutdown handle that only knows provider fields;
- does not expose installation disposal or duplicate-initialization coordination.

The repaired owned-fork candidate now has head:

`482cb975f78572bc65a9b263fb677b7a274e2fff`

That branch registers instrumentation against newly created providers before global publication and cleans up helper-created components when registration throws.

### Trace, logs, and metrics fanout

The reviewed aggregate implementations remain current at the pinned upstream head:

- `packages/sdk-trace/src/MultiSpanProcessor.ts` eagerly calls child shutdown and force-flush methods;
- `experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts` eagerly calls child methods inside `.map()` before `Promise.all`;
- `packages/sdk-metrics/src/MeterProvider.ts` eagerly calls collectors inside `.map()` and sets provider shutdown state before collector fanout.

The owned-fork characterization head `548b8a4b801bbc0a9624323585179de44e44e174` contains prepared cases for both the trace synchronous-escape form and the log/metric rejected-promise-but-skipped-child form.

## Prior-art searches

Read-only issue and pull-request searches were run for:

- `NodeSDK start twice`
- `NodeSDK repeated start`
- `MetricReader can not be bound to a MeterProvider again NodeSDK`
- `NodeSDK start idempotent`
- synchronous shutdown exceptions skipping later processors
- shutdown fanout after a throwing processor

No direct issue or PR matching the same repeated-start ownership split or synchronous fanout failure was returned.

This is not proof that no related discussion exists under different wording. It is enough to say that the targeted searches did not reveal an existing direct report or fix.

## Related but distinct report

A previous duplicate-registration report, `open-telemetry/opentelemetry-js#4804`, concerned application double initialization through separate setup paths. It was attributed to application startup duplication.

The current same-object finding is narrower and mechanically different:

- the same `NodeSDK` object is started twice;
- private provider ownership moves while global ownership does not;
- shutdown can then target the non-global provider;
- metrics fail differently after preceding startup work.

Use a redirect link when citing that prior report from Fieldwork:

https://redirect.github.com/open-telemetry/opentelemetry-js/issues/4804

## Decision impact

- Candidate A remains current against upstream main.
- Candidate B remains current and its self-review repair addresses an owned-fork regression rather than an upstream change.
- The provider shutdown, metric construction, interleaving, fanout, and global-ownership findings remain present in the reviewed source.
- The new prepared tests still require target execution before promotion.

No upstream issue, pull request, comment, review, reaction, or direct backlink was created.
