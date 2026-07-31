# Context7 public default-key comparison

Parent repair: PR #397  
Owning finding: #333  
Exact target: `upstash/context7@594a73133e14631af8c915a1b4f2c8039c964fe1`  
State: `target-comparison-active`  
Upstream contact authorized: no

## Question

When `CLIENT_IP_ENCRYPTION_KEY` is absent or empty, exact source encrypts `mcp-client-ip` with a fixed key published in the repository. The output looks encrypted but does not create a confidentiality boundary from an observer who knows that constant.

Compare:

1. **compatibility-preserving claim narrowing** — keep the public fallback and state that default output has no confidentiality boundary;
2. **explicit-key-only emission** — publish client-IP metadata only when a valid key is explicitly configured; otherwise omit the optional header with fixed diagnostics.

## Predeclared criteria

The preferred repair must:

- never publish plaintext client IP after malformed configuration or runtime cipher failure;
- avoid describing public-key ciphertext as confidential;
- preserve legacy service availability and all unrelated headers;
- preserve ciphertext for an explicit valid key;
- avoid logging raw IP, key material, or caught exception text;
- preserve full MCP package tests, formatting, lint, typecheck, and build;
- keep ciphertext authenticity and hosted-provider behavior outside the claim unless separately executed.

## Exact controls

### Current-source characterization

With the environment variable absent and with it set to the empty string:

- generate `mcp-client-ip` through exact target source;
- require ciphertext shape;
- decrypt it with the fixed source constant;
- require the exact selected IP plaintext;
- require no configuration diagnostic.

### Explicit-key-only candidate

- absent key: omit metadata, retain unrelated headers, fixed diagnostic;
- empty key: same;
- malformed key: omit metadata, fixed diagnostic, no raw IP/key;
- explicit valid synthetic key: retain ciphertext and decrypt only with that key, not the public fallback;
- runtime cipher failure: omit metadata, fixed diagnostic, no exception/IP/key text;
- no client IP: require no encryption-key diagnostic;
- run focused controls and the complete target MCP package gate.

## Provisional selection

Select explicit-key-only emission if the exact target gate passes. The public fallback cannot satisfy the confidentiality criterion because its decryption key is a source constant. The header is already optional, so omission under missing configuration is a narrower authority choice than emitting reversibly encoded identity metadata.

The compatibility-preserving option remains a valid losing policy only when the product deliberately wants telemetry continuity and clearly states that the default encoding is not confidential.

## Boundaries

This comparison uses a synthetic test IP and synthetic test key, local mocks, and exact public source. It makes no hosted Context7 request and uses no account, usable credential, private data, Redis operation, payment, or provider capacity.

AES-CBC authenticity and tamper detection remain separate. A green result does not establish production configuration prevalence, hosted acceptance of omitted metadata, deployment behavior, or upstream acceptance.
