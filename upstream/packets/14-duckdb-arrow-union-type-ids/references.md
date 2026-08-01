# References

## Internal coordination and ownership

- Fieldwork coordinator: https://github.com/teamleaderleo/fieldwork/issues/435
- Linux Fieldwork owner record: https://github.com/teamleaderleo/linux-fieldwork/issues/262
- Packet workflow branch at initial revision: https://github.com/teamleaderleo/fieldwork/tree/920f87cb25dd0cc7901d59ea2019cd4b4a193b94
- Packet branch: https://github.com/teamleaderleo/fieldwork/tree/p0/435-unit-14-duckdb-arrow-union-type-ids/upstream/packets/14-duckdb-arrow-union-type-ids

## Owned target records

- Characterization PR #12: https://github.com/teamleaderleo/duckdb/pull/12
- Characterization head: https://github.com/teamleaderleo/duckdb/commit/ed05ac593498fb4f95546ec591824ee23429088d
- Minimal candidate PR #14: https://github.com/teamleaderleo/duckdb/pull/14
- Candidate head: https://github.com/teamleaderleo/duckdb/commit/c962ece64c1356015aef15a37c0cc636f63b376b
- Candidate base: https://github.com/teamleaderleo/duckdb/commit/2c9e51aa33dd07e928edae66304430aeb038edd7
- Hardening PR #16: https://github.com/teamleaderleo/duckdb/pull/16
- Hardening head: https://github.com/teamleaderleo/duckdb/commit/fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2

## Tests and workflows

- Characterization run `30631902979`: https://github.com/teamleaderleo/duckdb/actions/runs/30631902979
- Characterization Main `30631892182`: https://github.com/teamleaderleo/duckdb/actions/runs/30631892182
- Candidate targeted run `30636432713`: https://github.com/teamleaderleo/duckdb/actions/runs/30636432713
- Candidate Main `30636350358`: https://github.com/teamleaderleo/duckdb/actions/runs/30636350358
- Candidate stale characterization `30636350353`: https://github.com/teamleaderleo/duckdb/actions/runs/30636350353
- Hardening Main `30659420924`: https://github.com/teamleaderleo/duckdb/actions/runs/30659420924
- Hardening targeted run `30659465467`: https://github.com/teamleaderleo/duckdb/actions/runs/30659465467
- Hardening targeted job `91251921754`: https://github.com/teamleaderleo/duckdb/actions/runs/30659465467/job/91251921754
- Hardening Fieldwork Ubuntu `30659420946`: https://github.com/teamleaderleo/duckdb/actions/runs/30659420946
- Hardening stale characterization `30659420937`: https://github.com/teamleaderleo/duckdb/actions/runs/30659420937

## Public prior art — read only

- Defect issue #21842: https://redirect.github.com/duckdb/duckdb/issues/21842
- Prior PR #21843: https://redirect.github.com/duckdb/duckdb/pull/21843
- Prior PR #21898: https://redirect.github.com/duckdb/duckdb/pull/21898

No public interaction occurred.

## Code and test paths

Candidate carrier:

- https://github.com/teamleaderleo/duckdb/blob/c962ece64c1356015aef15a37c0cc636f63b376b/tools/fieldwork/apply_arrow_union_type_id_mapping.py
- https://github.com/teamleaderleo/duckdb/blob/c962ece64c1356015aef15a37c0cc636f63b376b/test/arrow/arrow_union_type_ids.cpp
- https://github.com/teamleaderleo/duckdb/blob/c962ece64c1356015aef15a37c0cc636f63b376b/.github/workflows/fieldwork-arrow-union-type-id-candidate.yml

Hardening carrier:

- https://github.com/teamleaderleo/duckdb/blob/fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2/tools/fieldwork/apply_arrow_union_type_id_hardening.py
- https://github.com/teamleaderleo/duckdb/blob/fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2/tools/fieldwork/apply_arrow_union_type_id_mapping.py
- https://github.com/teamleaderleo/duckdb/blob/fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2/test/arrow/arrow_union_type_ids.cpp
- https://github.com/teamleaderleo/duckdb/blob/fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2/.github/workflows/fieldwork-arrow-union-type-id-candidate.yml
