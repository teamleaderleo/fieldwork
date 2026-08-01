# Tests and receipts — unit 19, Context7 client-IP encryption fallback

## In simple words

The baseline plaintext fallback and the fail-closed candidate were both exercised on exact Context7 source. The candidate passed three focused regressions, all 49 MCP package tests, formatting, lint, typecheck, build, patch identity, test identity, and receipt validation. Current upstream `master` is still the exact target revision used for those runs.

The largest contribution gap is product intent, not execution. Upstream already declined the same omission-on-failure behavior in issue #1965 and PR #2104.

## Identity

- Exact upstream base: `594a73133e14631af8c915a1b4f2c8039c964fe1`
- Exact current upstream relationship: `master` identical to that SHA on `2026-08-01`
- Exact candidate patch SHA-256: `bcdbef2c71e89d456267d3bc82a3eed2f62f03133b2dab326196d29fb24309d5`
- Exact target-executed carrier head: `3360d80d8aa90e3eaafea3367ff9dcfd4dfe0345`
- Exact workflow-free retained carrier head: `ec5fdb2cf3ce498fb88aa90991699d2c607b1246`
- Test date: `2026-07-31`
- Environment: GitHub Actions Ubuntu 24.04, Node `22.23.1`, pnpm `10.34.5`, Vitest `4.1.9`, Prettier `3.6.2`

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| malformed configured key emits raw selected IP on baseline | target-executed local helper | PR #343, run `30629165557`, job `91151287009` | pass, marker `3/3` | compiled helper; no hosted request |
| invalid key omits optional metadata on candidate | target-executed | `test/encryption.test.ts` | pass | one runtime-composed invalid key |
| runtime crypto failure omits optional metadata | target-executed | mocked `crypto.randomBytes` failure | pass | injected local failure |
| valid explicit key retains encrypted metadata | target-executed | focused positive control | pass | ciphertext form and non-plaintext equality, not confidentiality |
| unrelated headers remain | target-executed | source, server version, session, auth, IDE, client version, transport assertions | pass | named headers only |
| diagnostics exclude IP, key, and caught error text | target-executed | console-error spies | pass | two named failure paths |
| complete MCP package behavior remains green | full-gate | `pnpm --filter @upstash/context7-mcp test` | `49/49` pass | package suite only |
| upstream declined the same contract | public prior art | issue #1965, PR #2104 | confirmed | rationale limited to public comments |

## Baseline characterization

### Command or workflow

```text
Fieldwork PR #343
run 30629165557
job 91151287009
exact target upstash/context7@594a73133e14631af8c915a1b4f2c8039c964fe1
```

### Assertions

- selected forwarded identity is `198.51.100.77`;
- repository-default key yields ciphertext-shaped metadata;
- malformed configured key logs an invalid-key diagnostic;
- malformed configured key returns `198.51.100.77` unchanged as `mcp-client-ip`;
- reject-or-omit behavior is absent.

### Result

- status: `success`
- test count: `3/3` exact marker
- workflow and job: `30629165557` / `91151287009`
- artifact: `8792754564`, digest `sha256:6daa628f897636c8aca033e1de269d589217e40df6462038438e10e32eb4b677`
- observed behavior: plaintext fallback confirmed
- limit: no MCP session, hosted Context7 API, Redis operation, credential, or production deployment

## Candidate-focused tests

### Omission and compatibility controls

- Exact source head: target `594a73133e14631af8c915a1b4f2c8039c964fe1` plus patch `bcdbef2c...`
- Exact carrier: `3360d80d8aa90e3eaafea3367ff9dcfd4dfe0345`
- Command:

```text
pnpm --filter @upstash/context7-mcp exec vitest run test/encryption.test.ts
```

- Tests and assertions:
  - valid explicit key produces one `iv:ciphertext` value and preserves unrelated headers;
  - malformed key omits `mcp-client-ip`, emits the fixed invalid-key diagnostic, and excludes raw IP and key;
  - mocked runtime failure omits `mcp-client-ip`, emits the fixed failure diagnostic, and excludes raw IP, key, and injected exception text.
