# Target Map: Vercel AI SDK

Repository: https://github.com/vercel/ai

## Why it is here

The SDK sits directly in the path of model providers, streaming, tool calls, structured output, agent loops, and generative interfaces. Problems discovered while building agent-facing products may transfer naturally.

## Review entry points

- [Reliability review walkthrough](./reliability-review-walkthrough.md)
- [WorkflowAgent current-main check](./workflow-agent-current-main-check.md)
- [Target materials index](./README.md)

## Areas worth understanding

- provider abstraction and compatibility;
- streaming event semantics and reader ownership;
- tool-call lifecycle, approval, cancellation, and retries;
- structured-output validation and overlapping request generations;
- message conversion and persistence;
- framework adapters and server runtimes;
- durable reconnect, polling, and deadline authority;
- tests that compare provider-specific behaviour.

## Research selection

Vercel AI has enough providers, adapters, harnesses, and optional capabilities to support effectively unlimited compatibility work. Integration-specific behaviour is a legitimate entry point, but the existence of a discrepancy is not by itself a reason to keep digging.

Prefer investigations where the concrete case exposes clearly erroneous SDK behaviour, a meaningful user consequence, or an engineering question that transfers beyond one provider. Strong examples include state ownership, persistence and replay, parent/child isolation, cancellation, retries, resource identity, error settlement, concurrency, and public API semantics.

Provider-specific work can still qualify on its own when the consequence is substantial: data is lost, requests are sent somewhere materially different from the configured destination, durable history becomes unusable, a documented capability is represented incorrectly, or a provider event can corrupt SDK state. A named integration does not make a problem uninteresting; it simply should not be the only reason the problem was selected.

Deprioritize narrow completeness work whose main result is that one provider option, obscure combination, or small capability is not forwarded exactly as the provider permits. Do not recursively inspect neighboring options just because one parity gap was found.

A useful selection test is to remove the vendor names from the problem statement. If the remaining technical question is still interesting, the investigation is usually a strong fit. If it is not, require a concrete user consequence before promoting the work. When stronger evidence reduces a candidate to minor provider parity, record the result and stop rather than manufacturing a campaign around it.

## Evidence we can produce

- provider-independent reproductions;
- captured synthetic event streams;
- deterministic tool-call fixtures;
- compatibility matrices;
- TypeScript type regressions;
- reconnect, abort, and partial-failure tests;
- reader lock, unhandled-rejection, and stale-generation discriminators.

## Entry standard

Before proposing code, identify whether the behaviour belongs in the core SDK, a provider package, an example, the Workflow runtime, or application code. Confirm the expected semantics with documentation, tests, protocol specifications, implementation history, or maintainer direction.

Every delivery candidate should identify one owner for terminal settlement, cancellation, and resource release. Passing value assertions alone do not prove terminal ownership.

## Stop conditions

- provider behaviour is undocumented and cannot be tested safely;
- the change merely hides an application-level error;
- the proposal requires a broad API redesign without prior discussion;
- the behavior depends on an external runtime capability and cannot be fixed honestly in the SDK alone;
- the issue does not affect anything we are building or researching.
