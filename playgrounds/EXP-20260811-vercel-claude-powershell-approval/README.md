# Vercel AI SDK Claude PowerShell approval classification

## State

`COMPLETE — source-read + model-executed + target-test-prepared`

Owner: `chatgpt:gpt-5.6-sol`  
Created: `2026-08-11`  
Claim scope: interface  
Target: `target:vercel-ai`  
Target hub: #2  
Programme: #13  
Owned execution carrier: `teamleaderleo/ai#64`  
Public upstream contact authorized: `no`

## In simple words

Current Vercel AI SDK main added Claude Code's native `PowerShell` tool to the public harness catalog and marks it as a Bash-class tool.

The Claude sandbox bridge keeps a separate native-tool permission table. That table was unchanged by the catalog expansion and does not contain `PowerShell`. Unknown native tools fall back to `edit` inside the bridge.

Under `permissionMode: 'allow-edits'`, edit-class tools run without host approval while Bash-class tools must ask. The two tables therefore disagree specifically on PowerShell:

```text
public harness catalog     PowerShell → bash
bridge permission table    PowerShell → missing → fallback edit

allow-edits:
  bash → approval
  edit → allow
```

Current answer: PowerShell can bypass the Bash approval gate in `allow-edits` because the bridge classifies it through the unknown-tool fallback rather than the public catalog's Bash classification.

## Bounded question

Does native Claude Code `PowerShell` still require host approval under `permissionMode: 'allow-edits'` after current main added it to the built-in tool catalog?

At `cfc587bdfd8fd1996dd902edd14143be6e034baf`, the source answer is **no**.

## Exact subject

Public repository: https://github.com/vercel/ai  
Current public main: `cfc587bdfd8fd1996dd902edd14143be6e034baf`  
Retrieval date: `2026-08-11`

Primary paths:

- `packages/harness-claude-code/src/claude-code-harness.ts`;
- `packages/harness-claude-code/src/bridge/index.ts`.

Owned target-native carrier:

- `teamleaderleo/ai#64`;
- branch `fieldwork/claude-powershell-approval-tests`;
- exact base `cfc587bdfd8fd1996dd902edd14143be6e034baf`.

## Source map

### Public tool catalog

Current `CLAUDE_CODE_BUILTIN_TOOLS` includes:

```text
PowerShell
  toolUseKind: bash
```

That is the public interface classification exposed by the harness.

### Bridge permission table

`packages/harness-claude-code/src/bridge/index.ts` keeps an independent `NATIVE_TOOL_KINDS` map used by `createPermissionSettings()` and `nativeToolRequiresApproval()`.

The reviewed table includes `Bash` and `Monitor` as Bash-class tools but omits `PowerShell`.

Unknown native names take this fallback:

```text
NATIVE_TOOL_KINDS[nativeName] ?? 'edit'
```

### allow-edits rule

For `allow-edits`:

```text
requires approval ⇔ bridge kind == bash
```

Therefore:

```text
Bash       → bridge kind bash → approval
PowerShell → fallback edit    → no approval
```

`createPermissionSettings()` has the same omission: it builds Claude settings ask-rules by iterating the bridge table, so no `PowerShell(*)` ask rule is emitted either.

The callback and settings layers therefore agree with each other while disagreeing with the newly expanded public catalog.

## Competing explanations

### H1 — PowerShell is intentionally edit-class in allow-edits

**Rejected by the target's own public catalog.** Current main explicitly declares `PowerShell` with `toolUseKind: 'bash'`.

### H2 — the bridge's unknown-tool fallback still requests approval in allow-edits

**Rejected by source and model.** Unknowns become `edit`; allow-edits asks only for `bash`.

### H3 — Claude's native settings add a PowerShell ask rule independently

**Weakened by source.** `createPermissionSettings()` derives ask rules from the same bridge table that omits PowerShell.

### H4 — the mismatch is harmless because PowerShell is not exposed

**Rejected at current main.** The current public built-in catalog now exposes it.

## Executable discriminator

Run:

```sh
python3 playgrounds/EXP-20260811-vercel-claude-powershell-approval/run.py
```

Observed:

```json
{
  "bash_bridge_kind": "bash",
  "bash_host_kind": "bash",
  "bash_requires_approval_in_allow_edits": true,
  "classification_disagrees": true,
  "powershell_bridge_kind": "edit",
  "powershell_host_kind": "bash",
  "powershell_requires_approval_in_allow_edits": false
}
```

Bash is the negative control: the model recognizes the intended approval path. PowerShell diverges only because its bridge classification is missing.

Evidence class: `model-executed`.

## Target-native discriminator

Owned PR `teamleaderleo/ai#64` uses the real Claude bridge module with the Agent SDK mocked at the call boundary.

It starts a turn in `allow-edits`, extracts the bridge-provided `canUseTool`, invokes it with native `PowerShell`, and requires:

- host `requestToolApproval('ps-1')` to run;
- a `tool-approval-request` event to be emitted;
- a host denial to return a deny decision.

Current target behavior is expected to fail by returning `allow` before the host approval path.

Evidence class remains `target-test-prepared` until owned CI executes.

## Change thesis

Current behavior:

```text
current-main catalog adds PowerShell as bash
        ↓
bridge table does not add PowerShell
        ↓
unknown fallback becomes edit
        ↓
allow-edits auto-allows edit
        ↓
PowerShell skips host approval
```

Consequence: a caller selecting `allow-edits` expects shell-class native tools to remain approval-gated. PowerShell is classified as shell/Bash at the public interface but currently crosses that boundary as an edit inside the bridge.

Smallest repair:

```text
NATIVE_TOOL_KINDS.PowerShell = 'bash'
```

Then keep a focused regression proving both the `canUseTool` callback and generated ask settings preserve the Bash approval invariant.

A wider follow-up may compare the complete public catalog with the bridge table so future tool additions cannot silently drift. That should remain a separate refactor/test question after this current defect is fixed.

## Negative results and boundaries

- `allow-all` intentionally bypasses approval and is outside this finding.
- `allow-reads` already treats unknown tools as edit and therefore asks; the observed authority gap is specific to `allow-edits`.
- This finding concerns PowerShell classification, not the bridge credential environment campaign #802.
- No claim is made that a user has encountered the behavior in production.
- No provider credentials, production data, or paid calls were used.
- Public upstream remained read-only.

## Evidence classes

| Claim | Evidence class | Limit |
| --- | --- | --- |
| public catalog marks PowerShell as bash | `source-read` | current-main catalog |
| bridge table omits PowerShell | `source-read` | current-main bridge |
| unknown bridge tools fall back to edit | `source-read` | current-main permission function |
| allow-edits asks only for bash | `source-read` | current-main permission function/settings |
| Bash control passes while PowerShell diverges | `model-executed` | isolated model |
| real bridge routes PowerShell through host approval | `target-test-prepared` | carrier #64 queued |

## Recommendation

Promote directly to a bounded campaign if the target-native carrier fails for the expected product reason.

The implementation question is tiny:

> Does adding `PowerShell: 'bash'` to the bridge permission table restore `allow-edits` approval parity without changing any other native-tool permission behavior?

Keep the broader catalog/table drift check as a follow-up branch candidate, because current main already demonstrates that the two independently maintained classifications can diverge.

## Boundaries

- Automated third-party upstream contact is prohibited.
- All writes are confined to Fieldwork and the owned `teamleaderleo/ai` fork.
- No public Vercel AI SDK mutation occurred.
