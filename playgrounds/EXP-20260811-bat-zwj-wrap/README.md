## In simple words

Bat's current wrapping loop walks text one Unicode scalar at a time and decides row breaks from those scalar widths. That is risky for a multi-scalar grapheme whose terminal width is a property of the whole sequence.

The focused example is `👩‍💻`: WOMAN + ZWJ + PERSONAL COMPUTER is one extended grapheme cluster. At a two-column row budget, source reading predicts Bat will buffer `👩‍`, see `💻` push the scalar-width total past the row, and flush a newline inside the cluster.

The public CLI makes this directly testable with `--wrap=character --terminal-width 2 --plain --paging=never --color=never`. The control is `界a`, where the first grapheme is an ordinary two-column scalar and the row break should occur after it.

## Assignment

- Programme: #207 (`open-source-ecosystems`)
- Lane: #210 (`developer-tools-build-systems`)
- Worker: `GPT-5.6 Sol`
- Experiment: `EXP-20260811-bat-zwj-wrap`
- Target: `sharkdp/bat@af59a3218303837421ce06bb2dc3c545525bba0f`
- Evidence class: `source-read`, pending target execution
- Upstream contact authorized/performed: `false` / `false`

## Code map

`src/printer.rs` defines `char_width(c)` from `UnicodeWidthChar` and uses it inside `InteractivePrinter::print_line()`.

For wrapped output, the printer:

1. iterates `for c in text.chars()`;
2. adds `char_width(c)` to `current_width`;
3. flushes `line_buf` when `current_width > max_width`;
4. resets the width to the current scalar width;
5. appends that scalar to the new row buffer.

The file imports `UnicodeSegmentation`, but this wrapping loop itself is scalar-based.

Bat currently depends on `unicode-width = 0.2.2` and `unicode-segmentation = 1.13.2`.

## Public contract map

Bat's generated long help documents:

- `--wrap <mode>` with `character` and `word` modes;
- `--terminal-width <width>` to control output width.

That gives a CLI-level test without modifying target source.

## Discriminator

Critical input:

```text
👩‍💻a
```

Control input:

```text
界a
```

Both run through:

```text
bat --plain --paging=never --color=never --wrap=character --terminal-width 2
```

Classification is by exact UTF-8 output lines. A newline inside the `👩‍💻` cluster promotes the finding; a complete cluster on one row rejects the source-level hypothesis.

## Overlap

Focused open-issue search for emoji/grapheme/ZWJ wrapping returned no matching owner during intake. Refresh before promotion or any external proposal.

## Stop condition

Run the exact current target and classify the public CLI output. Third-party upstream remains read-only. Do not open or comment on an external issue/PR without explicit human authorization.
