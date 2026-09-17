# Vercel AI SDK Claude built-in capability metadata scout

## In simple words

Vercel AI's newest Claude Code harness commit added many native built-in tools to the public catalog, including `PowerShell`, canonical MCP resource names, scheduling/messaging tools, and workflow tools. The bridge that actually applies built-in permissions and filtering still carries older hand-maintained tool tables.

The strongest current finding is `PowerShell`: the public catalog explicitly classifies it as a shell tool, while the bridge does not know the name and falls back to treating it as an edit. Under the documented `allow-edits` mode, shell commands are supposed to request approval. The bridge helper therefore computes the wrong approval class for `PowerShell` at the pinned revision.

The same stale-table family makes several newly declared readonly tools look like edits inside the bridge and leaves the allowlist-complement fallback unaware of every newly added built-in. A small source-model probe reproduces these decisions. Target-native execution against the pinned Claude runtime remains the next gate before promotion.

## Assignment and fence

- Fieldwork lane: https://github.com/teamleaderleo/fieldwork/issues/793
- Programme: https://github.com/teamleaderleo/fieldwork/issues/13
- Target hub: https://github.com/teamleaderleo/fieldwork/issues/2
- Public target: https://github.com/vercel/ai
- Pinned target revision: `cfc587bdfd8fd1996dd902edd14143be6e034baf`
- Previous revision already covered by adjacent current-main scouts: `fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c`
- Retrieval date: 2026-08-11
- Claim scope: mechanism and interface
- Upstream contact authorized: `false`

The pinned commit is one commit after the adjacent scouts' source pin. Its change set modifies only the Claude Code public harness catalog, catalog/type tests, and a changeset. It does not modify `packages/harness-claude-code/src/bridge/index.ts` or `src/bridge/tool-filtering.ts`.

## Source map

### Public built-in catalog

Source:

- https://github.com/vercel/ai/blob/cfc587bdfd8fd1996dd902edd14143be6e034baf/packages/harness-claude-code/src/claude-code-harness.ts
- https://github.com/vercel/ai/blob/cfc587bdfd8fd1996dd902edd14143be6e034baf/packages/harness-claude-code/src/claude-code-harness.test.ts

The new catalog declares, among others:

- `PowerShell` as `toolUseKind: 'bash'`;
- `ListMcpResourcesTool`, `ReadMcpResourceTool`, `ReadMcpResourceDirTool`, `RefreshMcpTools`, `EnterPlanMode`, `LSP`, `ReportFindings`, `CronList`, `SendUserFile`, and `WaitForMcpServers` as `readonly`;
- `Artifact`, `CronCreate`, `CronDelete`, `DesignSync`, `PushNotification`, `RemoteTrigger`, `ScheduleWakeup`, `SendMessage`, `ShareOnboardingGuide`, and `Workflow` as `edit`.

The new test explicitly asserts `PowerShell.toolUseKind === 'bash'` and `ListMcpResourcesTool.toolUseKind === 'readonly'`.

### Bridge permission owner

Source:

- https://github.com/vercel/ai/blob/cfc587bdfd8fd1996dd902edd14143be6e034baf/packages/harness-claude-code/src/bridge/index.ts
- https://github.com/vercel/ai/blob/cfc587bdfd8fd1996dd902edd14143be6e034baf/packages/harness/src/v1/harness-v1-permission-mode.ts
- https://github.com/vercel/ai/blob/cfc587bdfd8fd1996dd902edd14143be6e034baf/content/docs/03-ai-sdk-harnesses/03-tools.mdx

`NATIVE_TOOL_KINDS` is a second hard-coded capability table. It ends at the older tool set. `PowerShell` and the other newly declared built-ins are absent.

`nativeToolRequiresApproval()` defaults an unknown native tool to `edit`:

```ts
const kind = NATIVE_TOOL_KINDS[input.nativeName] ?? 'edit';
if (input.permissionMode === 'allow-edits') return kind === 'bash';
return kind === 'edit' || kind === 'bash';
```

The public harness contract documents:

- `allow-all`: reads, edits, and shell commands proceed;
- `allow-edits`: reads and edits proceed, shell commands request approval;
- `allow-reads`: reads proceed, edits and shell commands request approval.

`createPermissionSettings()` also derives Claude permission ask rules only from `NATIVE_TOOL_KINDS`, so newly declared built-ins do not receive an explicit rule from this path.

### Bridge filtering owner

