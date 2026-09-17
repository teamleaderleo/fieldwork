## In simple words

Vercel AI head `cfc587bdfd8fd1996dd902edd14143be6e034baf` expanded the Claude Code harness's public built-in tool catalog. The public catalog assigns each new tool a `toolUseKind`, while the sandbox bridge keeps a second native-name-to-kind table that the same commit did not expand.

Exact target execution confirms the duplicate owners now disagree. Existing Bash and Read controls still behave correctly. New PowerShell has no generated bash-class ask rule under `allow-edits`; new CronList enters approval under `allow-reads` despite its public readonly kind.

Anthropic's documented permission order makes the PowerShell side authority-relevant: unresolved calls can reach `canUseTool` after permission-mode handling. The bounded repair belongs to campaign #814 and should remove or mechanically enforce parity between the two kind definitions.

## Exact source and evidence

Target: `vercel/ai`  
Exact public head: `cfc587bdfd8fd1996dd902edd14143be6e034baf`  
Introducing commit: same head, `fix(harness-claude-code): add missing Claude Code built-in tools`  
Fieldwork finding: #810  
Promoted campaign: #814  
Canonical characterization: `teamleaderleo/ai#60`  
Retired execution carrier: `teamleaderleo/ai#61`  
Run: `31425591736`  
Job: `93576403770`  
Runner: Ubuntu 24.04 / Node 22.23.1  
Evidence class: `target-executed`  
Upstream contact authorized: `false`

## Two owners of the same classification

Public catalog:

`packages/harness-claude-code/src/claude-code-harness.ts`

Bridge permission owner:

`packages/harness-claude-code/src/bridge/index.ts`

The bridge's native-kind table still contains the older catalog. Its effective local policy is:

```text
unknown native tool -> edit
allow-edits -> bash asks, edit allows
allow-reads -> edit/bash ask, readonly allows
```

The same table generates Claude permission `ask` rules.

## Drift inventory

New public `readonly` entries absent from the bridge map and therefore falling back to `edit`:

- `ListMcpResourcesTool`
- `ReadMcpResourceTool`
- `ReadMcpResourceDirTool`
- `RefreshMcpTools`
- `EnterPlanMode`
- `CronList`
- `LSP`
- `ReportFindings`
- `SendUserFile`
- `WaitForMcpServers`

New public `bash` entry absent from the bridge map:

- `PowerShell`

New public `edit` entries are also absent, but their fallback remains `edit`, so their effective kind aligns by accident.

## Exact target execution

The characterization exercises the actual bridge options Vercel passes to the pinned Agent SDK.

```text
@ai-sdk/harness-claude-code type-check: PASS
ordinary/package tests: 82 PASS
Fieldwork controls: 2 FAIL
```

Negative controls:

```text
Bash + allow-edits: PASS
  generated ask contains Bash(*)
  callback enters host approval path

Read + allow-reads: PASS
  callback returns allow
  no host approval request
```

Discriminators:

```text
PowerShell + allow-edits: FAIL
  generated ask rules were:
  [ 'Bash(*)', 'Monitor(*)' ]
  PowerShell(*) absent

CronList + allow-reads: FAIL
  expected callback behavior: allow
  observed callback behavior: deny
```

The package's remaining 82 tests pass beside these discriminators, separating the new catalog parity problem from broad harness failure.

## Contract context

Anthropic's Agent SDK permission documentation describes permission-mode processing before unresolved calls reach `canUseTool`. Claude Code's accept-edits mode auto-approves only bounded edit operations, including a narrow set of filesystem PowerShell cmdlets. Arbitrary PowerShell commands remain in ordinary permission handling.

This means the Vercel callback's `PowerShell -> edit` fallback can affect the final integration decision for unresolved PowerShell calls. No live harmful command was executed or claimed.

## Filtering negative result

The adjacent active/inactive built-in filtering path does not show the same bypass. Anthropic's `tools` list is an availability allowlist and `disallowedTools` removes exact native names. Vercel's filtering name map falls back to the new native name itself, so current new-tool filtering remains bounded even though the permission-kind table is stale.

## Duplicate / precedent result

A refreshed Vercel issue and pull-request search found no directly matching active work for PowerShell/new-built-in permission-kind parity.

The introducing catalog pull request was reviewed for alignment between the typed catalog and pinned Claude runtime. Its discussion did not address the separate bridge permission-kind table.

## Repair directions

### Shared kind definition

One native-name-to-kind definition is consumed by both public catalog metadata and bridge permission logic. This has the strongest ownership story, but module placement must remain safe for the bridge bundle.

### Mechanically enforced parity

Keep compact bridge runtime data while generating or validating it from the public catalog. This has a smaller runtime diff but must ensure every permission-relevant catalog entry participates automatically.

### Copy-only repair

Adding today's missing names to the bridge map repairs the current snapshot while preserving the exact drift mechanism. Retain only as a temporary comparison or combine it with a parity gate.

## Disposition

`PROMOTED -> #814`

Campaign #814 owns implementation comparison and exact candidate execution. The required controls include Bash/PowerShell, Read/CronList, all newly declared readonly entries, edit entries, allow-all, filtering, aliases, and a complete catalog parity check.

No third-party upstream mutation occurred.
