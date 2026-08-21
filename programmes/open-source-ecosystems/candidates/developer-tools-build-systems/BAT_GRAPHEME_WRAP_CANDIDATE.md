## In simple words

Bat candidate #824 now has a validated owned source candidate.

Current character/word wrapping walks Unicode scalars. The candidate walks extended grapheme clusters instead. Single-scalar width continues through Bat's existing `char_width()` helper, preserving its special control-character behavior. Multi-scalar graphemes use the existing `unicode-width` string policy, while word-wrap whitespace and carried remainder offsets move to grapheme byte boundaries.

The final candidate carrier is deliberately source-identity-safe. Rather than relying on a hand-authored unified diff, the owned fork stores an exact-source transformation script whose source snippets must each match exactly once. Fieldwork CI applies that transform to the fenced external Bat revision and asks Git to generate the resulting `src/printer.rs` diff mechanically.

- owned fork: `teamleaderleo/bat`
- branch: `candidate/grapheme-aware-wrap-20260811`
- final carrier: `82a88258292bba8b17807fb8024924dbe1a9860c`
- transformer: `fieldwork/apply_grapheme_wrap_candidate.py`
- source base: `sharkdp/bat@af59a3218303837421ce06bb2dc3c545525bba0f`
- validation run: `31443937141`, job `93634102817`
- disposition: `SOURCE-CANDIDATE VALIDATED IN OWNED CARRIER`

Two earlier hand-authored patch artifacts were malformed and rejected by `git apply` before candidate compilation. They are superseded and are not candidate-behavior evidence.

## Assignment

- Programme: #207 (`open-source-ecosystems`)
- Lane: #210 (`developer-tools-build-systems`)
- Candidate owner: #824
- Parent experiment PR: #822
- Candidate validation PR: #826
- Worker: `GPT-5.6 Sol`
- Target: `sharkdp/bat@af59a3218303837421ce06bb2dc3c545525bba0f`
- Owned candidate carrier: `teamleaderleo/bat@82a88258292bba8b17807fb8024924dbe1a9860c`
- Evidence entering candidate: `target-executed public CLI`
- Candidate evidence: `source-candidate-executed`
- Upstream contact authorized/performed: `false` / `false`

## Candidate source change

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

The single-scalar branch is intentional. Bat's existing `char_width()` maps control characters according to Bat's existing display policy. Routing every input through `UnicodeWidthStr` would risk changing that behavior.

### 3. Wrap by EGC instead of scalar

Replace scalar iteration with:

```rust
for grapheme in text.graphemes(true)
```

and append each complete grapheme with `push_str`.

The width accumulator uses `grapheme_width(grapheme)`. A line flush can therefore happen before or after an EGC, but never between its component scalars.

### 4. Keep word-wrap bookkeeping on the same boundary

- whitespace detection uses the first scalar of the grapheme;
- skipping the whitespace unit uses `graphemes(true).next()`;
- carried remainder width is recomputed by grapheme.

This keeps character wrapping, word-wrap byte offsets, and width accounting on the same text unit.

No dependency change is required.

## Executed validation

Exact baseline receipts:

```text
width-2 ZWJ:        '👩\u200d\n💻\n'
ASCII word wrap:    'ab\ncd\nef\n'
show-all control:   '␁␊\n'
```

The exact-source transformer then reported:

```text
FIELDWORK_RESULT candidate-transform=applied
```

Git mechanically generated the candidate diff from the transformed exact source.

Candidate grapheme receipts:

```text
width 2, 界:          '界\n'
width 2, 👩‍💻:       '👩\u200d💻\n'
width 4, 👩‍💻:       '👩\u200d💻\n'
width 1, é:          'é\n'
width 2, వ్రా:        'వ్రా\n'
```

Workflow receipt:

```text
FIELDWORK_RESULT candidate-grapheme-boundaries=preserved
```

Compatibility controls are byte-identical to baseline:

```text
ASCII word wrap:    'ab\ncd\nef\n'
show-all control:   '␁␊\n'
FIELDWORK_RESULT compatibility-controls=byte-identical
```

Repository checks pass:

```text
cargo fmt --check
cargo build --locked --bin bat
cargo test --locked --lib
```

Library result:

```text
144 passed; 0 failed
```

Full execution receipt:

`BAT_GRAPHEME_WRAP_CANDIDATE_EXECUTION.md`.

## Carrier history

Generation 1 (`31442928131`) and generation 2 (`31443646257`) both reproduced the exact baseline bug, then failed while parsing malformed hand-authored patch text. Candidate source never compiled in those runs.

The final carrier replaces hand-authored patch syntax with exact-once source substitutions. This removes patch-format ambiguity and makes source drift a hard failure rather than a fuzzy application.

## Decision

All original candidate gates passed:

1. exact baseline reproduces the ZWJ split;
2. exact-source transform applies;
3. candidate preserves width-2 ZWJ EGC;
4. scalar, wider-width, combining, and Telugu controls pass;
5. selected word-wrap and control-character outputs match baseline byte-for-byte;
6. formatting, build, and all library tests pass.

Disposition:

`SOURCE-CANDIDATE VALIDATED IN OWNED CARRIER`.

## Stop conditions

- External Bat remains read-only.
- Refresh Bat head and overlap before any external proposal.
- No external issue, pull request, comment, or review without explicit human authorization.
- If converting this into an owned source PR, use the mechanically generated `src/printer.rs` diff from the successful candidate run and add permanent regression coverage before proposing anything externally.