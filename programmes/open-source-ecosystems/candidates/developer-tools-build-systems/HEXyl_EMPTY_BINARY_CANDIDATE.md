## In simple words

Hexyl candidate #834 has a narrow empty-row repair to validate on exact source.

Exact current binary output at terminal width 80 uses one data panel and produces row widths `45,80,45`. The normal border renderer already follows `self.panels`; only the empty-input `No content` row hard-codes two data/character cells.

The candidate replaces that fixed formatter with the same panel-count arithmetic used by ordinary rows:

1. emit the left outer separator;
2. if enabled, emit the 8-column position cell and its outer separator;
3. emit exactly `self.panels` data cells, each `panel_sz()` columns, with the first containing `No content`;
4. emit exactly `self.panels` 8-column character cells when enabled;
5. use inner separators between sibling panels and outer separators at data/character boundaries.

No dependency or public option changes are required.

## Assignment

- Programme: #207
- Lane: #210
- Candidate owner: #834
- Parent experiment PR: #833
- Worker: `GPT-5.6 Sol`
- Target: `sharkdp/hexyl@6ecc29b9c8c84d08a7e860f7f69c22b113b480ea`
- Evidence entering candidate: `target-executed public CLI`
- Upstream contact authorized/performed: `false` / `false`

## Candidate gates

The executable candidate carrier must:

- reproduce baseline hexadecimal widths `80,80,80`;
- reproduce baseline binary widths `45,80,45`;
- apply the exact-source transform with hard source-snippet matching;
- make binary width-80 output `45,45,45`;
- keep hexadecimal width-80 output `80,80,80` and byte-identical to baseline;
- keep explicit `--panels=1`, `2`, and `3` empty rows internally width-consistent;
- keep `--no-characters` and `--no-position` empty rows internally width-consistent;
- pass `cargo fmt --check` and the Hexyl test suite.

If any non-binary control changes unexpectedly, stop and narrow the formatter before treating it as source-ready.

## Stop conditions

External Hexyl remains read-only. Refresh upstream head/overlap before any external proposal. No external issue, PR, comment, or review without explicit human authorization.