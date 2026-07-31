# Label Taxonomy

The label set is configured in this repository. Labels are a query surface; issue bodies and durable files still carry the authoritative details.

## Type labels

Each live work item should have exactly one primary type:

- `type:programme`
- `type:target`
- `type:batch`
- `type:finding`
- `type:lead`
- `type:campaign`
- `type:lane`
- `type:decision`
- `type:synthesis`
- `type:meta`

A `type:programme` issue is a long-lived research direction spanning several targets. A `type:target` issue is a long-lived hub and orientation record. Neither is an ordinary task backlog.

## Issue-state labels

Each live work item should have exactly one primary `state:*` label:

- `state:observed`
- `state:triage`
- `state:ready`
- `state:claimed`
- `state:investigating`
- `state:blocked`
- `state:ready-for-synthesis`
- `state:synthesising`
- `state:candidate`
- `state:seeking-direction`
- `state:submitted`
- `state:merged`
- `state:declined`
- `state:withdrawn`
- `state:negative-result`
- `state:dormant`
- `state:complete`

Replace the previous issue-state label during transitions. Do not accumulate state history as labels.

The issue body must mirror the live label exactly:

```text
Issue state: `state:<label>`
```

### Issue state is not finding state

`state:*` labels describe GitHub coordination: whether an issue is ready, claimed, being investigated, blocked, submitted, or complete.

Canonical findings use the separate technical transition vocabulary in `FINDINGS.md`:

```text
research-active
comparative-evaluation-active
review-ready
design-decision-ready
delivery-gate-ready
land-ready
stopped
closed
```

When an issue has a canonical finding, its body also carries:

```text
Finding state: `<finding transition state>`
```

There is no one-to-one mapping. For example, an issue may be `state:claimed` while its finding is `comparative-evaluation-active`. Validators and reviewers must compare `Issue state:` to the live label and version `Finding state:` against the canonical finding separately.

Use `Finding state: not applicable` when no canonical finding exists.

## Programme labels

Every issue belonging to a long-lived research direction should carry:

```text
programme:<stable-slug>
```

Examples:

- `programme:sdk-integration-lifecycle`
- `programme:agent-cli-execution`
- `programme:web-tooling-runtime-correctness`
- `programme:data-durable-workflows`

Programme labels group several targets and survive as scout lanes branch into findings and campaigns. Create them only for active programmes recorded in `programmes/registry.yml`.

## Target labels

Every issue about a recurring repository, project, protocol, or system should carry:

```text
target:<stable-slug>
```

Examples:

- `target:vercel-ai`
- `target:workers-sdk`
- `target:opentelemetry-js`
- `target:gemini-cli`
- `target:biome`
- `target:fieldwork`

The target is the system being studied or potentially changed. Create target labels when work becomes active; do not pre-create labels for every inbox entry.

Related work should share the target label and link to the stable hub described in `TARGET_HUBS.md`.

## Testbed labels

When an owned repository is used to exercise another target in a realistic integration, add:

```text
testbed:<stable-slug>
```

Create a testbed label only after a real trial begins and a Fieldwork issue or retained experiment records the target version, testbed revision, scenario, baseline, observed result, limitations, and rollback. Do not pre-create testbed labels from the candidate registry. If the owned repository itself is the subject, use `target:<slug>` instead.

## Coordination labels

These may accompany a type, issue state, programme, target, and testbed:

- `needs:human-decision`
- `needs:materialization`
- `needs:upstream-direction`
- `parallel-safe`
- `policy:reference-violation`

The interaction-reference workflow manages `policy:reference-violation` and removes it after correction.

## Common searches

```text
is:open label:"type:programme"
is:open label:"programme:sdk-integration-lifecycle"
is:open label:"type:target"
is:open label:"target:vercel-ai"
is:open label:"target:vercel-ai" label:"state:ready"
is:open label:"testbed:stensibly"
is:open label:"type:lane" label:"state:ready"
is:open label:"state:blocked"
is:open label:"state:ready-for-synthesis"
is:open label:"needs:human-decision"
is:open label:"policy:reference-violation"
is:open label:"type:batch"
```

## Display polish

The connector created the labels with GitHub's neutral default colour. Colours and descriptions are optional and can be adjusted manually later without changing the protocol.
