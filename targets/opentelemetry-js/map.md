# Target Map: OpenTelemetry JavaScript

Repository: https://github.com/open-telemetry/opentelemetry-js

Related contrib repository: https://github.com/open-telemetry/opentelemetry-js-contrib

## Why it is here

Observability is a cross-cutting need for agent systems, hosted runtimes, browser tools, and automation. OpenTelemetry work can turn local instrumentation problems into standards-aware, reusable results.

## Areas worth understanding

- context propagation across async boundaries;
- traces around tool and model calls;
- semantic conventions for emerging AI workloads;
- browser and Worker runtime support;
- exporter failure and shutdown behaviour;
- instrumentation correctness under retries and cancellation;
- test utilities and conformance fixtures.

## Evidence we can produce

- deterministic span trees;
- propagation matrices;
- runtime-specific reproductions;
- shutdown and retry fault injection;
- semantic-convention comparisons;
- instrumentation compatibility tests.

## Entry standard

Determine whether a change belongs in the core API/SDK, contrib instrumentation, semantic conventions, or an application package. Standards-facing proposals require prior discussion and precise terminology.

## Stop conditions

- the desired telemetry is application-specific;
- the proposal conflicts with an active specification decision;
- the reproduction cannot distinguish library behaviour from runtime behaviour;
- the work becomes metric churn without a concrete consumer need.
