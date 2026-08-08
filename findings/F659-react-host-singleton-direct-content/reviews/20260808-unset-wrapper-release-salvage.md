## In simple words

The broader HostSingleton direct-content cleanup needs a child-ownership design, but one release bug can be separated cleanly: a `dangerouslySetInnerHTML` wrapper whose `__html` is null or undefined never writes child content, so releasing that Fiber must not clear the persistent singleton's children.

## Narrow question

Can the release condition be changed from “the wrapper object exists” to “this Fiber actually supplied opaque direct content” without changing actual non-null direct-HTML behavior?

Current source pin: `ec61f187fe39b0aa8ec6b508f2553b2047dc30cc`.

Candidate condition:

```js
props.children == null && shouldSetTextContent(type, props)
```

For DOM HostSingleton types this is true for a non-null `dangerouslySetInnerHTML.__html` value and false for null/undefined `__html` wrappers.

## Why this split avoids the larger blocker

The change does not attempt to decide how actual opaque content should coexist with later external children. For actual non-null direct HTML, release keeps the current whole-node clearing behavior exactly as before.

It only removes false cleanup authority in cases where React performed no direct content write at all.

This repairs two concrete cases without selecting a policy for the larger design:

- body unset-wrapper release preserves an external child;
- html unset-wrapper release preserves the existing `documentElement`, `head`, and `body` identities.

A reversing control keeps actual non-null body direct HTML clearing on release unchanged.

## Executable verifier

Owned React PR 24 is a verifier only. It contains:

- one patch with the release-condition change and three focused tests;
- one workflow running the focused singleton tests in development and production plus changed-file lint;
- no clean source promotion step.

## Evidence class

- source semantics: source-read;
- regression and candidate: target-test-prepared until PR 24 executes;
- public overlap search: no matching issue or PR found in the current read-only search;
- upstream contact authorized/performed: false / false.

## Disposition

**EXECUTE narrow release-only repair.** Keep it independent from ordinary direct-content update cleanup, head direct-content ownership, html content contract, and Activity ownership.