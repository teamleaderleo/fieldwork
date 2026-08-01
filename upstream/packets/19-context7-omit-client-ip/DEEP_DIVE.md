# Deep dive — unit 19, Context7 client-IP encryption fallback

## In simple words

Context7's MCP server adds an `mcp-client-ip` request header. A module-level key selects AES-256-CBC encryption. When the configured key is malformed or encryption throws, current source returns the input IP unchanged and places that plaintext value in the same header.

Fieldwork's candidate changes the helper return type to `string | undefined`, returns `undefined` for those two failures, and adds the header only after successful encryption. Exact target-native tests and package gates passed. The technical result is coherent.

Upstream already reviewed the same contract. Issue #1965 and PR #2104 proposed omission on failure and were closed after a maintainer said the behavior was not intended. That public decision owns the current disposition: retain the evidence and retire the contribution.

## Governing invariant

> A contribution that changes client-IP fallback semantics requires current maintainer acceptance of the new wire behavior; local safety preference alone cannot override an explicit upstream decision.

## Current behavior

- entrypoint: `generateHeaders(context)` in `packages/mcp/src/lib/encryption.ts`
- state owner: module-level `ENCRYPTION_KEY`, selected once from `CLIENT_IP_ENCRYPTION_KEY || DEFAULT_ENCRYPTION_KEY`
- caller-visible result: a `Record<string, string>` containing base telemetry headers and optional session, auth, client, transport, and client-IP metadata
- side effects: fixed or exception-bearing `console.error` diagnostics on encryption failures
- cleanup owner: none; the helper is synchronous and allocates only local buffers/cipher objects
- persistence or publication boundary: the returned map is used for outbound Context7 API request headers
- failure ordering: key validation precedes IV generation and cipher creation; either failure path currently returns the raw input IP

## Source map

