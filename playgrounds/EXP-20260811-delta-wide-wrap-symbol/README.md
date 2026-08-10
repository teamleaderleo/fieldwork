## In simple words

Delta accepts a two-column grapheme as a wrap marker even though the option contract says the marker must have display width 1. On exact target source, that mismatch can make unlimited wrapping stop making progress, and the same failure now reproduces through the built public `delta` command.

With marker `+`, the focused wrapper owner terminates at content width 2 and the real CLI completes under the same narrow side-by-side budget. With the accepted marker `界` (one grapheme, two columns), the owner reaches an 8-second watchdog and the public CLI reaches the same watchdog.

This experiment is promoted to Fieldwork candidate #820.

## Assignment

- Programme: #207 (`open-source-ecosystems`)
- Lane: #210 (`developer-tools-build-systems`)
- Worker: `GPT-5.6 Sol`
- Experiment: `EXP-20260811-delta-wide-wrap-symbol`
- Candidate owner: #820
- Target repository: `dandavison/delta`
- Exact target: `95a0e224f55ccfdf3a7d1278fdea98a3edb9fbf4`
- Claim scope: mechanism + CLI reachability
- Evidence class: `target-executed`
- Final workflow run: `31440774199`
- Final job: `93624827655`
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

When a line must split, it subtracts the wrap marker's real display width from the available content width. The same function tries to prevent a no-progress wrap when only the marker fits:

```rust
let max_lines = if line_width <= INLINE_SYMBOL_WIDTH_1 {
    1
} else {
    wrap_config.max_lines
};
```

That guard uses the constant 1 rather than the accepted marker's real width.

### Unlimited mode

Public `--wrap-max-lines unlimited` maps to internal no-limit mode.

At content width 2 with marker `界` (width 2), zero columns remain for source text. Each iteration emits the marker while re-queueing the complete source text.

## Target execution: owner

The workflow fetched and fenced exact target source, injected test-only controls locally, and compiled before applying watchdogs.

### Validator reachability

```text
marker:          界
grapheme count:  1
display width:   2
configuration:   accepted
```

### One-column control

```text
marker:          +
content width:   2
text:            abc
max lines:       unlimited
result:          a+ / bc
```

Result: terminates.

### Two-column discriminator

```text
marker:          界
content width:   2
text:            abc
max lines:       unlimited
```

Receipt:

```text
FIELDWORK_RESULT owner-two-column-marker=watchdog-expired
```

Result: target owner does not make progress before the 8-second watchdog.

## Target execution: public CLI

The same exact checkout built `target/debug/delta` and received this minimal diff through stdin:

```text
diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1 +1 @@
-abc
+def
```

Both runs used:

```text
--side-by-side
--width 16
--line-fill-method=spaces
--wrap-max-lines unlimited
```

Width 16 creates 8-column panels. Default side-by-side line-number formatting consumes six columns, leaving the two-column content budget used by the owner test.

### CLI control

```text
--wrap-left-symbol +
```

Receipt:

```text
FIELDWORK_RESULT cli-one-column-marker=terminated
```

The command emitted its wrapped diff immediately.

### CLI discriminator

```text
--wrap-left-symbol 界
```

Receipt:

```text
FIELDWORK_RESULT cli-two-column-marker=watchdog-expired
```

The command did not terminate before the 8-second watchdog.

Machine-readable receipt: `result.json`.

## Promotion

This is now a user-reachable candidate rather than an internal-only mechanism finding.

Candidate owner: Fieldwork #820.

The next source work belongs in an owned Delta fork and should compare two repair layers:

1. **Contract repair:** validate actual terminal display width 1 for all wrap marker options.
2. **Progress hardening:** make `wrap_line()` guarantee that every loop consumes input or terminates, even if an invalid custom configuration reaches the owner.

The second layer is important because internal callers can bypass public option validation.

Regression controls should preserve:

- one-column `+` unlimited wrapping;
- wide marker handling without nontermination;
- narrow lines where only a marker fits;
- existing wrapping snapshots.

## Stop condition

Experiment complete and promoted. Continue implementation only in an owned fork or the Fieldwork candidate record. Refresh Delta upstream overlap before any external proposal. External issue, pull-request, comment, review, or other upstream interaction remains manual human work.