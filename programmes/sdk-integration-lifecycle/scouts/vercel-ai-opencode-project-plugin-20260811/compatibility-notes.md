# Compatibility scan for the OpenCode project-config boundary

Date: 2026-08-11

Fieldwork lead: #831  
Pinned Vercel AI source: `74556f7946cdf50aa41c01c5d5b3bd2b733acc86`

## In simple words

The public OpenCode harness contract does not describe repository-local `opencode.json` or `.opencode` configuration as an adapter feature.

Current docs enumerate adapter settings for authentication, MCP servers, model/provider selection, reasoning, bridge port/startup, and bridge-token minting. Project config is absent from that list. The package README only says the harness connects `HarnessAgent` to OpenCode through a sandboxed bridge.

The current unit tests also do not assert that checked-out repository OpenCode config should be honored. Their `.opencode` assertion checks the opposite concern for harness-provided skills: skills are written under sandbox HOME and are explicitly kept out of `/.opencode/` and the project workspace.

This lowers the documented compatibility cost of setting `OPENCODE_DISABLE_PROJECT_CONFIG=1` by default. Existing consumers may still rely on the inherited OpenCode behavior, so an explicit opt-in remains a sensible migration option.

## Surfaces reviewed

- `content/providers/02-ai-sdk-harnesses/04-opencode.mdx`
- `packages/harness-opencode/README.md`
- `packages/harness-opencode/src/opencode-harness.test.ts`
- repository search for `opencode.json`
- repository search for `OPENCODE_DISABLE_PROJECT_CONFIG`

## Findings

1. The public adapter settings list has no project-config or plugin-discovery setting.
2. Repository search returned no `opencode.json` references in the Vercel AI source tree at the pinned revision.
3. Repository search returned no `OPENCODE_DISABLE_PROJECT_CONFIG` reference at the pinned revision.
4. The harness unit test that mentions `.opencode` verifies harness skills are not written there; it does not establish project-config compatibility as a supported contract.
5. The Pi harness provides a nearby policy precedent by disabling filesystem extension discovery while retaining explicit caller-supplied extension factories.

## Contribution implication

A small first patch can plausibly set `OPENCODE_DISABLE_PROJECT_CONFIG=1` in the OpenCode bridge environment and add a regression fixture. If maintainers want to preserve deliberate repository-local OpenCode customization, expose an explicit opt-in and document the trust consequence.

Target-native execution of the #831 discriminator remains the final evidence gate before campaign promotion.
