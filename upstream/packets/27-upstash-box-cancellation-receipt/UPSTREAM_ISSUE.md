# Upstream issue draft — cancellation requests can publish unconfirmed terminal state

Draft status: `not applicable — direct pull request preferred after repair`  
Public interaction authorized: `no`

A focused source change and target-native regression can explain the behavior directly. An issue-first discussion becomes useful only if maintainers want a different public receipt vocabulary, a breaking `cancel()` contract, or built-in terminal reconciliation before reviewing code.

## Proposed issue text if direction is requested

### Summary

`Run.cancel()` currently combines local stream shutdown, a best-effort cancellation request, and a terminal `cancelled` status. Request failure is suppressed, so the SDK can report terminal cancellation without confirmed remote outcome. Concurrent calls can also send duplicate requests.

### Reproduction

1. Create a `Run` with a mocked cancellation endpoint.
2. Make the endpoint return an HTTP error.
3. Call `cancel()` and inspect `run.status`.
4. Call `cancel()` concurrently on one run object and count requests.

### Observed behavior

- request failure is swallowed;
- local status becomes `cancelled`;
- concurrent callers send separate requests;
- on TypeScript streaming runs, local observer abort and timeout abort share one stream error path.

### Expected behavior

Cancellation-request delivery and remote terminal outcome should remain separate facts. Local observer shutdown should end observation without asserting a remote terminal result. Repeated callers on one run object should share one request result.

### Candidate direction

- preserve existing `cancel()` return contracts;
- add an explicit immutable request receipt;
- share one request per in-memory run object;
- keep remote outcome unknown until server/event data updates the run;
- distinguish cancellation-request observer shutdown from timeout.

### Compatibility and risks

- additive API;
- no endpoint or wire change;
- failure receipts remain cached, so retry stays explicit;
- cross-object identity remains outside scope;
- stream error behavior needs a focused compatibility decision.

### Evidence limits

- local mocked execution only;
- no hosted endpoint, provider idempotency, billing, or production-frequency claim;
- one Linux execution environment;
- maintainer naming preference unknown.

### Versions and environment

- executed source: `b55d832d6e3ae0156e32d21ea3863e231dfff9cd`;
- current relevant source inspected: `9f7533c645f6b519f612aa977f6f4acf86655db7`;
- Ubuntu 24.04, Node 22, Python 3.12.

## Filing checklist

- [ ] Repeat current upstream issue and PR search.
- [ ] Reproduce on a current public revision.
- [ ] Remove internal evidence links.
- [ ] Follow current issue template.
- [ ] Check current AI disclosure policy.
- [ ] Record exact user authorization.
