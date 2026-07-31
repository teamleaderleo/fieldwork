# Context7 malformed encryption-key metadata fallback

Parent finding: Fieldwork #333.

State: `target-test-prepared / exact-head identity repair`

## In simple words

Context7's local metadata helper encrypts the selected client IP when its configured key is usable. Source inspection and one earlier non-promotable harness run indicate that a malformed configured key logs an error and returns the selected IP as plaintext instead.

This is a separate configuration-failure boundary from the listener, CORS, and trusted-proxy findings. It does not establish hosted configuration or hosted trust.

## Exact target

- repository: `upstash/context7`;
- source: `594a73133e14631af8c915a1b4f2c8039c964fe1`;
- package: `@upstash/context7-mcp` `3.2.5`;
- source path: `packages/mcp/src/lib/encryption.ts`;
- focused helper: `fieldwork-metadata-fallback-receipt.mjs`.

## Question

When `CLIENT_IP_ENCRYPTION_KEY` is malformed, does the compiled local metadata helper:

1. preserve forwarded identity selection;
2. fail closed by rejecting configuration or omitting `mcp-client-ip`; or
3. fail open by returning the selected IP unchanged?

## Current source prediction

The exact source validates the configured key's shape. When validation fails, it logs an invalid-key diagnostic and returns the input string rather than throwing or omitting the metadata field.

The strict reversing repair is therefore either:

- reject startup or metadata generation under malformed configuration; or
- omit `mcp-client-ip` and retain a bounded local error receipt.

A repair must not silently publish plaintext selected identity.

## Focused control

The helper runs the compiled target module in isolated child processes so module-level environment caching cannot make the two key cases share configuration.

It requires:

- repository-default key: selected identity retained internally and outbound metadata has ciphertext shape;
- runtime-composed malformed configured key: selected identity retained internally, outbound metadata equals the selected IP in plaintext, and stderr contains the invalid-key diagnostic;
- strict repair discriminator: reject-or-omit behavior is currently absent;
- no MCP session, hosted Context7 request, Redis operation, usable credential, or account.

The malformed fixture is assembled at runtime rather than stored as a credential-shaped environment assignment.

## Exact-head workflow contract

The focused workflow must:

1. check out Fieldwork at `${{ github.event.pull_request.head.sha || github.sha }}`;
2. assert the actual checkout SHA before copying or executing the helper;
3. check out exact Context7 source;
4. install and build the exact MCP package;
5. execute only the focused helper;
6. require the `FIELDWORK_CONTEXT7_METADATA_FALLBACK_EXACT=3/3` marker;
7. assert the receipt's `fieldworkHead` equals the verified checkout;
8. upload the narrow JSON receipt.

Fieldwork integrity runs independently on the same branch head.

## Historical harness evidence

PR #343 historical head `2b63a9854db1d9db5fb845e70c2b3401842ccd30` produced run `30627737510` and artifact `8792248270`, digest `sha256:c619ab873cabd07f6a44f67899f3e1ceb040ee215c421b1565d7392fc2e2d99d`.

The artifact's helper outcome matched the source prediction, but the workflow checked out the synthetic pull-request merge ref while labeling the artifact with the PR head. Review `4827914873` therefore correctly blocks exact-head promotion. That run remains harness evidence only.

## Evidence boundary

A green repaired run would be `target-executed-local-helper` for exact compiled source. It would not prove:

- a hosted Context7 deployment uses malformed configuration;
- a hosted API receives or trusts the value;
- the value crosses an MCP session or Redis boundary;
- every transport or deployment path shares the helper;
- a source repair is complete or compatible.

## Next transition

Run the focused exact-head workflow and Fieldwork integrity. Inspect the receipt, transfer its exact identity here, remove the temporary workflow, and compare reject-configuration versus omit-metadata source sketches without contacting upstream.

No merge, deployment, real credential, private data, spending, hosted request, or public upstream interaction is authorized.
