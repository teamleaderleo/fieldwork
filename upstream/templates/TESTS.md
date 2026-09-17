# Tests and receipts — <unit and title>

## In simple words

<State what has actually run, what it proves, and the largest important gap.>

## Identity

- Exact upstream base:
- Exact candidate head:
- Exact execution carrier head, if any:
- Test date:
- Environment and platform:

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| `<claim>` | `<class>` | `<link or command>` | `<pass/fail/prepared>` | `<limit>` |

## Baseline characterization

### Command or workflow

```text
<exact command>
```

### Assertions

- `<assertion>`

### Result

- status:
- test count:
- workflow and job:
- artifact or receipt:
- observed behavior:

## Candidate-focused tests

Repeat this block for each distinct test group.

### <group name>

- Exact source head:
- Command or workflow:
- Tests and assertions:
- Result:
- Failure classification, if red:
- Coverage limit:

## Ordinary repository gates

| Gate | Exact command or workflow | Result | Notes |
| --- | --- | --- | --- |
| format |  |  |  |
| lint |  |  |  |
| typecheck or compile |  |  |  |
| focused package tests |  |  |  |
| complete target-declared suite |  |  |  |
| build or generated output |  |  |  |
| platform matrix |  |  |  |

Use `not run` or `not applicable`; never leave an ambiguous blank in the completed packet.

## Reversing controls

- `<control that fails on baseline and passes on candidate>`
- `<compatibility control that passes on both>`
- `<hostile or failure-path control>`
- `<unrelated-resource isolation control>`

## Soak, leak, and cleanup controls

- iterations:
- resources observed:
- timers/tasks/processes/files/listeners before and after:
- cancellation or interruption behavior:
- immediate rerun result:

## Setup and harness failures

| Attempt | Failure | Classification | Product claim affected? | Repair or stop |
| --- | --- | --- | --- | --- |
| `<link>` | `<failure>` | `setup | dependency | runner | fixture | packaging | product` | `<yes/no>` | `<action>` |

## Checks prepared but not executed

- `<test link>` — `<why not executed and what remains>`

## Platform and integration gaps

- `<platform or environment>`
- `<provider, proxy, browser, filesystem, process, or database path>`

## Cleanup receipt

- Temporary workflows removed from canonical source head: `yes | no`
- Publisher or execution-only files removed: `yes | no`
- Generated residue checked: `yes | no`
- Immediate rerun performed: `yes | no`
- Remaining temporary branches or PRs:

## Current test judgment

`ACCEPT | REPAIR | HOLD | EXECUTE | REJECT`

Reason: `<one paragraph>`

Clearing condition: `<one exact next gate>`
