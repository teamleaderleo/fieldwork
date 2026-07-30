# Adaptive Coordination

## In simple words

Coordinate only enough to prevent duplicated work, unclear responsibility, lost evidence, and unsafe external effects. The purpose of the system is to help useful work continue across people, agents, chats, and branches. The process should adapt when evidence reveals a better question or a better way to divide the work.

This document explains how to interpret the more detailed Fieldwork protocols. It is a working agreement, not another ceremony layer.

## The coordination kernel

Substantial work needs only a few durable facts:

- the question or outcome being pursued;
- one current responsible owner;
- the relevant programme, target, issue, branch, or record;
- the evidence boundary and current uncertainty;
- the next useful action;
- the external-action authority boundary.

Everything else should earn its cost by preventing a real failure mode.

## Issues dispatch; repository records explain

Use an issue for short coordination:

- what is worth checking;
- why it matters;
- who currently owns it;
- blockers, transfers, and next actions;
- links to durable results.

Put source maps, experiments, commands, results, reasoning, and evidence limits in repository records and artifacts. A pull request is the review surface for a concrete change or coherent result set.

A small dispatch issue can begin with:

```text
Question:
Why this is worth checking:
Useful starting points:
Known boundaries:
Owner:
```

Add more structure only when the work needs it.

## Ownership without permanent roles

Use a GitHub identity for a human and a short stable callsign for an agent or temporary worker. Attribution should make continuation and review possible; it does not create permanent employee-style roles, exclusive expertise, or authority.

One owner is responsible for moving a piece of work. That owner may consult others, split off independent questions, hand over responsibility, or close with a negative result. Record transfers and meaningful scope changes rather than forcing the original assignment to remain artificially true.

## Give an appetite, not a script

A scout or investigation should have a bounded appetite and a distinguishing question. The worker should be free to choose the useful source reading, fixtures, experiments, and comparisons within that boundary.

A broad scout may discover:

- a focused investigation;
- several independent branches;
- a reusable fixture or context map;
- an already-solved or unsupported premise;
- a valuable negative result;
- a reason to stop.

That is adaptation, not workflow failure.

## Review according to risk and knowledge

Choose review depth from consequences, uncertainty, reversibility, and the value of another perspective.

- Tiny probes and clear negative results may receive coordinator acceptance or light review.
- Bounded reversible repository work may use careful self-review.
- Security findings, destructive operations, broad ecosystem claims, upstream packets, and consequential changes should receive stronger independent or specialist review.

Do not assign fixed reviewer rings merely to manufacture independence. Select the reviewer who can most usefully challenge the evidence and assumptions when the work is ready.

## Let records mature

Start records early enough to preserve thought and evidence. They may remain rough while the question is still moving. Improve, split, promote, synthesize, abandon, or supersede them as the work becomes clearer.

No document must pretend to be final before the evidence is final. No negative result needs to be dressed up as a defect. Preserve failed hypotheses and useful dead ends.

## Keep shared state small

Workers should normally edit their owned result or branch. Shared registries, status files, and syntheses should change when coordination needs a durable update, not after every local action.

Avoid both extremes:

- one giant shared document edited by everyone;
- one issue, branch, or pull request for every trivial observation.

Use the smallest durable unit that another worker can understand and continue.

## External GitHub references

Follow [`REFERENCE_POLICY.md`](REFERENCE_POLICY.md).

Direct links to third-party GitHub issues, pull requests, discussions, and commits can create backlinks, notifications, and implied participation in an upstream project. Quiet research uses `redirect.github.com` references by default. Direct references among controlled `teamleaderleo/*` repositories remain normal.

A direct third-party cross-reference belongs only to an explicitly authorized upstream interaction.

## Precedence and improvement

Detailed protocols remain useful checklists and safety boundaries, but they are not ends in themselves. Interpret them through this agreement:

> Preserve responsibility, evidence, recoverability, and external safety; adapt the rest to the work.

When a protocol causes repeated stalls, duplicate work, misleading ownership, unnecessary approval, or evidence loss, change the protocol and preserve the correction in Git history.
