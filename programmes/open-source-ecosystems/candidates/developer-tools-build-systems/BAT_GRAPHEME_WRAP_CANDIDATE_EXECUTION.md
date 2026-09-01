## In simple words

The Bat grapheme-aware wrapping candidate is now validated on exact target source.

Exact Bat `af59a3218303837421ce06bb2dc3c545525bba0f` reproduces the known width-2 ZWJ split:

```text
👩‍💻 -> 👩‍\n💻\n
```

The owned candidate carrier transforms the wrapping owner to iterate extended grapheme clusters, while preserving Bat's existing single-scalar `char_width()` behavior. On the same exact source, the candidate changes the width-2 output to:

```text
👩‍💻 -> 👩‍💻\n
```

The candidate also preserves a two-column scalar, the same ZWJ grapheme at width 4, a combining grapheme, and a Telugu grapheme. Ordinary ASCII word wrapping and Bat's control-character/show-all output remain byte-identical to baseline. `cargo fmt --check` and all 144 Bat library tests pass.

This is strong enough to classify as a validated owned source candidate. External Bat remains read-only and no upstream contact has occurred.

## Assignment

- Programme: #207 (`open-source-ecosystems`)
- Lane: #210 (`developer-tools-build-systems`)
- Candidate owner: #824
- Candidate validation PR: #826
- Parent experiment PR: #822
- Worker: `GPT-5.6 Sol`
- External target: `sharkdp/bat@af59a3218303837421ce06bb2dc3c545525bba0f`
- Owned candidate branch: `teamleaderleo/bat:candidate/grapheme-aware-wrap-20260811`
- Owned candidate carrier: `82a88258292bba8b17807fb8024924dbe1a9860c`
- Fieldwork candidate head at execution: `3b3c452a4639b2e848a43531c1e35259d9d7ae70`
- Workflow run: `31443937141`
- Job: `93634102817`
- Evidence class: `source-candidate-executed`
- Upstream contact authorized/performed: `false` / `false`

## Carrier evolution

Two earlier candidate generations never executed candidate semantics.

### Generation 1

Run `31442928131`, job `93631191701` built exact baseline and reproduced the bug, then rejected a hand-authored unified diff before candidate compilation.

Classification: `carrier failure / malformed patch syntax`.

### Generation 2

Run `31443646257`, job `93633266288` again built exact baseline and preserved compatibility controls, then `git apply` rejected the hand-authored diff as corrupt before candidate compilation.

Classification: `carrier failure / malformed patch syntax`.

Neither generation is evidence against the source candidate.

### Generation 3 — executed candidate

The final carrier drops hand-authored diff syntax from the critical path. The owned fork stores:

`fieldwork/apply_grapheme_wrap_candidate.py`

The script performs exact-once source substitutions against the fenced Bat revision. If any source snippet differs, it stops. Fieldwork CI applies the transform and then asks Git itself to generate the real candidate diff mechanically.

Result:

```text
FIELDWORK_RESULT candidate-transform=applied
```

The generated diff is preserved in workflow logs and contains only `src/printer.rs` changes.

## Candidate source change

### Width helper

Single-scalar graphemes retain Bat's existing width owner:

```rust
char_width(c)
```

This is important because Bat maps control characters specially when needed.

Multi-scalar graphemes use the already-present `unicode-width` string policy:

```rust
grapheme.width()
```

The helper is:

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

### Wrapping unit

The active wrapping loop changes from scalar iteration:

```rust
for c in text.chars()
```

to EGC iteration:

```rust
for grapheme in text.graphemes(true)
```

The line buffer appends complete graphemes, so a wrap can occur before or after an EGC but cannot land between its component scalars.

### Word-wrap bookkeeping

The candidate keeps the same logical whitespace behavior while moving byte accounting to the same grapheme unit:

- whitespace detection inspects the first scalar of each grapheme;
- skipped whitespace length uses the next grapheme's byte length;
- carried remainder width is recomputed by grapheme.

No dependency changes are required; exact Bat already carries `unicode-segmentation` and `unicode-width`.

## Baseline receipts

Exact unpatched Bat:

```text
FIELDWORK_BASELINE_ZWJ '👩\u200d\n💻\n'
FIELDWORK_BASELINE baseline-word.out 'ab\ncd\nef\n'
FIELDWORK_BASELINE baseline-control.out '␁␊\n'
```

The baseline therefore preserves the confirmed bug and establishes compatibility bytes before candidate application.

## Candidate grapheme receipts

Exact candidate output:

```text
candidate-scalar.out     '界\n'
candidate-zwj2.out       '👩\u200d💻\n'
candidate-zwj4.out       '👩\u200d💻\n'
candidate-combining.out  'é\n'
candidate-indic.out      'వ్రా\n'
```

Workflow receipt:

```text
FIELDWORK_RESULT candidate-grapheme-boundaries=preserved
```

This covers:

- ordinary two-column scalar `界`;
- the original ZWJ discriminator at width 2;
- ZWJ relaxed-width control at width 4;
- combining grapheme `e\u{301}`;
- Telugu multi-scalar grapheme `వ్రా`.

## Compatibility receipts

Candidate ASCII word wrapping is byte-identical to baseline:

```text
baseline-word.out  'ab\ncd\nef\n'
candidate-word.out 'ab\ncd\nef\n'
```

Candidate control/show-all output is byte-identical to baseline:

```text
baseline-control.out  '␁␊\n'
candidate-control.out '␁␊\n'
```

Workflow receipt:

```text
FIELDWORK_RESULT compatibility-controls=byte-identical
```

## Repository checks

The executed candidate passed:

```text
cargo fmt --check
cargo build --locked --bin bat
cargo test --locked --lib
```

Library result:

```text
144 passed; 0 failed
```

Fieldwork integrity also passed on the candidate execution head.

## What is established

**Observed on exact target code:**

- baseline Bat splits the width-2 ZWJ grapheme inside its EGC;
- the owned candidate preserves that EGC;
- two-column scalar, combining, Telugu, and wider-width controls pass;
- selected word-wrap and control-character compatibility outputs are byte-identical;
- formatting, build, and all library tests pass.

**Source-supported:**

- the candidate changes the wrapping unit from Unicode scalar to extended grapheme cluster;
- no new dependency is introduced;
- single-scalar width policy remains on Bat's existing helper.

**Still requires review:**

- broader performance impact of EGC iteration on very long lines;
- whether maintainers prefer a shared width helper elsewhere in Bat;
- broader integration/e2e matrix beyond the focused compatibility controls and library suite;
- upstream design/acceptance, which has not been requested or attempted.

## Disposition

`SOURCE-CANDIDATE VALIDATED IN OWNED CARRIER`.

Recommended next source step:

1. retain the mechanically generated `src/printer.rs` diff as the canonical candidate patch;
2. add permanent regression tests near Bat's wrapping integration tests if the owned fork is converted into a source PR;
3. refresh current upstream head and EGC-wrap overlap before any external proposal;
4. keep upstream interaction gated on explicit human authorization.

No third-party upstream mutation or contact occurred.