Source:

- https://github.com/vercel/ai/blob/cfc587bdfd8fd1996dd902edd14143be6e034baf/packages/harness-claude-code/src/bridge/tool-filtering.ts
- https://github.com/vercel/ai/blob/cfc587bdfd8fd1996dd902edd14143be6e034baf/packages/harness-claude-code/src/bridge/tool-filtering.test.ts

`PUBLIC_TO_NATIVE` is another pre-expansion table. Explicit new native names survive `toNativeName()` by identity, so a direct deny such as `inactiveTools: ['PowerShell']` still becomes `disallowedTools: ['PowerShell']`.

For allow filtering, however, `resolveInactiveNativeTools()` derives the inactive complement from `Object.keys(PUBLIC_TO_NATIVE)`. Every newly added tool is absent from that complement. The same turn also passes the positive `tools` allowlist to Claude, so this source observation does not establish a direct allowlist escape. It establishes that the adapter's denial/approval fallback has stale coverage.

## Finding A — PowerShell loses shell-command approval classification

Disposition: **RETAIN — strongest; target-native discriminator needed**

### Current behavior

The public catalog says `PowerShell` is a shell command capability. The bridge permission table does not contain `PowerShell`, so its helper falls back to `edit`.

For `permissionMode: 'allow-edits'`:

- `Bash` -> `bash` -> approval required;
- `Monitor` -> `bash` -> approval required;
- `PowerShell` -> fallback `edit` -> approval not required by `nativeToolRequiresApproval()`.

`createPermissionSettings()` likewise emits ask rules for known bash tools but cannot emit `PowerShell(*)` because the name is absent from `NATIVE_TOOL_KINDS`.

### Consequence

The adapter's own permission calculation disagrees with its public catalog and documented permission-mode contract for a shell-execution tool. If the pinned Claude runtime reaches the host `canUseTool` path according to these settings, `allow-edits` can permit `PowerShell` where the adapter says shell commands require approval.

### Evidence

- `source-read`: exact catalog, permission helper, settings builder, docs, and commit diff;
- `model-executed`: `probe.mjs` yields `allowEditsApproval: false` for `PowerShell`, while the catalog kind is `bash`;
- `target-executed`: pending.

### Competing explanations

1. **Stale duplicate table** — the catalog was expanded and the bridge permission table was missed. Current source strongly supports this.
2. **Intentional fallback** — all new native tools are intentionally treated as edits. This conflicts with the new explicit `PowerShell: 'bash'` declaration and with the `allow-edits` shell-command contract.
3. **Claude runtime independently asks anyway** — possible. A target-native test must distinguish this before claiming an observed approval bypass.

### Target-native discriminator

With the pinned bridge dependencies (`@anthropic-ai/claude-agent-sdk@0.3.213`, `@anthropic-ai/claude-code@2.1.213`):

1. run a Claude Code harness turn with `permissionMode: 'allow-edits'`;
2. provoke a `PowerShell` call and a `Bash` control call;
3. capture whether each emits `tool-approval-request` before execution;
4. negative control: an ordinary edit such as `Write` should proceed under `allow-edits`;
5. repeat `PowerShell` under `allow-reads`, where the fallback still asks, to separate the mode-specific classification error.

Reversing evidence: the runtime independently forces `PowerShell` approval under `allow-edits` despite the stale Vercel tables, with no user-visible or execution difference.

## Finding B — newly declared readonly tools fall back to edit in the bridge

Disposition: **RETAIN WITH FINDING A — same owning defect family**

Examples include `ListMcpResourcesTool`, `ReadMcpResourceTool`, `EnterPlanMode`, `LSP`, `ReportFindings`, `CronList`, and `WaitForMcpServers`.

The public catalog calls these readonly. The bridge's unknown-name fallback calls them edit. Under `allow-reads`, `nativeToolRequiresApproval()` therefore returns `true` for them.

The model probe demonstrates the mismatch for `ListMcpResourcesTool` and `EnterPlanMode`. This is the inverse of the PowerShell case: the stale table becomes over-restrictive rather than permissive.

Current consequence is interface friction and inconsistent approval behavior. Keep this in the same repair boundary: deriving permission classification from one canonical catalog or proving generated parity between the tables.

`SendUserFile` was deliberately kept out of the promoted readonly examples despite its catalog tag. It sends files to a user and therefore deserves a separate semantic decision about what `readonly` means. The current scout does not use it to strengthen the readonly claim.

