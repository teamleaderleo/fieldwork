# Context7 client-IP default-key policy result

Result state: `client policy selected / hosted receiver compatibility hold`

Parent repair: PR #397  
Comparison PR: #420  
Exact target: `upstash/context7@594a73133e14631af8c915a1b4f2c8039c964fe1`  
Exact target-executed Fieldwork head: `8a1d2ae75d4fe0dc73c9178ba05a31abff72abee`  
Workflow-free result parent: `42aa526b33153102cdade06b9fce0c332e0cfc12`  
Workflow: `30658005611`, attempt `1`  
Upstream contact authorized: `no`

## In simple words

Context7 adds an optional encrypted client-IP header to requests sent by its MCP server. Exact public source uses a fixed public AES key when no key is configured. The compatibility candidate therefore produces ciphertext that is reversible by anyone who knows the source constant.

Both bounded client policies passed the same exact package gates. Explicit-key-only is the stronger **client/owned-deployment policy** because it publishes the optional identity header only when an operator supplies a valid private key.

That does not prove the hosted Context7 receiver accepts arbitrary client-selected keys. The public repository exposes the producer but not the hosted receiver/decryptor or its key-provisioning contract. Hosted and public-upstream policy therefore remain `Unknown / HOLD`.

## Question and candidates

The accepted malformed/runtime-failure repair already omits `mcp-client-ip` rather than publishing plaintext when encryption fails. The remaining client-side question was what to do when `CLIENT_IP_ENCRYPTION_KEY` is absent or empty.

### Compatibility retained

Keep the public fallback key. Preserve the header under absent and empty configuration, while stating that the ciphertext is reversible obfuscation rather than confidentiality.

### Explicit key only

Remove the public fallback. Publish the optional header only when a valid explicit 64-hex key is configured. Under absent, empty, malformed, or runtime-failed encryption, omit only `mcp-client-ip` with fixed diagnostics and retain unrelated headers and service operation.

## Predeclared client-policy criteria

The selected client policy must:

- avoid claiming confidentiality from a public fixed key;
- never fall back to plaintext;
- preserve service availability and unrelated headers;
- preserve metadata encrypted with a valid explicit key;
- avoid retaining the raw IP, key, or caught exception text in diagnostics;
- emit no key diagnostic when no client IP exists;
- pass target formatting, focused controls, typecheck, build, complete package tests, lint, and diff hygiene;
- keep hosted receiver compatibility, ciphertext authenticity, production prevalence, and upstream acceptance outside the claim unless separately established.

## Exact execution

Both rows checked out the literal Fieldwork comparison head and exact public target source on Ubuntu 24.04 with Node 22 and pnpm 10. Both applied the accepted malformed/runtime omission patch with zero fuzz. The explicit row then applied the explicit-key-only delta.

### Compatibility retained

Job `91247126130`: success.

- focused default-key and accepted encryption controls: 6/6 passed;
- complete MCP package suite: 52/52 passed across five test files;
- typecheck and build: success;
- lint, target formatting, and diff hygiene: success;
- artifact `8804020681`;
- artifact digest `sha256:fc13c053065673e9f8179f989ca0bceaf80528f1ff5c52d814d973050e965003`;
- retained diff SHA-256 `ec63c7f4dfa096fa1900ea920301a53d7291bbf7725b00073e567e202e49e770`;
- exact retained changed files:
  - `packages/mcp/src/lib/encryption.ts`;
  - `packages/mcp/test/default-key-policy.test.ts`.

Observed: absent and empty configuration emit ciphertext that decrypts to the exact synthetic client IP using the public source constant. No configuration diagnostic is emitted.

### Explicit key only

Job `91247126050`: success.

- focused default-key and accepted encryption controls: 6/6 passed;
- complete MCP package suite: 52/52 passed across five test files;
- typecheck and build: success;
- lint, target formatting, and diff hygiene: success;
- artifact `8804022360`;
- artifact digest `sha256:3a98a54d3d162dc9d96126a323042b75f5537f16ac64d38de1d0525b0de2aa4c`;
- retained diff SHA-256 `4b6d6ce3ef8ba4cd7a02bce79e5dcc5e5219331215c3bbee9d767ee4d7aac550`;
- exact retained changed files:
  - `packages/mcp/src/lib/encryption.ts`;
  - `packages/mcp/test/default-key-policy.test.ts`.

