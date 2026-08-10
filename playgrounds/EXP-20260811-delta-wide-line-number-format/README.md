## In simple words

Delta lets users customize the literal text around side-by-side line numbers. Current parsing records those literal prefixes and suffixes by counting grapheme clusters, then uses that number as terminal-column width when deciding how much code fits in each panel.

One grapheme can occupy two columns. On exact Delta source, `界{nm}` is target-executed as metadata width 2 while rendered `界1` occupies width 3. In fixed width-20 side-by-side mode, Delta plans eight content columns on the left even though the real line-number field leaves seven. The ASCII control `|{nm}` stays aligned at width 2.

The mismatch also changes final rendered output at the exact boundary: an eight-character source line survives with `|{nm}`, while the same line no longer appears complete with `界{nm}`. This experiment is promoted to Fieldwork candidate #821.

## Assignment

- Programme: #207 (`open-source-ecosystems`)
- Lane: #210 (`developer-tools-build-systems`)
- Worker: `GPT-5.6 Sol`
- Experiment: `EXP-20260811-delta-wide-line-number-format`
- Candidate owner: #821
- Target: `dandavison/delta@95a0e224f55ccfdf3a7d1278fdea98a3edb9fbf4`
- Claim scope: mechanism + rendered consequence
- Evidence class: `target-executed`
- Final workflow run: `31441079950`
- Final job: `93625722481`
- Upstream contact authorized/performed: `false` / `false`

## Source map

`src/format.rs` parses line-number format strings. For literal prefix/suffix text it stores:

```rust
prefix_len = prefix.graphemes(true).count();
suffix_len = suffix.graphemes(true).count();
```

`FormatStringPlaceholderData::width()` later returns those values as widths.

`src/features/line_numbers.rs::LineNumbersData::formatted_width()` combines that metadata with number-field width.

`src/features/side_by_side.rs::available_line_width()` subtracts `formatted_width()` from the panel width. This decides how much code can fit before final painting.

The literal prefix itself is emitted unchanged, so the terminal sees its real display width.

## Exact target execution

The workflow fetched exact target source read-only, fenced the checkout SHA, injected execution-only tests locally, and ran the focused owner plus rendered boundary.

### Wide prefix

```text
format:                 界{nm}
metadata total width:   2
rendered example:       界1
actual display width:   3
difference:             +1 physical column
```

Result: `PASS`.

### ASCII negative control

```text
format:                 |{nm}
metadata total width:   2
rendered example:       |1
actual display width:   2
difference:             0
```

Result: `PASS`.

### Real side-by-side budget

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

## Rendered-output consequence

Boundary diff:

```text
-abcdefgh
+zzzzzzzz
```

Configuration:

```text
--side-by-side
--width 20
--line-fill-method=spaces
--wrap-max-lines 2
--line-numbers-right-format |{np}
```

Two left formats were compared:

```text
control: |{nm}
wide:    界{nm}
```

The target test establishes:

```text
ASCII control contains complete abcdefgh: true
wide prefix reaches rendered output:      true
wide output contains complete abcdefgh:   false
```

The final workflow run reports all focused tests passing, including:

```text
fieldwork_delta_wide_prefix_gives_content_one_extra_panel_column ... ok
fieldwork_delta_wide_prefix_changes_rendered_boundary_output ... ok
```

Machine-readable receipt: `result.json`.

## Promotion

Candidate owner: Fieldwork #821.

The narrow repair owner is line-number format width metadata. A source candidate should budget literal prefixes and suffixes by terminal display width instead of grapheme count while preserving placeholder-number width behavior.

Regression controls should retain:

- ASCII `|{nm}` behavior unchanged;
- `界{nm}` budgeted at its real width;
- the rendered boundary keeps the intended content budget;
- existing one-column format snapshots unchanged.

## Overlap refresh

Before promotion, current Delta head was refreshed and remains `95a0e224f55ccfdf3a7d1278fdea98a3edb9fbf4`. Focused searches found no matching open upstream issue or PR for wide Unicode line-number literal width.

## Stop condition

Experiment complete and promoted. Continue implementation only in an owned Delta fork or the Fieldwork candidate record. External issue, pull-request, comment, review, or other upstream interaction remains manual human work.