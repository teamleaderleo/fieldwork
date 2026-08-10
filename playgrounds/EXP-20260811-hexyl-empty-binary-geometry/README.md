## In simple words

Hexyl has a compact empty-input geometry lead in binary mode. Binary bytes use eight base digits, which makes each data panel wider and can reduce the automatic layout to one panel at an ordinary terminal width. The normal border renderer respects `self.panels`.

The special empty-input row takes a different path: it resets base-digit state for the message, writes `No content`, and emits fixed separator cells rather than deriving every cell from the active panel count. That can make the empty row wider than its surrounding one-panel border.

This experiment runs the exact current Hexyl binary against an empty file in binary and hexadecimal modes, strips ANSI sequences, and records every rendered row width.

## Assignment

- Programme: #207 (`open-source-ecosystems`)
- Lane: #210 (`developer-tools-build-systems`)
- Worker: `GPT-5.6 Sol`
- Experiment: `EXP-20260811-hexyl-empty-binary-geometry`
- Target: `sharkdp/hexyl@6ecc29b9c8c84d08a7e860f7f69c22b113b480ea`
- Related upstream report: [#288](https://redirect.github.com/sharkdp/hexyl/issues/288)
- Evidence class: `source-read`, pending `target-executed`
- Upstream contact authorized/performed: `false` / `false`

## Source map

Binary base uses `base_digits = 8`; hexadecimal uses `base_digits = 2`.

Panel width is derived from base-digit width and group size. At an ordinary fixed terminal width, binary mode can therefore select fewer panels than hexadecimal mode.

Normal top/bottom borders are emitted by iterating the active panel count.

The empty-input special case in `Printer::print_all()` does not use the same loop for its `No content` row. Its fixed cells are the leading explanation for the issue screenshot where binary mode has a short border and an over-wide message row.

## Target discriminator

Create one zero-byte file and run exact Hexyl twice with a fixed 80-column terminal width and color disabled:

```text
hexadecimal control
binary discriminator
```

Strip ANSI escapes and record the Unicode display width of every non-empty output line.

Expected control:

```text
all hexadecimal table rows have one consistent width
```

Positive discriminator:

```text
binary border rows share one width
binary No content row has a different width
```

The workflow also records exact stdout so any unexpected layout can be remapped rather than inferred from width alone.

## Stop condition

Stop after the real binary classifies both bases. If the binary row mismatch reproduces while hexadecimal stays consistent, promote the empty-row geometry owner into a candidate. Otherwise retain a negative result.

External Hexyl remains read-only. No upstream interaction is authorized.