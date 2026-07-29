# Integration Context: Retry and Idempotency

Context ID: `CTX-retry-idempotency`
Owner: Fieldwork
Date: 2026-07-29
Related experiment: `playgrounds/examples/retry-idempotency/`
Claim scope: integration and operational

## Context question

When a client cannot tell whether a side-effecting request completed, how can a retry avoid creating the effect twice, and what larger workflows depend on that property?

## System role

The mechanism sits between a caller that may retry and a service that owns a durable side effect.

```text
caller
→ unreliable response boundary
→ service operation
→ durable side effect
→ later user or operator observation
```

The ambiguous case occurs when the service commits the effect but the response is lost before the caller receives it. The caller observes failure even though the service changed state.

## Contract boundaries

Relevant properties include:

- whether the operation is safe to repeat;
- whether request identity survives retries;
- whether the service remembers the original outcome;
- whether the same identity can be reused with a different payload;
- how long deduplication state is retained;
- whether retries are bounded and delayed;
- whether the caller can reconcile state after uncertainty;
- whether traces and logs correlate all attempts to one logical operation.

## Representative scenarios

### Side-effecting API request after a lost response

Evidence label: **Normative and observed in the accompanying model**

1. The caller sends a request.
2. The service commits one durable effect.
3. The response is lost.
4. The caller retries because it cannot distinguish failure-before-commit from failure-after-commit.
5. A naive service creates a second effect.
6. An idempotent service recognizes the logical request and replays the original result.

RFC 9110 defines idempotent HTTP methods and explains why they can be repeated automatically after a communication failure. It also says clients should not automatically retry non-idempotent methods unless they know the request semantics are idempotent or can determine that the original request was not applied.

### Resource provisioning workflow

Evidence label: **Documented**

AWS describes resource-creation workflows where retrying after an uncertain response could create duplicate resources, and explains using caller-provided request identifiers to make retries safe.

### Orders, payments, job creation, and message handling

Evidence label: **Illustrative**

These are common classes of side-effecting workflows where duplicate execution could be harmful. This dossier does not claim that any particular product uses the exact mechanism in the playground. Project-specific claims require their own sources or observations.

## Failure propagation

A local retry mistake can become:

- duplicate durable records or resources;
- repeated billing, delivery, or execution;
- contradictory client and server state;
- manual reconciliation work;
- retry amplification during partial outages;
- misleading success and failure metrics;
- audit records that cannot identify one logical operation.

The actual consequence depends on the surrounding workflow. The playground demonstrates duplicate effects, not any particular financial, operational, or security outcome.

## Operational visibility

A realistic integration should make the logical operation observable across attempts:

- retain the operation or idempotency identifier;
- correlate retries in logs and traces;
- distinguish committed, replayed, rejected, and unknown outcomes;
- record retry count, delay, timeout, and final disposition;
- expose reconciliation state when the result remains uncertain.

The W3C Trace Context Recommendation defines standard HTTP headers for propagating tracing context across services. OpenTelemetry's HTTP semantic conventions define common telemetry names for HTTP spans, metrics, logs, and exceptions, though parts of those conventions remain under staged stability guidance.

## Deployment assumptions

The playground deliberately assumes:

- one logical service owns the side effect;
- deduplication state survives the retry;
- the same key and payload identify the same logical operation;
- the response can be lost after server processing;
- there is no concurrent race between two service instances;
- retention, eviction, replication, and crash recovery are omitted.

A production design must investigate those omitted boundaries.

## Real-world evidence

| Claim | Label | Source | Version/date | Retrieved | Section/path | Limitations |
|---|---|---|---|---|---|---|
| HTTP distinguishes idempotent methods and permits retry after some communication failures. | Normative | [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html) | June 2022 | 2026-07-29 | Section 9.2.2 | HTTP method semantics do not provide application-level deduplication for arbitrary side effects. |
| Retrying a non-idempotent operation requires knowledge that its semantics are idempotent or that it was not applied. | Normative | [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html) | June 2022 | 2026-07-29 | Section 9.2.2 | Client and intermediary behaviour still depends on implementation and policy. |
| Caller request identifiers can make resource-creation retries safe. | Documented | [Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) | AWS Builders' Library | 2026-07-29 | Main article | Describes AWS design experience, not a universal protocol. |
| Retries should be controlled, bounded, delayed, and used with idempotent operations. | Documented | [Control and limit retry calls](https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_mitigate_interaction_failure_limit_retries.html) | Current AWS Well-Architected guidance | 2026-07-29 | Implementation guidance | Vendor guidance; exact policy depends on workload. |
| Standard HTTP trace headers propagate request context across service boundaries. | Normative | [W3C Trace Context](https://www.w3.org/TR/trace-context/) | Recommendation, 23 November 2021 | 2026-07-29 | Abstract and header definitions | Trace correlation does not guarantee complete recording or business-operation identity. |
| Common HTTP telemetry names improve consistency across traces, metrics, logs, and exceptions. | Documented | [OpenTelemetry HTTP semantic conventions](https://opentelemetry.io/docs/specs/semconv/http/) | Retrieved 2026-07-29 | 2026-07-29 | HTTP conventions | Stability is mixed and migration guidance can change. |

## Mapping to tests

| Wider property | Experiment case | What it demonstrates | What it does not demonstrate |
|---|---|---|---|
| A repeated logical request can replay one committed outcome. | `safe-retry-after-lost-response` | One retained key and payload produce one effect across two attempts. | Persistence, distributed races, retention windows, or real HTTP behaviour. |
| A naive retry can duplicate a side effect. | `naive-retry-duplicates-effect` | The model commits twice after the caller loses the first response. | Frequency or severity in any actual service. |
| Reusing one key with different intent should not silently replay success. | `key-reuse-with-different-payload` | The model rejects a mismatched payload and keeps one effect. | The correct conflict status or API contract for a specific project. |
| Distinct logical operations remain distinct. | `distinct-operations-remain-distinct` | Different keys produce two effects. | Key generation quality, collision handling, or tenancy boundaries. |

## Competing architectures

Different systems can handle ambiguity through:

- naturally idempotent state replacement;
- compare-and-set or version preconditions;
- caller-provided idempotency keys;
- server-generated operation handles;
- durable queues with deduplicated consumers;
- transactional outbox or inbox records;
- read-after-failure reconciliation instead of automatic retry;
- workflow engines with durable step identity.

The playground models only caller-provided request identity with remembered outcomes.

## Open assumptions

- How long must request identity be retained?
- Which component owns retries?
- Can several retry layers amplify traffic?
- How are concurrent duplicate requests serialized?
- What happens after deduplication state is evicted?
- Does the operation span several services or databases?
- Which identifier should appear in tracing and audit records?
- How is an unknown final outcome reconciled?

## Decisions enabled

The example supports deciding whether a target investigation needs to test retry identity and duplicate effects. It does not justify a project-specific change until the target's actual workflow and contract are mapped.