Observed:

- absent and empty configuration omit `mcp-client-ip` with fixed diagnostics;
- no client IP produces no key-configuration diagnostic;
- a valid explicit synthetic key retains ciphertext and decrypts to the exact synthetic IP with that key;
- the same ciphertext does not decrypt to the exact IP with the public fallback constant;
- malformed configuration and injected cipher failure omit metadata without raw IP, key, or exception text;
- session, authorization, transport, client, source, and version headers remain available.

## Artifact and receipt identity

Independent artifact inspection confirmed both uploaded target packages are self-contained for the executed surface. Each retained applied diff contains the exact product file and shared target-native control listed above.

The immutable artifact receipts use custom conditional strings such as `target-executed-when-focused-passes`. Those strings are not Fieldwork evidence classes and remain immutable historical data.

The committed workflow-free receipts supersede that vocabulary with claim-scoped records containing:

- `evidenceClass: target-executed`;
- exact supporting step and `success` status;
- exact Fieldwork and target heads;
- artifact ID and digest;
- applied-diff SHA-256;
- exact changed-file list;
- explicit `notClaimed` boundaries.

No rerun is required for this receipt normalization because no target byte, behavior claim, artifact, or selection criterion changed.

## Decision

### Client / owned deployment

`SELECT EXPLICIT-KEY-ONLY`.

Both candidates satisfy the named package compatibility and availability controls. Compatibility retained fails the client-local confidentiality criterion by construction: the key needed to recover the identity value is published in source and was used successfully in the exact target control.

Explicit-key-only changes only optional metadata publication under missing configuration and grants less identity-disclosure authority.

### Hosted Context7 and public upstream

`HOLD / UNKNOWN`.

Local success with a synthetic explicit key does not prove the hosted receiver knows or accepts arbitrary client-selected keys. Public receiver source or an authorized end-to-end contract is absent. Prior upstream rejection of omission should remain relevant precedent, but it does not supply the missing technical rationale.

Do not present this packet as an upstream-ready source repair or hosted compatibility proof.

## Evidence table

| Claim | Evidence class | Limit |
| --- | --- | --- |
| Public fallback ciphertext is recoverable with the source constant. | `target-executed` | exact synthetic IP and exact public source |
| Explicit-key-only omits absent/empty optional metadata. | `target-executed` | client/package behavior only |
| No client IP produces no key diagnostic. | `target-executed` | exact focused control |
| Valid explicit-key ciphertext remains supported. | `target-executed` | synthetic key; local producer/decryptor |
| Public fallback does not recover explicit-key ciphertext to the exact IP. | `target-executed` | exact synthetic discriminator |
| Both candidates pass the complete MCP package gate. | `target-executed` | Ubuntu 24.04 / Node 22 / package scope |
| Hosted receiver accepts arbitrary explicit keys. | `not established` | receiver/provisioning contract unavailable |
| Ciphertext authenticity. | `not established` | AES-CBC integrity is separate |
| Production prevalence or migration cost. | `not established` | no production deployment |
| Upstream acceptance or merge readiness. | `not established` | no upstream contact authorized |

## Limits

All values were synthetic and all execution was local or mocked. The comparison did not make a hosted Context7 request, use a usable credential, access private data, contact Redis, or exercise production deployment.

AES-CBC authenticity and tamper detection remain separate. Behavior outside the named Ubuntu/Node environment is unmeasured.

## Transition

1. run Fieldwork integrity on the workflow-free receipt-normalization head;
2. obtain eligible independent complete-diff review of the five-file package;
3. for an owned deployment, integrate the explicit-key-only source and target-native controls with operator-facing configuration/help;
4. for public upstream consideration, first resolve the receiver/key-provisioning contract or preserve the hold;
5. public upstream contact remains separately authorized.

No merge, release, deployment, credential use, private-data access, spending, or public-upstream interaction is included or authorized.
