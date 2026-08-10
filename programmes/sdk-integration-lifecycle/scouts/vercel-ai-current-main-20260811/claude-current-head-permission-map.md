## In simple words

Vercel AI current head `cfc587bdfd8fd1996dd902edd14143be6e034baf` expanded the Claude Code harness's public built-in tool catalog. The public catalog assigns each new tool a `toolUseKind`, while the sandbox bridge keeps a second native-name-to-kind table that was not expanded by the same commit.

The duplicate tables now disagree. Most disagreement makes read-only tools ask for permission unnecessarily in `allow-reads`. One entry is more consequential: public `PowerShell` is classified as `bash`, while the bridge has no `PowerShell` entry and defaults unknown native tools to `edit`. Under the bridge callback's `allow-edits` policy, known bash tools require approval and unknown/edit tools do not.

This file records source behavior and the exact target discriminator. It does not yet claim that the composed Claude runtime will execute arbitrary PowerShell without a prompt; the pinned Agent SDK / Claude Code permission layer may add an independent gate before or around Vercel's callback. That wider authority claim needs composed execution or equivalent primary-source evidence.

## Exact source

Target: `vercel/ai`  
Current public head: `cfc587bdfd8fd1996dd902edd14143be6e034baf`  
Introducing commit: same head, `fix(harness-claude-code): add missing Claude Code built-in tools`  
Canonical characterization: `teamleaderleo/ai#60`  
Execution carrier: `teamleaderleo/ai#61`  
Upstream contact authorized: `false`

## Two owners of the same classification

Public catalog:

`packages/harness-claude-code/src/claude-code-harness.ts`

The catalog now exposes these newly added tool kinds:

| Native/public name | Public `toolUseKind` | Present in bridge `NATIVE_TOOL_KINDS`? | Bridge callback fallback |
| --- | --- | --- | --- |
| `ListMcpResourcesTool` | readonly | no | edit |
| `ReadMcpResourceTool` | readonly | no | edit |
| `ReadMcpResourceDirTool` | readonly | no | edit |
| `RefreshMcpTools` | readonly | no | edit |
| `EnterPlanMode` | readonly | no | edit |
| `Artifact` | edit | no | edit |
| `CronCreate` | edit | no | edit |
| `CronDelete` | edit | no | edit |
| `CronList` | readonly | no | edit |
| `DesignSync` | edit | no | edit |
| `LSP` | readonly | no | edit |
| `PowerShell` | bash | no | edit |
| `PushNotification` | edit | no | edit |
| `RemoteTrigger` | edit | no | edit |
| `ReportFindings` | readonly | no | edit |
| `ScheduleWakeup` | edit | no | edit |
| `SendMessage` | edit | no | edit |
| `SendUserFile` | readonly | no | edit |
| `ShareOnboardingGuide` | edit | no | edit |
| `WaitForMcpServers` | readonly | no | edit |
| `Workflow` | edit | no | edit |

Bridge owner:

`packages/harness-claude-code/src/bridge/index.ts`

The bridge's `NATIVE_TOOL_KINDS` still ends with the older catalog. Its permission function uses:

```text
unknown native tool -> edit
allow-edits -> only bash requires approval
allow-reads -> edit or bash requires approval
```

The same stale table also generates Claude permission `ask` rules. A new name absent from the table cannot receive an explicit kind-derived ask rule there.

## Consequences by mode

### `allow-all`

No difference from this table drift: the harness bypasses permissions when there are no inactive tools.

### `allow-edits`

New `edit` tools match the fallback. New read-only tools also become allowed, which is permissive in the same direction as the mode.

`PowerShell` differs: public metadata says `bash`; the bridge callback sees an unknown name, falls back to `edit`, and therefore returns `allow` without asking its host approval path. Existing `Bash` remains classified as `bash` and requests approval.

This establishes a Vercel-local callback-policy mismatch. Whether the pinned Claude runtime independently prompts before execution remains a separate discriminator.

### `allow-reads`

Ten new public read-only tools fall back to `edit`, so the Vercel callback requests approval when the public catalog says the operation is read-only:

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

This is an ergonomics/contract drift even if the upstream runtime is conservative too.

## Target-native discriminator

`teamleaderleo/ai#60` contains four controls against exact current head:

1. existing `Bash` + `allow-edits` must enter the approval path;
2. new `PowerShell` + `allow-edits` must behave like its declared bash kind;
3. existing `Read` + `allow-reads` must proceed without approval;
4. new `CronList` + `allow-reads` must behave like its declared readonly kind.

The test exercises the actual `canUseTool` callback Vercel passes to the pinned Agent SDK. Carrier #61 runs package type-check and the focused Node suite. Execution is pending at this record.

## Competing explanations

1. **Vercel permission drift:** the new public catalog should also drive the bridge's permission classification; duplicated maps simply diverged.
2. **Deliberate conservative fallback:** unknown tools intentionally default to edit, and the public `toolUseKind` serves only host presentation/filtering. This could explain extra prompts for read-only additions, but it does not explain why a public bash-class addition receives the edit fallback under `allow-edits`.
3. **Claude runtime owns the final gate:** the pinned Agent SDK / Claude Code runtime may independently classify PowerShell and ask before Vercel's callback can weaken authority. If so, the local mismatch remains real while the external security consequence narrows.

## Promotion gate

Retain a finding after target execution proves the callback/config mismatch. Promote to a security/correctness campaign only after composed evidence establishes that the mismatch changes effective execution authority, or primary runtime contracts prove Vercel's callback is authoritative for the disputed PowerShell path.

A likely repair owner is one shared tool-kind definition consumed by both the public catalog and bridge permission code. Copying twenty-one entries into a second map repairs today's list while preserving the drift mechanism.
