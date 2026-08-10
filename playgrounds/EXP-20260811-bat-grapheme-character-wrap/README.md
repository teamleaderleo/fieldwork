## In simple words

Bat's public `--wrap=character` path currently walks Unicode scalars one at a time. That is a risky boundary for text such as ZWJ emoji, where several scalars form one extended grapheme cluster that should stay together as a display unit.

The focused discriminator uses the real Bat binary at exact source `af59a3218303837421ce06bb2dc3c545525bba0f`.

At terminal width 2:

- `界` is the two-column scalar control and should remain intact;
- `👩‍💻` is the ZWJ grapheme under test.

At terminal width 4, `👩‍💻` is the width-relaxed control and should remain intact.

If the narrow ZWJ case becomes `👩‍\n💻\n` while both controls hold, Bat's character-wrapping owner has a user-visible grapheme-boundary split.

## Assignment

- Programme: #207 (`open-source-ecosystems`)
- Lane: #210 (`developer-tools-build-systems`)
- Worker: `GPT-5.6 Sol`
- Experiment: `EXP-20260811-bat-grapheme-character-wrap`
- Target: `sharkdp/bat@af59a3218303837421ce06bb2dc3c545525bba0f`
- Owned fork execution surface: `teamleaderleo/bat` PR #1
- Claim scope: mechanism
- Evidence class: `source-read`, pending `target-executed`
- Upstream contact authorized/performed: `false` / `false`

## Source map

`src/printer.rs` imports both Unicode segmentation and Unicode width helpers, but the active character-wrapping loop processes content with:

```rust
for c in text.chars() {
    let cw = char_width(c);
    current_width += cw;
    ...
    if current_width > max_width {
        // flush current line and begin another
    }
    line_buf.push(c);
}
```

This means a line break can occur after one scalar and before the next scalar even when both belong to one grapheme cluster.

The public command surface exposes:

```text
--wrap=character
--terminal-width <width>
```

so the source branch is directly testable through the shipped binary.

## Exact fixtures

All runs disable decoration, color, and paging so stdout is plain text.

### Control A — one scalar, two columns

Input:

```text
界
```

Command context:

```text
--style=plain
--color=never
--decorations=never
--paging=never
--wrap=character
--terminal-width=2
```

Expected control output:

```text
界\n
```

### Discriminator — one ZWJ grapheme

Input:

```text
👩‍💻
```

Same width-2 command context.

Source-level prediction:

```text
👩‍\n💻\n
```

because the woman scalar consumes two columns, the ZWJ consumes zero, and the laptop scalar triggers the next scalar-width overflow.

### Control B — relaxed width

Same ZWJ input with:

```text
--terminal-width=4
```

Expected control output:

```text
👩‍💻\n
```

## Overlap

A focused current search found no matching open Bat issue or PR for grapheme/ZWJ character wrapping at the time of this experiment.

## Stop condition

Classify the real CLI output on exact target source. If the narrow ZWJ case splits while both controls hold, promote into a candidate owner and use the owned Bat fork for repair exploration. Keep external upstream read-only and keep any upstream contact human-authorized.