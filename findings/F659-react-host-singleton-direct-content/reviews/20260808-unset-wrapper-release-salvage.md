## In simple words

The broader HostSingleton direct-content cleanup needs a child-contribution design, but one release bug separates cleanly: a `dangerouslySetInnerHTML` wrapper whose `__html` is null or undefined never writes child content, so releasing that Fiber must not clear the persistent singleton's children.

## Narrow question

Can the release condition be changed from “the wrapper object exists” to “this Fiber actually performed a non-null direct-HTML write” without changing actual non-null direct-HTML behavior?

Original source pin: `ec61f187fe39b0aa8ec6b508f2553b2047dc30cc`.

The relevant release logic is unchanged on current public/fork main `2042572329425f9ebf35ae6287ea5bab72b2c497`.

## Refined candidate condition

Do **not** use the broader renderer `shouldSetTextContent()` predicate for this narrow release repair.

The exact DOM write performed by the `dangerouslySetInnerHTML` setter is controlled by the wrapper/object and non-null `__html` value:

```js
const innerHTML = props.dangerouslySetInnerHTML;
if (
  typeof innerHTML === 'object' &&
  innerHTML !== null &&
  innerHTML.__html != null
) {
  instance.textContent = '';
}
```

Why this is a better narrow predicate:

- `{__html: null}` -> no DOM `innerHTML` write, no release clear;
- `{__html: undefined}` -> no DOM write, no release clear;
- `{__html: ''}` -> actual direct-HTML write of an empty contribution, preserves current release behavior;
- `{__html: 0}` / `{__html: false}` / TrustedHTML object -> actual non-null direct write, preserves current release behavior;
- string/number/bigint `children` are irrelevant to this DSIH-specific cleanup decision;
- future changes to `shouldSetTextContent()` cannot accidentally broaden this release authority.

This patch remains a **current-architecture repair**. In the leading long-term body model, even non-null DSIH child cleanup should eventually move out of singleton property release and into the body contribution lifecycle.

## Why this split avoids the larger blocker

The change does not decide how actual opaque content should coexist with later external children.

For actual non-null DSIH, release keeps the current whole-child-list clearing behavior exactly as before.

It only removes false cleanup authority where React performed no direct content write at all.

Focused cases:

- body unset-wrapper release preserves an external child;
- html unset-wrapper release preserves the existing `documentElement`, `head`, and `body` identities;
- reversing control keeps actual non-null body DSIH clearing on release unchanged.

The html null-wrapper case protects persistent identity without endorsing non-null html DSIH, which remains a separate contract hold.

## Executable verifier

Owned React PR 24 is a verifier-only lane with:

- one patch carrying the refined release condition and three focused tests;
- development and production focused singleton tests;
- changed-file lint;
- no clean source promotion step.

## Runner receipts so far

### Run 1 — packet failure, no semantic evidence

The first focused workflow reached a hosted runner and failed during `git apply --check` before Node setup or any React test.

```text
error: corrupt patch at fieldwork/host-singleton-unset-direct-html-release.patch:22
```

Review found incorrect hand-written unified-diff hunk counts.

### Run 2 — packet failure, no semantic evidence

After correcting the hunk counts, the next hosted run again failed during `git apply --check`, this time at the end of the patch because the hand-built patch file lacked a terminating newline.

No React development/production test executed in either run.

Both failures are **verifier-quality evidence only**, not evidence for or against the candidate.

Shared lint / ESLint E2E succeeded on related heads, but those workflows do not apply/run the focused candidate patch and therefore do not promote the semantic claim.

### Current verifier head

The packet now has:

- audited hunk counts;
- terminating newline;
- refined exact-DISIH-write predicate.

Current React verifier head: `bbfddd5e7eb45e14e6df5303783a3e04dc5f475a`.

The new focused workflow was queued at the last status read. Promotion remains blocked until a run reaches the actual development/production tests.

## Evidence class

- source semantics: high-confidence source-read;
- public-current revalidation: source-read, release logic unchanged;
- first two focused workflows: executed preflight failures, **zero product tests**;
- current candidate/tests: target-test-prepared;
- public overlap search: no matching direct issue/PR owner found in current read-only search;
- upstream contact authorized/performed: false / false.

## Disposition

**EXECUTE / strongest narrow current-source candidate.**

Keep it independent from ordinary DSIH update cleanup, body contribution architecture, head/html non-null direct-content policy, and Suspense/Activity child ownership.

If the corrected focused development/production tests pass, this is the first lane I would consider promoting to a clean internal source candidate.