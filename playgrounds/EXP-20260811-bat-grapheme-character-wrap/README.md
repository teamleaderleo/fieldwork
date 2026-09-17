## In simple words

Bat's public `--wrap=character` path can insert a line break inside one extended grapheme cluster because the active wrapping owner walks Unicode scalars one at a time.

This is target-executed through the real Bat binary at exact source `af59a3218303837421ce06bb2dc3c545525bba0f`.

The corrected fixture matrix is decisive:

```text
terminal width 2, 界       -> 界\n
terminal width 2, 👩‍💻    -> 👩‍\n💻\n
terminal width 4, 👩‍💻    -> 👩‍💻\n
```

The two-column scalar control remains intact. The same ZWJ grapheme remains intact when the terminal is wide enough. Only the narrow ZWJ case splits between component scalars.

This experiment is promoted to Fieldwork candidate #824.

## Assignment

- Programme: #207 (`open-source-ecosystems`)
- Lane: #210 (`developer-tools-build-systems`)
- Worker: `GPT-5.6 Sol`
- Experiment: `EXP-20260811-bat-grapheme-character-wrap`
- Candidate owner: #824
- Target: `sharkdp/bat@af59a3218303837421ce06bb2dc3c545525bba0f`
- Owned fork execution surface: `teamleaderleo/bat` PR #1
- Claim scope: mechanism + public CLI consequence
- Evidence class: `target-executed`
- Corrected run: `31442103819`, job `93628773416`
- Retained harness-bypass run: `31441666371`, job `93627473861`
- Upstream contact authorized/performed: `false` / `false`

## Source map

### Wrapping owner

`src/printer.rs` imports Unicode segmentation and width helpers, while the active character/word wrapping loop processes content with:

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

A line break can therefore occur after one scalar and before the next scalar even when both belong to one grapheme cluster.

### Printer selection

`src/controller.rs` selects:

```text
loop_through=true  -> SimplePrinter
loop_through=false -> InteractivePrinter
```

Piped CLI configuration leaves loop-through enabled unless an interactive-output condition is forced. `--decorations=always` forces `InteractivePrinter`; `--style=plain` keeps the visible decoration set empty, so stdout stays clean.

### Existing Unicode stack

The exact target already uses `unicode-segmentation` and `unicode-width`, so a repair can be evaluated without adding a new Unicode dependency.

## Target execution

The final workflow fetched exact source read-only, fenced the checkout SHA, built `bat`, and ran the real binary with:

```text
--style=plain
--color=never
--decorations=always
--paging=never
--wrap=character
```

### Control A — one scalar, two columns

Input:

```text
界
```

Terminal width: `2`.

Observed:

```text
FIELDWORK_CONTROL scalar-width2= '界\n'
```

Result: intact.

### Discriminator — one ZWJ extended grapheme

Input:

```text
👩‍💻
```

Terminal width: `2`.

Observed:

```text
FIELDWORK_ZWJ_OUTPUT '👩\u200d\n💻\n'
FIELDWORK_RESULT zwj-width2=split-inside-grapheme
```

Result: Bat emits the woman scalar and ZWJ, then a newline, then the laptop scalar.

### Control B — relaxed width

Same ZWJ input, terminal width `4`.

Observed:

```text
FIELDWORK_CONTROL zwj-width4= '👩\u200d💻\n'
```

Result: intact.

Machine-readable receipt: `result.json`.

## Why the fixture discriminates the owner

At width 2 under the current scalar loop:

- `👩` contributes two columns;
- ZWJ contributes zero;
- `💻` contributes two and pushes `current_width` over the line budget;
- Bat flushes the existing buffer `👩‍` before appending `💻`.

The `界` control shows that a normal two-column scalar itself is handled correctly. The width-4 control shows the EGC is preserved when the scalar sum does not cross the boundary.

## Retained first-generation receipt

Run `31441666371`, job `93627473861` used `--decorations=never` and observed intact output in all cases.

Source remapping showed that this combination selected `SimplePrinter`, which writes input through rather than invoking the wrapping owner.

Classification: `harness bypass / wrong printer path`, rather than a negative result.

## Candidate direction

Candidate owner: Fieldwork #824.

The narrow repair seam is the wrapping loop. Evaluate consuming extended grapheme clusters instead of individual Unicode scalars while retaining:

- Bat's special width treatment for control characters;
- word-wrap whitespace detection at grapheme boundaries;
- correct byte indices for carried remainders;
- existing one-scalar behavior.

Regression matrix should include:

- `界` at width 2;
- `👩‍💻` at widths 2 and 4;
- combining `e\u{301}`;
- one multi-scalar Indic grapheme;
- whitespace/word-wrap carry behavior;
- control-character display behavior.

## Overlap

Focused current searches found no matching open Bat issue or PR for grapheme/ZWJ character wrapping at experiment start. A broader historical search surfaced unrelated Unicode/wrapping reports but no active owner for this exact EGC-boundary path.

## Stop condition

Experiment complete and promoted. Continue source work only in the owned Bat fork or candidate #824. Refresh Bat head and overlap before any external proposal. External issue, pull-request, comment, review, or other upstream interaction remains manual human work.