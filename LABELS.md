# Label Taxonomy

The label set is configured in this repository. Labels are a query surface; issue bodies and durable files still carry the authoritative details.

## Type labels

Each live work item should have exactly one primary type:

- `type:batch`
- `type:finding`
- `type:lead`
- `type:campaign`
- `type:lane`
- `type:decision`
- `type:synthesis`
- `type:meta`

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

## Coordination labels

These may accompany a type and state:

- `needs:human-decision`
- `needs:materialization`
- `needs:upstream-direction`
- `parallel-safe`
- `policy:reference-violation`

The interaction-reference workflow manages `policy:reference-violation` and removes it after correction.

## Common searches

```text
is:open label:"type:lane" label:"state:ready"
is:open label:"state:blocked"
is:open label:"state:ready-for-synthesis"
is:open label:"needs:human-decision"
is:open label:"policy:reference-violation"
is:open label:"type:batch"
```

## Display polish

The connector created the labels with GitHub's neutral default colour. Colours and descriptions are optional and can be adjusted manually later without changing the protocol.
