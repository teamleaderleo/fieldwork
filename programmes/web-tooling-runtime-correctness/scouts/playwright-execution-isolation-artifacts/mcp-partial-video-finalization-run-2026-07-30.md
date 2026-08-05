# Playwright partial video finalization — executed MCP reproduction and ownership review

Date: 2026-07-30

Parent scout: #26

Central candidate: #153

Upstream contact authorized: `false`

No upstream contact occurred.

## In simple words

The video tool is a delivery driver with two recordings.

The first recording reaches its destination. Delivering the second fails. The driver returns only the second error and forgets to say that the first recording was delivered.

MCP and CLI show the result through different public interfaces, but both use the same video implementation in Playwright core. The production fix belongs in core; MCP and CLI each need a regression for their response and exit behavior.

## Executed MCP fork records

| Field | Value |
| --- | --- |
| Repository | `teamleaderleo/playwright-mcp` |
| Test PR | `#1` |
| Execution PR | `#2` |
| Test head | `a934c22ede5d000c8d97579fa54f23969ed3d1db` |
| Execution head | `95c376ffaf91d58c79e23804209d75166659471a` |
| Workflow run | `30493907347` |
| Job | `90718154318` |
| Runner | Ubuntu 24.04 |
| Node | 20 |
| Browser | Google Chrome |
| Workers | 1 |

## Final MCP scenario

1. Create an initial page.
2. Start video recording to `video.webm`.
3. Create a directory at the derived second-page destination `video-1.webm`.
4. Open a second page.
5. Stop video recording.

Page recordings use internal temporary files. The directory does not prevent the second screencast from starting. It causes the second recording's final copy to fail during stop.

## Exact MCP result

Repository dependency installation, Chrome installation, and build all completed successfully.

Before the final receipt assertion, the test proved:

- `video.webm` exists;
- it is a regular file;
- it contains non-zero bytes.

The second recording failed to copy to its requested destination:

```text
EISDIR: illegal operation on a directory, copyfile '<temporary>.webm' -> '<output>/video-1.webm'
```

The stop response contained only that error. It did not identify the completed `video.webm`, and the final assertion failed:

```text
Expected substring: "video.webm"
Received string: "### Error ... video-1.webm"
```

## Supported conclusion

This is partial success with an all-error receipt.

The first recording was not lost from the filesystem. It became undiscoverable through the tool response because a later recording failed to finalize.

## Run history and causal correction

### Run `30493430429`

The test requested recording before an initial page existed. `browser_start_video` returned an error. This is a harness miss and does not support the candidate.

### Run `30493678395`

After adding an initial page, the test reached stop. It showed the directory triggers failure during final copy rather than screencast startup. This corrected the mechanism but did not yet prove the first output existed.

### Run `30493907347`

The final test added filesystem assertions for the first recording before requiring its receipt. Those assertions passed. Only the receipt assertion failed.

Only this final run supports the candidate.

## Production ownership

The Playwright CLI entrypoint imports:

```text
playwright-core/lib/tools/cli-client/program
playwright-core/lib/coreBundle
```

and uses the core tools registry. Playwright MCP also delegates tool execution to Playwright core.

Supported ownership conclusion:

- **Playwright core** owns recording session state, per-page finalization, completed-file identity, and mixed Result/Error construction.
- **Playwright MCP** owns a target regression for MCP `CallToolResult` text and `isError` behavior.
- **Playwright CLI** owns a target regression for command output and exit behavior.

A separate production patch in the MCP or CLI wrapper would duplicate the wrong boundary.

## Core prototype

Owned Playwright PR `teamleaderleo/playwright#30`, corrected head `f5f8bf778a9b112aa481bbcaa408e24fe8d22bda`, applies an experimental patch in CI that:

- tracks each recording as page, final filename, and startup promise;
- prevents new recording ownership while stop is active;
- shares one stop operation across callers;
- settles every recording rather than throwing on the first failure;
- verifies a successful destination is an existing regular file;
- links the exact completed path instead of allocating a replacement destination;
- protects reported files from output-budget cleanup;
- adds completed links and individual failures to the existing mixed Result/Error response;
- clears the active recording session once so repeated stop cannot duplicate finalization.

Workflow run `30497712121` is queued. No prototype result is claimed yet.

## CLI public-surface probe

The earlier CLI probe repeated the disproven failed-start premise and assumed `video-stop` exited successfully. It has been corrected.

Owned records:

- test PR `teamleaderleo/playwright-cli#1`, head `09fa200ba19a5fce344b02fd4932c3d273f2cf97`;
- execution PR `teamleaderleo/playwright-cli#2`, head `a7708c860bf556580b904470ce9445dde3547f13`;
- workflow run `30500400972`, queued.

The CLI test drives `open`, `video-start`, `tab-new`, and `video-stop`, captures nonzero command output, proves `video.webm` is a non-empty completed file, and requires output to name both the completed path and the failed `video-1.webm` destination.

Expected current result: the CLI reports only the failed destination, matching the core all-error behavior.

## Proposed result contract

Stopping multiple recordings should preserve per-recording outcomes:

- completed recordings retain stable output paths;
- failed recordings retain individual errors;
- one failure does not erase earlier successes;
- the overall tool call may still indicate partial failure;
- repeated stop or retry does not duplicate completed outputs.

The existing core `Response` can already serialize Result and Error sections together with `isError: true`; no new public MCP field is required for the first repair slice.

## Page-close constraint

`Screencast.stop()` performs both protocol stop and artifact `saveAs()` to the requested destination.

A page closed before explicit stop may therefore leave a tracked recording without a completed output. The result contract must classify success from the actual final file, not the planned filename.

Required control:

- close one of two recorded pages before stop;
- preserve the other page's completed path;
- report the closed page's actual completed or failed finalization outcome;
- repeated stop must not retry or duplicate either result.

## Anti-patterns

Do not:

- report the entire batch as successful;
- suppress the failed finalization error;
- delete completed outputs to regain apparent atomicity;
- return only a generic partial-success sentence without stable paths;
- assume start-time validation covers later filesystem failures;
- patch MCP and CLI separately when core owns the recording session.

## Required matrix

- all recordings finalize successfully;
- first success plus later failure;
- first failure plus later success;
- multiple failures;
- failure while closing one page;
- failure while closing the browser;
- repeated stop after partial failure;
- concurrent stop callers;
- Linux, macOS, and Windows;
- MCP and CLI public surfaces.

## Evidence classification

Executed target reproduction on Playwright MCP under Ubuntu 24.04, Node 20, and Chrome.

Core and CLI prototypes are prepared and queued, not executed results.
