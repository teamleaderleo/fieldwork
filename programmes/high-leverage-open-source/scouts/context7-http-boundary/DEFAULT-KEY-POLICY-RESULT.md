# Context7 client-IP default-key policy result

## In simple words

Context7 adds an optional encrypted client-IP header to requests sent by its MCP server. Exact source uses a public fixed key when no key is configured, so the resulting ciphertext can be reversed by anyone who knows the source constant. Two exact-source candidates both preserve package compatibility, but only explicit-key-only emission avoids presenting publicly reversible identity metadata as confidential. The selected direction is to omit the optional header unless an operator supplies a valid explicit key.

Parent repair: PR #397  
Comparison PR: #420  
Exact target: `upstash/context7@594a73133e14631af8c915a1b4f2c8039c964fe1`  
Exact target-executed Fieldwork head: `8a1d2ae75d4fe0dc73c9178ba05a31abff72abee`  
Workflow: `30658005611`, attempt `1`  
State: `target-executed / workflow-retirement`  
Upstream contact authorized: no

## Question and candidates

The accepted malformed/runtime-failure repair already omits `mcp-client-ip` rather than publishing plaintext when encryption fails. The remaining question was what to do when `CLIENT_IP_ENCRYPTION_KEY` is absent or empty.

### Compatibility retained

Keep the public fallback key. Preserve the header under absent and empty configuration, while stating that the ciphertext is not a confidentiality boundary.

### Explicit key only

Remove the public fallback. Publish the optional header only when a valid explicit 64-hex key is configured. Under absent, empty, malformed, or runtime-failed encryption, omit only `mcp-client-ip` with fixed diagnostics and retain unrelated headers and service operation.

## Predeclared criteria

The selected policy must:

- avoid claiming confidentiality from a public fixed key;
- never fall back to plaintext;
- preserve service availability and unrelated headers;
- preserve metadata encrypted with a valid explicit key;
- avoid retaining the raw IP, key, or caught exception text in diagnostics;
- pass target formatting, focused controls, typecheck, build, full package tests, lint, and diff hygiene;
- keep hosted behavior and ciphertext authenticity outside the claim unless separately executed.

## Exact execution

Both rows checked out the literal Fieldwork comparison head and exact public target source on Ubuntu 24.04 with Node 22 and pnpm 10. Both applied the accepted malformed/runtime omission patch with zero fuzz. The explicit row then applied the explicit-key-only delta.

### Compatibility retained

Job `91247126130`: success.

- focused default-key and accepted encryption controls: 6/6 passed;
- complete MCP package suite: 52/52 passed across five test files;
- typecheck: success;
- build: success;
- lint: success;
- target formatting and diff hygiene: success;
- artifact `8804020681`;
- artifact digest `sha256:fc13c053065673e9f8179f989ca0bceaf80528f1ff5c52d814d973050e965003`;
- exact retained diff SHA-256 `ec63c7f4dfa096fa1900ea920301a53d7291bbf7725b00073e567e202e49e770`.

Observed result: when the key is absent or empty, exact candidate source emits ciphertext that decrypts to the exact synthetic client IP using the public source constant. No configuration diagnostic is emitted.

### Explicit key only

Job `91247126050`: success.

- focused default-key and accepted encryption controls: 6/6 passed;
- complete MCP package suite: 52/52 passed across five test files;
- typecheck: success;
- build: success;
- lint: success;
- target formatting and diff hygiene: success;
- artifact `8804022360`;
- artifact digest `sha256:3a98a54d3d162dc9d96126a323042b75f5537f16ac64d38de1d0525b0de2aa4c`;
- exact retained diff SHA-256 `4b6d6ce3ef8ba4cd7a02bce79e5dcc5e5219331215c3bbee9d767ee4d7aac550`.

Observed result:

- absent and empty configuration omit `mcp-client-ip` with fixed diagnostics;
- no client IP produces no key-configuration diagnostic;
- a valid explicit synthetic key retains ciphertext and decrypts to the exact synthetic IP with that key;
- the same ciphertext does not decrypt to the exact IP with the public fallback constant;
- malformed configuration and injected cipher failure omit metadata without raw IP, key, or exception text;
- session, authorization, transport, client, source, and version headers remain available.

## Decision

`SELECT EXPLICIT-KEY-ONLY`.

Both candidates satisfy target compatibility and service-availability controls. Compatibility retained fails the confidentiality criterion by construction: the key needed to recover the identity value is published in source and was used successfully in the exact target control. Explicit-key-only removes that ambiguity while changing only optional metadata publication under missing configuration.

The losing compatibility-retained policy remains viable only when the product deliberately prioritizes default telemetry continuity and clearly states that the public-key encoding is reversible and non-confidential.

## Evidence labels

- **Observed:** exact target source uses the public fallback when the environment key is absent or empty.
- **Observed:** the compatibility candidate's emitted value decrypts with the public source constant.
- **Observed:** both candidates pass the named focused and complete MCP package gates.
- **Observed:** the explicit candidate preserves valid explicit-key metadata and omits absent/empty metadata.
- **Inferred:** explicit-key-only is the narrower authority choice because the header is optional and missing configuration no longer publishes reversibly encoded identity metadata.
- **Unknown:** production configuration prevalence, hosted treatment of omitted metadata, operator migration cost, and maintainer preference.

## Limits

All values were synthetic and all execution was local or mocked. The comparison did not make a hosted Context7 request, use a usable credential, access private data, contact Redis, or exercise production deployment.

AES-CBC authenticity and tamper detection remain separate. The result does not establish configuration prevalence, production impact, hosted acceptance, upstream acceptance, merge readiness, or behavior outside the named Ubuntu/Node environment.

## Transition

Retain the explicit delta, shared target control, this result, and exact candidate receipts. Remove the temporary comparison workflow from the canonical review head. A later source packet should integrate target-native tests and operator-facing configuration/help wording, then execute an exact target branch without Fieldwork-only carrier machinery.

No merge, release, deployment, credential use, private-data access, spending, or public-upstream interaction is included or authorized.
