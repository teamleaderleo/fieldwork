# Upstream Packet: Keep Claude built-in permission kinds aligned with bridge policy

Campaign: #814  
Target: Vercel AI SDK  
State: `candidate — mismatch executed; shared-kind repair awaiting exact candidate gates`

> This packet is preparation-only. A human must perform any Vercel upstream interaction manually outside Fieldwork automation.

## In simple words

The Claude Code harness now has two owners for one permission fact.

The public built-in catalog says which native tools are `readonly`, `edit`, or `bash`. The sandbox bridge keeps a separate native-name table to generate approval rules and decide whether unresolved tool calls enter host approval.

The latest public catalog expansion updated the first owner but left the second behind. Exact target tests proved the difference: existing Bash and Read behave correctly, new PowerShell misses its bash-class ask rule under `allow-edits`, and new CronList is denied under `allow-reads` even though the public catalog marks it readonly.

The proposed repair moves the bridge authority map into one small shared local module, fills the current native aliases/classes, and adds a mechanical test that derives every explicit public `toolUseKind` and compares bridge callback/rule behavior.

Vercel's current contribution guide encourages issue/reproduction-first reports. The executed mismatch can therefore be reviewed independently of the repair candidate while its final build/package gates wait for hosted-runner capacity.

## Proposal

I propose giving Claude native permission kind one enforceable bridge authority source and making the public catalog/bridge relationship executable in tests.

```text
public built-in catalog
       │ explicit toolUseKind
       ▼
mechanical parity test ◀──── shared native-kind map
                              │
                              ├── generated permissions.ask
                              └── canUseTool approval decision
```

A future catalog addition with an explicit permission kind should fail target validation if bridge authority disagrees.

## Current and proposed behavior

Current public metadata:

```text
Bash       -> bash
PowerShell -> bash
Read       -> readonly
CronList   -> readonly
```

Current bridge behavior:

```text
known Bash       -> bash
unknown PowerShell -> edit fallback
known Read       -> readonly
unknown CronList -> edit fallback
```

Under the bridge policy:

```text
allow-edits:
  bash -> approval
  edit -> allow

allow-reads:
  readonly -> allow
  edit/bash -> approval
```

Preferred candidate:

```text
Bash       -> shared bash
PowerShell -> shared bash
Read       -> shared readonly
CronList   -> shared readonly
...current aliases/classes retained explicitly
```

## Consequence

Exact package execution proved both directions of drift:

- PowerShell lacks the generated bash-class ask rule its public metadata requires;
- CronList enters approval where its public readonly classification says it should proceed.

The readonly side is a correctness/developer-experience regression.

The PowerShell side is authority-relevant. Anthropic's Agent SDK permission model evaluates permission mode and then routes unresolved calls through `canUseTool`. Accept-edits auto-approves bounded edit operations; arbitrary unresolved PowerShell commands can still reach the Vercel callback. A public bash-class tool falling back to edit can therefore change the integration's approval decision.

No destructive command was executed in this research.

## Reproduction

```text
source revision: cfc587bdfd8fd1996dd902edd14143be6e034baf
environment: Ubuntu 24.04 / Node 22.23.1
owned characterization: teamleaderleo/ai branch research/claude-code-new-tool-permissions-cfc587
execution run: 31425591736
job: 93576403770
```

Executed result:

```text
@ai-sdk/harness-claude-code type-check: PASS
ordinary/package tests: 82 PASS
Fieldwork controls: 2 FAIL
```

Negative controls:

```text
Bash + allow-edits: PASS
  generated ask contains Bash(*)
  callback enters approval

Read + allow-reads: PASS
  callback returns allow
  no approval request
```

Discriminators:

```text
PowerShell + allow-edits: FAIL
  generated ask rules exactly [ 'Bash(*)', 'Monitor(*)' ]
  PowerShell(*) absent

CronList + allow-reads: FAIL
  expected allow
  observed deny
```

Deterministic: yes for the mocked Agent SDK callback boundary.

## Cause

`packages/harness-claude-code/src/claude-code-harness.ts` owns the public built-in catalog and explicit `toolUseKind` metadata.

