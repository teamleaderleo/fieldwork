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

## Research selection guidance

Scout this target broadly and continuously. A crowded Vercel AI portfolio is a reason to raise the promotion bar, while exploration can keep sampling new code, recent changes, provider boundaries, feature interactions, and composition paths.

Prefer questions that reveal an interesting engineering contract, especially when several individually reasonable features compose into an unclear owner for identity, authority, state, retries, persistence, cancellation, or terminal outcome. Recent fixes are useful starting points because they expose assumptions that may still survive in neighboring modes or continuation paths.

Treat a technically real defect as a research result before treating it as a delivery candidate. Promote when the finding has a compelling engineering story that a human reviewer can defend: a surprising interaction, a meaningful invariant, a concrete consequence, a clear owning boundary, and evidence that distinguishes the proposed interpretation from plausible alternatives.

Strong candidates often answer questions such as:

- Which identity survives UI state, model history, provider storage, reconnect, and replay?
- Which component owns cancellation or retry authority after work fans out, suspends, resumes, or crosses a provider boundary?
- Does a generic SDK option retain its meaning when translated through a provider-specific capability or server-side tool?
- When two persistence modes coexist, which artifacts are replayed, referenced, reconstructed, or deliberately omitted?
- Does an adapter preserve the caller's intent when defaults, approvals, runtime capabilities, or provider-side state interact?

Let low-consequence correctness findings, obvious local omissions, and mechanically valid cleanup remain findings or negative results unless the deeper interaction earns further work. Merge velocity, repository popularity, and easy patch size are useful context rather than promotion criteria.

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
