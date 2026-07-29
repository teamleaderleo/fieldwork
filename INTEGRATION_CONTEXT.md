# Integration Context

An isolated experiment answers whether a mechanism behaves a certain way under declared conditions. It does not, by itself, establish where the mechanism is used, whether the tested boundary appears in a larger system, or what consequence follows when it fails.

Fieldwork records that wider context separately so experiments can remain small without encouraging oversized claims.

## Claim scopes

Use the narrowest scope supported by the evidence:

1. **Mechanism** — one function, parser, protocol rule, or local state transition.
2. **Interface** — behaviour across one declared boundary between components.
3. **Integration** — behaviour inside a realistic multi-component workflow.
4. **Operational** — consequences under deployment, load, retries, observability, recovery, or partial failure.
5. **Ecosystem** — adoption, interoperability, governance, or compatibility across projects.

A mechanism-level experiment may motivate broader research. It may not silently claim integration, operational, or ecosystem consequences.

## When context is required

Create an integration-context record when a report asserts any of the following:

- the behaviour is useful in a larger application;
- a failure could duplicate, lose, corrupt, delay, leak, or misattribute real work;
- an upstream project should change because downstream users depend on the behaviour;
- a toy reproduction represents a production or interoperability scenario;
- an experiment should become a campaign, contribution, recommendation, or reusable benchmark;
- several projects or components participate in the same workflow.

A disposable mechanism check does not need this record.

## Context dossier

Use `templates/integration-context.md`. A useful dossier records:

- **system role** — where the tested mechanism sits;
- **actors and workflow** — caller, intermediary, callee, storage, operator, and user;
- **contract boundaries** — inputs, outputs, state, side effects, retries, ordering, and ownership;
- **failure propagation** — what downstream observation changes when the mechanism fails;
- **operational visibility** — traces, logs, metrics, audit records, or user-visible symptoms;
- **deployment assumptions** — topology, version boundaries, concurrency, persistence, and recovery;
- **real-world evidence** — standards, official documentation, source code, public incidents, usage examples, or direct observations;
- **open assumptions** — plausible context that remains unverified;
- **representative scenarios** — small examples that connect the isolated test to the larger workflow.

## Evidence labels

Label each consequential statement:

- **Normative** — required or defined by a standard or specification.
- **Documented** — stated by an official project or product source.
- **Observed** — reproduced or measured directly by Fieldwork.
- **Inferred** — conclusion drawn from documented or observed evidence.
- **Illustrative** — deliberately hypothetical example used to explain possible use.
- **Unknown** — unresolved and not safe to assume.

Do not present illustrative architecture as proof that a target project uses that architecture.

## Research fan-out

A coordinator may split broader context into independent lanes or probes:

1. **Mechanism lane** — source path, local behaviour, and minimal reproduction.
2. **Usage lane** — actual callers, integrations, examples, dependants, and deployment patterns.
3. **Contract lane** — standards, protocol rules, API guarantees, and compatibility promises.
4. **Operations lane** — retries, timeouts, concurrency, observability, rollback, and recovery.
5. **Adversarial lane** — malformed input, partial failure, abuse, resource exhaustion, and security consequences.
6. **Synthesis lane** — reconcile which wider claims are demonstrated, inferred, illustrative, or unsupported.

Do not fan out every small experiment. Use these lanes when context is important enough that one worker would otherwise conflate several kinds of evidence.

## Citation record

For sources supporting broader claims, retain:

- title and publisher;
- stable URL;
- version, revision, or publication date;
- retrieval date;
- exact claim supported;
- evidence label;
- relevant section, heading, or path;
- limitations or volatility.

External GitHub issue, pull-request, discussion, and commit references remain wrapped under `REFERENCE_POLICY.md`.

Prefer primary sources: standards, official documentation, source at an exact revision, maintainer policy, and directly reproducible behaviour. Secondary commentary can discover leads but should not carry a consequential claim when a primary source exists.

## Context ladder for experiments

A strong retained experiment may progress through this ladder:

```text
isolated mechanism
→ representative boundary
→ realistic workflow
→ failure propagation
→ observable consequence
→ integration decision
```

The experiment need not implement the full application. It should include the smallest model that preserves the property being claimed.

## Promotion gate

Before promoting an experiment into an upstream packet or broad recommendation, ask:

- Is the claimed usage documented or merely plausible?
- Does the toy model preserve the important state and failure boundaries?
- Could another architecture produce a different outcome?
- Is the consequence visible to users, operators, or dependent components?
- What evidence would falsify the integration claim?
- Have version, deployment, and compatibility assumptions been recorded?

If those questions remain unanswered, promote the mechanism finding while keeping the wider claim explicitly provisional.

## Canonical worked context

`contexts/patterns/retry-idempotency.md` and `playgrounds/examples/retry-idempotency/` demonstrate the intended relationship:

- a tiny deterministic simulator validates the local retry behaviour;
- a context dossier explains why the same boundary appears in order creation, resource provisioning, job submission, and similar side-effecting workflows;
- standards and official guidance support the distinction between safe retries and duplicate effects;
- the example does not claim to reproduce any specific upstream implementation.