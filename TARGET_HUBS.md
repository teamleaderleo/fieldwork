# Target Hubs

## In simple words

Each active repository, project, protocol, or system gets one stable Fieldwork issue that explains what it is, why we are investigating it, and where all related work can be found. Every related issue carries the same `target:*` label.

## Label model

### Target labels

Use:

```text
target:<stable-slug>
```

The target is the system being studied or potentially changed. It may be an external repository, an owned repository, a protocol, or a cross-project system.

Examples:

- `target:vercel-ai`
- `target:workers-sdk`
- `target:opentelemetry-js`
- `target:fieldwork`

Create target labels when a target becomes active or receives a hub. Do not pre-create a label for every registry entry.

### Testbed labels

Use:

```text
testbed:<stable-slug>
```

A testbed is an owned repository used to exercise another target in a realistic integration. For example, an issue may carry both `target:vercel-ai` and `testbed:stensibly`.

Create testbed labels lazily when a real trial begins. Do not label a repository as a testbed merely because it could be one.

### Multiple targets

An issue may carry several `target:*` labels when the question genuinely spans several systems. The issue body must identify one primary target or explain why no single primary target exists.

## Golden target issue

A target hub is a long-lived `type:target` issue with `state:observed` unless active work changes its state.

It should contain:

- an `In simple words` block;
- repository or project root;
- target map;
- target label;
- change thesis;
- important code and integration surfaces;
- current experiments and campaigns;
- owned testbeds used;
- open and historical label searches;
- upstream-contact boundary;
- a short current-direction section.

The hub is an index and shared orientation point. It is not a giant task list and should not duplicate every child report.

## Linking

Every finding, lead, campaign, lane, decision, synthesis, or batch assignment about a target should:

1. carry the target label;
2. name the target hub in the body or durable report;
3. record child dependencies through Fieldwork links;
4. keep external issue and pull-request references quiet under `REFERENCE_POLICY.md`.

The hub discovers related work through label searches, so agents do not need to maintain a fragile hand-written list of every issue.

## Pinning

Do not pin every target hub. GitHub pinning is a scarce top-level navigation surface and becomes useless when every target is treated as special.

Prefer pinning at most:

- the live Fieldwork workboard;
- a target index or operating entrypoint;
- one temporarily important programme.

Target hubs remain easy to discover through `type:target`, `target:*`, `targets/hubs.yml`, and the repository README.

## Lifecycle

Create a hub when:

- a target is mapped and likely to receive recurring work;
- several issues or experiments need one shared orientation point;
- an owned repository becomes a recurring research subject;
- a cross-project protocol needs stable context.

Keep the hub open while the target remains relevant. Mark it dormant when there is no active work and its map is stale. Close it only when the target is intentionally retired from Fieldwork.

## Existing hubs

The initial mapped targets are recorded in `targets/hubs.yml`. Future hubs should be added there when created.