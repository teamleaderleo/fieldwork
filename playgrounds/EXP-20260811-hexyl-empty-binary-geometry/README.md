## In simple words

Exact Hexyl reproduces the empty-file binary table bug reported in #288.

At fixed terminal width 80 on `sharkdp/hexyl@6ecc29b9c8c84d08a7e860f7f69c22b113b480ea`:

```text
hexadecimal row widths: 80, 80, 80
binary row widths:      45, 80, 45
```

The hexadecimal control is internally consistent. Binary mode auto-selects one panel, so its top and bottom borders are 45 columns, but the special `No content` row remains 80 columns.

This experiment is promoted to Fieldwork candidate #834.

## Assignment

- Programme: #207
- Lane: #210
- Worker: `GPT-5.6 Sol`
- Experiment: `EXP-20260811-hexyl-empty-binary-geometry`
- Candidate owner: #834
- Target: `sharkdp/hexyl@6ecc29b9c8c84d08a7e860f7f69c22b113b480ea`
- Related report: [#288](https://redirect.github.com/sharkdp/hexyl/issues/288)
- Final run: `31444376782`
- Final job: `93635352237`
- Evidence class: `target-executed`
- Upstream contact authorized/performed: `false` / `false`

## Source map

Binary base uses a wider byte representation and can select one data panel at the tested width. Normal border rendering loops over `self.panels`.

The empty-input branch in `Printer::print_all()` resets `base_digits = 2` for the message geometry, prints the header through normal border code, then emits a fixed `No content` row with two data-panel-style cells and two fixed 9-column character cells. That row does not follow the active panel count.

## Exact target receipt

Hexadecimal output:

```text
┌────────┬─────────────────────────┬─────────────────────────┬────────┬────────┐
│        │ No content              │                         │        │        │
└────────┴─────────────────────────┴─────────────────────────┴────────┴────────┘
```

Widths: `80,80,80`.

Binary output:

```text
┌────────┬─────────────────────────┬────────┐
│        │ No content              │                         │        │        │
└────────┴─────────────────────────┴────────┘
```

Widths: `45,80,45`.

Workflow receipt:

```text
FIELDWORK_CONTROL hexadecimal-row-width-consistent= True
FIELDWORK_RESULT binary-row-width-consistent= False
FIELDWORK_RESULT empty-binary-geometry=mismatch-reproduced
```

Machine-readable receipt: `result.json`.

## Promotion

Candidate #834 owns the repair direction: derive the empty row from `self.panels`, `panel_sz()`, and the existing vertical separator glyph rather than fixed two-panel cells.

Fieldwork PR #835 executes that candidate against exact source with one-/two-/three-panel and panel-toggle controls.

## Stop condition

Experiment complete and promoted. External Hexyl remains read-only. Continue source work in candidate #834/#835 only; refresh upstream overlap before any external proposal.