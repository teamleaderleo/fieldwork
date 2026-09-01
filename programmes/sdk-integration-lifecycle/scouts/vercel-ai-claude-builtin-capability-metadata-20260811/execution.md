# Execution receipt

## In simple words

The source-model probe executed under local Node and reproduced the permission/filtering decisions copied from Vercel AI SDK revision `cfc587bdfd8fd1996dd902edd14143be6e034baf`.

The key discriminator is `PowerShell`: the public catalog class is `bash`, the bridge table has no entry, the fallback class is `edit`, and `allow-edits` therefore returns `false` from the copied `nativeToolRequiresApproval()` logic.

## Command

```bash
node programmes/sdk-integration-lifecycle/scouts/vercel-ai-claude-builtin-capability-metadata-20260811/probe.mjs
```

## Result

- exit status: `0`;
- `PowerShell.allowEditsApproval`: `false`;
- new readonly examples such as `ListMcpResourcesTool` and `EnterPlanMode` receive fallback `edit` and `allowReadsApproval: true`;
- allow-mode inactive complement derived from the old map contains neither `PowerShell` nor `Workflow`;
- explicit deny of `PowerShell` preserves the native name.

Captured output: `probe-output.json`.

## Evidence classification

- Vercel source and tests: `source-read`;
- probe: `model-executed`;
- Vercel target-native package/runtime execution: pending;
- real Claude Code approval event trace: pending.

The probe is a discriminator for pure adapter logic. It does not claim behavior of the external Claude runtime beyond the exact arguments and helper decisions Vercel constructs.

## Next target-native command family

A follow-up on an owned Vercel AI fork should add a focused Claude bridge permission test that compares `Bash`, `PowerShell`, `Write`, and one new readonly tool under `allow-edits` / `allow-reads`, then run the package's native test command and ordinary gates at one exact head.

Upstream contact authorized: `false`.
