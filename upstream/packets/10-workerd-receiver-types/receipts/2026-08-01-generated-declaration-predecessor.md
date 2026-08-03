# Unit 10 predecessor generated-declaration receipt

## Classification

`TARGET EXECUTED — HISTORICAL PREDECESSOR EVIDENCE`

This receipt records execution carrier Fieldwork PR #475. It does not replace the current workerd source PR #5, inherited-global repair carriers #9/#10, or the required source-plus-generated-snapshot review.

## Exact identities

- Fieldwork carrier: `teamleaderleo/fieldwork#475`;
- carrier branch: `execution/435-unit-10-generated-diff`;
- carrier head: `0663df89be0c18faf87f3b0cbf52543121587e44`;
- exact workerd base: `d82c2a45a8695aac30d4d24828ce1ee7fb11909b`;
- exact workerd candidate: `d9c685f095f7984f959769e901099309552bc9c9`;
- workflow run: `30692780279`;
- job: `91350395334`;
- Fieldwork integrity: `30692780295`, success.

## Executed gates

The one-file Fieldwork carrier:

1. checked out the exact candidate with full history;
2. built baseline declarations at the exact base;
3. built candidate declarations;
4. ran `//types:test/types/fetch-receiver`;
5. rejected leakage of `__JSG_GENERATED_RECEIVER__` into public declarations;
6. retained the complete baseline/candidate file inventories and generated declaration diff.

Every named job step completed successfully.

## Artifact

- artifact ID: `8817238802`;
- name: `unit-10-generated-declarations-d9c685f095f7984f959769e901099309552bc9c9`;
- ZIP digest: `sha256:4f3c5ef8043797e4b16cda9ebe7ae4ba4e8812368e6f7eda91e60bfdfde3398f`;
- retention expiry: `2026-10-30`.

Artifact summary:

```text
base_sha=d82c2a45a8695aac30d4d24828ce1ee7fb11909b
candidate_sha=d9c685f095f7984f959769e901099309552bc9c9
changed_files=4
added_lines=2478
removed_lines=1044
added_receiver_lines=1488
removed_receiver_lines=0
```

## Evidence boundary

This establishes that the predecessor receiver-aware candidate built generated declarations, passed its focused receiver fixture, and produced a complete review artifact without internal-marker leakage.

It does not establish the current implementation head `18a117c28773cd7aa0ee599e03439c5fbbf06584`, inherited Worker-global ancestry semantics, final global receiver type, current generated snapshots, or current complete-types/lint gates.

Those remain owned by the current packet source and workerd carriers #9/#10.

## Carrier retirement

Fieldwork PR #475 contains one workflow file only. Its unique result is transferred here, so the PR may close without merge. The branch and immutable workflow/artifact history remain available as provenance.

No public upstream interaction occurred or is authorized.
