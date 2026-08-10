## In simple words

Delta says each side-by-side wrap marker has display width 1, but its validator checks that the option contains one grapheme cluster. Those are different properties: `界` is one grapheme and two terminal columns.

That becomes consequential in the wrapping loop. The loop subtracts the marker's real display width from the space available for source text. It has a special guard intended to stop wrapping when only the marker fits, but that guard compares the line width against the constant `1` because validated markers are assumed to be one column. With a two-column marker in a two-column line, no source grapheme fits before the marker. In unlimited mode there is no line-count stop, so source reading predicts the same input will be pushed back forever.

This experiment tests that exact sequence against current Delta source. A one-column marker is the negative control.

## Assignment

- Programme: #207 (`open-source-ecosystems`)
- Lane: #210 (`developer-tools-build-systems`)
- Worker: `GPT-5.6 Sol`
- Experiment: `EXP-20260811-delta-wide-wrap-symbol`
- Target repository: `dandavison/delta`
- Exact target: `95a0e224f55ccfdf3a7d1278fdea98a3edb9fbf4`
- Claim scope: mechanism
- Upstream contact authorized: `false`
- Upstream contact performed: `false`

## Source map

### Option intake

`src/wrapping.rs` builds `WrapConfig` from the public options:

- `--wrap-left-symbol`;
- `--wrap-right-symbol`;
- `--wrap-right-prefix-symbol`.

All three call `ensure_display_width_1()`.

The error produced by that helper says the symbol's **display width** must be 1. The implementation checks:

```rust
arg.grapheme_indices(true).count()
```

against `INLINE_SYMBOL_WIDTH_1 == 1`.

So one two-column grapheme passes the documented check.

### Wrapping owner

`wrap_line()` segments source text into graphemes and records each grapheme's real `UnicodeWidthStr::width()`.

When a line must split, it computes available source-text width as:

```text
current fit before overflow
- wrap_left_symbol.width()
```

The same function tries to prevent a no-progress wrap when only the marker fits:

```rust
let max_lines = if line_width <= INLINE_SYMBOL_WIDTH_1 {
    1
} else {
    wrap_config.max_lines
};
```

That guard uses the constant 1, not the accepted marker's real width.

### Unlimited mode

Public `--wrap-max-lines` accepts `unlimited`. `adapt_wrap_max_lines_argument()` maps `unlimited` to internal `0`; `line_limit_reached` treats `0` as no limit.

With:

```text
line width = 2
left marker = 界 (one grapheme, width 2)
text = abc
max lines = unlimited
```

source reading predicts:

```text
abc -> no source grapheme fits before 界 -> emit 界 -> push abc back
    -> no source grapheme fits before 界 -> emit 界 -> push abc back
    -> ...
```

The one-column marker `+` is the negative control; it leaves one column for source text and therefore makes progress.

## Why this is worth executing

This is stronger than the nearby `truncate_str()` debug assertion for graphemes wider than two columns. It combines:

- a public option;
- a validator that promises the wrong property;
- a downstream algorithm that relies on the promised property;
- an explicit unlimited mode;
- a deterministic negative control.

The remaining reachability question is whether the exact target configuration accepts the wide marker and the wrapper behaves as the source model predicts. The retained CI probe answers only that narrow mechanism first.

## Exact controls

The execution-only test material is `delta_probe_tests.rs`.

1. **Validator reachability** — construct configuration with `--wrap-left-symbol 界`; require one grapheme and actual display width 2.
2. **Negative control** — with marker `+`, width 2 and unlimited wrapping, `abc` must terminate as `a+` / `bc`.
3. **Watchdog discriminator** — with marker `界`, width 2 and unlimited wrapping, run the target-native test under an external timeout after compilation. Record termination versus watchdog expiry as an experiment result rather than treating timeout itself as CI failure.

## Competing explanations

### A. Configuration rejects the wide marker earlier

If true, stop. The source helper would be misleading but the no-progress loop would be unreachable through the tested public option path.

### B. Another wrapping branch makes progress

If both the one- and two-column cases terminate, retain a negative result and inspect the actual transition before proposing anything.

### C. Wide marker acceptance plus no-progress loop

If configuration accepts `界`, the `+` control terminates, and only the wide-marker test reaches the watchdog, the mechanism is target-executed.

A later promotion would still need an ordinary CLI reproduction showing a realistic narrow panel/configuration reaches the same owner.

## Stop condition

Stop this experiment after the three controls classify the mechanism. Do not create a Delta source candidate from source reading alone. Any external issue, pull request, comment, review, or other interaction remains manual human work.