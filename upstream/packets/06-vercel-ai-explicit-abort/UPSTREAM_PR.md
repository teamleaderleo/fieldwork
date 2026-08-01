# Upstream pull-request draft

Status: `hold — exact-head execution and contribution routing required; existing upstream PR #16852 is open`

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
- request provider-reader cancellation before callback completion;
- make provider values and errors arriving after abort yield to the selected abort;
- directly cancel a provider stream returned after abort but before internal registration;
- preserve consumer-scoped reader cancellation.

### Cancellation-promise semantics

The model-call stream returned by the SDK has request-level cancellation settlement through its existing Web Streams pipe layers. Its outer `cancel()` promise settles after forwarding cancellation while provider cleanup remains pending, and provider cleanup rejection is contained.

A target-native regression preserves those exact semantics and the exact abort reason. No extra cancellation wrapper or production change is required for this boundary.

### Tests

Target-native Node and Edge controls cover or are prepared for:

- pending provider read;
- root and representative derived result settlement;
- pre-aborted signal;
- active cooperative local tool;
- pending `onAbort` callback;
- provider error immediately after abort;
- multiple consumers and callback/cancel cardinality;
- provider stream returned during the registration gap;
- model-call cancellation while provider cleanup remains pending;
- rejected provider cleanup without an unhandled rejection;
- ordinary reader cancellation as a negative control;
- listener, timer, and reader cleanup.

Historical focused execution passed six Node and six Edge tests plus package TypeScript, formatting/lint, and diff hygiene. Exact current-head ordinary CI receipts should be inserted from `TESTS.md` after completion.

### Compatibility

- no public API addition;
- one explicit operation abort remains one abort outcome;
- ordinary consumer cancellation remains scoped to the consumer;
- committed external tool effects remain committed and are never represented as reversed;
- incomplete provider close remains a separate result-model question.

### Prior work

- Fixes or continues #15430.
- Supersedes or updates #16852 only with maintainer agreement.

### Checklist before use

- [x] clean current-public-base source branch materialized;
- [x] callback-independent settlement and abort/provider-error arbitration executed on the retained repair diff;
- [x] cancellation-promise behavior reproduced in a dependency-free exact-stack model;
- [x] target-native cancellation regression merged into the canonical owned-fork branch;
- [ ] Node and Edge tests pass on the exact canonical head;
- [ ] package TypeScript passes on the exact canonical head;
- [ ] formatting/lint passes on the exact canonical head;
- [ ] `git diff --check` passes on the exact canonical head;
- [ ] ordinary repository CI passes;
- [ ] complete current diff independently reviewed;
- [ ] contribution route agreed because #16852 already exists;
- [ ] public contact explicitly authorized.
