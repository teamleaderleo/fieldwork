# Target Map: Vercel AI SDK

Repository: https://github.com/vercel/ai

## Why it is here

The SDK sits directly in the path of model providers, streaming, tool calls, structured output, agent loops, and generative interfaces. Problems discovered while building agent-facing products may transfer naturally.

## Areas worth understanding

- provider abstraction and compatibility;
- streaming event semantics;
- tool-call lifecycle and retries;
- structured-output validation;
- message conversion and persistence;
- framework adapters and server runtimes;
- tests that compare provider-specific behaviour.

## Evidence we can produce

- provider-independent reproductions;
- captured synthetic event streams;
- deterministic tool-call fixtures;
- compatibility matrices;
- TypeScript type regressions;
- reconnect, abort, and partial-failure tests.

## Entry standard

Before proposing code, identify whether the behaviour belongs in the core SDK, a provider package, an example, or application code. Confirm the expected semantics with documentation, tests, or maintainer direction.

## Stop conditions

- provider behaviour is undocumented and cannot be tested safely;
- the change merely hides an application-level error;
- the proposal requires a broad API redesign without prior discussion;
- the issue does not affect anything we are building or researching.
