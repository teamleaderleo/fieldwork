## In simple words

The exact Zellij grapheme draft preserves the reporter's Telugu text while assigning materially fewer columns than the same `unicode-width 0.2.2` scalars consume under legacy per-codepoint terminal semantics.

This is now target-executed on Zellij's own grid test harness. Six focused controls passed on exact draft source `d5c04daccfac765814e55ef2b89543bbe711629d`. The critical cluster `ద్యం` is stored at one Zellij column while scalar `unicode-width` totals three. The nearby `వ్రా` control is two columns under both policies. An ordinary `CUB 2` control then demonstrates the direct cursor consequence: a scalar-width caller intends column 1 while the draft grid reaches column 0.

This establishes the grid/interface mechanism. It does not yet establish that the reporter's visible duplicated word is caused by this mechanism; that requires a real shell/PTY/outer-terminal capture.

## Assignment

- Programme: #207 (`open-source-ecosystems`)
- Lane: #210 (`developer-tools-build-systems`)
- Parent scout: #561
- Fieldwork scout PR: #790
- Worker: `GPT-5.6 Sol`
- Target: `zellij-org/zellij`
- External draft source: `d5c04daccfac765814e55ef2b89543bbe711629d`
- Owned execution carrier: `teamleaderleo/zellij#1`
- Carrier head: `8b50ae87f2f58f9294572a78ce2b639254873eba`
- Workflow run: `31423503911`
- Job: `93569631164`
- Environment: GitHub-hosted Ubuntu 24.04; Rust toolchain declared by target `1.92.0`
- Claim scope: interface mechanism
- Evidence class: `target-executed`
- Upstream contact authorized: `false`
- Upstream contact performed: `false`

## Exact execution

The owned carrier is based directly on the external draft SHA and contains only an execution workflow plus Fieldwork test material. The workflow appends the focused controls to Zellij's existing `zellij-server/src/panes/unit/grid_tests.rs` at run time and executes:

```sh
cargo test --locked -p zellij-server fieldwork_telugu --lib -- --nocapture
```

Run `31423503911`, job `93569631164` completed successfully.

Exact target result:

```text
running 6 tests
fieldwork_telugu_critical_cluster_preserves_text_but_diverges_from_scalar_columns ... ok
fieldwork_telugu_control_cluster_has_no_width_drift ... ok
fieldwork_telugu_control_cursor_move_stays_aligned_without_2027 ... ok
fieldwork_telugu_full_reporter_line_has_twenty_four_internal_columns_and_thirty_two_scalar_columns ... ok
fieldwork_telugu_scalar_cursor_move_targets_a_different_column_without_2027 ... ok
fieldwork_telugu_reporter_residual_has_nine_internal_columns_and_eleven_scalar_columns ... ok

test result: ok. 6 passed; 0 failed; 0 ignored; 0 measured; 1318 filtered out
```

The run's exact source fence recorded:

```text
event_base=d5c04daccfac765814e55ef2b89543bbe711629d
event_head=8b50ae87f2f58f9294572a78ce2b639254873eba
```

The checkout itself was GitHub's synthetic PR merge commit. The workflow treats the event base and event head as the source identities rather than mislabeling the synthetic merge as product source.

## Retained harness correction

Run `31423353566`, job `93569134097` failed before test injection or product execution.

The first workflow generation tried to resolve the base branch name inside a depth-1 pull-request checkout. GitHub had checked out a synthetic merge commit without a local `research/upstream-4800-snapshot` branch ref, so `git merge-base` failed with `Not a valid object name`.

Classification: `harness failure`.

The repair uses `github.event.pull_request.base.sha` and `github.event.pull_request.head.sha`, requiring the event base to equal the external draft SHA. No product assertion from the failed generation is retained.

## Six controls

### 1. Critical Telugu cluster

Input:

```text
ద్యం
```

Assertions:

```text
draft retained text: ద్యం
draft internal cursor: 1
UnicodeWidthChar scalar total: 3
```

Result: `PASS`.

### 2. Nearby negative control

Input:

```text
వ్రా
```

Assertions:

```text
draft internal cursor: 2
UnicodeWidthChar scalar total: 2
```

Result: `PASS`.

This prevents the conclusion from becoming a blanket claim that Telugu conjuncts always disagree.

### 3. Exact visible residual

Input:

```text
ఒక పద్యం వ్రాయి
```

Assertions:

```text
draft retained text: exact input
draft internal cursor: 9
UnicodeWidthChar scalar total: 11
```

