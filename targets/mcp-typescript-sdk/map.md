# Target Map: MCP TypeScript SDK

Repository: https://redirect.github.com/modelcontextprotocol/typescript-sdk

## In simple words

A TypeScript implementation of the Model Context Protocol. It sits between agent applications and tools or servers, so transport, session, cancellation, capability, and error semantics can affect every integration above it.

## Areas worth understanding

- client and server lifecycle;
- transports and reconnection;
- capability negotiation;
- request identity and cancellation;
- progress, partial results, and errors;
- schema and runtime agreement;
- compatibility across protocol and SDK versions;
- tests around teardown and recovery.

## Evidence we can produce

- synthetic client/server pairs;
- malformed and reordered message fixtures;
- transport interruption experiments;
- compatibility matrices;
- realistic Stensibly integration trials;
- type/runtime mismatch reproductions.

## Current submitted issue

- [Legacy Streamable HTTP reconnects continue after the client request times out](https://redirect.github.com/modelcontextprotocol/typescript-sdk/issues/2615)
- Filed by the owner after review of Campaign #65 / Lane #67 evidence.
- Filing is complete; the defect is not fixed and no implementation commitment is recorded.
- Further upstream interaction requires a new explicit owner decision.

## Entry standard

Identify whether a behavior belongs to the protocol, SDK, transport, or application. Record exact protocol and SDK revisions before interpreting results.

## Stop conditions

- the claim depends on an unspecified protocol behavior;
- the scenario cannot distinguish SDK behavior from application misuse;
- the work is only example or documentation cleanup;
- current contribution policy makes implementation inappropriate without direction.
