## In simple words

Delta lets users customize the literal text around side-by-side line numbers. Current parsing records those literal prefixes and suffixes by counting grapheme clusters, then uses that number as a terminal-column width when deciding how much code fits in each panel.

One grapheme can occupy two columns. With `界{nm}`, current metadata predicts one prefix column plus one number column. The rendered field `界1` occupies three terminal columns. The source then gives code one extra column of panel budget.

This experiment executes that exact accounting path and keeps an ASCII prefix as a negative control.

## Assignment

- Programme: #207 (`open-source-ecosystems`)
- Lane: #210 (`developer-tools-build-systems`)
- Worker: `GPT-5.6 Sol`
- Experiment: `EXP-20260811-delta-wide-line-number-format`
- Target: `dandavison/delta@95a0e224f55ccfdf3a7d1278fdea98a3edb9fbf4`
- Claim scope: mechanism
- Upstream contact authorized/performed: `false` / `false`

## Source map

`src/format.rs` parses line-number format strings. For literal prefix/suffix text it stores:

```rust
prefix_len = prefix.graphemes(true).count();
suffix_len = suffix.graphemes(true).count();
```

`FormatStringPlaceholderData::width()` later returns those values as widths.

`src/features/line_numbers.rs::LineNumbersData::formatted_width()` combines that metadata with number-field width.

`src/features/side_by_side.rs::available_line_width()` subtracts `formatted_width()` from the panel width. This value decides wrapping and truncation before the final painted panel is produced.

The painted literal prefix itself is emitted unchanged, so the terminal sees its real display width.

## Exact discriminator

At one-digit line numbers:

```text
format:                界{nm}
metadata prefix width: 1 grapheme
metadata total width:  2 columns claimed
rendered field:         界1
terminal display width: 3 columns
```

For a fixed overall side-by-side width of 20, each panel starts at 10 columns. Current metadata therefore plans 8 content columns on the left; the actual rendered prefix leaves 7.

Negative control:

```text
format: |{nm}
metadata total: 2
actual display:  2
```

## Why the mechanism is consequential

The mismatch sits upstream of Delta's wrap/truncate decision. A line may be classified as fitting or split at a column that physically belongs to the line-number field. The final panel painter has its own width guard, so a complete user-visible claim still needs a rendered-output discriminator: the likely symptom is late truncation or different wrapping of content that the planner believed would fit.

That separation is intentional. This experiment proves or falsifies the accounting owner first.

## Controls

Execution material: `delta_line_number_probe.rs`.

1. Wide prefix `界{nm}`: current `formatted_width()` versus actual `UnicodeWidthStr` width.
2. ASCII prefix `|{nm}`: both paths agree.
3. Real side-by-side config with width 20: compare planned content width with actual prefix-consumed panel width.

## Stop condition

Stop after target execution classifies these three controls. If the one-column over-budget is confirmed, run a separate rendered-output fixture before proposing source. A source candidate would need to consider all callers that currently interpret grapheme counts as terminal widths, rather than replacing counts mechanically without compatibility review.