Result: `PASS`.

### 4. Full reporter line

Input:

```text
వసంత ఋతువు గురించి ఒక కంద పద్యం వ్రాయి
```

Assertions:

```text
draft retained text: exact input
draft internal cursor: 24
UnicodeWidthChar scalar total: 32
```

Result: `PASS`.

### 5. Ordinary cursor-move discriminator

After placing `ద్యం`, the grid cursor is column 1 while a scalar-width caller's arithmetic is column 3. The test then sends ordinary `CSI 2 D` (`CUB 2`).

Observed:

```text
scalar-width caller intended: 3 - 2 = 1
draft grid actual:          1 - 2 saturates to 0
```

Result: `PASS`.

The exact draft source comments that CUB counts display columns in all modes, including 2027. The disagreement therefore comes from prior text-width ownership rather than a different CUB encoding.

### 6. Cursor-move negative control

After placing `వ్రా`, both policies are at column 2. `CUB 1` moves both to column 1.

Result: `PASS`.

## What the run establishes

**Observed:**

- draft `d5c04d...` preserves all tested Telugu scalars in its grid;
- its internal cursor is 9 for the reporter's short phrase and 24 for the full line;
- actual `UnicodeWidthChar` from the target dependency gives 11 and 32 respectively;
- `ద్యం` is a 1-versus-3 discriminator;
- `వ్రా` is a 2-versus-2 control;
- an ordinary cursor-back command produces a different destination when the caller's prior width arithmetic is scalar-based.

**Documented:**

- the draft always performs grapheme segmentation while `grapheme_cluster_mode` separately controls mode-2027 cursor/edit semantics;
- the draft output serializer emits the full grapheme text while using the cached cell width for chunk arithmetic;
- the draft client probes the outer host for mode 2027 and only enables it when the host reports support;
- JLine's first-party mode-2027 documentation describes the legacy boundary as per-codepoint `wcwidth()` cursor positioning and mode 2027 as grapheme-cluster positioning.

**Inferred:**

- mixed legacy/2027 semantics can make an inner application's cursor arithmetic, Zellij's grid, and the outer terminal disagree;
- current Alacritty is a strong representative legacy-host path because its inspected input loop advances per scalar and current code search found no mode-2027 implementation;
- the reporter's duplicate may arise when an interactive application redraws from a scalar-derived cursor while Zellij has already compressed the preceding Telugu text into fewer internal columns.

**Unknown:**

- the reporter's exact shell/readline/editor stack during paste;
- the exact redraw bytes that produced the duplicated word;
- whether a real Alacritty + draft Zellij capture reproduces the visible duplicate under controlled conditions;
- whether a current-main rebase of the draft would keep the same width helper and grid behavior.

## Existing broad validation did not catch this

The external draft's own exact-head GitHub workflows are green:

- Rust workflow `26150745487`: success;
- End to End tests `26150745492`: success.

The focused Telugu controls therefore expose an uncovered compatibility boundary on an otherwise broadly green draft.

## Mode compatibility context

See:

`programmes/open-source-ecosystems/scouts/developer-tools-build-systems/ZELLIJ_GRAPHEME_MODE_MATRIX.md`

The key point is that a multiplexer has two independent width relationships:

```text
inner application <-> Zellij grid <-> outer terminal
```

The inner application can opt into mode 2027 independently of whether the outer terminal supports mode 2027. A complete design has to define mixed-mode translation instead of assuming those two relationships share one width policy.

## Current source relation

The active external draft remains open at `d5c04daccfac765814e55ef2b89543bbe711629d`.

Current Zellij `main` inspected by the scout is `f42ca3c79c65c967ab1da39dc5c99838a45cce04`. The draft and current main have diverged from merge base `b558b31ed192652f75ecc35d6753a7d5d0046023` with substantial independent histories.

This receipt therefore reviews the exact draft the reporter tested. It does not authorize a current-main implementation claim.

## Disposition

`TARGET-EXECUTED MIXED-WIDTH MECHANISM / ACTIVE EXTERNAL DRAFT OWNER`.

Next bounded work:

1. capture one real legacy inner-application redraw sequence through the exact draft;
2. preserve PTY bytes, draft grid cursor/text, serialized Zellij output and host cursor state;
3. run a positive mode-2027 inner/outer control if a supporting host is available;
4. refresh or rebase the draft against current main before considering source design;
5. prepare concise feedback for the active draft only if a human authorizes upstream contact.

No third-party upstream mutation or contact occurred.