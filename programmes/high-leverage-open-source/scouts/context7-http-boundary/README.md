# Context7 HTTP bind and forwarded-identity probe

Parent finding: Fieldwork #333.

State: `target-executed / workflow-free`

## Question

Does Context7 HTTP mode present itself as loopback-only while binding an unspecified address, and can a direct caller control the client identity that Context7's local header generator places in outbound API metadata?

## Exact target

- repository: `upstash/context7`;
- source head: `594a73133e14631af8c915a1b4f2c8039c964fe1`;
- package: `@upstash/context7-mcp` `3.2.5`;
- HTTP server: `packages/mcp/src/index.ts`;
- IP parser: `packages/mcp/src/lib/client-ip.ts`;
- header generator: `packages/mcp/src/lib/encryption.ts`.

## Source prediction

The exact source:

1. calls `app.listen(port)` without a host;
2. logs `http://localhost:<port>/mcp`;
3. exposes anonymous `/mcp` and authenticated `/mcp/oauth`;
4. emits wildcard CORS and permits Authorization/API-key headers;
5. accepts `X-Forwarded-For` directly and prefers its first public-looking value over the socket address;
6. falls back to the first forwarded value even when every forwarded address is private;
7. constructs `ClientContext.clientIp` from that parser result in the HTTP route;
8. emits encrypted `mcp-client-ip` metadata from `ClientContext.clientIp` in `generateHeaders()`.

Node documents an omitted listen host as the unspecified IPv6 address `::` when available or `0.0.0.0` otherwise.

## Executed controls

The exact target workflow:

- started the real published HTTP CLI with inert Redis environment values;
- verified the startup message named localhost;
- inspected the actual listening socket;
- reached `/ping` through loopback;
- reached `/ping` through the runner's non-loopback IPv4 address;
- sent a realistic anonymous `/mcp` preflight requesting POST plus Authorization and `X-Context7-API-Key`;
- verified the response returned wildcard CORS and allowed those methods and headers;
- ran target-native Vitest controls proving client-supplied forwarded identity overrides socket identity;
- fed that selected identity into `generateHeaders()`, using the exact `CLIENT_IP_ENCRYPTION_KEY` variable with a known test-only key;
- decrypted `mcp-client-ip` locally and verified it represented the caller-selected forwarded value;
- retained a strict reversing control requiring socket identity to win without an explicit trusted-proxy policy;
- reran existing Context7 client-IP tests, lint, formatting, typecheck, and build;
- uploaded one exact-head JSON receipt.

## Exact execution receipt

- target-executed Fieldwork head: `76d4c73b7e1a779d69d9e07f1eee6370fb9eb072`;
- Context7 workflow: `30627822712`, success;
- job: `91147027515`, success;
- exact-head Fieldwork integrity: `30627822695`, success;
- artifact: `8792236985`;
- artifact digest: `sha256:7e5ecab111645209127587f10061609e7ff3aaf116098bfc67be9b0c81514d57`;
- inspected receipt JSON SHA-256: `8193c6f2b24246006177f66bcd6e3e2cf1cc48819ef6534ba1c548ce49b04249`;
- generated at: `2026-07-31T11:46:41.731Z`;
- runner family: `ubuntu-24.04`, Node 22.

Every recorded workflow phase was `success`: target verification, package build, network probe, identity suite, static/build gates, receipt assembly, and upload.

### Listener and preflight outcome

- startup text: `Context7 Documentation MCP Server v3.2.5 running on HTTP at http://localhost:38731/mcp`;
- actual listener: `*:38731`;
- loopback `/ping`: reached, returning the expected pong receipt;
- runner non-loopback IPv4 `/ping`: reached;
- realistic OPTIONS response: HTTP 200;
- `Access-Control-Allow-Origin: *`;
- allowed methods: GET, POST, OPTIONS, DELETE;
- allowed headers include Authorization and `X-Context7-API-Key`.

### Forwarded identity outcome

- existing Context7 client-IP suite: 34 passed;
- Fieldwork controls: four ordinary passes plus one intentional expected-failure repair discriminator;
- public forwarded IP overrides socket identity;
- an all-private forwarded list also overrides socket identity under current parser behavior;
- socket identity is used when the forwarded header is absent;
- caller-selected `198.51.100.77` reaches encrypted outbound `mcp-client-ip` metadata and decrypts back to the same value;
- trusted-proxy-first behavior is absent and remains the explicit reversing control.

The receipt records the parser and parser-to-metadata path as `target-executed`, HTTP route context wiring as `source-read`, hosted API receipt as `not-executed`, and browser private-network exposure as `not-claimed`.

## Claim classes

| Claim | Evidence class | Limit |
| --- | --- | --- |
| startup names localhost | target-executed on the Linux runner | one target revision and runner family |
| listener accepts the non-loopback runner address | target-executed on the Linux runner | browser policy, firewall, containers, IPv6, and other systems remain separate |
| realistic anonymous preflight receives wildcard CORS and credential-header allowance | target-executed on the Linux runner | static server response only; no browser private-network claim |
| forwarded caller value overrides socket identity | target-executed parser control | direct Express request object |
| parser-selected value becomes encrypted `mcp-client-ip` output | target-executed parser-to-header composition | local `generateHeaders()` execution; no hosted request |
| HTTP route places `getClientIp(req)` into `ClientContext.clientIp` | source-read | route composition is not invoked by the local parser/header test |
| hosted Context7 API receives or trusts that metadata | not executed | no hosted API call or server-side inspection |

## Encryption-key boundary

Exact source reads `CLIENT_IP_ENCRYPTION_KEY`. The metadata control sets that variable to a known test-only AES key and decrypts the generated value locally. The repository also contains a static fallback transport-format key, but this carrier does not claim that a hosted deployment uses the fallback or treats `mcp-client-ip` as authenticated identity.

Malformed-key plaintext fallback remains a separate question in PR #343.

## Selected repair family

The executed evidence supports two separable repairs for later source-candidate evaluation:

1. bind loopback by default, require explicit remote-host opt-in, and print the actual bound address;
2. ignore forwarded identity by default and accept it only under a bounded trusted-proxy, hop, or CIDR policy.

Authentication for remote binds and origin allowlisting remain additional deployment controls; they are not substitutes for an honest listener address or bounded identity trust.

## Credential and network boundary

The real server constructs its Redis client during startup. The probe supplied syntactically valid inert values and avoided MCP initialize/session requests, so no Redis or Context7 API call was required. `/ping`, socket inspection, OPTIONS preflight, parser controls, encryption, decryption, and receipt generation remained local to the hosted GitHub runner.

The probe used no Context7 API key, no usable Redis credential, no account, no payment, no private repository, and no public upstream interaction.

## Evidence limit

The probe establishes local bind, presentation, CORS, parser, and parser-to-header behavior on the Linux hosted runner. It does not claim every firewall, browser private-network policy, container runtime, IPv6 configuration, or operating system exposes the listener identically. It also does not execute the hosted Context7 API or establish how the hosted service interprets the metadata.

## Carrier retirement

The one-off workflow was removed after this receipt transfer. Its removal does not mean target behavior reran on the later cleanup head. The durable carrier is this report plus the exact network script and identity test.

The workflow-free branch still requires current-main packaging and exact-head Fieldwork integrity. No source repair, merge, deployment, real credential use, or public upstream interaction is authorized.
