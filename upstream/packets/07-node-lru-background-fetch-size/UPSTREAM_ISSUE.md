# Upstream issue draft — archived route not used

Status: `ARCHIVED — direct pull request submitted instead`

The owner chose the direct-PR route and submitted [isaacs/node-lru-cache#410](https://redirect.github.com/isaacs/node-lru-cache/pull/410). No upstream issue was filed for Unit 07.

This file is retained only as historical drafting context. It should not be copied or filed unless the upstream maintainer later explicitly asks for a separate issue.

## Historical issue summary

`backgroundFetchSize` is used as the provisional calculated size of a missing-key background fetch. Runtime values outside the intended nonnegative-integer domain could enter size and eviction arithmetic without validation, and synchronous `fetchMethod` mutation could change the value used by the already-dispatched operation.

The submitted repair validates the option, snapshots it before invoking user `fetchMethod`, and carries that operation-local value into provisional accounting. Zero remains supported; stale refresh and no-size paths retain their existing behavior.

## Historical evidence boundary

Released `lru-cache@11.5.2` probes demonstrated invalid runtime values reaching live accounting, including `NaN`, negative/fractional values, infinity, and runtime strings. Production prevalence remains unknown.

## Filing boundary

Do not file this issue as a second upstream contact merely because the draft exists. The direct upstream pull request is the active public record. Any additional upstream issue, comment, review, reaction, or other interaction requires explicit owner direction for that exact action.
