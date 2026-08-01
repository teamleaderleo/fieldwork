# Continuation handoff

## Disposition

`REPAIR`

The minimal candidate is technically promising and has passing focused and ordinary workflows. The hardening child needs diagnosis before its validation set can graduate into a clean source candidate.

## Exact revisions

- Packet base: `920f87cb25dd0cc7901d59ea2019cd4b4a193b94`
- Packet branch: `p0/435-unit-14-duckdb-arrow-union-type-ids`
- Characterization head: `ed05ac593498fb4f95546ec591824ee23429088d`
- Candidate base: `2c9e51aa33dd07e928edae66304430aeb038edd7`
- Candidate head: `c962ece64c1356015aef15a37c0cc636f63b376b`
- Hardening head: `fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2`
- Intended clean source branch: `fix/arrow-sparse-union-type-id-map` — absent

## Current blocker

Hardening targeted run `30659465467`, job `91251921754`, reaches a successful debug build and then fails the positive mapping test group. The connected log response exposes the failing step and duration but omits the assertion body. The retained artifact confirms both generators ran and preserves the exact hardened patch.

## Continuation sequence

1. Open or download the full log for job `91251921754` through an environment that exposes the assertion body, or rerun the focused test locally from hardening head `fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2`.
2. Compare the failure against the passing minimal candidate at `c962ece64c1356015aef15a37c0cc636f63b376b`.
3. Repair the hardening generator/test pair while preserving the proven logical-ID mapping behavior.
4. Create `teamleaderleo/duckdb:fix/arrow-sparse-union-type-id-map` from `2c9e51aa33dd07e928edae66304430aeb038edd7`.
5. Materialize only product source and focused tests. Exclude Fieldwork workflows/scripts and the five formatting-only paths listed in `analysis.md`.
6. Run the focused sparse-ID, offset, duplicate-ID, unknown-ID, and malformed-buffer tests plus relevant repository checks.
7. Record commands, outputs, workflow links, and the exact new source head in `tests.md`, `README.md`, and issue #435.
8. Keep public upstream read-only until explicit authorization arrives.

## Durable locations

- Packet: `upstream/packets/14-duckdb-arrow-union-type-ids/`
- Candidate PR: https://github.com/teamleaderleo/duckdb/pull/14
- Hardening PR: https://github.com/teamleaderleo/duckdb/pull/16
- Coordination: https://github.com/teamleaderleo/fieldwork/issues/435

No material observation from this pass is intentionally left only in chat.