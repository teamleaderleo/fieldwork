# Neovim LSP final-newline incremental-sync desynchronization

Date: 2026-09-01  
Programme: high-leverage-open-source  
Worker: ChatGPT  
Claim scope: interface  
Upstream contact authorized: `false`

## In simple words

Neovim's LSP client can tell a language server a different document than the one the user is actually editing when an edit changes the final-newline state at end of file.

The core problem survives on current `master`: full-document sync knows whether the buffer ends in an EOL, while incremental change tracking snapshots only the array of buffer lines. Two documents with identical lines but different final-newline state therefore become indistinguishable to the incremental tracker. Once that state diverges, later formatter responses and edits are interpreted against different documents on the editor and server sides.

## Question

Can Neovim's incremental LSP tracker preserve the final-newline bit so that every sequence of incremental `didChange` events reconstructs the same bytes as `vim.lsp._buf_get_full_text()`?

## Assignment boundary

Expected deliverable: current-head source/test map, overlap check, a deterministic protocol-state discriminator, candidate design, and recommendation.  
Owned output path: `programmes/high-leverage-open-source/scouts/neovim-lsp-final-newline-desync/report.md`  
Dependencies: public Neovim source/issues/PRs. No owned Neovim fork currently exists.  
Target revision: `neovim/neovim` `9a29622b545fc76c8b44d0e2b90f318a599eef39`.  
Stop condition: prove or falsify that current incremental state cannot represent final-EOL changes, identify the smallest regression seam, and check active PR overlap; upstream remains read-only.

## Upstream evidence

Issue: https://redirect.github.com/neovim/neovim/issues/36653

The issue reports that editing the last line without selecting its terminating newline sends incorrect incremental LSP changes and corrupts the language server's internal document. The visible reproducer uses `ts_query_ls`: after the desynchronizing edit, repeated formatting alternately adds and removes an empty final line; reloading the buffer resets the server-side document and stops the behavior.

The reporter later logged the actual `textDocument/didChange` payloads. In the desynchronizing path, the replacement text sent for the reconstructed document omitted its trailing newline. In the control path that included the trailing newline in the edit, the change payload preserved it.

A maintainer asked for a current-head retest; the reporter confirmed the issue on a later 0.12 development build. No pull request claiming issue 36653 was found in the current overlap search.

## Current-head source state

Pinned `master`: `9a29622b545fc76c8b44d0e2b90f318a599eef39`.

Production owners:

- `runtime/lua/vim/lsp/_changetracking.lua`
- `runtime/lua/vim/lsp/sync.lua`
- `runtime/lua/vim/lsp.lua`

### Full-sync representation

`vim.lsp._buf_get_full_text(bufnr)` joins all `nvim_buf_get_lines(...)` results using the buffer's line ending and then explicitly appends one final line ending when `vim.bo[bufnr].eol` is true.

So the full LSP document distinguishes these two states:

```text
{"alpha"}, eol=false  => "alpha"
{"alpha"}, eol=true   => "alpha\n"
```

### Incremental representation

`_changetracking.lua` stores each incremental buffer snapshot as:

```lua
---@field lines string[] snapshot of buffer lines from last didChange
```

Initialization and every update obtain those lines through `nvim_buf_get_lines(...)`. The tracker stores no `eol`/terminal-newline state alongside `lines`.

It then calls `sync.compute_diff(prev_lines, curr_lines, ...)`. `sync.compute_diff` receives the line arrays and line-ending encoding, but no previous/current final-EOL flags.

Therefore the two full documents above collapse onto the same incremental snapshot `{ "alpha" }`. A diff function receiving identical observable state cannot emit the missing `\n` insertion/removal reliably.

## Deterministic discriminator

The strongest regression does not require a real language server.

Attach the existing incremental-sync test harness to a one-line buffer, capture the authoritative bytes from `vim.lsp._buf_get_full_text()`, perform an edit sequence that toggles or crosses the final-newline state while leaving the visible final line content equivalent, and apply every generated `TextDocumentContentChangeEvent` to an in-test server-side string.

After every event, assert:

```text
reconstructed_server_document == vim.lsp._buf_get_full_text(bufnr)
```

The reported visual-paste reproducer is one input sequence. A smaller direct control should exercise both directions:

1. final EOL present -> absent;
2. final EOL absent -> present;
3. same edit away from EOF as a negative control.

This turns the bug from a formatter-specific symptom into a protocol invariant.

Existing regression owner: `test/functional/plugin/lsp/incremental_sync_spec.lua`. Its harness already attaches `sync.compute_diff` directly to `on_lines` and records generated content changes.

## Proofability / consequence

**Proofability: 5/5.** Current source has a representational mismatch: full sync stores the final-EOL bit in the serialized text, while incremental state discards it. The existing test harness can compare an incrementally reconstructed server string against authoritative full text after each edit.

**Consequence: 4/5 at interface scope.** The documented result is a language server holding a different document from Neovim, with formatting already observed to oscillate because server and editor disagree at EOF. Any stronger claim about arbitrary language servers applying destructive edits to unrelated ranges is plausible but remains **Unknown** until independently demonstrated.

**Cross score: excellent.** A protocol-state corruption bug with a compact, server-independent invariant.

## Candidate design

The change tracker needs to make final-EOL state part of its snapshot identity. A narrow design would retain both:

- `lines: string[]`
- the prior/current terminal-newline state (`vim.bo[bufnr].eol` or an equivalent serialized-text boundary)

Then the incremental diff path must account for transitions of that bit at EOF. Another viable design is to canonicalize the tracked representation so the final EOL is encoded into the line model itself, provided every existing range computation continues to obey LSP position rules.

The regression should be written before choosing the implementation because EOF positions are protocol-sensitive: LSP positions cannot name a location after a line terminator on the same line, so inserting/removing the final newline may require a range/text form different from ordinary same-line edits.

## Overlap

Current PR search for issue 36653 / final-newline incremental LSP tracking found no direct candidate. The current `master` source still has the line-array-only buffer state described above.

## Evidence labels

- Formatter oscillation and malformed incremental payloads: **Documented** in the upstream issue and follow-up logs.
- Full-text serializer includes terminal EOL: **Observed** on pinned current source.
- Incremental buffer snapshot stores only lines and cannot distinguish equal lines with different EOL state: **Observed** on pinned current source.
- Existing server-independent test seam: **Observed** in `incremental_sync_spec.lua`.
- Current direct PR overlap: **Observed** by PR search.
- Broad downstream edit corruption beyond the documented formatter behavior: **Unknown**.
- Owned-fork red/green execution: **Unavailable** until an owned Neovim fork is created.

## Recommendation

Retain as a high-priority contribution candidate. It clears the proofability bar cleanly and has meaningful protocol consequence. Create an owned Neovim fork if we decide to implement, add a red invariant test that reconstructs the server document after every incremental event, then make final-EOL state explicit in change tracking. Keep upstream read-only until a fresh bounded greenlight.