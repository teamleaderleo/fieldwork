## In simple words

Zellij sits between an application and a host terminal, and each side can independently use legacy per-codepoint cursor widths or mode-2027 grapheme widths.

The active grapheme draft preserves full grapheme text, but its grid width is grapheme-based even while the inner application's `?2027` mode is off. The client separately probes the outer terminal and enables host `?2027` only when the host reports support.

That creates four possible mode combinations. Source reading says the draft is naturally aligned only when both sides use grapheme semantics. The exact Telugu probe is testing the most common legacy/legacy quadrant, where `ద్యం` is cached as one Zellij column while a scalar-width consumer counts three.

## Evidence boundary

Target draft: `zellij-org/zellij@d5c04daccfac765814e55ef2b89543bbe711629d`  
Current Alacritty inspected: `alacritty/alacritty@1b2b36a64e88068ad02c95fad00ee2fad31c00bf`  
JLine primary mode-2027 documentation inspected: `jline/jline3@35fc24edb6065b7a8f0d5e490f72040b6c03a377`, `website/docs/advanced/grapheme-cluster-mode.md`  
Owned execution carrier: `teamleaderleo/zellij#1`  
Claim scope: interface mechanism  
Upstream contact authorized: `false`

Evidence labels in this file:

- **Documented** — stated in source comments or first-party project documentation.
- **Observed** — produced by a retained Fieldwork execution receipt.
- **Inferred** — consequence derived from documented/observed mechanics and still awaiting an end-to-end capture.
- **Unknown** — unresolved.

## The two independent mode owners

### Inner application -> Zellij grid

**Documented.** The draft adds `Grid::grapheme_cluster_mode`, toggled by inner PTY escape sequences `CSI ? 2027 h/l`.

The field comment says this flag changes cursor/edit operations and that segmentation itself is always on. The grid also answers DECRPM 2027 queries, so applications can discover that Zellij implements the mode.

The cell's grapheme width, however, is computed by the draft helper whenever scalars are appended. That helper does not take `grapheme_cluster_mode` as an argument. Therefore an inner application can remain in legacy mode while stored cell widths already follow the draft's grapheme policy.

### Zellij client -> outer terminal

**Documented.** The draft client sends `CSI ? 2027 $ p` during startup. It parses the host DECRPM response and enables `CSI ? 2027 h` only when the host reports support but the mode is currently reset. It disables the mode on exit only when Zellij enabled it.

Current Alacritty code search found no mode-2027 implementation. Its inspected terminal input path calls `UnicodeWidthChar::width()` per scalar and attaches only width-zero scalars to the preceding cell.

JLine's first-party mode-2027 documentation describes the same contract in explicit terms: without mode 2027, terminal cursor movement is per-codepoint `wcwidth()`; with 2027, the terminal uses grapheme-cluster segmentation. It also calls graceful fallback without 2027 a best practice.

## Compatibility matrix

| Inner app semantics | Outer host semantics | Draft grid width | Expected relation | Current evidence |
| --- | --- | --- | --- | --- |
| legacy scalar | legacy scalar | grapheme width | **mismatch**: inner and host count scalars while grid caches EGC width | leading Telugu carrier |
| grapheme / 2027 | legacy scalar | grapheme width | **output mismatch**: inner and grid agree; host can advance farther on serialized scalars | source-read; host integration pending |
| legacy scalar | grapheme / 2027 | grapheme width | **inner mismatch**: grid and host agree; legacy app can issue cursor/edit commands from a larger scalar count | source-read; simulated CUB control pending |
| grapheme / 2027 | grapheme / 2027 | grapheme width | aligned in principle | existing draft direction; exact Telugu integration still unexecuted |

The table describes width ownership only. Rendering, font shaping, application-specific redraw strategy and shell behavior can add other differences.

## Exact Telugu discriminator

The reporter's short residual is:

```text
ఒక పద్యం వ్రాయి
```

The retained dependency-free probe derives:

```text
legacy scalar width: 11
draft cached width:   9
```

Critical cluster:

```text
ద్యం
legacy scalar width: 3
draft cached width:  1
```

Negative control:

```text
వ్రా
legacy scalar width: 2
draft cached width:  2
```

**Inferred.** A legacy application that emits `ద్యం` and then uses ordinary `CUB 2` from its scalar-width cursor intends to move from column 3 to column 1. The draft has already placed its cursor at column 1, so the same command reaches column 0. The owned target-native carrier includes this exact discriminator plus the aligned `వ్రా` control.

## Output-path pressure

**Documented.** The draft output serializer positions each `CharacterChunk`, increments its local `chunk_width` by each `TerminalCharacter.width()`, and appends the complete `TerminalCharacter.grapheme()` string to the host output.

**Inferred.** On an outer host using legacy scalar width, disagreement can accumulate within a chunk because the host receives all Unicode scalars while Zellij's chunk arithmetic uses the narrower cached width. A later absolute reposition can reset the cursor, but it cannot make the preceding chunk's per-cell advances identical.

A real host capture is still required before claiming the reporter's visible duplication is caused by this output path.

## Current-main relation

The external draft and current Zellij `main` have diverged from merge base `b558b31ed192652f75ecc35d6753a7d5d0046023`. At the refresh used by this scout, current main is `f42ca3c79c65c967ab1da39dc5c99838a45cce04`; the compare reports substantial independent histories.

The owned execution carrier therefore answers the behavior of exact draft `d5c04d...`, which is the branch named in the reporter's follow-up. It is not a current-main implementation candidate.

## Ranked discriminators

1. **Legacy inner / legacy host target-native grid control.** Exact draft, exact Telugu clusters, ordinary cursor movement. This is running on the owned carrier.
2. **Legacy inner / mode-2027 host serialization control.** Confirm that auto-enabling the host does not repair an inner app whose width arithmetic remains scalar.
3. **Mode-2027 inner / legacy host output control.** Feed a correctly 2027-aware inner sequence and parse the resulting Zellij output through a legacy host model or real Alacritty.
4. **Both 2027.** Use a supporting host and a 2027-aware test application as the positive integration control.
5. **Real shell capture.** Only after the lower-level matrix survives, reproduce the reporter phrase with one named shell/readline stack and retain PTY bytes, grid cursor, serialized output and copied text.

## Design pressure, not a patch proposal

A multiplexer cannot assume the inner application's width mode equals the outer terminal's width mode. Any repair direction must explain how Zellij translates between the two when they differ.

Possible families to compare later:

- keep separate inner-grid and outer-render width policies;
- render with explicit cursor normalization when the outer mode differs from stored cell semantics;
- preserve a legacy-compatible width per cell until the inner app enables 2027, while separately translating to the host mode;
- another approach that makes mixed-mode behavior explicit and testable.

No family is selected yet. The draft's memory/performance work also makes cell-representation growth a real cost, so a fix should avoid duplicating large per-cell state without measurement.

## Stop condition

Do not prepare production source until:

- the exact draft target-native Telugu control executes;
- at least one mixed-mode boundary is demonstrated with retained evidence;
- the draft is refreshed or rebased against current main;
- the repair owner can state both inner-application and outer-host semantics;
- overlap with the active external draft is refreshed;
- any public feedback remains manual human work.
