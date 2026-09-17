## In simple words

Zellij's current release loses parts of Telugu text because its grid stores one Unicode scalar per cell and deliberately drops width-zero scalars. The active upstream grapheme draft fixes that data-loss problem by storing full grapheme clusters.

The reporter then found a new failure on that draft: pasting Telugu can make the cursor drift and duplicate a word. The strongest mechanism lead is a column-count disagreement. The draft gives some Telugu graphemes fewer columns than the outer terminal gives the same scalars. For the exact reported line, a deterministic model of the inspected code gives 24 internal Zellij columns versus 32 columns under current Alacritty's scalar policy. The shorter phrase that visibly duplicates is 9 versus 11. One cluster, `ద్యం`, is 1 versus 3.

That is specific enough to promote into a target-native residual probe. It is also already inside an active upstream grapheme rewrite, so the useful next move is to test and feed evidence into that draft after authorization, not to start a parallel source patch.

## Assignment

- Programme: #207 (`open-source-ecosystems`)
- Lane: #210 (`developer-tools-build-systems`)
- Parent scout: #561
- Worker: `GPT-5.6 Sol`
- Target repository: `zellij-org/zellij`
- Target issue: [#5292](https://redirect.github.com/zellij-org/zellij/issues/5292)
- Active overlapping draft: [#4800](https://redirect.github.com/zellij-org/zellij/pull/4800)
- Upstream contact authorized: `false`
- Upstream contact performed: `false`
- Evidence class: `source-read + deterministic mechanism probe`
- Disposition: `PROMOTE — target-native residual probe; active-draft feedback candidate`

## Exact revisions

### Fieldwork

- Base head: `2b5e3ce23236e98dbd4c209a70fdfcd03ece8a9a`

### Zellij current main

- Commit: `f42ca3c79c65c967ab1da39dc5c99838a45cce04`
- `zellij-server/src/panes/terminal_character.rs` blob: `12463af88e7efc02d13a7fddc4b790ac45eea527`
- `zellij-server/src/panes/grid.rs` blob: `927c14a341c2124d7d3d1bd87d9c39cf9559f9e6`

### Zellij active grapheme draft

- Head: `d5c04daccfac765814e55ef2b89543bbe711629d`
- Base recorded by the PR: `b558b31ed192652f75ecc35d6753a7d5d0046023`
- `zellij-server/src/panes/terminal_character.rs` blob: `b1e924f7f36e7e35d99273f2a88815a06293fff0`
- `zellij-server/src/panes/grid.rs` blob: `626dc3f132df251b62726db5c4b61855c965db91`
- `zellij-server/src/output/mod.rs` blob: `899178917e0620b77993fe66f9dc79200e4ba08f`
- `zellij-utils/src/grapheme_width.rs` blob: `51c19d6149d7b01824fd38f4b64d9b7827dec515`

### Outer-terminal comparison

- Alacritty inspected commit: `1b2b36a64e88068ad02c95fad00ee2fad31c00bf`
- `alacritty_terminal/src/term/mod.rs` blob: `8eb67975e0ee7d877edaa5c9f38b6c8da6a2ff1f`
- `alacritty_terminal/Cargo.toml` blob: `bd58353e26e2f1b6d212b0383be56049a9eeffa7`
- Alacritty lockfile resolves `unicode-width` to `0.2.2`.
- `unicode-rs/unicode-width` tag: `v0.2.2`
- `src/lib.rs` blob: `a312037fc848a31c0e43c090e369492bb3534cff`

## Current overlap changed the question

The earlier Fieldwork intake treated #5292 as an open lead with no matching repair found. Current overlap changes that materially.

The issue now points to draft #4800. The reporter says they built that draft and confirmed that copy/paste out of Zellij preserves the Telugu conjuncts that current Zellij loses. They also report a new behavior on the draft: pasting `ఒక పద్యం వ్రాయి` can become `ఒక ఒక పద్యం వ్రాయి`, and the duplicated content remains in Zellij's buffer when copied back out.

So the old question, "where are combining marks discarded?", is already owned by the draft. The residual question is narrower:

> Does the draft preserve the grapheme text but assign different terminal-column widths from the outer terminal, causing cursor/render drift that can overwrite or duplicate content?

## Code map

### 1. Current Zellij loses data at grid ingestion

Current `TerminalCharacter` stores one `char` plus styles and a cached width from `UnicodeWidthChar`.

Current `Grid::add_character` then reads that scalar width and explicitly returns early when the width is zero. The source comment itself says this drops variation selectors and breaks grapheme segmentation.

That path explains the original #5292 loss mechanism: viramas and other zero-width scalars can disappear before render or clipboard extraction.

### 2. Draft #4800 changes the cell from scalar to grapheme

The draft changes `TerminalCharacter` to store the full extended grapheme cluster in `ColdString`, with methods including `grapheme()` and `push_scalar()`.

`Grid::add_character` keeps streaming EGC state. It uses `unicode_segmentation::GraphemeCursor` to decide whether the next scalar extends the prior cell. When it does, it calls `push_scalar()`, measures any width delta, and adjusts the internal cursor.

That is a real repair for the old data-loss path, and the reporter's copy test agrees.

### 3. Draft #4800 introduces a custom grapheme-width policy

`zellij-utils/src/grapheme_width.rs` is the draft's shared width policy for the grid and pane-content consumers.

For a multi-scalar grapheme it starts at the base scalar width. It recomputes the prefix width when a later scalar has width other than 1. A later scalar whose width is exactly 1 is skipped, except regional indicators.

The source explicitly describes this as making spacing combining marks such as Indic vowel signs contribute zero inside the grapheme. It also skips width-1 consonants after a virama.

This is the important branch condition for Telugu.

### 4. The draft serializes the full grapheme using its internal width

`zellij-server/src/output/mod.rs` increments `chunk_width` by `t_character.width()` and then appends `t_character.grapheme()` to the VTE output.

So Zellij can position/render according to one width while the outer terminal receives the literal Unicode scalars and applies its own width rules.

### 5. Current Alacritty uses per-scalar `unicode-width`

The reporter's environment names Alacritty as the outer terminal. In the inspected current Alacritty source, `Handler::input` calls `c.width()` for each input scalar. Width-zero scalars are attached to the previous cell; width-1 and width-2 scalars advance the terminal grid normally.

The current Alacritty lockfile resolves `unicode-width` `0.2.2`.

That crate says that, outside its listed special string cases, string width is the sum of character widths. `Grapheme_Extend` scalars are width zero and ordinary remaining scalars fall through to width one. Telugu has no special ligature rule in that list.

I found no `2027` or `grapheme cluster` handling in the inspected Alacritty tree through code search. The draft only enables outer-terminal CSI `?2027` mode when the host reports support; unsupported hosts continue without it.

## Executed mechanism probe

Probe:

`programmes/open-source-ecosystems/scouts/developer-tools-build-systems/ZELLIJ_TELUGU_WIDTH_PROBE.py`

Command:

```sh
python3 programmes/open-source-ecosystems/scouts/developer-tools-build-systems/ZELLIJ_TELUGU_WIDTH_PROBE.py
```

The probe is dependency-free. It fixes the exact reporter text and its EGC segmentation, transcribes only the `unicode-width 0.2.2` rules needed by those Telugu code points, and transcribes the draft helper's width loop. It is intentionally a mechanism model rather than a terminal emulator.

Observed output in the scout environment:

```text
residual
cluster unicode-width-0.2.2 draft
'ద్యం'  3  1  U+0C26 U+0C4D U+0C2F U+0C02
'వ్రా'  2  2  U+0C35 U+0C4D U+0C30 U+0C3E
'యి'    1  1  U+0C2F U+0C3F
TOTAL   11 9
DELTA   2

full-issue-fixture
cluster unicode-width-0.2.2 draft
'సం'    2  1  U+0C38 U+0C02
'తు'    2  1  U+0C24 U+0C41
'వు'    2  1  U+0C35 U+0C41
'గు'    2  1  U+0C17 U+0C41
'రిం'   2  1  U+0C30 U+0C3F U+0C02
'చి'    1  1  U+0C1A U+0C3F
'కం'    2  1  U+0C15 U+0C02
'ద్యం'  3  1  U+0C26 U+0C4D U+0C2F U+0C02
'వ్రా'  2  2  U+0C35 U+0C4D U+0C30 U+0C3E
'యి'    1  1  U+0C2F U+0C3F
TOTAL   32 24
DELTA   8

RESULT residual=11/9 full=32/24 critical-cluster=ద్యం:3/1 control=వ్రా:2/2
```

## Why `ద్యం` is a useful discriminator

`ద్యం` is:

- U+0C26 TELUGU LETTER DA — width 1;
- U+0C4D TELUGU SIGN VIRAMA — `Grapheme_Extend`, width 0;
- U+0C2F TELUGU LETTER YA — width 1;
- U+0C02 TELUGU SIGN ANUSVARA — a spacing mark and width 1 under `unicode-width 0.2.2`.

The draft begins at width 1. The virama triggers a prefix recomputation, which stays at 1. The later YA is width 1, so the draft skips it. The later anusvara is also width 1, so the draft skips it too. Final draft width: 1.

Current Alacritty's inspected scalar path sees 1 + 0 + 1 + 1 = 3.

The nearby control `వ్రా` behaves differently. Its final AA sign is width 0, so that final scalar triggers another prefix recomputation after the width-1 RA, bringing the draft back to 2. Both policies therefore give `వ్రా` width 2.

That pair is valuable because it can falsify a broad explanation like "the draft always treats Telugu conjuncts as one column." The disagreement depends on scalar order and which later scalar causes a recomputation.

## Competing explanations

### A. The residual is still caused by grapheme data loss

Evidence against: the reporter says draft #4800 preserves the conjuncts on copy to an external editor. The draft cell and output paths now carry the complete grapheme string.

Status: `deprioritized for the residual`.

### B. Zellij and the outer terminal disagree about display columns

Evidence for:

- the draft's helper intentionally suppresses width-1 scalars inside some EGCs;
- current Alacritty advances those same scalars individually with locked `unicode-width 0.2.2`;
- the exact reporter residual models as 9 versus 11 columns;
- the full reporter fixture models as 24 versus 32 columns;
- `ద్యం` gives a compact 1-versus-3 discriminator;
- Zellij serializes the literal grapheme while using its own cached width for chunk arithmetic.

Status: `leading mechanism`.

### C. The shell/readline/application itself duplicates the pasted word

Possible, because the visible symptom is produced while pasting into an interactive terminal application. The current evidence does not identify which application was active during the reporter's paste.

A target-native capture can separate this: compare bytes sent to the PTY, bytes emitted by the child, Zellij's grid text, and outer-terminal cursor position after each grapheme.

Status: `live alternative; weaker than the width mismatch lead`.

### D. CSI ?2027 support eliminates the mismatch on capable hosts

The draft explicitly queries outer-terminal support for grapheme mode and enables it when supported. Current Alacritty code search did not expose support for that mode, while its input path remains scalar-width based.

A host that implements 2027 may behave differently and belongs in the comparison matrix.

Status: `host-dependent branch; target-native matrix needed`.

## Test map and gap

The draft already adds width tests for:

- Devanagari vowel signs;
- Tamil vowel signs;
- a Devanagari virama conjunct;
- combining grave;
- keycaps;
- flags;
- ZWJ emoji;
- VS16 widening;
- selection extraction using the same width helper.

A search of the draft patch found no Telugu fixture. The exact #5292 sequence therefore exercises an uncovered ordering: a virama, a width-1 consonant, and then a width-1 spacing mark (`ద్యం`), plus several base+spacing-mark graphemes such as `సం` and `తు`.

## Contribution viability

Zellij's current contribution guide says maintainers are overloaded and are presently able to accept code contributions mainly for larger Roadmap projects; minor fixes may wait a long time. The active draft already owns this grapheme domain.

That makes the efficient path:

1. produce a target-native, exact-fixture receipt;
2. turn it into a minimal failing test or precise draft feedback;
3. seek upstream contact authorization before posting anything;
4. avoid a competing parallel PR.

## Ranked next probes

1. **Exact draft grid probe — highest value.** Run `d5c04d...` and feed the precise #5292 text through the grid parser. Record the internal cursor after each EGC and assert the critical `ద్యం` boundary. Compare with a per-scalar `unicode-width 0.2.2` host model.
2. **Real Alacritty + draft Zellij capture.** Reproduce `ఒక పద్యం వ్రాయి`, capture Zellij's `--debug` PTY bytes, copied grid text, and visible cursor/duplicate result. This decides whether the 9-versus-11 mismatch actually causes the reporter's duplicate.
3. **Host comparison.** Repeat with one outer terminal that reports CSI `?2027` support and one that does not. This separates a generic grapheme policy bug from the unsupported-host branch.
4. **Indic spacing-mark sweep.** Generate EGCs containing `Grapheme_Cluster_Break=SpacingMark` and post-virama consonants across Indic scripts, then compare the draft helper against its underlying scalar policy. This can show whether Telugu is one instance of a broader rule error.
5. **Only after the policy is decided: source candidate.** Add the smallest regression test around the chosen column contract. Treat width behavior as a compatibility contract, because changing it affects grid placement, selection, wrapping, rendering and memory/performance work in the same draft.

## Stop conditions

- Refresh this scout if draft #4800 moves from `d5c04daccfac765814e55ef2b89543bbe711629d` before any source proposal.
- Stop parallel implementation work if the active draft adds the exact Telugu case or documents a host-specific column contract that explains the observed result.
- Keep all third-party upstreams read-only until Fieldwork records explicit authorization for external contact.

## Recommendation

`PROMOTE — target-native residual probe; active-draft feedback candidate.`

The original data-loss bug has active overlap and appears repaired by the draft according to the reporter. The residual duplication has a narrow, falsifiable width-policy mechanism with an exact discriminator and runnable probe. The next useful evidence is target-native execution around `ద్యం` and the 9-versus-11 short phrase, followed by an outer-terminal capability comparison.
