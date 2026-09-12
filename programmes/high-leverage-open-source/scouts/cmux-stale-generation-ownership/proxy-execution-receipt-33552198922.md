# Remote proxy stale-generation execution receipt

Fieldwork issue: #931  
Owned-fork candidate: `teamleaderleo/cmux#6`  
Execution carrier: `teamleaderleo/cmux#8`  
Workflow run: `33552198922`  
Job: `100004099358` — `Prove stale proxy red-green`  
Evidence class: `target-executed`  
Upstream contact authorized: `false`

## In simple words

The target-native package test reproduces the stale-owner failure on the unmodified broker and passes after the tunnel-generation fence. The same run verifies the ordinary current-owner fatal-failure behavior and the full `CmuxRemoteWorkspace` package.

## Source coordinates

Original scout pin: `manaflow-ai/cmux@eaa899cb20bd411019744fbd2bdedeb397f3070b`.

Executed restack base: `manaflow-ai/cmux@2ead47750ab2f47c13972d0709d99cdcbaa8ad73`.

Executed candidate history:

```text
2ead47750ab2f47c13972d0709d99cdcbaa8ad73
  -> 80c54e08917a02ae91436a1495fe6296ea6c2bda  RED regression only
  -> 3f11ef644ce14d43e8086edb346dc4659a3e0c32  GREEN generation fence
```

The workflow explicitly verified both parent relationships, verified that the red commit changes only `RemoteProxyBrokerStaleGenerationTests.swift`, and ran `git diff --check` through green.

Current upstream checked after execution: `6044a8b3f43152d2e6fc17f771fd4b277b393118`.

`RemoteProxyBroker.swift` has blob SHA `efdb05374e725727efd346684e5cc0ff1d15cb76` at all three upstream coordinates:

- original scout pin `eaa899cb20bd411019744fbd2bdedeb397f3070b`;
- executed base `2ead47750ab2f47c13972d0709d99cdcbaa8ad73`;
- checked current main `6044a8b3f43152d2e6fc17f771fd4b277b393118`.

The three upstream commits after the executed base touched only cmux-tui/workflow/doc files, so the tested broker source remained byte-identical through the current-main check.

## Environment

GitHub-hosted `macos-15-arm64` runner, macOS 15.7.7. Repository Xcode selector chose Xcode 26.3 / macOS SDK 26.2. Swift reported Apple Swift 6.2.4 targeting arm64 macOS.

## RED discriminator

Command:

```sh
swift test \
  --package-path Packages/macOS/CmuxRemoteWorkspace \
  --filter RemoteProxyBrokerStaleGenerationTests.staleFatalCallbackCannotStopSuccessor
```

At RED `80c54e08917a02ae91436a1495fe6296ea6c2bda`, the focused Swift Testing case executed and failed with:

```text
Caught error: Error Domain=cmux.remote.pty Code=40
"remote daemon tunnel is not ready"
```

The carrier treated that exact failure as the expected red result and recorded exit status 1.

This is the ownership discriminator: after B replaces A under the same transport key, firing A's retained fatal callback removes the current tunnel, so the subsequent synchronous broker query cannot reach B.

## GREEN result

At GREEN `3f11ef644ce14d43e8086edb346dc4659a3e0c32`, the same focused test passed.

The repair adds one per-installed-tunnel UUID, captures it in that tunnel's fatal callback, requires the callback generation to equal the entry's current tunnel generation before teardown/publication/restart handling, and clears the generation on runtime teardown.

## Negative control

The existing `RemoteProxyBrokerTests.fatalFailureRestarts` test passed on green. A fatal callback from the current tunnel therefore still performs the intended stop/error/retry behavior; only stale-generation callbacks are discarded.

## Package result

`swift test --package-path Packages/macOS/CmuxRemoteWorkspace` passed:

```text
95 tests in 18 suites passed
```

## Evidence limit

This receipt proves the broker behavior and repair on the declared package/runtime test boundary at an upstream source blob that remained byte-identical through the checked current main. It does not by itself establish end-user frequency, upstream acceptance, or wider deployment impact.

Third-party upstream remained read-only.
