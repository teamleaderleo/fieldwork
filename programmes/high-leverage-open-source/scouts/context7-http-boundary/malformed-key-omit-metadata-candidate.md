# Context7 omission-on-encryption-failure candidate

Parent finding: #333

Retained evidence: PR #343

State: `target-execution-repair`

Upstream contact authorized: `no`

## In simple words

Exact Context7 execution proved that a malformed configured client-IP encryption key causes the local metadata helper to log an error and send the selected IP unchanged as plaintext `mcp-client-ip` metadata.

The selected repair keeps the primary documentation service available but omits that optional metadata header whenever encryption cannot be completed. Other headers remain available. Diagnostics are fixed and do not retain the raw IP, key material, or exception message.

## Exact identity

- Fieldwork base: `c247681f80d3504045e5b34dd99aeda4907a2829`;
- Fieldwork branch: `candidate/333-context7-omit-client-ip-on-encryption-failure`;
- exact target: `upstash/context7@594a73133e14631af8c915a1b4f2c8039c964fe1`;
- target source path: `packages/mcp/src/lib/encryption.ts`;
- target test path: `packages/mcp/test/encryption.test.ts`;
- retained patch: `malformed-key-omit-metadata.patch`;
- warning-clean patch SHA-256: `7c7834b3e6515107bd85a1fcc3d46e6d340eb9ae68de9bbed458fe867d422d83`;
- mirrored target-native test: `malformed-key-omit-metadata.test.ts`.

## Evidence input

PR #343 retained exact target execution at Fieldwork head `fd736a826044b92b1e82a5501fedce5cc4837020`:

- focused workflow `30629165557`: success;
- job `91151287009`: success;
- artifact `8792754564`, digest `sha256:6daa628f897636c8aca033e1de269d589217e40df6462038438e10e32eb4b677`;
- exact marker `FIELDWORK_CONTEXT7_METADATA_FALLBACK_EXACT=3/3`;
- final workflow-free evidence head `0e524522d708787e0bf9a8d3c83d8a60bbe66370`;
- complete-diff technical acceptance `4828502576`.

That execution proved the compiled helper returned selected IP `198.51.100.77` unchanged when the configured key was malformed. It did not execute a source repair.

## Selected contract

The candidate changes only the client-IP metadata encryption boundary:

1. successful encryption returns ciphertext and retains `mcp-client-ip`;
2. invalid key shape returns no client-IP metadata and emits one fixed configuration diagnostic;
3. runtime cipher failure returns no client-IP metadata and emits one fixed runtime diagnostic;
4. neither diagnostic includes the raw client IP, configured key, or exception message;
5. session, authorization, client-information, transport, source, and server-version headers remain available;
6. listener, CORS, forwarded-IP selection, MCP routing, Redis behavior, and hosted API semantics are unchanged.

## Source shape

`encryptClientIp()` changes from `string` to `string | undefined`. It no longer returns plaintext input under either validation or cipher failure. `generateHeaders()` adds `mcp-client-ip` only when encryption returns a value.

The runtime catch deliberately does not log the caught error object because its message or stack may contain provider, key, IP, or other private context.

## Target-native reversing controls

The new Vitest file covers:

- valid configured key: ciphertext-shaped metadata and every unrelated header retained;
- malformed configured key: client-IP metadata omitted, unrelated headers retained, fixed diagnostic emitted, no raw IP or key in diagnostic;
- injected `randomBytes()` failure: client-IP metadata omitted, unrelated headers retained, fixed diagnostic emitted, no raw IP or exception text in diagnostic.

The test resets modules and environment between cases because the target reads the encryption key at module load. The runtime failure uses a local crypto mock and does not make a network request.

## First exact execution

Prepared head `561224ea00aff5b212608c48dbb28e1c2f9a5067` produced run `30631807091`, job `91159672157`.

The run established:

- exact Fieldwork checkout verification: passed;
- exact target checkout and patch SHA verification: passed;
- zero-fuzz patch application and mirrored-test equality: passed;
- focused omission controls: `3/3`, passed;
- complete MCP package suite: four files and 49 tests, passed;
- package format check: failed on `test/encryption.test.ts` before lint, typecheck, build, or receipt assembly.

This is a presentation-only carrier failure. The source contract and complete package tests passed. The warning-clean generation restructures the three long test declarations to the target's Prettier shape and changes no assertions or source behavior.

## Required exact execution

The temporary executor must:

1. verify the actual Fieldwork checkout SHA before using any candidate bytes;
2. check out exact target source `594a7313...`;
3. validate and apply the retained patch with zero fuzz;
4. prove the applied target test is byte-identical to the mirrored retained test;
5. run the focused encryption test;
6. run the complete MCP package test suite;
7. run format, lint, typecheck, and build gates;
8. retain exact source, patch, job, and artifact identities;
9. use no hosted Context7 request, MCP session, Redis operation, usable credential, or account.

## Evidence boundary

A green run would establish target-executed compatibility for the exact local package and named gates. It would not establish hosted configuration prevalence, production impact, every deployment or transport path, upstream acceptance, merge readiness, or public disclosure authority.

## Stop and recovery

If any ordinary package gate fails, classify whether the candidate broke compatibility or the executor is defective before changing the source contract. Do not weaken omission, privacy, or unrelated-header controls merely to obtain green execution.

After a green exact run, inspect and transfer the receipt, remove the temporary workflow, run workflow-free Fieldwork integrity, and obtain complete-diff review. No public upstream interaction is authorized.
