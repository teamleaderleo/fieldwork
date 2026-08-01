# Upstream issue draft — client-IP metadata falls back to plaintext when encryption fails

Draft status: `retired — exact public issue already closed not planned`  
Public interaction authorized: `no`

## Filing decision

Do not file a new issue. [`upstash/context7#1965`](https://github.com/upstash/context7/issues/1965) already contains the same source observation, impact description, expected behavior, and fail-closed omission proposal. It was closed `not planned` on 2026-04-03 after a maintainer stated that omission was not the intended behavior. Refiling would duplicate a resolved public discussion.

The text below is retained only as a compact archival draft for a maintainer-invited reopening.

---

## Summary

The MCP header helper returns the raw client IP when `CLIENT_IP_ENCRYPTION_KEY` is malformed or when AES encryption throws. The returned value is then sent in the same `mcp-client-ip` header used for encrypted values.

Could the intended failure contract be clarified? A fail-closed option would omit the optional header when encryption cannot complete while leaving all other request headers unchanged.

## Reproduction

1. Run `@upstash/context7-mcp` from commit `594a73133e14631af8c915a1b4f2c8039c964fe1` with a malformed nonempty `CLIENT_IP_ENCRYPTION_KEY`.
2. Call `generateHeaders()` with a client IP.
3. Inspect `mcp-client-ip` and the emitted diagnostic.

Minimal source path:

```text
packages/mcp/src/lib/encryption.ts
validateEncryptionKey() -> encryptClientIp() -> generateHeaders()
```

## Observed behavior

`encryptClientIp()` logs the invalid-key diagnostic and returns the input IP. `generateHeaders()` assigns that value to `mcp-client-ip`. The same plaintext return occurs in the catch path after a runtime crypto error.

## Expected behavior for a fail-closed contract

When encryption cannot complete, omit `mcp-client-ip` and continue generating unrelated request headers. Emit a fixed local diagnostic that excludes the raw IP, configured key, and caught exception text.

## Current source observation

At [`encryption.ts@594a731`](https://github.com/upstash/context7/blob/594a73133e14631af8c915a1b4f2c8039c964fe1/packages/mcp/src/lib/encryption.ts), both failure paths return `clientIp`, and the caller assigns the result without distinguishing ciphertext from plaintext.

## Candidate direction

- change `encryptClientIp()` to return `string | undefined`;
- return `undefined` for malformed-key and runtime cipher failures;
- add `mcp-client-ip` only when encryption returns a value;
- keep successful encryption and all unrelated headers unchanged;
- use fixed diagnostics without sensitive or exception text.

## Compatibility and risks

- downstream client-IP metadata becomes absent during local encryption failures;
- any service dependency on the existing plaintext fallback needs explicit consideration;
- this proposal does not change missing/empty-key use of the fixed public default key;
- the wire behavior change is the same core choice previously declined in PR #2104.

## Evidence limits

- executed on Ubuntu 24.04 with Node 22 against the local MCP package;
- no hosted Context7 API or service-side consumer was exercised;
- production frequency and impact are unmeasured;
- default-key confidentiality and AES-CBC authenticity are separate questions.

## Versions and environment

- project commit: `594a73133e14631af8c915a1b4f2c8039c964fe1`
- MCP package: `3.2.5`
- platform: Ubuntu 24.04
- runtime: Node `22.23.1`
- relevant configuration: malformed nonempty `CLIENT_IP_ENCRYPTION_KEY`

## Additional context

- Existing report: [`#1965`](https://github.com/upstash/context7/issues/1965)
- Existing implementation: [`#2104`](https://github.com/upstash/context7/pull/2104)
- Adjacent default-key discussion: [`#1366`](https://github.com/upstash/context7/issues/1366)

---

## Filing checklist

- [x] Current upstream issue and PR search repeated on `2026-08-01`.
- [x] Exact duplicate issue and PR identified.
- [x] Current source confirmed unchanged at the exact executed revision.
- [x] Severity and prevalence wording bounded.
- [x] Private and Fieldwork-only links excluded from the archival public draft.
- [ ] Current target issue template and AI-disclosure policy rechecked if maintainers invite reopening.
- [ ] Exact user authorization to file recorded.

Current action: `do not file`.