## Finding C — allowlist fallback complement omits the new catalog

Disposition: **RETAIN AS DEFENSE/PARITY TEST; no standalone campaign yet**

`resolveInactiveNativeTools({ mode: 'allow', toolNames: ['read'] })` computes its complement from the old `PUBLIC_TO_NATIVE` keys. The probe shows that the resulting inactive set contains neither `PowerShell` nor `Workflow`.

A direct deny remains a useful negative control: `resolveInactiveNativeTools({ mode: 'deny', toolNames: ['PowerShell'] })` returns `['PowerShell']` because unknown names pass through unchanged.

The positive `tools` allowlist is still sent to Claude for allow mode. Therefore current source does not establish that a new tool can execute outside `activeTools`. The retained question is whether stale fallback coverage changes behavior during permission prompting, runtime drift, or a future Claude allowlist regression.

The existing tool-filtering tests cover pass-through of `Workflow` in a requested allowlist/denylist but do not assert the complement against the declared public catalog.

## Negative results and narrowed branches

### Mixed read/write native tools

`DesignSync`, `RemoteTrigger`, `Artifact`, and `ShareOnboardingGuide` combine read-like and write-like actions but are classified as `edit` in the public catalog. This is conservative under the three-level permission vocabulary. No defect is retained from those declarations.

### Broad "all new tools bypass approval" hypothesis

Rejected. Unknown names fall back to `edit`, which still requires approval under `allow-reads`. The permissive mismatch is mode- and capability-specific; `PowerShell` under `allow-edits` is the sharp case.

### Broad explicit-deny failure

Rejected from the source model. Deny mode preserves unknown native names by identity and passes them to `disallowedTools`.

### Catalog metadata as the direct runtime owner

Rejected. Repository search finds `toolUseKind` mainly in declarations/tests. Claude Code runtime permission behavior is currently owned by the separate bridge map. This duplication is the source of the drift.

## Probe

Run:

```bash
node programmes/sdk-integration-lifecycle/scouts/vercel-ai-claude-builtin-capability-metadata-20260811/probe.mjs
```

The probe models only the exact small tables and pure helper behavior from the pinned source. It is intentionally classified `model-executed`.

Key expected output:

- `PowerShell`: catalog `bash`, bridge fallback `edit`, `allowEditsApproval: false`;
- `ListMcpResourcesTool`: catalog `readonly`, bridge fallback `edit`, `allowReadsApproval: true`;
- `EnterPlanMode`: catalog `readonly`, bridge fallback `edit`, `allowReadsApproval: true`;
- allow-mode complement for only `read`: omits both `PowerShell` and `Workflow`;
- explicit deny of `PowerShell`: preserves `['PowerShell']`.

## Likely repair boundary

The smallest durable owner should remove or mechanically synchronize duplicate capability inventories.

Candidate directions, in preference order for testing:

1. derive bridge permission kinds and public/native name translation from the canonical built-in catalog or a shared generated descriptor;
2. keep separate runtime tables but add an exhaustive parity test over every declared built-in, including `toolUseKind`, public/native naming, allow/deny complement, and permission-mode decisions;
3. at minimum add the newly introduced names to both bridge tables and regression-test `PowerShell` under `allow-edits` plus readonly aliases under `allow-reads`.

A simple one-line `PowerShell` entry fixes the sharp case while leaving the drift mechanism intact. Prefer one ownership source if the adapter design permits it.

## Ranked next branches

1. **PowerShell `allow-edits` target-native approval discriminator** — highest consequence and smallest falsifier. Owner: Claude bridge permission settings + callback. Promotion gate: real pinned-runtime event trace.
2. **Generated parity test for public catalog vs bridge permission/filter tables** — likely best repair guard if target-native PowerShell reproduces. Owner: Claude harness/bridge boundary.
3. **Readonly alias behavior under `allow-reads`** — useful compatibility/ergonomics control after the PowerShell test.
4. **Allowlist-complement defense test** — retain as parity coverage; promote only if target execution shows a behavioral escape or incorrect approval path.

## Recommendation

**RETAIN and dispatch one target-native experiment.**

The source-level defect is concrete: the public catalog moved while both bridge capability inventories stayed on the older generation. `PowerShell` gives the most consequential semantic disagreement. A pinned-runtime approval trace should decide whether this becomes a campaign or remains an internal parity hardening finding.

No third-party upstream state was changed.
