# Tests and exact receipts

## Characterization — `teamleaderleo/duckdb#12`

Head: `ed05ac593498fb4f95546ec591824ee23429088d`

| Run | Result | Meaning |
| --- | --- | --- |
| Characterization `30631902979` | success | Sparse IDs `{3,7}` and sliced parents failed on unpatched source as expected. |
| Main `30631892182` | success | Ordinary repository workflow passed for the carrier head. |

## Minimal candidate — `teamleaderleo/duckdb#14`

Base: `2c9e51aa33dd07e928edae66304430aeb038edd7`

Head: `c962ece64c1356015aef15a37c0cc636f63b376b`

| Run | Result | Meaning |
| --- | --- | --- |
| Fieldwork Ubuntu `30636432713` | success | Generated mapping patch built and passed the focused sparse-ID and offset tests. |
| Main `30636350358` | success | Ordinary repository workflow passed. |
| Characterization `30636350353` | failure | Expected-failure carrier became stale because the candidate fixed its case. |

Candidate comparison from base to head: eight commits; changed paths are carrier workflow files, `test/arrow/CMakeLists.txt`, `test/arrow/arrow_union_type_ids.cpp`, and `tools/fieldwork/apply_arrow_union_type_id_mapping.py`. Product source is generated during CI rather than committed on the carrier branch.

## Hardening child — `teamleaderleo/duckdb#16`

Head: `fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2`

| Run | Result | Meaning |
| --- | --- | --- |
| Main `30659420924` | success | Ordinary repository workflow passed. |
| Targeted `30659465467` | failure | Checkout, patch generation, carrier checks, and debug build passed; focused positive mapping test group failed after about 13.11 seconds. |
| Fieldwork Ubuntu `30659420946` | failure | Specialized workflow red at this head. |
| Characterization `30659420937` | failure | Expected-failure carrier remains stale after applying a fix. |

Targeted job: `91251921754`.

Artifact: `arrow-union-type-id-patch`, ID `8805129666`.

Artifact receipts:

```text
Arrow sparse union type-id mapping candidate applied
Arrow sparse union type-id hardening applied
```

Artifact files:

```text
arrow-union-type-id-hardened.patch
candidate-generation.txt
carrier-files.txt
source-files.txt
```

The available job-log API response did not include the failed assertion text. The packet therefore records the failing step and timing without guessing the expression or row.

## Test cases represented by the carriers

- sparse logical type codes `{3, 7}` map to child indexes `{0, 1}`;
- parent offsets `1` and `2` preserve correct tag and child reads;
- duplicate logical IDs are rejected;
- unknown and out-of-range logical IDs are rejected;
- malformed `int16` type-ID storage is rejected by the hardening child.

## Tests executed during packet work

Packet work reviewed existing CI receipts, exact workflow/job metadata, generated artifact contents, branch comparisons, source/test diffs, and public prior-art records. No new target test was run because no clean source branch could be materialized from a verified passing product-source commit in the connected workspace.