| Area | Exact path and symbol | Responsibility | Relevant tests |
| --- | --- | --- | --- |
| metadata encryption and header assembly | [`encryption.ts@594a731`](https://github.com/upstash/context7/blob/594a73133e14631af8c915a1b4f2c8039c964fe1/packages/mcp/src/lib/encryption.ts) | validates key, encrypts client IP, assembles headers | [retained regression](./fixtures/malformed-key-omit-metadata.test.ts) |
| package commands | [`package.json@594a731`](https://github.com/upstash/context7/blob/594a73133e14631af8c915a1b4f2c8039c964fe1/packages/mcp/package.json) | test, format, lint, typecheck, build gates | workflow `30635777158` |
| exact upstream prior implementation | [`encryption.ts@5a36c50`](https://github.com/upstash/context7/blob/5a36c505e88da3fe74d34ae3f4dd01124031bb88/packages/mcp/src/lib/encryption.ts) | returns `undefined` and conditionally adds header | PR #2104 had no added tests |
| Fieldwork candidate | [retained patch](./patches/malformed-key-omit-metadata.patch) | same core contract plus bounded diagnostics and tests | run `30635777158`, job `91172880796` |

## Reproduction or characterization

### Setup

- exact upstream revision: `594a73133e14631af8c915a1b4f2c8039c964fe1`
- package: `@upstash/context7-mcp` `3.2.5`
- environment: Ubuntu 24.04, Node `22.23.1`, pnpm `10.34.5`, Vitest `4.1.9`
- fixture: selected IP `198.51.100.77`; malformed runtime-composed key; mocked `crypto.randomBytes` failure
- baseline workflow: PR #343, run `30629165557`, job `91151287009`
- candidate workflow: run `30635777158`, job `91172880796`

### Baseline result

The compiled target helper selected `198.51.100.77`. A malformed configured key logged the invalid-key diagnostic and returned `198.51.100.77` unchanged as `mcp-client-ip`. Reject-or-omit behavior was absent.

### Candidate result

The exact candidate patch:

- retained ciphertext-shaped metadata under a valid explicit key;
- omitted `mcp-client-ip` for an invalid key;
- omitted `mcp-client-ip` after injected cipher failure;
- preserved source, version, session, authorization, client, and transport headers;
- emitted fixed diagnostics that excluded the raw IP, configured key, and injected exception text.

Focused controls passed `3/3`; the complete package suite passed `49/49`; format, lint, typecheck, and build passed.

## Failure model

1. `generateHeaders()` receives a context containing `clientIp`.
2. It calls `encryptClientIp(clientIp)`.
3. `validateEncryptionKey()` rejects a malformed configured key, or `randomBytes`/cipher work throws.
4. Current source logs and returns `clientIp`.
5. `generateHeaders()` assigns that returned plaintext to `headers["mcp-client-ip"]`.

Steps 1–5 are source-read. The malformed-key sequence was target-executed. Runtime cipher failure was target-executed against the candidate through a controlled mock; the baseline catch behavior is directly source-supported.

## Consequence and claim boundary

### Established

- malformed configured keys can produce plaintext client-IP metadata in the self-hosted MCP helper;
- the candidate eliminates plaintext fallback in the two named failure paths by omitting the optional field;
- unrelated header generation and package gates remain green under the exact test matrix;
- upstream previously received and declined the same omission-on-failure wire contract.

### Inferred

- omission can reduce downstream client-IP availability during local configuration or crypto failures;
- upstream may depend on receiving a client-IP-shaped value even when encryption fails, which is consistent with the maintainer decision but was not explained publicly.

### Unknown or unmeasured

- hosted Context7 treatment of the header;
- production frequency of malformed keys or runtime crypto errors;
- telemetry, billing, abuse, or routing dependency on the field;
- every operating system, Node/OpenSSL combination, deployment topology, and package consumer;
- maintainer reasoning beyond the concise public statement.

## Selected implementation

No implementation is selected for upstream delivery. The retained candidate is the strongest technical version if maintainers later invite this behavior:

- `encryptClientIp()` owns encryption success or omission;
- failure returns `undefined` instead of a value that can be confused with ciphertext;
- `generateHeaders()` owns conditional field insertion;
- fixed diagnostics avoid retaining sensitive inputs or exception text;
- every unrelated header follows the existing path.

The implementation remains archived because its core contract matches declined PR #2104.

## Compatibility analysis

- public API: internal helper only; `generateHeaders()` keeps its exported type
- source compatibility: internal return type widens to `string | undefined`
- binary or wire compatibility: failure requests lose `mcp-client-ip`; this is the principal behavioral change
- persistence or format compatibility: no persisted format; header absence replaces plaintext fallback
- platform behavior: synchronous Node crypto; executed on Linux/Node 22
- performance and allocation: no meaningful success-path change; failure path avoids attaching one header
- cancellation, retry, and recovery: not applicable; synchronous helper
- generated output: TypeScript build passed; no checked-in generated file change
- migration or rollback: one production hunk plus one test file; rollback restores current fallback

## Adversarial and edge controls

- valid explicit key: ciphertext retained and differs from input
- malformed key: metadata omitted; fixed diagnostic only
- runtime cipher failure: metadata omitted; exception text excluded
- unrelated-resource isolation: session, authorization, client, transport, source, and server-version headers retained
- missing/empty key: intentionally excluded from the candidate because current source uses the public default key successfully
- repeated failure/log volume: not measured
- platform boundary: Linux/Node 22 only

## Review risks

- **Wire compatibility:** omission may violate an upstream service expectation. The public maintainer rejection is decisive evidence that this risk or product intent outweighs the proposed change today.
- **Privacy framing:** successful encryption under the fixed public default key establishes encoding, not confidentiality. The packet makes no broader confidentiality claim.
- **Exception handling:** PR #2104 retained exception text in logs; the Fieldwork candidate improves this by using fixed diagnostics. That improvement does not alter the declined omission contract.
- **Duplicate contribution:** re-opening a polished version would still repeat issue #1965 and PR #2104.

## Reversing evidence

Reopen the conclusion only if:

- a Context7 maintainer explicitly requests fail-closed omission or a design discussion;
- current source replaces the fallback semantics or introduces a documented contract that supports omission;
- a new accepted public issue identifies a materially different compatibility boundary;
- the user explicitly authorizes revisiting the declined behavior and supplies a new rationale.

## Adjacent work excluded

- public fixed default-key confidentiality;
- missing and empty key policy;
- AES-CBC authenticity or tamper detection;
- forwarded-IP trust and proxy-chain parsing;
- HTTP listener, reachability, CORS, authentication, and hosted service behavior;
- documentation-only explanation of current intended fallback.
