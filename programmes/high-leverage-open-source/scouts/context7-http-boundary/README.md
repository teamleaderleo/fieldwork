# Context7 HTTP bind and forwarded-identity probe

Parent finding: Fieldwork #333.

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

## Controls

The workflow builds exact Context7 source, then:

- starts the real published HTTP CLI with inert Redis environment values;
- verifies the startup message names localhost;
- inspects the actual listening socket;
- reaches `/ping` through loopback;
- reaches `/ping` through the runner's non-loopback IPv4 address;
- sends a realistic anonymous `/mcp` preflight requesting POST plus Authorization and `X-Context7-API-Key`;
- verifies the response returns wildcard CORS and allows those methods and headers;
- runs target-native Vitest controls proving client-supplied forwarded identity overrides socket identity;
- feeds that selected identity into `generateHeaders()`, using the exact `CLIENT_IP_ENCRYPTION_KEY` variable with a known test-only key;
- decrypts `mcp-client-ip` locally and verifies it represents the caller-selected forwarded value;
- retains a strict reversing control requiring socket identity to win without an explicit trusted-proxy policy;
- reruns existing Context7 client-IP tests, lint, formatting, typecheck, and build;
- uploads one exact-head JSON receipt on success or failure.

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

## Durable receipt

The workflow uploads `context7-http-boundary-receipt.json` with:

- Fieldwork and target heads;
- workflow-step outcomes;
- startup text and listener address;
- loopback and non-loopback reachability;
- the exact CORS request and response;
- parser and parser-to-metadata outcomes;
- explicit claim classes and exclusions.

The receipt assembly and artifact upload use `if: always()` so a failed characterization retains the partial evidence available before failure.

## Credential and network boundary

The real server constructs its Redis client during startup. The probe supplies syntactically valid inert values and avoids MCP initialize/session requests, so no Redis or Context7 API call is required. `/ping`, socket inspection, OPTIONS preflight, parser controls, encryption, decryption, and receipt generation remain local to the hosted GitHub runner.

The probe uses no Context7 API key, no usable Redis credential, no account, no payment, no private repository, and no public upstream interaction.

## Evidence limit

The probe establishes local bind, presentation, CORS, parser, and parser-to-header behavior on the Linux hosted runner. It does not claim every firewall, browser private-network policy, container runtime, IPv6 configuration, or operating system exposes the listener identically. It also does not execute the hosted Context7 API or establish how the hosted service interprets the metadata.
