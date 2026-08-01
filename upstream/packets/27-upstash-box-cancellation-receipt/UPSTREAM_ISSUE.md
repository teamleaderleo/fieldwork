# Upstream issue draft — cancellation requests can publish unconfirmed terminal state

Draft status: `not applicable — direct pull request preferred after repair`  
Public interaction authorized: `no`

A focused source change and target-native regression can explain the behavior directly. An issue-first discussion becomes useful only if maintainers want to decide receipt vocabulary, command/code stream parity, a breaking `cancel()` contract, or built-in terminal reconciliation before reviewing code.

## Proposed issue text if direction is requested

### Summary

`Run.cancel()` currently combines local stream shutdown, a best-effort cancellation request, and a terminal `cancelled` status. Request failure is suppressed, so the SDK can report terminal cancellation without confirmed remote outcome. Concurrent calls can also send duplicate requests.

For TypeScript agent streams, cancellation and timeout abort the same controller. The iterator maps either cause to terminal `cancelled` and `Stream timed out`.

### Reproduction

1. Create a `Run` with a mocked cancellation endpoint.
2. Make the endpoint return an HTTP error.
3. Call `cancel()` and inspect `run.status`.
4. Call `cancel()` concurrently on one run object and count requests.
5. Start a real mocked `box.agent.stream()` body read and call `cancel()` while the read is pending.

### Observed behavior

- request failure is swallowed;
- local status becomes `cancelled`;
- concurrent callers send separate requests;
- a caller-requested agent-stream abort is reported as `Stream timed out`;
- command/code streams currently do not attach the same local abort controller used by agent streams.

### Expected behavior

Cancellation-request delivery and remote terminal outcome should remain separate facts. Caller-requested agent-stream shutdown should preserve rejection for catch-based consumers, identify cancellation rather than timeout, and use the existing nonterminal `detached` state until authoritative run data arrives. Repeated callers on one run object should share one request result.

### Candidate direction

- preserve existing `cancel()` return contracts;
- add an explicit immutable request receipt;
- share one request per in-memory run object;
- keep remote outcome unknown until server/event data updates the run;
- privately record the first owner of an agent-stream abort;
- preserve timeout behavior separately;
- narrow local observer-shutdown claims to agent stream unless command/code streams are deliberately widened.

### Open naming and scope questions

- What does a successful cancellation endpoint response establish: sent, acknowledged, accepted, or another request stage?
- Should command/code streams gain equivalent local observer controllers, or should the behavior remain agent-stream-specific?

### Compatibility and risks

- additive API;
- no endpoint or wire change;
- cancellation still rejects the iterator, preserving catch-based consumers;
- error prose and local status change from false timeout/terminal cancellation to cancellation-specific/`detached`;
- failure receipts remain cached, so retry stays explicit;
- cross-object identity remains outside scope.

### Evidence limits

- local mocked execution only;
- no hosted endpoint, provider idempotency, billing, or production-frequency claim;
- one Linux execution environment;
- selected first-owner repair remains unexecuted;
- maintainer naming and stream-parity preferences unknown.

### Versions and environment

- executed source: `b55d832d6e3ae0156e32d21ea3863e231dfff9cd`;
- current relevant source inspected: `9f7533c645f6b519f612aa977f6f4acf86655db7`;
- open CLI compatibility head inspected: `fce8c8cfc269bc09d07eb991ee39d0433029027e`;
- Ubuntu 24.04, Node 22, Python 3.12.

## Filing checklist

- [ ] Repeat current upstream issue and PR search.
- [ ] Reproduce on a current public revision.
- [ ] Settle request-state vocabulary and stream scope.
- [ ] Remove internal evidence links.
- [ ] Follow current issue template.
- [ ] Check current AI disclosure policy.
- [ ] Record exact user authorization.
