# Unit 14 — DuckDB sparse Arrow union type IDs

## Current disposition

`REPAIR`

The focused candidate in [`teamleaderleo/duckdb#14`](https://github.com/teamleaderleo/duckdb/pull/14) has passing candidate and main workflows at exact head `c962ece64c1356015aef15a37c0cc636f63b376b`. The hardening child in [`teamleaderleo/duckdb#16`](https://github.com/teamleaderleo/duckdb/pull/16) adds stronger malformed-input checks, but its targeted workflow fails at exact head `fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2`. GitHub retained the generated patch and receipts, while the available job-log endpoint omitted the failed assertion body.

A clean target-source branch named `fix/arrow-sparse-union-type-id-map` does not yet exist. Creating an empty branch or copying the carrier commits would produce a misleading source record, so materialization is deferred until the passing candidate patch is applied as source commits and the hardening failure is diagnosed.

## Assignment

- Unit: `14`
- Target: DuckDB
- Proposed contribution: `fix(arrow): map sparse union type IDs to child indices`
- Owner record: [`teamleaderleo/linux-fieldwork#262`](https://github.com/teamleaderleo/linux-fieldwork/issues/262)
- Coordination issue: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)
- Packet branch: `p0/435-unit-14-duckdb-arrow-union-type-ids`
- Packet base: `920f87cb25dd0cc7901d59ea2019cd4b4a193b94`
- Assigned packet path: `upstream/packets/14-duckdb-arrow-union-type-ids/`
- Public upstream contact: none; unauthorized

## Source ladder

1. Characterization: [`teamleaderleo/duckdb#12`](https://github.com/teamleaderleo/duckdb/pull/12), head `ed05ac593498fb4f95546ec591824ee23429088d`.
2. Minimal candidate: [`teamleaderleo/duckdb#14`](https://github.com/teamleaderleo/duckdb/pull/14), head `c962ece64c1356015aef15a37c0cc636f63b376b`, base `2c9e51aa33dd07e928edae66304430aeb038edd7`.
3. Hardening child: [`teamleaderleo/duckdb#16`](https://github.com/teamleaderleo/duckdb/pull/16), head `fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2`.
4. Intended clean branch: `teamleaderleo/duckdb:fix/arrow-sparse-union-type-id-map` — absent at packet completion.

## Packet contents

- `analysis.md` — defect mechanism, candidate review, CI interpretation, and prior art.
- `approaches.md` — attempted approaches and branch decision.
- `tests.md` — exact workflow runs, commands, revisions, and outcomes.
- `references.md` — durable source, test, workflow, issue, and prior-art links.
- `issue-draft.md` — private draft for possible maintainer-direction-first contact.
- `pr-draft.md` — private source PR draft.
- `handoff.md` — continuation steps and current blockers.

## Instruction audit

Read from `p0/435-upstream-packet-workflow` at `920f87cb25dd0cc7901d59ea2019cd4b4a193b94`:

- `START_HERE.md`
- `AGENTS.md`
- `CHARTER.md`
- `CODE_FIRST.md`
- `PLAIN_LANGUAGE.md`
- `METHOD.md`
- `REFERENCE_POLICY.md`
- `COORDINATION.md`
- `REVIEWING.md`
- `PROGRAMMES.md`
- `TARGET_HUBS.md`
- `upstream/README.md`
- `upstream/INDEX.md`

`START_HERE.md` also names `notes/PROGRAMME_GUIDE.md` and `AGENT_FIELD_GUIDE.md`; neither path exists on that exact branch/revision. This repository-state gap is preserved here rather than silently substituted.
