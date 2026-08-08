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

### First runner receipt

The first focused verifier run reached a hosted runner and failed during `git apply --check` before Node setup or any React test executed.

Exact failure:

```text
error: corrupt patch at fieldwork/host-singleton-unset-direct-html-release.patch:22
```

Review found incorrect hand-written unified-diff hunk counts:

- source hunk declared new count `9` but contained `10` lines;
- test hunk declared new count `80` but contained `88` lines.

This is a **verifier-packet failure**, not evidence for or against the release condition.

The same PR head's shared lint and ESLint E2E workflows completed successfully, but those do not execute the focused candidate patch and therefore do not promote the semantic claim.

The patch counts were corrected on the owned verifier branch at React commit `70c5969cc546f906727fb4a6aff47103a1d54c7e`. A new focused verifier run was triggered automatically and is queued at the time of this note.

Do not collapse the failed preflight into a semantic red test. Preserve it as verifier-quality evidence.

## Evidence class

- source semantics: source-read;
- first focused workflow: executed verifier preflight failure, no product tests ran;
- corrected regression and candidate: target-test-prepared until the new PR 24 run executes;
- shared lint / ESLint E2E on the prior head: executed/pass but insufficient for candidate acceptance;
- public overlap search: no matching issue or PR found in the current read-only search;
- upstream contact authorized/performed: false / false.

## Disposition

**EXECUTE narrow release-only repair.** Keep it independent from ordinary direct-content update cleanup, head direct-content ownership, html content contract, and Activity ownership. Promotion remains blocked on a real focused development/production test receipt from the corrected patch packet.