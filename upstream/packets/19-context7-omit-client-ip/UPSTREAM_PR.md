# Upstream pull-request draft — fix(mcp): omit client-IP metadata when encryption fails

Draft status: `retired — equivalent PR #2104 closed unmerged`  
Proposed head: `none; teamleaderleo/context7 admission absent`  
Proposed base: `upstash/context7 master at 594a73133e14631af8c915a1b4f2c8039c964fe1`  
Public interaction authorized: `no`

## Submission decision

Do not open this pull request. [`upstash/context7#2104`](https://github.com/upstash/context7/pull/2104) already changed the same return type and conditional header insertion, and a maintainer closed it because omission was not the intended behavior. The draft remains below so a future worker can compare any new maintainer request against the exact tested candidate.

---

## Summary

- omit optional `mcp-client-ip` metadata when the configured encryption key is malformed or the cipher throws;
- preserve successful encrypted metadata and every unrelated request header;
- emit fixed failure diagnostics without the client IP, configured key, or caught exception text;
- add focused target-native regressions for success and both failure paths.

## Problem

`encryptClientIp()` currently returns the input IP when key validation fails or encryption throws. `generateHeaders()` then publishes that value under the same `mcp-client-ip` header used for encrypted metadata. A caller or downstream observer cannot distinguish that fallback from the intended encrypted form by header name alone.

## Change

- widen the internal helper return type to `string | undefined`;
- return `undefined` after malformed-key validation failure;
- return `undefined` after runtime cipher failure;
- add `mcp-client-ip` only after successful encryption;
- replace exception-bearing diagnostics with fixed messages;
- leave source, server version, session, authorization, client, and transport headers unchanged.

## Tests

- `pnpm --filter @upstash/context7-mcp exec vitest run test/encryption.test.ts` — `3/3` passed;
- `pnpm --filter @upstash/context7-mcp test` — `49/49` passed;
- `pnpm --filter @upstash/context7-mcp format:check` — passed;
- `pnpm --filter @upstash/context7-mcp lint:check` — passed;
- `pnpm --filter @upstash/context7-mcp typecheck` — passed;
- `pnpm --filter @upstash/context7-mcp build` — passed.

## Compatibility

- public API: unchanged; `generateHeaders()` keeps `Record<string, string>`;
- existing behavior retained: valid-key encryption and unrelated headers;
- behavior changed: `mcp-client-ip` is absent instead of plaintext on two failures;
- platform or runtime notes: executed on Ubuntu 24.04, Node 22.23.1;
- performance or allocation notes: success path remains materially unchanged;
- migration or rollback: one production file and one test file; revert restores current fallback.

## Alternatives considered

- **retain plaintext fallback:** preserves current upstream behavior and service metadata availability; selected by current upstream intent;
- **send a marker value:** still publishes a failure token and requires downstream protocol changes;
- **hash the IP:** broader format change, and an unsalted IPv4 hash remains enumerable;
- **require an explicit key:** coherent confidentiality policy but broader than this failure-path repair;
- **throw and fail the request:** converts optional telemetry failure into service failure.

## Limits

- missing or empty key behavior remains unchanged and uses the public fixed default key;
- this change does not claim confidentiality for default-key ciphertext;
- AES-CBC authenticity is outside scope;
- hosted Context7 service behavior and downstream consumers were not exercised;
- listener, CORS, proxy trust, and IP selection are separate work.

## Related work

- [`#1965`](https://github.com/upstash/context7/issues/1965) — exact issue, closed not planned
- [`#2104`](https://github.com/upstash/context7/pull/2104) — exact implementation, closed unmerged
- [`#1366`](https://github.com/upstash/context7/issues/1366) — adjacent default-key documentation concern
- [`#2056`](https://github.com/upstash/context7/pull/2056) — broader hashing alternative, author-closed

---

## Submission checklist

- [ ] Owned fork admitted and branch created.
- [ ] Current maintainer direction reverses or supersedes the decision on #1965/#2104.
- [x] Diff fence limited to product source and target-native test.
- [x] Temporary workflows and Fieldwork files absent from the proposed target diff.
- [x] Focused regression and ordinary package gates executed on exact target source.
- [x] Current duplicate and overlap search complete as of `2026-08-01`.
- [ ] Current contribution and AI-disclosure policies rechecked at filing time.
- [ ] Exact user authorization to open the pull request recorded.

Current action: `do not submit`.
