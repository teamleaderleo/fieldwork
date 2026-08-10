## In simple words

Delta accepts a two-column grapheme as a wrap marker even though the option contract says the marker must have display width 1. On exact current source, that mismatch can make unlimited wrapping stop making progress.

This is target-executed now. With line width 2, marker `+` and text `abc`, the wrapper terminates as `a+` / `bc`. With the accepted marker `界` (one grapheme, two columns), the same unlimited-wrap owner never consumes source text and reaches the external 8-second watchdog.

The next bounded step is the built command itself: feed a minimal diff to `delta --side-by-side --width 16 --wrap-max-lines unlimited` with the same markers. Width 16 gives an 8-column panel; the default six-column line-number field leaves a two-column content budget, reaching the exact owner condition through public CLI options.

## Assignment

- Programme: #207 (`open-source-ecosystems`)
- Lane: #210 (`developer-tools-build-systems`)
- Worker: `GPT-5.6 Sol`
- Experiment: `EXP-20260811-delta-wide-wrap-symbol`
- Target repository: `dandavison/delta`
- Exact target: `95a0e224f55ccfdf3a7d1278fdea98a3edb9fbf4`
- Claim scope: mechanism
- Evidence class: `target-executed`
- Workflow run: `31425334965`
- Job: `93575567871`
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

When a line must split, it computes available source-text width using the wrap marker's real display width. The same function tries to prevent a no-progress wrap when only the marker fits:

```rust
let max_lines = if line_width <= INLINE_SYMBOL_WIDTH_1 {
    1
} else {
    wrap_config.max_lines
};
```

That guard uses the constant 1, rather than the accepted marker's real width.

### Unlimited mode

Public `--wrap-max-lines unlimited` maps to internal `0`; `line_limit_reached` treats `0` as no limit.

With:

```text
line width = 2
left marker = 界 (one grapheme, width 2)
text = abc
max lines = unlimited
```

the owner has zero width available for source text, emits the marker, pushes `abc` back, and repeats.

## Exact target execution

The workflow fetched exact target source read-only, verified the SHA, injected test-only controls locally, compiled the target, and ran three discriminators.

### 1. Public configuration reaches the bad state

Input marker:

```text
界
```

Observed:

```text
grapheme count = 1
display width = 2
configuration = accepted
```

Result: `PASS`.

### 2. One-column negative control terminates

Configuration:

```text
marker = +
line width = 2
text = abc
max lines = unlimited
```

Observed:

```text
a+
bc
```

Result: `PASS`.

### 3. Two-column marker stops making progress

Configuration:

```text
marker = 界
line width = 2
text = abc
max lines = unlimited
```

The compiled target test was run under an external watchdog after all compilation completed.

Observed receipt:

```text
FIELDWORK_RESULT two-column-marker=watchdog-expired
```

The watchdog expired after 8 seconds while the one-column control completed immediately.

Result: `TARGET-EXECUTED NONTERMINATION`.

Full machine-readable receipt: `result.json`.

## Why this is a strong bug candidate

The executed chain now contains:

1. a public option;
2. a validator whose error text promises display width 1;
3. an accepted value that violates that promise;
4. downstream code that relies on the promised one-column property;
5. public unlimited wrapping;
6. a target-executed no-progress loop;
7. a one-column negative control that terminates.

The remaining gate is user-facing command reachability, rather than the mechanism itself.

## Next discriminator: real CLI

Build exact target source, then feed this minimal diff through the normal binary:

```text
diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1 +1 @@
-abc
+def
```

Use side-by-side fixed width 16 and space fill so each panel is width 8. Default side-by-side line-number formatting consumes six columns, leaving the two-column content width used by the target test.

Run the same binary twice under watchdogs:

- `--wrap-left-symbol +` must complete;
- `--wrap-left-symbol 界` is classified as completion versus watchdog expiry.

If the wide-marker CLI run reaches the watchdog while the control completes, promote this into a durable Delta scout/owned-fork regression candidate. If the CLI path introduces a guard that prevents the condition, retain the internal target result and stop promotion.

## Stop condition

Stop after the ordinary CLI discriminator classifies the public path. Any source candidate remains in an owned fork for local review. External issue, pull-request, comment, review, or other upstream interaction remains manual human work.