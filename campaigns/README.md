# Campaigns

A campaign is one bounded parent investigation. Parallel work lives in lane directories and lane issues.

## Required files

```text
campaigns/<campaign-id>-<slug>/
├── STATUS.md
├── question.md
├── lanes/
│   └── <lane-id>-<slug>/
│       ├── report.md
│       └── artifacts/
├── synthesis.md
├── decision.md
└── closeout.md
```

Create files as they become necessary; empty placeholders are optional.

## Ownership

- Coordinator: `STATUS.md`, synthesis, decision, and closeout.
- Lane owner: that lane's report and artifacts.
- Human decision-maker: explicit approval for upstream contact and consequential scope changes.

## Identifiers

Campaign identifiers are stable and zero-padded. Lane identifiers are stable within the campaign. Issue numbers may be recorded, but directory identities do not change when issues move or are recreated.

## Durable status

`STATUS.md` is a bounded snapshot, not a replacement for the issue queue. It records the campaign state, coordinator, parent issue, active lane identifiers, target revisions, and next decision.
