# cmux remote resource bounds promoted — 2026-09-01

Owned fork: `teamleaderleo/cmux`  
Code branch: `fix/remote-resource-bounds`  
Promoted commit: `e2ed1cf14ad4f14d404b5a834a39689cf470af7c`  
Upstream contact authorized: `false`

## What changed

The two previously measured remote-retention candidates now live in real source paths in the cmux fork rather than being applied only as Fieldwork patch overlays.

Promoted production source includes:

- `Packages/macOS/CmuxRemoteDaemon/Sources/CmuxRemoteDaemon/Client/RemoteDaemonEventDeliveryQueue.swift`
- `Packages/macOS/CmuxRemoteDaemon/Sources/CmuxRemoteDaemon/Client/RemoteDaemonRPCClient.swift`
- `Packages/macOS/CmuxRemoteDaemon/Sources/CmuxRemoteDaemon/Client/RemoteDaemonRPCClient+Events.swift`
- `Packages/macOS/CmuxRemoteDaemon/Sources/CmuxRemoteDaemon/Client/RemoteDaemonRPCClient+RPC.swift`
- `Packages/macOS/CmuxRemoteWorkspace/Sources/CmuxRemoteWorkspace/Tunnel/RemoteProxyOutputBudget.swift`
- `Packages/macOS/CmuxRemoteWorkspace/Sources/CmuxRemoteWorkspace/Tunnel/RemoteDaemonProxySession.swift`
- `Packages/macOS/CmuxRemoteWorkspace/Sources/CmuxRemoteWorkspace/Rewriters/RemoteLoopbackHTTPResponseStreamRewriter.swift`

Deterministic regression coverage was promoted alongside the source. The 200 MiB event-delivery and slow-reader load harnesses remain experiment-only and were deliberately excluded from the production-source commit.

## RPC event-delivery owner

The production event queue now owns decoded stream/PTY payload backlog before subscriber callback dispatch. Current configured limits are:

- proxy subscription: 96 MiB / 65,536 events;
- PTY subscription: 16 MiB / 16,384 events;
- shared RPC-client process budget: 128 MiB / 131,072 events;
- drain batch: 16 callbacks.

On overflow, queued payload is purged, budget reservations are released, and the overflowing subscription is retired immediately so later frames stop reaching base64 decode. Already-admitted delivery retains FIFO ordering through one terminal error callback.

## Proxy local-send owner

The local proxy output path now reserves capacity before `NWConnection.send` and releases it through content-processed completion/reservation teardown. Current configured limits are:

- per proxy session: 96 MiB / 65,536 sends;
- process-wide: 256 MiB / 262,144 sends;
- loopback HTTP response header buffering: 64 KiB.

Capacity exhaustion closes the affected stream rather than dropping TCP payload bytes.

## Direct-source verification

Promotion workflow run `33573850827`, job `100073397892`, started from the already-green candidate stack, removed experiment-only load suites, staged only production source plus deterministic tests, and ran both packages against the actual promoted files:

- `swift test --package-path Packages/macOS/CmuxRemoteDaemon` — success;
- `swift test --package-path Packages/macOS/CmuxRemoteWorkspace` — success.

The promotion job then committed `fix(remote): bound event and proxy output retention` as `e2ed1cf14ad4f14d404b5a834a39689cf470af7c` and deleted its own one-off promotion workflow.

The earlier full composition gate remains the scaling evidence for the same code stack: run `33571263196` passed the complete daemon package, complete workspace package, healthy 200-session proxy control, the 96 MiB per-session slow-reader breaker, and the 256 MiB process-wide breaker.

## Evidence boundary

This promotion establishes that the measured candidate is now real source in the owned cmux fork and that both Swift packages pass against that source. It does not authorize an upstream PR or maintainer contact. The large load probes and candidate-history patch files stay available on the investigation branch as reproduction material.
