# Unit 19 — fix(mcp): omit client-IP metadata when encryption fails

## In simple words

Context7's MCP header helper returns the raw client IP when its configured encryption key is malformed or the cipher throws. Fieldwork produced and fully executed a narrow candidate that omits the optional `mcp-client-ip` header in those two failure paths, preserves unrelated headers, and emits fixed diagnostics without retaining the IP, key, or exception text.

Current public prior art changes the contribution decision. Upstream issue [#1965](https://github.com/upstash/context7/issues/1965) reported the same fail-open behavior, and upstream PR [#2104](https://github.com/upstash/context7/pull/2104) implemented the same `string | undefined` plus conditional-header contract. A maintainer closed both on 2026-04-03 with the statement that this was not the intended behavior. Current `master` still points to the exact revision Fieldwork executed and retains the plaintext fallback.

The technical candidate remains useful evidence. Re-submitting it would repeat a declined contribution without new maintainer direction, so this unit is retired from upstream preparation.

## Current disposition

`RETIRE`

Last verified: `2026-08-01`  
Worker: `GPT-5.6 Thinking`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

## Contribution

- Target project: `upstash/context7`
- Proposed upstream destination: `upstash/context7` `master`
- Archived proposed title: `fix(mcp): omit client-IP metadata when encryption fails`
- Contribution synopsis: omit optional client-IP metadata when encryption cannot complete, while preserving all unrelated request headers and fixed privacy-bounded diagnostics.
- Work class: `upstream-fork research / prior-art validation`

## Exact identities

- Public upstream base inspected: [`594a73133e14631af8c915a1b4f2c8039c964fe1`](https://github.com/upstash/context7/commit/594a73133e14631af8c915a1b4f2c8039c964fe1)
- Current upstream relationship: `master` was identical to `594a73133e14631af8c915a1b4f2c8039c964fe1` on `2026-08-01`
- Owned target fork: `teamleaderleo/context7` admission absent; no fork created because the unit is retired
- Intended source branch, if the decision is explicitly reopened: `fix/omit-client-ip-on-encryption-failure`
- Canonical owned source head: `none`
- Exact public prior-art source head: [`5a36c505e88da3fe74d34ae3f4dd01124031bb88`](https://github.com/upstash/context7/commit/5a36c505e88da3fe74d34ae3f4dd01124031bb88)
- Exact Fieldwork target-executed carrier head: [`3360d80d8aa90e3eaafea3367ff9dcfd4dfe0345`](https://github.com/teamleaderleo/fieldwork/commit/3360d80d8aa90e3eaafea3367ff9dcfd4dfe0345)
- Exact workflow-free retained carrier head: [`ec5fdb2cf3ce498fb88aa90991699d2c607b1246`](https://github.com/teamleaderleo/fieldwork/commit/ec5fdb2cf3ce498fb88aa90991699d2c607b1246)
- Fieldwork packet branch: [`p0/435-unit-19-context7-omit-client-ip`](https://github.com/teamleaderleo/fieldwork/tree/p0/435-unit-19-context7-omit-client-ip/upstream/packets/19-context7-omit-client-ip)
- Exact packet head: recorded in the packet pull request and final `#435` handoff because a commit cannot contain its own SHA
- Execution carriers: [PR #370](https://github.com/teamleaderleo/fieldwork/pull/370), current packaging [PR #397](https://github.com/teamleaderleo/fieldwork/pull/397)
- Baseline characterization: [PR #343](https://github.com/teamleaderleo/fieldwork/pull/343)

## Current code and tests

### Product code

- [`packages/mcp/src/lib/encryption.ts@594a731`](https://github.com/upstash/context7/blob/594a73133e14631af8c915a1b4f2c8039c964fe1/packages/mcp/src/lib/encryption.ts) — current helper, public default key, and plaintext failure fallback.
- [`packages/mcp/src/lib/encryption.ts@5a36c50`](https://github.com/upstash/context7/blob/5a36c505e88da3fe74d34ae3f4dd01124031bb88/packages/mcp/src/lib/encryption.ts) — declined prior implementation of the same fail-closed contract.
- [Retained tested patch](./patches/malformed-key-omit-metadata.patch) — Fieldwork candidate with privacy-bounded diagnostics.

### Target-native tests

- [Retained Vitest regression](./fixtures/malformed-key-omit-metadata.test.ts) — valid-key compatibility, malformed-key omission, runtime-cipher-failure omission, unrelated-header preservation, and diagnostic privacy.

### Required generated or dependency files

- `not applicable`

## Changed-file fence if revived

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `packages/mcp/src/lib/encryption.ts` | production fallback behavior | yes |
| `packages/mcp/test/encryption.test.ts` | target-native regression coverage | yes |

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| malformed configured key emits raw IP on the baseline | target-executed | PR #343, run `30629165557`, job `91151287009` | local compiled helper; no hosted request |
| candidate omits metadata on malformed key and runtime cipher failure | target-executed | run [`30635777158`](https://github.com/teamleaderleo/fieldwork/actions/runs/30635777158), job [`91172880796`](https://github.com/teamleaderleo/fieldwork/actions/runs/30635777158/job/91172880796) | exact target and patch only |
| focused regressions pass | target-executed | `3/3`, artifact [`8795244374`](https://github.com/teamleaderleo/fieldwork/actions/runs/30635777158/artifacts/8795244374) | three named cases |
| complete MCP suite and ordinary gates pass | full-gate | `49/49`, format, lint, typecheck, build | Node 22, Ubuntu 24.04 |
| equivalent fail-closed contribution was declined upstream | public prior art | issue #1965 and PR #2104 | maintainer rationale is concise but explicit |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)
- [Exact execution receipt](./receipts/context7-omit-client-ip-on-encryption-failure.json)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Exact duplicate issue: [`upstash/context7#1965`](https://github.com/upstash/context7/issues/1965), closed `not planned` on `2026-04-03`
- Exact duplicate PR: [`upstash/context7#2104`](https://github.com/upstash/context7/pull/2104), closed unmerged on `2026-04-03`
- Adjacent public-default-key issue: [`upstash/context7#1366`](https://github.com/upstash/context7/issues/1366), closed after maintainers removed the warning and said the default was not a problem
- Broader hashing alternative: [`upstash/context7#2056`](https://github.com/upstash/context7/pull/2056), closed by its author for private-mirror maintenance
- Equivalent implementation found: `yes`
- Relationship to prior work: `independent validation of a declined upstream contract`

## Remaining work

Complete only after an explicit reopening trigger:

1. obtain user authority to revisit a maintainer-declined behavior;
2. identify new public maintainer direction or a materially different compatibility contract;
3. create `teamleaderleo/context7`, materialize a clean source branch, and rerun the exact target gates only after steps 1 and 2.

## Blockers and limits

- Upstream already declined the same omission-on-failure behavior.
- No owned Context7 fork exists.
- The candidate proves local package behavior and ordinary gates; it makes no hosted-service, production-prevalence, provider-treatment, or confidentiality claim.
- Missing/empty key behavior, the fixed public default key, and AES-CBC authenticity are adjacent concerns outside this retired unit.
- Public upstream interaction remains unauthorized.

## Latest handoff

State: `RETIRE`  
Exact source head: `none`; exact declined prior-art head `5a36c505e88da3fe74d34ae3f4dd01124031bb88`  
Exact executed candidate carrier: `3360d80d8aa90e3eaafea3367ff9dcfd4dfe0345`  
Exact packet head: see packet PR and final `#435` handoff  
Tests: focused `3/3`; complete MCP `49/49`; format, lint, typecheck, build, patch identity, mirror identity, and diff hygiene passed  
Temporary machinery remaining: `none in the retained workflow-free carrier`  
Next worker action: `stop unless the user supplies a new reopening trigger`  
Public upstream interaction: `none`
