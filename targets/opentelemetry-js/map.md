# Target Map: OpenTelemetry JavaScript

Repository: https://redirect.github.com/open-telemetry/opentelemetry-js

Related contrib repository: https://redirect.github.com/open-telemetry/opentelemetry-js-contrib

## In simple words

OpenTelemetry JS supplies process-wide telemetry plumbing for traces, metrics, logs, context, instrumentation, processing, and export. The active Fieldwork investigation found that convenience startup helpers can lose agreement with the global APIs about which providers they installed and own. The work is now split into several independently reviewable proposals rather than one lifecycle rewrite.

## Current promoted proposal packet

Canonical coordination and evidence:

- target hub: https://github.com/teamleaderleo/fieldwork/issues/4
- scout lane: https://github.com/teamleaderleo/fieldwork/issues/19
- synthesis PR: https://github.com/teamleaderleo/fieldwork/pull/32
- proposal index: `programmes/sdk-integration-lifecycle/scouts/otel-context-lifecycle-boundaries/artifacts/upstream-candidate-map.md`
- cross-language comparison: `programmes/sdk-integration-lifecycle/scouts/otel-context-lifecycle-boundaries/artifacts/cross-language-lifecycle-comparison.md`

Current candidates, in recommended order:

1. **NodeSDK one-start-attempt guard** — implemented as an isolated draft in the user-owned fork.
2. **`startNodeSDK()` failed-creation cleanup** — implemented as a separate isolated draft.
3. **Trace-provider shutdown contract** — issue draft first; provider-level one-shot shutdown and post-shutdown no-op behavior require agreement.
4. **Metric-reader binding transactionality** — metrics-specific issue and eventual patch; NodeSDK cannot repair a constructor that never returned.
5. **Process-global registration ownership and disposal** — umbrella design issue covering duplicate helper instances, replacement, restart, and safe cleanup.

These are not one bug and should not become one mega-issue or mega-PR. Each proposal must contain its own reproduction, consequence, owning boundary, alternatives, validation plan, and uncertainty. The Fieldwork synthesis is optional supplemental context, not a prerequisite for understanding an eventual upstream report.

Upstream contact remains unauthorized.

## Why it is here

Observability is a cross-cutting need for agent systems, hosted runtimes, browser tools, and automation. OpenTelemetry work can turn local instrumentation problems into standards-aware, reusable results.

## Current direction

The current lifecycle evidence supports three broad principles:

- convenience-helper initialization should be deterministic and one-shot unless replacement is explicitly supported;
- provider shutdown state should be enforced at the provider layer rather than delegated to every processor or caller;
- global or instrumentation cleanup requires explicit ownership and must not blindly remove another component's installation.

Historical issues and other language SDKs are useful citations for user pressure and design precedent, but they do not replace JavaScript-specific source analysis and reproductions.

## Areas worth understanding

- context propagation across async boundaries;
- traces around tool and model calls;
- semantic conventions for emerging AI workloads;
- browser and Worker runtime support;
- exporter failure and shutdown behaviour;
- instrumentation correctness under retries and cancellation;
- global provider and instrumentation ownership;
- provider construction and rollback;
- test utilities and conformance fixtures.

## Evidence we can produce

- deterministic span trees;
- propagation matrices;
- runtime-specific reproductions;
- shutdown and retry fault injection;
- semantic-convention comparisons;
- instrumentation compatibility tests;
- lifecycle state-machine characterizations;
- cross-language contract comparisons;
- owned-fork candidate fixes kept separate from characterization.

## Entry standard

Determine whether a change belongs in the core API/SDK, Node SDK helper, signal-specific SDK, contrib instrumentation, semantic conventions, or an application package. Standards-facing and global-lifecycle proposals require prior discussion, precise terminology, source-pinned evidence, and explicit ownership analysis.

Follow `PROPOSALS.md` when one investigation produces multiple possible upstream units.

## Stop conditions

- the desired telemetry is application-specific;
- the proposal conflicts with an active specification decision;
- the reproduction cannot distinguish library behaviour from runtime behaviour;
- an existing upstream proposal already covers the same bounded defect;
- cleanup cannot establish ownership safely;
- cross-language precedent is being mistaken for proof of the JavaScript behavior;
- the work becomes metric churn without a concrete consumer need.