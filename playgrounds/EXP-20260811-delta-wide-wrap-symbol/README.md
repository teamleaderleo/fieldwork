## In simple words

Delta's unlimited wrapper can stop making progress when the next source grapheme does not fit in the columns left before the wrap marker. This now reproduces with a completely valid one-column `+` marker: at content width 2, input beginning with the two-column grapheme `界` is re-queued unchanged on every wrap iteration.

The exact target owner and the built public `delta` command both reach an 8-second watchdog for that valid configuration. The ASCII control terminates immediately.

There is a second bug in the same area: wrap-marker validation says display width must be 1 but actually checks grapheme count, so a two-column grapheme such as `界` is accepted as a marker and provides another route into the same no-progress family.

This experiment is promoted to Fieldwork candidate #820. The wrap-loop progress invariant is now the primary owner; marker validation is a secondary defense layer.

## Assignment

- Programme: #207 (`open-source-ecosystems`)
- Lane: #210 (`developer-tools-build-systems`)
- Worker: `GPT-5.6 Sol`
- Experiment: `EXP-20260811-delta-wide-wrap-symbol`
- Candidate owner: #820
- Target repository: `dandavison/delta`
- Exact target/current head: `95a0e224f55ccfdf3a7d1278fdea98a3edb9fbf4`
- Claim scope: mechanism + CLI reachability
- Evidence class: `target-executed`
- Latest workflow run: `31489009549`
- Latest job: `93770852535`
- Upstream contact authorized: `false`
- Upstream contact performed: `false`

## Source map

### Primary owner: `wrap_line()` can requeue unchanged text

`src/wrapping.rs` segments a source segment into graphemes and records each grapheme's real terminal width. When a line must split, it computes how much source width can fit before the left wrap marker.

If the first grapheme is wider than that remaining width, the byte split position stays zero. The code then sets the next line to the entire original `text`, pushes that unchanged segment back on the stack, emits the marker, resets the current line, and repeats.

With finite wrapping, the line-count limit eventually stops the loop. Public `--wrap-max-lines unlimited` maps to internal `max_lines == 0`, so there is no line-count stop.

The existing guard only special-cases `line_width <= INLINE_SYMBOL_WIDTH_1`, where the constant is 1. It does not cover a two-column line with a valid one-column marker when the next source grapheme itself occupies two columns.

### Secondary owner: marker validation counts graphemes

All three public wrap-marker options pass through `ensure_display_width_1()`:

- `--wrap-left-symbol`;
- `--wrap-right-symbol`;
- `--wrap-right-prefix-symbol`.

The helper's error says the symbol's display width must be 1, but the implementation checks one grapheme cluster with `grapheme_indices(true).count()`. A one-grapheme/two-column marker therefore passes.

## Target execution: exact owner

The workflow fetched and fenced the exact current Delta source, injected test-only controls locally, and compiled before applying watchdogs.

### ASCII negative control

```text
marker:          +
content width:   2
text:            abc
max lines:       unlimited
result:          a+ / bc
```

Result: terminates.

### Valid marker + wide source grapheme

```text
marker:          +
content width:   2
text:            界a
max lines:       unlimited
```

Receipt:

```text
FIELDWORK_RESULT owner-valid-marker-wide-grapheme=watchdog-expired
```

Result: exact target owner makes zero source progress before the 8-second watchdog.

### Accepted two-column marker

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

This remains useful as a separate configuration-contract bug, but it is no longer required to trigger nontermination.

## Target execution: public CLI

The same exact checkout built `target/debug/delta`. Runs used:

```text
--side-by-side
--width 16
--line-fill-method=spaces
--wrap-max-lines unlimited
```

Width 16 gives 8-column panels; default side-by-side line-number formatting leaves the two-column content budget exercised by the owner tests.

### ASCII control

A minimal replacement diff with ASCII content and valid marker `+` terminates:

```text
FIELDWORK_RESULT cli-one-column-marker-ascii=terminated
```

### Valid marker + wide source fixture

The replacement line begins with `界` while the marker stays `+`:

```text
+界a
```

Receipt:

```text
FIELDWORK_RESULT cli-valid-marker-wide-grapheme=watchdog-expired
```

This proves the broader failure is reachable through valid public configuration.

### Wide marker route

With ASCII replacement text and `--wrap-left-symbol 界`:

```text
FIELDWORK_RESULT cli-two-column-marker=watchdog-expired
```

Machine-readable receipt: `result.json`.

## Promotion

Candidate owner: Fieldwork #820.

Source work should now prioritize two layers in this order:

1. **Progress invariant:** every `wrap_line()` split must consume at least one source grapheme or terminate safely. Re-queuing an unchanged source segment must never continue an unlimited loop.
2. **Contract repair:** validate actual terminal display width 1 for wrap marker options rather than grapheme count.

A useful repair should preserve existing output when a split can make progress and choose an explicit safe outcome when the next grapheme cannot fit before the marker. That outcome needs testing rather than assumption because it affects truncation and side-by-side alignment.

Regression controls should retain:

- valid `+` + ASCII unlimited wrapping terminates with existing output;
- valid `+` + leading two-column grapheme terminates;
- accepted/rejected wide-marker behavior cannot hang;
- finite wrapping remains bounded;
- existing wrapping snapshots remain unchanged away from the no-progress boundary.

## Stop condition

Experiment complete and promoted. Continue implementation only in an owned fork or the Fieldwork candidate record. Refresh Delta overlap before any external proposal. External issue, pull-request, comment, review, or other upstream interaction remains manual human work.
