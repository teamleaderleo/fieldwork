## In simple words

Bat candidate #824 has a narrow repair that can be evaluated without changing dependencies or broad terminal behavior.

Current character/word wrapping walks Unicode scalars. The candidate walks extended grapheme clusters instead. Single-scalar width continues through Bat's existing `char_width()` helper, preserving its special control-character behavior. Multi-scalar graphemes use the existing `unicode-width` string policy, while word-wrap whitespace and carried remainder offsets move to grapheme byte boundaries.

The candidate is stored as an executable unified diff in the owned fork rather than being written directly into the large `src/printer.rs` blob through the connector:

- owned fork: `teamleaderleo/bat`
- branch: `candidate/grapheme-aware-wrap-20260811`
- patch head: `dd11e13120f693505dddd45eb0f489dca0e80465`
- patch: `fieldwork/bat-grapheme-aware-wrap.patch`
- source base: `sharkdp/bat@af59a3218303837421ce06bb2dc3c545525bba0f`

Fieldwork CI fetches both exact revisions, extracts the patch from the owned fork, requires `git apply --check`, applies it to exact Bat source, builds/tests the candidate, and executes baseline-versus-candidate controls.

## Assignment

- Programme: #207 (`open-source-ecosystems`)
- Lane: #210 (`developer-tools-build-systems`)
- Candidate owner: #824
- Parent experiment PR: #822
- Worker: `GPT-5.6 Sol`
- Target: `sharkdp/bat@af59a3218303837421ce06bb2dc3c545525bba0f`
- Owned candidate patch: `teamleaderleo/bat@dd11e13120f693505dddd45eb0f489dca0e80465`
- Evidence entering candidate: `target-executed public CLI`
- Upstream contact authorized/performed: `false` / `false`

## Candidate diff

The patch makes four related changes in `src/printer.rs`.

### 1. Reuse the existing string-width trait

Import `UnicodeWidthStr` alongside `UnicodeWidthChar`.

### 2. Add one grapheme-width helper

```rust
fn grapheme_width(grapheme: &str) -> usize {
    let mut chars = grapheme.chars();
    match (chars.next(), chars.next()) {
        (Some(c), None) => char_width(c),
        (Some(_), Some(_)) => grapheme.width(),
        (None, _) => 0,
    }
}
```

The single-scalar branch is intentional. Bat's existing `char_width()` maps control characters to two display columns. Sending every input through `UnicodeWidthStr` would risk changing that policy.

### 3. Wrap by EGC instead of scalar

Replace `for c in text.chars()` with `for grapheme in text.graphemes(true)` and append each complete grapheme with `push_str`.

The width accumulator uses `grapheme_width(grapheme)`. A line flush can therefore happen before or after an EGC, but never between its component scalars.

### 4. Keep word-wrap bookkeeping on the same boundary

- whitespace detection uses the first scalar of the grapheme;
- skipping the whitespace unit uses `graphemes(true).next()` rather than `chars().next()`;
- carried remainder width is recomputed by grapheme.

This avoids fixing character wrapping while leaving word-wrap byte offsets on a different unit.

## Execution matrix

### Required bug controls

```text
character wrap, width 2, 界       -> intact
character wrap, width 2, 👩‍💻    -> intact after candidate
character wrap, width 4, 👩‍💻    -> intact
```

The unpatched exact source is already recorded as:

```text
width 2, 👩‍💻 -> 👩‍\n💻\n
```

### Additional grapheme controls

- combining grapheme `e\u{301}` at width 1 stays intact;
- Telugu `వ్రా` at width 2 stays intact as one EGC.

### Compatibility comparisons

Before applying the patch, CI builds the exact baseline and records:

- ordinary ASCII word wrapping;
- control-character/show-all output.

After applying/building the candidate, the same commands must be byte-identical to baseline.

### Repository checks

- `git apply --check` must pass;
- `cargo fmt --check` must pass after applying the patch;
- focused library tests must pass;
- exact target and exact candidate patch revisions must be printed in the receipt.

## Decision rule

Promote this candidate toward an owned source PR only if:

1. exact unpatched Bat reproduces the known ZWJ split;
2. the patch applies cleanly to the exact base;
3. the patched binary preserves the width-2 ZWJ EGC;
4. scalar, wider-width, combining, and Telugu controls pass;
5. baseline/candidate ASCII word-wrap and control-character outputs match;
6. formatting and library tests pass.

If any compatibility control changes, stop and narrow the patch before treating it as source-ready.

## Stop conditions

- External Bat remains read-only.
- Refresh Bat head and overlap before any external proposal.
- No external issue, pull request, comment, or review without explicit human authorization.
- If the candidate passes, keep the exact patch receipt in Fieldwork and the owned fork; do not infer that the external project would accept the design without maintainer review.