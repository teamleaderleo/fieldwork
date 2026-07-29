# Label Taxonomy

The label set is configured in this repository. Labels are a query surface; issue bodies and durable files still carry the authoritative details.

## Type labels

Each live work item should have exactly one primary type:

- `type:target`
- `type:batch`
- `type:finding`
- `type:lead`
- `type:campaign`
- `type:lane`
- `type:decision`
- `type:synthesis`
- `type:meta`

A `type:target` issue is a long-lived hub and orientation record. It is not an ordinary task backlog.

## State labels

Each live work item should have one primary state:

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

Replace the previous state label during transitions. Do not accumulate state history as labels.

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

Example:

```text
target:vercel-ai
testbed:stensibly
```

Create testbed labels only when a real trial begins. If the owned repository itself is the subject, use `target:<slug>` instead.

## Coordination labels

These may accompany a type, state, target, and testbed:

- `needs:human-decision`
- `needs:materialization`
- `needs:upstream-direction`
- `parallel-safe`
- `policy:reference-violation`

The interaction-reference workflow manages `policy:reference-violation` and removes it after correction.

## Common searches

```text
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