`packages/harness-claude-code/src/bridge/index.ts` independently owns `NATIVE_TOOL_KINDS` for bridge authority. Unknown native names default to `edit`.

The catalog expansion added many explicit kinds without updating the second map. New edit entries happen to align with the edit fallback; new readonly and bash entries do not.

## Invariant

```text
Every public Claude built-in with an explicit permission kind must produce
matching bridge approval behavior and matching generated ask rules.
```

## Scope

Included:

- Claude Code harness built-in permission classification;
- generated `permissions.ask` rules;
- bridge `canUseTool` approval policy;
- current aliases/native names;
- mechanical parity regression.

Excluded:

- changing active/inactive built-in filtering;
- changing transport, event translation, approval messaging, or query lifecycle;
- claiming execution of a live harmful PowerShell command;
- changing tools that intentionally have no explicit public permission kind without separate evidence.

## Candidate implementation

```text
owned fork: teamleaderleo/ai
candidate PR: #70
base revision: cfc587bdfd8fd1996dd902edd14143be6e034baf
candidate head: 133937a1e09618a5de2e2b14207560477092120e
changed components:
  packages/harness-claude-code/src/native-tool-kinds.ts
  packages/harness-claude-code/src/bridge/index.ts
  packages/harness-claude-code/src/bridge/native-tool-kind-parity.fieldwork.test.ts
```

Production bridge movement is deliberately small: import the shared local map and remove the old inline duplicate table. The package's tsup configuration has separate host and sandbox bridge entries and bundles local source imports, so the shared module adds no sandbox runtime package dependency.

Exact candidate build/full-package verification remains queued. Do not describe #70 as executed or ready yet.

## Verification plan

Candidate carrier #71 is configured to run:

```text
git diff --check
@ai-sdk/harness-claude-code type-check
host + sandbox bridge build
full Node package tests
```

The parity matrix itself derives all explicitly classified public built-ins and checks:

- allow-reads callback semantics;
- allow-edits callback semantics;
- bash ask rules under allow-edits;
- edit/bash ask rules under allow-reads.

Existing filtering behavior was separately reviewed as a negative result: exact native-name fallback plus Agent SDK `tools` / `disallowedTools` semantics do not expose the same new-tool bypass.

## Tradeoffs and alternatives

### Copy today's missing names into the old bridge table

This fixes the immediate snapshot but preserves the exact duplication that caused the defect. It is a weak long-term repair.

### Broadly rewrite every public catalog declaration to import the shared map directly

This would create one literal value owner everywhere, but it touches many tool declarations and increases review cost.

### Selected candidate direction

Keep one small shared bridge authority map and make public agreement mechanical through a complete parity test. This keeps the production diff narrow while making future explicit-kind drift executable.

Known limit: public tools with no explicit `toolUseKind` still rely on bridge classification/fallback and require separate semantic judgment.

## Recovery

The repair has no persisted-state migration. Reverting the shared-map import restores the prior permission table behavior. The parity test can remain useful independently as a guard.

## Upstream context

A refreshed issue/PR search found no directly matching active Vercel AI work for PowerShell/new-built-in bridge permission parity. The catalog pull request that introduced the new tools was reviewed for typed-catalog/runtime alignment; its discussion did not cover the separate bridge permission map.

## AI assistance

AI systems performed source comparison, target-test preparation, contract research, candidate design, owned-fork implementation, and evidence synthesis. The target mismatch is backed by an exact package execution receipt. The production candidate still requires exact build/package execution and human source review before any public use.

The current Vercel contribution guide and PR template contain no dedicated AI-assistance disclosure field found in this review. A human submitter should recheck policy at submission time.

## Human accountability

```text
reproduced problem:           yes
reviewed every final change:  pending human review
can defend implementation:    pending human review
ran final candidate gates:    pending
checked current policy:       yes, 2026-08-11
automated upstream write:     no
```

## Maintainer decision requested

Should Claude built-in permission kind have one bridge-owned source plus a mechanical public-catalog parity gate, so new typed catalog entries cannot silently change approval behavior when the bridge map lags behind?
