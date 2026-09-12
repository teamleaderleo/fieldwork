# Remote proxy stale-generation execution receipt

## In simple words

The exact-current cmux fork test proves the bug and the repair on the same source coordinate: the test-only commit lets retired tunnel A remove successor B, while the generation-fenced commit leaves B current. The ordinary current-owner fatal-failure path still restarts, and the full remote-workspace package passes.

Evidence class: `target-executed`  
Target: `manaflow-ai/cmux`  
Exact upstream base: `6044a8b3f43152d2e6fc17f771fd4b277b393118`  
Owned-fork PR: `teamleaderleo/cmux#6`  
RED: `e9ea500cebfba753444e961e2ef9d6af079ec096`  
GREEN: `8daa014321001d9aec128a9112720fb74e2ae11d`  
Workflow run: `33554543666`  
Job: `100012026075`  
Upstream contact authorized: `false`

## Environment

GitHub-hosted macOS 15.7.7 arm64 (`macos-15-arm64` image). Repository Xcode selector chose Xcode 26.3 / macOS SDK 26.2. Apple Swift version 6.2.4; Swift target `arm64-apple-macosx15.0`.

## Exact assertions

The verifier checked ancestry and required the RED diff to contain only:

`Packages/macOS/CmuxRemoteWorkspace/Tests/CmuxRemoteWorkspaceTests/RemoteProxyBrokerStaleGenerationTests.swift`

RED executed:

`RemoteProxyBrokerStaleGenerationTests.staleFatalCallbackCannotStopSuccessor`

and failed with:

`Error Domain=cmux.remote.pty Code=40 "remote daemon tunnel is not ready"`

The workflow explicitly required that failure text before accepting the red phase.

GREEN ran the same focused test and passed.

Negative control:

`RemoteProxyBrokerTests.fatalFailureRestarts`

passed, showing that a failure from the current tunnel still stops/restarts its own runtime.

The full `CmuxRemoteWorkspace` Swift package then passed **95 tests in 18 suites**.

## Interpretation

The deterministic discriminator distinguishes callback freshness, not merely final output. A key-only A callback can mutate B; adding a per-installed-runtime UUID drops A while preserving current-owner failure handling.

Consequence supported: **2. stale destructive effect** and **3. stale publication / UI lies**. Duplicate remote command execution was not tested and is not claimed.

## Evidence limit

This is target-native package execution on macOS at the exact current source coordinate. It does not establish ecosystem prevalence or upstream acceptance. The run also reports an existing Swift 6.2 Sendable warning in the managed-cloud refresh path; that warning is outside this candidate diff.

Third-party upstream remained read-only.
