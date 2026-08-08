# Deep dive — <unit and title>

## In simple words

<Explain the mechanism, defect or missing capability, selected correction, and current evidence.>

## Governing invariant

> <One precise rule the target should preserve.>

## Current behavior

Describe the baseline behavior without assuming the proposed repair is correct.

- entrypoint:
- state owner:
- caller-visible result:
- side effects:
- cleanup owner:
- persistence or publication boundary:
- relevant concurrency, cancellation, retry, or failure ordering:

## Source map

| Area | Exact path and symbol | Responsibility | Relevant tests |
| --- | --- | --- | --- |
| `<area>` | `<commit-pinned link>` | `<owner>` | `<commit-pinned links>` |

## Reproduction or characterization

### Setup

- exact upstream revision:
- environment:
- fixture or input:
- command:

### Baseline result

<Observed result, including negative controls.>

### Candidate result

<Observed result after the selected change, when executed.>

## Failure model

Trace the exact sequence that creates the behavior:

1. `<event>`
2. `<state transition>`
3. `<failure or race>`
4. `<incorrect or missing result>`

Distinguish confirmed steps from inference.

## Consequence and claim boundary

### Established

- `<claim and evidence>`

### Inferred

- `<bounded inference>`

### Unknown or unmeasured

- `<frequency, platform, deployment, scale, compatibility, or impact limit>`

## Selected implementation

Explain:

- which component now owns the invariant;
- why the change belongs at that boundary;
- new or changed states and transitions;
- error and cleanup precedence;
- why unrelated behavior stays unchanged;
- code links pinned to the candidate head.

## Compatibility analysis

- public API:
- source compatibility:
- binary or wire compatibility:
- persistence or format compatibility:
- platform behavior:
- performance and allocation:
- cancellation, retry, and recovery:
- generated output:
- migration or rollback:

Mark fields `not applicable` rather than omitting them.

## Adversarial and edge controls

- `<re-entry>`
- `<concurrency>`
- `<cancellation or interruption>`
- `<failure before ownership transfer>`
- `<failure after partial effect>`
- `<cleanup failure>`
- `<same-key or same-resource collision>`
- `<unrelated-resource isolation>`
- `<platform or runtime boundary>`

## Review risks

Name the strongest plausible objections to the selected change and the exact control or source argument addressing each one.

## Reversing evidence

The conclusion should be reopened if:

- `<specific test or source fact>`
- `<specific maintainer contract or compatibility requirement>`
- `<current-main replacement or equivalent upstream work>`

## Adjacent work excluded

List nearby questions that are intentionally separate so the unit remains reviewable.
