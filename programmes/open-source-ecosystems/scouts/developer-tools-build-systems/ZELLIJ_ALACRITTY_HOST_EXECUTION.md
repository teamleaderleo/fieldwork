## In simple words

The mixed-width boundary is now executed on both sides of the actual interface.

Exact Zellij grapheme draft `d5c04daccfac765814e55ef2b89543bbe711629d` stores the Telugu discriminator `ద్యం` at column 1, while exact Alacritty terminal source `1b2b36a64e88068ad02c95fad00ee2fad31c00bf` advances the same bytes to column 3. For the reporter's short phrase, Zellij reaches column 9 and Alacritty reaches column 11. For the full reporter line, Zellij reaches column 24 and Alacritty reaches column 32.

The cursor consequence is target-executed too. After `ద్యం`, ordinary `CUB 2` reaches column 0 inside the Zellij draft and column 1 in Alacritty. The nearby `వ్రా` control stays aligned at width 2 and reaches column 1 after `CUB 1` on both sides.

This establishes a real interface disagreement between the exact draft the reporter tested and the inspected Alacritty host path. It still does not prove the reporter's visible duplicated word without a real child-process redraw capture, but the width/cursor mismatch itself is no longer model-only.

## Assignment

- Programme: #207 (`open-source-ecosystems`)
- Lane: #210 (`developer-tools-build-systems`)
- Parent scout: #561
- Fieldwork scout PR: #790
- Worker: `GPT-5.6 Sol`
- Zellij draft: `d5c04daccfac765814e55ef2b89543bbe711629d`
- Alacritty source: `1b2b36a64e88068ad02c95fad00ee2fad31c00bf`
- Zellij execution run: `31423503911`, job `93569631164`
- Alacritty execution run: `31425870506`, job `93577301537`
- Alacritty owned carrier head: `6caf970f3de2b8229c79d69d7776cf5e07036ad5`
- Evidence class: `paired-target-executed`
- Claim scope: interface mechanism
- Upstream contact authorized: `false`
- Upstream contact performed: `false`

## Zellij side

The focused Zellij run executed six controls against exact draft source and completed:

```text
6 passed; 0 failed; 1318 filtered out
```

Observed:

```text
ద్యం                    Zellij cursor 1
వ్రా                    Zellij cursor 2
ఒక పద్యం వ్రాయి         Zellij cursor 9
వసంత ఋతువు గురించి ఒక కంద పద్యం వ్రాయి   Zellij cursor 24
```

After `ద్యం`, `CSI 2 D` moves the Zellij grid from column 1 to column 0.

See `ZELLIJ_TELUGU_WIDTH_EXECUTION.md` for the full Zellij-side receipt.

## Alacritty side

The owned carrier fetched exact public Alacritty source read-only, verified the checkout SHA, appended four execution-only tests to `alacritty_terminal/src/term/mod.rs`, and ran:

```sh
cargo test --locked -p alacritty_terminal fieldwork_telugu_host --lib -- --nocapture
```

Run `31425870506`, job `93577301537` completed successfully:

```text
running 4 tests
fieldwork_telugu_host_control_cluster_uses_two_columns ... ok
fieldwork_telugu_host_full_reporter_line_uses_thirty_two_columns ... ok
fieldwork_telugu_host_critical_cluster_uses_three_scalar_columns ... ok
fieldwork_telugu_host_reporter_residual_uses_eleven_columns ... ok

test result: ok. 4 passed; 0 failed; 0 ignored; 0 measured; 132 filtered out
```

The exact checkout fence recorded:

```text
alacritty=1b2b36a64e88068ad02c95fad00ee2fad31c00bf
carrier=6caf970f3de2b8229c79d69d7776cf5e07036ad5
```

Observed:

```text
ద్యం                    Alacritty cursor 3
వ్రా                    Alacritty cursor 2
ఒక పద్యం వ్రాయి         Alacritty cursor 11
వసంత ఋతువు గురించి ఒక కంద పద్యం వ్రాయి   Alacritty cursor 32
```

After `ద్యం`, `CSI 2 D` moves Alacritty from column 3 to column 1. After `వ్రా`, `CSI 1 D` moves Alacritty from column 2 to column 1.

## Paired discriminator

```text
input                               Zellij draft   Alacritty
ద్యం                                1              3
వ్రా                                2              2
ఒక పద్యం వ్రాయి                     9              11
full reporter line                  24             32

ద్యం + CUB 2 destination            0              1
వ్రా + CUB 1 destination            1              1
```

The `వ్రా` negative control is important: this is sequence-sensitive behavior rather than a generic difference for all Telugu conjuncts.

## Retained harness correction

Alacritty run `31424544712` failed during compilation before any assertion executed because the injected test used `let mut parser = ansi::Processor::new();`, which left the timeout type parameter ambiguous in that unit-test context.

The repaired carrier changed only that line to an explicit `ansi::Processor` type. The test inputs, expected cursor columns, exact Alacritty source SHA, and command remained unchanged.

Classification of the earlier run: `harness failure`.

## What is established

**Observed on real target code:**

- the exact Zellij draft preserves the complete Telugu text and caches narrower column counts for the reporter fixture;
- exact Alacritty consumes the same literal bytes at larger scalar-based column counts;
- ordinary cursor-back commands therefore reach different destinations after the critical cluster;
- the nearby control remains aligned.

**Source-supported:**

- Zellij serializes complete grapheme strings while using its cached grapheme width for output chunk arithmetic;
- Alacritty's terminal input path uses scalar `UnicodeWidthChar` widths;
- Alacritty's exact build resolves `unicode-width 0.2.2`;
- current inspected Alacritty code has no mode-2027 implementation found in the scout's code search.

**Inferred:**

- an interactive child application that redraws using the legacy scalar column ledger can address a different location than Zellij's grapheme-compressed grid believes it is addressing;
- this is a strong mechanism for overwrite/duplication behavior in the reporter's Alacritty setup.

**Still unknown:**

- the reporter's exact inner application and redraw bytes;
- whether the exact visible duplicated word is reproduced end-to-end under a controlled PTY capture;
- how the draft should translate between legacy and mode-2027 width ledgers;
- whether the active draft will preserve this implementation after rebasing onto current main.

## Disposition

`PAIRED-TARGET-EXECUTED WIDTH/CURSOR MISMATCH / ACTIVE EXTERNAL DRAFT OWNER`.

Next bounded work:

1. capture one real legacy child-process redraw sequence through the exact Zellij draft;
2. record child output bytes, Zellij grid state, serialized host output, and host cursor state;
3. compare with a mode-2027-capable path if available;
4. refresh the external draft before proposing any source change;
5. keep upstream feedback gated on explicit human authorization.

No third-party upstream mutation or contact occurred.