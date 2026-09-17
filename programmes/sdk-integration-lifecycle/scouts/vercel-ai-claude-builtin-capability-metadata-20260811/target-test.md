# Owned-fork characterization carrier

## In simple words

The owned `teamleaderleo/ai` fork contains the exact pinned public Vercel revision `cfc587bdfd8fd1996dd902edd14143be6e034baf`. A focused test-only characterization was prepared on top of that revision to make the stale filtering inventory fail against the newly expanded public built-in catalog.

## Carrier

- repository: `teamleaderleo/ai`
- branch: `fieldwork/claude-builtin-filter-parity-characterization`
- characterization commit: `4f34b766267ca73545a38be60964b97c064e3b47`
- parent/public pin: `cfc587bdfd8fd1996dd902edd14143be6e034baf`
- changed target file: `packages/harness-claude-code/src/bridge/tool-filtering.test.ts`
- production target files changed: none

The added test imports `createClaudeCode()`, derives the complete expected native built-in inventory from `harness.builtinTools`, then compares it to:

```ts
resolveInactiveNativeTools({ mode: 'allow', toolNames: [] })
```

At the pinned source, the public catalog contains the newly added tools while `PUBLIC_TO_NATIVE` still contains the older inventory. The characterization is therefore expected to fail until the bridge filtering inventory reaches parity or the duplication is removed.

## Review-carrier note

A draft fork PR was briefly opened as `teamleaderleo/ai#55`. The fork's default `main` is substantially behind the pinned Vercel head, so that PR contained a large unrelated sync delta. It was immediately closed. The focused branch/commit remains the evidence carrier.

This carrier is classified `target-test-prepared`, not `target-executed`: no CI or repository-native test run has been observed for the characterization commit yet.

## Relationship to the strongest permission finding

This characterization proves the stale inventory mechanism on the filtering side with a target-native test file. It does not directly execute the private bridge `nativeToolRequiresApproval()` helper, so the `PowerShell` `allow-edits` permission result remains `source-read + model-executed` pending a real bridge/runtime approval trace.

Upstream contact authorized: `false`.
