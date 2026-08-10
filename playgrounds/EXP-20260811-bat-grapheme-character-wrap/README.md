## In simple words

Bat's public `--wrap=character` path contains a scalar-by-scalar wrapping owner. That is a risky boundary for text such as ZWJ emoji, where several scalars form one extended grapheme cluster that should stay together as a display unit.

The focused discriminator uses the real Bat binary at exact source `af59a3218303837421ce06bb2dc3c545525bba0f`.

At terminal width 2:

- `界` is the two-column scalar control and should remain intact;
- `👩‍💻` is the ZWJ grapheme under test.

At terminal width 4, `👩‍💻` is the width-relaxed control and should remain intact.

The first target generation produced a useful harness negative: all text stayed intact because `--decorations=never` in piped mode made Bat choose `SimplePrinter`, bypassing the wrapping owner entirely. Current source confirms `Controller` selects `SimplePrinter` when `loop_through` is true, and CLI config sets `loop_through=false` when decorations are explicitly forced on.

The corrected generation therefore uses `--decorations=always` together with `--style=plain`. That forces `InteractivePrinter` while keeping the visible decoration set empty, so stdout remains clean and the real wrapping owner executes.

## Assignment

- Programme: #207 (`open-source-ecosystems`)
- Lane: #210 (`developer-tools-build-systems`)
- Worker: `GPT-5.6 Sol`
- Experiment: `EXP-20260811-bat-grapheme-character-wrap`
- Target: `sharkdp/bat@af59a3218303837421ce06bb2dc3c545525bba0f`
- Owned fork execution surface: `teamleaderleo/bat` PR #1
- Claim scope: mechanism
- Evidence class: `source-read`, pending corrected `target-executed`
- First harness run: `31441666371`, job `93627473861`
- Corrected target run: `31441904287` queued at latest receipt
- Upstream contact authorized/performed: `false` / `false`

## Source map

### Wrapping owner

`src/printer.rs` imports Unicode segmentation and width helpers, while the active character-wrapping loop processes content with:

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

This permits a line break after one scalar and before the next scalar even when both belong to one grapheme cluster.

### Printer selection

`src/controller.rs` selects:

```text
loop_through=true  -> SimplePrinter
loop_through=false -> InteractivePrinter
```

`src/bin/bat/app.rs` makes piped output `loop_through=true` unless an interactive-output condition is forced, including `--decorations=always`.

That distinction explains the first run and defines the corrected execution path.

### Existing dependencies

The exact target already carries:

```text
unicode-segmentation = 1.13.2
unicode-width = 0.2.2
```

so a future repair can be evaluated against Bat's existing Unicode stack rather than introducing a new dependency.

## Exact fixtures

All corrected runs use:

```text
--style=plain
--color=never
--decorations=always
--paging=never
--wrap=character
```

`--decorations=always` is present solely to enter `InteractivePrinter`; plain style keeps the visible decoration set empty.

### Control A — one scalar, two columns

Input:

```text
界
```

with:

```text
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

with terminal width 2.

Source-level prediction through `InteractivePrinter`:

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

## Retained first-generation receipt

Run `31441666371`, job `93627473861` used `--decorations=never` and observed:

```text
width 2, 界      -> 界\n
width 2, 👩‍💻   -> 👩‍💻\n
width 4, 👩‍💻   -> 👩‍💻\n
```

Classification: `harness bypass / SimplePrinter`, rather than a negative result about the scalar wrapping owner.

No target assertion failed; the execution path was wrong for the bounded question.

## Overlap

Focused current searches found no matching open Bat issue or PR for grapheme/ZWJ character wrapping at experiment start. A broader closed-issue scan surfaced historical Unicode/wrapping topics but no existing owner for this exact EGC-boundary question.

## Stop condition

Classify the corrected real CLI output on exact target source through `InteractivePrinter`. If the narrow ZWJ case splits while both controls hold, promote into a candidate owner and use the owned Bat fork for repair exploration. If it remains intact, inspect the executed wrapping state before closing the hypothesis. Keep external upstream read-only and keep any upstream contact human-authorized.