# Era scope amendment for Lane #66

Date: 2026-07-30

This amendment narrows the protocol-era wording in the Lane #66 report without changing its executed finding.

## Correct scope

The retry-coupling reproduction is a finding in the **MCP TypeScript SDK v2 package's 2025-era compatibility path**.

The v2 SDK speaks the 2025-era protocol by default. Protocol revision `2026-07-28` requires explicit negotiation or pinning.

The affected 2025-era Streamable HTTP contract permits:

- POST responses carried by resumable SSE streams;
- event IDs and `Last-Event-ID` replay;
- server-directed polling through repeated GET requests;
- stream-local SSE `retry` instructions;
- multiple simultaneous SSE streams.

Under that supported contract, Lane #66 confirmed that stream A can retain its own replay ID while using stream B's later retry value.

## Native 2026 control

Compliant `2026-07-28` Streamable HTTP:

- has no standalone GET stream endpoint;
- has no protocol-level session;
- does not support resumable SSE or `Last-Event-ID`;
- cancels by closing the request's SSE response stream.

The owned-fork protocol-era probe confirmed that a compliant modern SSE response ending without an event ID schedules no GET resumption. Therefore the Lane #66 mechanism is not a compliant native-2026 reconnect defect.

A server claiming `2026-07-28` that nevertheless emits a resumable event ID can still provoke the generic transport into a legacy-style GET. That is a separate robustness boundary, not the basis of the Lane #66 issue packet.

## Wording correction

Read the report's phrase “credible v2 issue candidate” as:

> credible issue candidate in the v2 SDK's supported legacy Streamable HTTP compatibility behavior.

The package/version attribution remains `@modelcontextprotocol/client@2.0.0`; the protocol attribution is 2025-era, chiefly `2025-11-25` for the reviewed contract.

## Verification

- original Lane #66 matrix: workflow run `30476941445`, Node 20/22/24;
- protocol-era control matrix: workflow run `30479313714`, Node 20/22/24;
- inspected Node 22 final suite: 39 files and 815 tests passed;
- upstream contact remained unauthorized and unused.