- Result: `3/3 passed`
- Workflow/job: [`30635777158`](https://github.com/teamleaderleo/fieldwork/actions/runs/30635777158) / [`91172880796`](https://github.com/teamleaderleo/fieldwork/actions/runs/30635777158/job/91172880796)
- Coverage limit: Linux/Node 22; local package behavior only

### Complete MCP package suite

```text
pnpm --filter @upstash/context7-mcp test
```

- Result: `4` files, `49/49` tests passed
- Breakdown: `client-ip` 34, candidate encryption 3, JWT 10, certificate 2
- Coverage limit: target-declared package suite; no hosted integration

## Ordinary repository gates

| Gate | Exact command or workflow | Result | Notes |
| --- | --- | --- | --- |
| install | `pnpm install --frozen-lockfile` | pass | all six workspace projects |
| format | `pnpm --filter @upstash/context7-mcp format:check` | pass | all matched files used Prettier style |
| lint | `pnpm --filter @upstash/context7-mcp lint:check` | pass | ESLint |
| typecheck | `pnpm --filter @upstash/context7-mcp typecheck` | pass | `tsc --noEmit` |
| focused package tests | focused Vitest command above | `3/3` pass | exact mirrored test |
| complete target-declared suite | `pnpm --filter @upstash/context7-mcp test` | `49/49` pass | all MCP package tests |
| build | `pnpm --filter @upstash/context7-mcp build` | pass | `tsc` plus executable mode command |
| patch check/application | `git apply --check`, indexed apply | pass | exact target and patch digest |
| mirrored-test identity | `cmp` retained test to applied target test | pass | byte-identical |
| diff hygiene | `git diff --check --cached` | pass | exact applied diff |
| receipt validation | JSON identity assertions | pass | target, carrier, patch digest |
| platform matrix | not run | single Ubuntu/Node 22 job |

## Reversing controls

- baseline malformed-key behavior emits plaintext; candidate malformed-key behavior omits the field;
- valid-key ciphertext and unrelated headers pass under the candidate;
- injected runtime failure exercises the catch path and diagnostic privacy;
- full package suite controls unrelated MCP behavior.

## Soak, leak, and cleanup controls

- iterations: one focused run plus complete package run
- resources observed: no listener, child process, file, database, or network resource created by the focused test
- cancellation or interruption behavior: not applicable to synchronous helper
- immediate rerun result: not separately executed

## Setup and harness failures

| Attempt | Failure | Classification | Product claim affected? | Repair or stop |
| --- | --- | --- | --- | --- |
| run `30625351470` | unquoted 64-digit key became scientific notation; six formatting differences | fixture/packaging | no for listener/CORS evidence; identity candidate incomplete | quote key and format test |
| run `30632516479` | stale expected patch digest | packaging | no product execution occurred | refresh digest fence |
| run `30633097419` | retained patch test differed from mirror | packaging | earlier generation only | regenerate test hunk and retain `cmp` |
| run `30633209521` | focused `3/3` and package `49/49` passed; target formatting failed | packaging | source behavior supported, full-gate claim incomplete | apply target Prettier bytes |
| run `30635012019` | focused and full tests passed; two files still failed formatting | packaging | source behavior supported, full-gate claim incomplete | target-owned formatter generation |
| run `30635777158` | none | success | final exact candidate evidence | retire workflow after receipt transfer |

## Checks prepared but not executed

- missing and empty `CLIENT_IP_ENCRYPTION_KEY` decryption control — excluded after the unit was narrowed, then rendered unnecessary for this retired contribution; remains relevant to a separate default-key unit
- hosted Context7 header handling — no authority or credentials
- other operating systems and Node/OpenSSL versions — no matrix run

## Artifact and receipt

- artifact ID: `8795244374`
- artifact digest: `sha256:c2de1d9c85b96c11b6620f49c8004f6329def70e47c011720e27ff5a1eb3d300`
- artifact size: `1488` bytes
- extracted receipt SHA-256: `3dc726f2ad2099bccf4e01ca748a19ffc68567d177ecac88ad1ebf0b37e6b2a1`
- retained receipt: [`receipts/context7-omit-client-ip-on-encryption-failure.json`](./receipts/context7-omit-client-ip-on-encryption-failure.json)

## Platform and integration gaps

- Windows and macOS
- Node versions outside 22
- hosted Context7 service and API
- downstream provider treatment of missing versus plaintext metadata
- Redis, auth, billing, abuse, and telemetry consumers

## Cleanup receipt

- Temporary workflows removed from canonical retained carrier: `yes`
- Publisher or execution-only files removed: `yes`
- Generated residue checked: `yes`
- Immediate rerun performed: `no separate rerun after workflow retirement; workflow-free Fieldwork integrity passed`
- Remaining temporary branches or PRs: historical branches and PRs remain as immutable evidence; no temporary workflow lives in the packet branch

## Current test judgment

`REJECT`

Reason: the candidate is technically green, but exact public prior art proves upstream already evaluated and declined the same wire contract. More execution cannot clear a product-intent rejection.

Clearing condition: explicit new maintainer direction accepting omission, or a materially different accepted contract.
