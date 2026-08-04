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
