# Context7 malformed encryption-key metadata fallback

Parent finding: Fieldwork #333.

State: `target-executed-local-helper / workflow-free`

## In simple words

Context7's compiled local metadata helper encrypts the selected client IP when its configured key is usable. Under a malformed configured `CLIENT_IP_ENCRYPTION_KEY`, exact execution proved that the helper logs an invalid-key diagnostic and returns the selected IP unchanged as plaintext metadata.

This is a separate configuration-failure boundary from the listener, CORS, and trusted-proxy findings. It does not establish hosted configuration, hosted receipt, or hosted trust.

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

## Exact execution receipt

- exact Fieldwork execution head: `fd736a826044b92b1e82a5501fedce5cc4837020`;
- focused workflow: `30629165557`, success;
- focused job: `91151287009`, success;
- exact-head Fieldwork integrity: `30629165583`, success;
- artifact: `8792754564`;
- artifact digest: `sha256:6daa628f897636c8aca033e1de269d589217e40df6462038438e10e32eb4b677`;
- inspected JSON SHA-256: `7cd39b105145a49fce9bdc1c18a1bf74401a8919fb7aa9dd8580e95c7a7c307b`;
- retained stdout SHA-256: `1bc5e916574b34512879f743f2dd5b61974868c716e4e5e5d2bf081869bdacfb`;
- exact marker: `FIELDWORK_CONTEXT7_METADATA_FALLBACK_EXACT=3/3`.

Every focused job step passed: exact Fieldwork checkout, actual-head verification, exact target checkout, dependency installation, target build, focused helper execution, receipt verification, diff hygiene, and artifact upload.

The inspected receipt records:

```text
schemaVersion: 1
evidenceClass: target-executed-local-helper
fieldworkHead: fd736a826044b92b1e82a5501fedce5cc4837020
exactTarget: 594a73133e14631af8c915a1b4f2c8039c964fe1
selectedIp: 198.51.100.77
socketIp: 203.0.113.9
```

Exact outcomes:

- forwarded identity remained selected;
- the repository-default key produced ciphertext-shaped metadata;
- the runtime-composed malformed configured key emitted `198.51.100.77` unchanged as plaintext metadata;
- reject-or-omit repair behavior was absent;
- MCP session creation, hosted Context7 API calls, Redis operations, and usable credential use were all false.

## Mechanism

The exact source validates the configured key's shape. When validation fails, it logs an invalid-key diagnostic and returns the input string rather than throwing or omitting the metadata field.

The helper executes the compiled target module in isolated child processes so module-level environment caching cannot make the default-key and malformed-key cases share configuration. The malformed fixture is assembled at runtime rather than stored as a credential-shaped environment assignment.

## Reversing repair family

A bounded source repair should choose one of two fail-closed contracts:

- reject startup or metadata generation under malformed configuration; or
- omit `mcp-client-ip` and retain a bounded local configuration-error receipt.

A repair must not silently publish the selected identity as plaintext.

The two repair families differ operationally. Rejecting startup gives the strongest configuration signal but can make the complete local server unavailable. Omitting optional metadata preserves service availability but must not disguise the configuration error. A later source candidate should compare repository conventions and ordinary tests before selecting one.

## Historical harness evidence

PR #343 historical head `2b63a9854db1d9db5fb845e70c2b3401842ccd30` produced run `30627737510` and artifact `8792248270`, digest `sha256:c619ab873cabd07f6a44f67899f3e1ceb040ee215c421b1565d7392fc2e2d99d`.

That helper outcome matched the exact result above, but the old workflow checked out the synthetic pull-request merge ref while labeling the artifact with the PR head. Review `4827914873` correctly blocked exact-head promotion. That old run remains harness evidence only.

A later broad Context7 workflow run `30629165530` was a retirement echo from the replaced workflow generation and failed outside the focused carrier. It is not the canonical malformed-key receipt. The focused exact-head workflow `30629165557` and integrity `30629165583` own this conclusion.

## Evidence boundary

Evidence class: `target-executed-local-helper` for exact compiled source `594a7313...` under Node 22 on the named Linux runner family.

This establishes only the local parser-selected identity to metadata-helper fallback under malformed configuration. It does not prove:

- a hosted Context7 deployment uses malformed configuration;
- a hosted API receives, persists, or trusts the value;
- the value crosses an MCP session or Redis boundary;
- every transport or deployment path shares this helper;
- the hosted service interprets `mcp-client-ip` as identity authority;
- either source repair family is complete or compatible;
- production impact, exploitability, or deployment prevalence.

## Carrier retirement

The focused workflow was removed after exact receipt transfer at cleanup head `fcd35454373a9c141e805793ace10219c2d00933`. Its removal does not mean the target reran on the later cleanup generation. The durable carrier is this report plus the isolated helper.

Listener reachability, CORS, valid-key metadata composition, and trusted-proxy behavior remain owned by #355/#333. They are not rerun or widened here.

## Next transition

Run Fieldwork integrity on the final workflow-free documentation head, then obtain complete-diff review of the two-file retained evidence carrier. Compare reject-configuration versus omit-metadata source sketches against target repository conventions without contacting upstream.

No merge, deployment, real credential, private data, spending, hosted request, or public upstream interaction is authorized.
