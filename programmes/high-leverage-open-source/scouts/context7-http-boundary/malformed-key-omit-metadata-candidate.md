# Context7 omission-on-encryption-failure candidate

Parent finding: #333  
Retained defect evidence: PR #343  
Listener and forwarded-identity evidence: PR #355  
State: `target-executed / workflow-retirement`  
Upstream contact authorized: `no`

## In simple words

Exact Context7 execution proved that a malformed configured client-IP encryption key can send the selected IP unchanged as plaintext `mcp-client-ip` metadata.

The accepted candidate keeps the documentation service and every unrelated header available while omitting that optional metadata whenever encryption cannot be completed. Diagnostics are fixed and retain no raw IP, configured key, or caught exception text.

## Exact accepted identity

- Fieldwork base: `c247681f80d3504045e5b34dd99aeda4907a2829`;
- Fieldwork branch: `candidate/333-context7-omit-client-ip-on-encryption-failure`;
- exact target-executed Fieldwork head: `3360d80d8aa90e3eaafea3367ff9dcfd4dfe0345`;
- exact target: `upstash/context7@594a73133e14631af8c915a1b4f2c8039c964fe1`;
- target package: `@upstash/context7-mcp` `3.2.5`;
- target source path: `packages/mcp/src/lib/encryption.ts`;
- target test path: `packages/mcp/test/encryption.test.ts`;
- retained patch: `malformed-key-omit-metadata.patch`;
- retained patch SHA-256: `bcdbef2c71e89d456267d3bc82a3eed2f62f03133b2dab326196d29fb24309d5`;
- mirrored target-native test: `malformed-key-omit-metadata.test.ts`;
- complete technical review: `4829033192` — `ACCEPT SOURCE CANDIDATE / RETIRE EXECUTION WORKFLOW`.

The connected author account is not an eligible independent accepter.

## Defect evidence input

PR #343 retained exact compiled-helper execution at Fieldwork head `fd736a826044b92b1e82a5501fedce5cc4837020`:

- focused workflow `30629165557`: success;
- job `91151287009`: success;
- artifact `8792754564`;
- artifact digest `sha256:6daa628f897636c8aca033e1de269d589217e40df6462038438e10e32eb4b677`;
- exact marker `FIELDWORK_CONTEXT7_METADATA_FALLBACK_EXACT=3/3`;
- final workflow-free evidence head `0e524522d708787e0bf9a8d3c83d8a60bbe66370`;
- complete-diff technical acceptance `4828502576`.

That execution proved the selected IP `198.51.100.77` was emitted unchanged when the configured encryption key was malformed. It did not execute a repair.

## Accepted source contract

The candidate changes only the client-IP metadata encryption boundary:

1. successful encryption returns ciphertext and retains `mcp-client-ip`;
2. invalid key shape returns no client-IP metadata and emits one fixed configuration diagnostic;
3. runtime cipher failure returns no client-IP metadata and emits a different fixed runtime diagnostic;
4. neither diagnostic includes the raw client IP, configured key, or caught exception text;
5. session, authorization, client-information, transport, source, and server-version headers remain available;
6. listener, CORS, forwarded-IP selection, MCP routing, Redis behavior, and hosted API semantics remain unchanged.

`encryptClientIp()` changes from `string` to `string | undefined`. `generateHeaders()` publishes `mcp-client-ip` only when encryption returns a value. The runtime catch deliberately discards the error object because its message or stack may contain IP, key, provider, path, or other private context.

## Target-native controls

The retained Vitest file covers:

- valid configured key: ciphertext-shaped metadata and every unrelated header retained;
- malformed configured key: client-IP metadata omitted, unrelated headers retained, fixed diagnostic emitted, no raw IP or key in diagnostic;
- injected `randomBytes()` failure: client-IP metadata omitted, unrelated headers retained, fixed diagnostic emitted, no raw IP, key, or injected exception text in diagnostic.

The test resets modules and environment between cases because the target reads the encryption key at module load. The runtime failure uses a local crypto mock and performs no network request.

## Exact accepted execution

At Fieldwork head `3360d80d8aa90e3eaafea3367ff9dcfd4dfe0345`:

- target workflow `30635777158`: success;
- exact target job `91172880796`: success;
- Fieldwork integrity `30635777191`: success;
- focused omission controls: `3/3`;
- complete MCP package suite: `49/49`;
- target Prettier, ESLint, TypeScript typecheck, and build: success;
- exact Fieldwork checkout and target checkout verification: success;
- patch SHA verification, zero-fuzz apply check/application, mirrored-test equality, and applied-diff hygiene: success;
- exact JSON receipt validation and upload: success;
- artifact `8795244374`;
- artifact digest `sha256:c2de1d9c85b96c11b6620f49c8004f6329def70e47c011720e27ff5a1eb3d300`.

The exact receipt records:

- `validKeyCiphertextRetained: true`;
- `malformedKeyMetadataOmitted: true`;
- `runtimeCipherFailureMetadataOmitted: true`;
- `unrelatedHeadersRetained: true`;
- `rawIpAbsentFromDiagnostics: true`;
- `keyAbsentFromDiagnostics: true`;
- `exceptionTextAbsentFromDiagnostics: true`;
- no hosted Context7 API call, MCP session, Redis operation, usable credential, or upstream interaction.

## Carrier history

Earlier red generations remain bounded carrier evidence:

1. head `0cf0296c0ec2fa46538d7267d2315eda6b1c33bf` used a runner-environment server-version oracle; the target correctly emitted package version `3.2.5`;
2. head `58b30421473861b455254c38126d5879404dd858` passed focused `3/3` and complete `49/49` but stopped at target formatting;
3. temporary formatter workflow `30635438074` produced target-owned Prettier `3.6.2` bytes in artifact `8795095262`, digest `sha256:c1ad7d75a28a7f3e4d25108f116920effcb72df7002499472acbd0a61622f732`;
4. those exact bytes were transferred into the retained patch and mirrored test, and the temporary formatter workflow was deleted before the accepted run.

No source conclusion is borrowed from the red carrier generations.

## Evidence boundary

Evidence class: `target-executed-source-candidate` for the exact local package source and named gates.

Not established:

- hosted configuration prevalence or production impact;
- every deployment or transport path;
- upstream acceptance;
- merge readiness;
- a direct owned Context7 source branch;
- provider treatment of omitted identity metadata.

## Final transition

Remove the exact execution workflow, retain only this report, the patch, and the mirrored test, run workflow-free Fieldwork integrity, verify the three-file fence, and obtain complete-diff review of that final generation.

No hosted Context7 request, MCP session, Redis operation, usable credential, account, merge, deployment, spending, private data, or public upstream interaction occurred or is authorized.
