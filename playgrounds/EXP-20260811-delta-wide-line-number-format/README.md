## In simple words

Delta lets users customize the literal text around side-by-side line numbers. Current parsing records those literal prefixes and suffixes by counting grapheme clusters, then uses that number as a terminal-column width when deciding how much code fits in each panel.

One grapheme can occupy two columns. On exact Delta source, `界{nm}` is target-executed as metadata width 2 while the rendered field `界1` is width 3. In a fixed width-20 side-by-side configuration, Delta plans eight content columns on the left even though the real line-number field leaves seven. The ASCII control `|{nm}` stays aligned at width 2.

That accounting result is established. The current follow-up pushes an eight-column boundary line through Delta's real renderer. The discriminator asks whether the ASCII prefix preserves all eight content columns while the wide prefix loses content at the final panel-width guard.

## Assignment

- Programme: #207 (`open-source-ecosystems`)
- Lane: #210 (`developer-tools-build-systems`)
- Worker: `GPT-5.6 Sol`
- Experiment: `EXP-20260811-delta-wide-line-number-format`
- Target: `dandavison/delta@95a0e224f55ccfdf3a7d1278fdea98a3edb9fbf4`
- Claim scope: mechanism
- Evidence class: `target-executed`
- Workflow run: `31425645220`
- Job: `93576574346`
- Upstream contact authorized/performed: `false` / `false`

## Source map

`src/format.rs` parses line-number format strings. For literal prefix/suffix text it stores:

```rust
prefix_len = prefix.graphemes(true).count();
suffix_len = suffix.graphemes(true).count();
```

`FormatStringPlaceholderData::width()` later returns those values as widths.

`src/features/line_numbers.rs::LineNumbersData::formatted_width()` combines that metadata with number-field width.

`src/features/side_by_side.rs::available_line_width()` subtracts `formatted_width()` from the panel width. This value decides wrapping before the final painted panel is produced.

The painted literal prefix itself is emitted unchanged, so the terminal sees its real display width.

## Exact target execution

The workflow fetched exact target source read-only and injected three focused tests.

### Wide prefix

```text
format:                 界{nm}
metadata total width:   2
rendered example:       界1
actual display width:   3
delta:                   +1 physical column
```

Result: `PASS`.

### ASCII negative control

```text
format:                 |{nm}
metadata total width:   2
rendered example:       |1
actual display width:   2
delta:                   0
```

Result: `PASS`.

### Real side-by-side budget

Configuration:

```text
overall fixed width:     20
left panel width:        10
left format:             界{nm}
metadata line-number:    2
actual line-number:      3
planned content width:   8
actual content width:    7
```

Result: `PASS`.

Machine-readable receipt: `result.json`.

## Rendered-output discriminator

The follow-up target fixture uses this diff boundary:

```text
-abcdefgh
+zzzzzzzz
```

Both sides contain eight single-column characters. The config uses:

```text
--side-by-side
--width 20
--line-fill-method=spaces
--wrap-max-lines 2
--line-numbers-right-format |{np}
```

Two left formats are compared:

```text
control: |{nm}
wide:    界{nm}
```

The control has a true two-column line-number field and exactly eight content columns. The wide case is planned identically by current metadata, while its true line-number field consumes three columns.

The target test requires:

- control output contains the complete `abcdefgh`;
- wide-prefix output contains the configured `界`;
- wide-prefix output does not contain the complete `abcdefgh`.

If that passes, the accounting mismatch has a user-visible truncation consequence. If the full text survives, a downstream path masks this boundary and the mechanism remains an internal accounting bug only.

## Stop condition

Stop after the rendered-output target fixture classifies the consequence. Any source candidate should repair the width contract at its owner and retain ASCII/multicolumn controls. External issue, pull-request, comment, review, or other upstream interaction remains manual human work.