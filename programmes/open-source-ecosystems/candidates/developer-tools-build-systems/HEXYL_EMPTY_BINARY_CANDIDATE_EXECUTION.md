## In simple words

Hexyl candidate #834 is validated on exact target source.

Baseline exact Hexyl at terminal width 80 reproduces:

```text
hexadecimal: 80,80,80
binary:      45,80,45
```

The candidate replaces the fixed empty-input two-panel formatter with a row that loops over the active panel count while preserving Hexyl's existing outer vertical separator glyph.

After the candidate:

```text
hexadecimal: 80,80,80  byte-identical to baseline
binary:      45,45,45
```

Explicit one-, two-, and three-panel layouts are internally width-consistent, as are `--no-characters`, `--no-position`, and data-only controls. Formatting, build, and the full Hexyl test suite pass.

## Assignment

- Programme: #207
- Lane: #210
- Candidate owner: #834
- Parent experiment PR: #833
- Candidate validation PR: #835
- Worker: `GPT-5.6 Sol`
- Target: `sharkdp/hexyl@6ecc29b9c8c84d08a7e860f7f69c22b113b480ea`
- Fieldwork candidate head at execution: `ecb7e4800ebcee605fcfe41a433f3e8b26b46bcf`
- Workflow run: `31444710944`
- Job: `93636314470`
- Evidence class: `source-candidate-executed`
- Upstream contact authorized/performed: `false` / `false`

## Candidate evolution

The first candidate generation used the active panel count correctly but selected Hexyl's inner separator glyph between empty-row cells. Existing empty-output coverage expects the outer vertical glyph throughout that special row, so the test suite rejected the visual change.

The narrowed candidate keeps the panel-count loop and uses `outer_sep` at every empty-row cell boundary. This preserves the existing two-panel hexadecimal output byte-for-byte while repairing one-panel binary geometry.

## Generated source diff

The exact-source transformer changes only the empty branch in `Printer::print_all()`.

Instead of fixed formatting for two data panels and two character cells, it now:

1. emits one leading outer separator;
2. emits the optional 8-column position cell;
3. loops over `self.panels` data cells of `panel_sz()` columns, putting `No content` only in the first;
4. loops over `self.panels` 8-column character cells when enabled;
5. uses the existing outer vertical separator for each empty-row boundary.

Fieldwork CI generated the resulting Git diff mechanically after the exact-source transform applied.

## Baseline receipts

```text
baseline hexadecimal widths: [80, 80, 80]
baseline binary widths:      [45, 80, 45]
```

## Candidate receipts

Auto layout at terminal width 80:

```text
candidate hexadecimal widths: [80, 80, 80]
candidate binary widths:      [45, 45, 45]
FIELDWORK_RESULT hexyl-empty-binary-geometry=fixed
FIELDWORK_RESULT hexadecimal-control=byte-identical
```

Explicit binary panel counts:

```text
panels=1 -> [45, 45, 45]
panels=2 -> [80, 80, 80]
panels=3 -> [115, 115, 115]
FIELDWORK_RESULT explicit-panel-controls=consistent
```

Panel toggles:

```text
--no-characters                  -> [36, 36, 36]
--no-position                    -> [36, 36, 36]
--no-characters --no-position    -> [27, 27, 27]
FIELDWORK_RESULT panel-toggle-controls=consistent
```

## Repository checks

The executed candidate passes:

```text
cargo fmt --check
cargo build --locked --bin hexyl
cargo test --locked
```

Test totals:

```text
10 library tests passed
5 main/unit tests passed
41 integration tests passed
0 failures
```

## Disposition

`SOURCE-CANDIDATE VALIDATED IN FIELDWORK CARRIER`.

Recommended next step is permanent regression coverage for empty binary auto layout plus explicit panel/toggle cases before any external proposal. External Hexyl remains read-only and upstream interaction remains human-gated.