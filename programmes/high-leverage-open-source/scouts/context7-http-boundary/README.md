# Context7 HTTP bind and forwarded-identity probe

Parent finding: Fieldwork #333.

## Question

Does Context7 HTTP mode present itself as loopback-only while binding an unspecified address, and can a direct caller control the client identity forwarded to the hosted Context7 API?

## Exact target

- repository: `upstash/context7`;
- source head: `594a73133e14631af8c915a1b4f2c8039c964fe1`;
- package: `@upstash/context7-mcp` `3.2.5`;
- HTTP server: `packages/mcp/src/index.ts`;
- IP parser: `packages/mcp/src/lib/client-ip.ts`.

## Source prediction

The exact source:

1. calls `app.listen(port)` without a host;
2. logs `http://localhost:<port>/mcp`;
3. exposes anonymous `/mcp` and authenticated `/mcp/oauth`;
4. emits wildcard CORS and permits Authorization/API-key headers;
5. accepts `X-Forwarded-For` directly and prefers its first public-looking value over the socket address;
6. falls back to the first forwarded value even when every forwarded address is private.

Node documents an omitted listen host as the unspecified IPv6 address `::` when available or `0.0.0.0` otherwise.

## Controls

The workflow builds exact Context7 source, then:

- starts the real published HTTP CLI with inert Redis environment values;
- verifies the startup message names localhost;
- inspects the actual listening socket;
- reaches `/ping` through loopback;
- reaches `/ping` through the runner's non-loopback IPv4 address;
- verifies anonymous `/mcp` preflight returns wildcard CORS and Authorization/API-key header allowance;
- runs target-native Vitest controls proving client-supplied forwarded identity overrides socket identity;
- retains a strict reversing control requiring socket identity to win without an explicit trusted-proxy policy;
- reruns the existing Context7 client-IP tests, lint, formatting, typecheck, and build.

## Credential and network boundary

The real server constructs its Redis client during startup. The probe supplies syntactically valid inert values and avoids MCP initialize/session requests, so no Redis or Context7 API call is required. `/ping`, socket inspection, OPTIONS preflight, and the parser controls remain local to the hosted runner.

The probe uses no Context7 API key, no usable Redis credential, no account, no payment, no private repository, and no public upstream interaction.

## Evidence limit

The probe establishes local bind, presentation, CORS, and forwarded-header behavior on the Linux hosted runner. It does not claim every firewall, browser private-network policy, container runtime, IPv6 configuration, or operating system exposes the listener identically.
