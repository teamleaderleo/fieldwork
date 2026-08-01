# Upstream pull-request draft

Status: `hold — repair and execution required; existing upstream PR #16852 is open`

Do not post without explicit authorization.

## Proposed title

`fix(ai): make explicit abort settlement nonblocking`

## Draft body

### Background

An explicit caller abort can fire while `streamText` is blocked on a provider read. Public result promises, the outward stream, provider work, tools, and callbacks need one terminal owner.

This change builds on the pending-read fix in #16852 and broadens the terminal contract.

### Summary

- observe the caller abort independently of provider reads;
- reject result roots once with the abort reason;
- publish and close the outward abort outcome before observability callbacks finish;
- request provider-reader cancellation independently;
- make provider values and errors arriving after abort yield to the selected abort;
- directly request cancellation of a provider stream returned after abort but before internal registration;
- contain rejection from direct provider cancellation and avoid awaiting a cancellation promise that may never settle;
- preserve consumer-scoped reader cancellation.

### Tests

Target-native Node and Edge controls cover:

- pending provider read;
- root and representative derived result settlement;
- pre-aborted signal;
- active cooperative local tool;
- pending `onAbort` callback;
- provider error immediately after abort;
- multiple consumers and callback/cancel cardinality;
- provider stream returned during the registration gap;
- rejecting and never-settling direct provider cancellation;
- ordinary reader cancellation as a negative control;
- listener, timer, reader, and unhandled-rejection cleanup.

Exact commands and receipts should be inserted from `TESTS.md` after current-head execution.

### Compatibility

- no public API addition;
- one explicit operation abort remains one abort outcome;
- ordinary consumer cancellation remains scoped to the consumer;
- committed external tool effects remain committed and are not represented as reversed;
- incomplete provider close remains a separate result-model question.

### Prior work

- Fixes or continues #15430.
- Supersedes or updates #16852 only with maintainer agreement.

### Checklist before use

- [ ] hostile direct-cancel repair committed;
- [ ] Node focused tests pass on exact current-base head;
- [ ] Edge focused tests pass on exact current-base head;
- [ ] package TypeScript passes;
- [ ] formatting/lint passes;
- [ ] `git diff --check` passes;
- [ ] ordinary repository CI passes;
- [ ] complete current diff independently reviewed;
- [ ] contribution route agreed because #16852 already exists;
- [ ] public contact explicitly authorized.