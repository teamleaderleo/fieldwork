# Playwright MCP partial video finalization — executed reproduction

Date: 2026-07-30

Parent scout: #26

Central candidate: #153

Upstream contact authorized: `false`

No upstream contact occurred.

## In simple words

The video tool is a delivery driver with two recordings.

The first recording reaches its destination. Delivering the second fails. The driver returns only the second error and forgets to say that the first recording was delivered.

## Owned fork records

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

## Final scenario

1. Create an initial page.
2. Start video recording to `video.webm`.
3. Create a directory at the derived second-page destination `video-1.webm`.
4. Open a second page.
5. Stop video recording.

Page recordings use internal temporary files. The directory does not prevent the second screencast from starting. It causes the second recording's final copy to fail during stop.

## Exact result

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

## Proposed result contract

Stopping multiple recordings should preserve per-recording outcomes:

- completed recordings retain stable output paths;
- failed recordings retain individual errors;
- one failure does not erase earlier successes;
- the overall tool call may still indicate partial failure;
- repeated stop or retry does not duplicate completed outputs.

## Anti-patterns

Do not:

- report the entire batch as successful;
- suppress the failed finalization error;
- delete completed outputs to regain apparent atomicity;
- return only a generic partial-success sentence without stable paths;
- assume start-time validation covers later filesystem failures.

## Required matrix

- all recordings finalize successfully;
- first success plus later failure;
- first failure plus later success;
- multiple failures;
- failure while closing one page;
- failure while closing the browser;
- repeated stop after partial failure;
- Linux, macOS, and Windows;
- corresponding CLI behavior.

## Evidence classification

Executed target reproduction on Playwright MCP under Ubuntu 24.04, Node 20, and Chrome.

No production repair has been implemented or selected.
