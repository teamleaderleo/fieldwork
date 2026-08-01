# Approaches — unit 19, Context7 client-IP encryption fallback

## In simple words

The strongest implementation is a narrow fail-closed omission: successful encryption retains the header; malformed-key and cipher-failure paths omit it. Fieldwork executed that design thoroughly. Upstream had already received the same design in PR #2104 and declined it, so the selected action is to retire the contribution while preserving the evidence.

## Decision criteria

1. prevent accidental plaintext/ciphertext ambiguity in the same header;
2. preserve unrelated request metadata and successful encryption behavior;
3. keep diagnostics bounded and free of the IP, key, and exception text;
4. respect upstream's wire-compatibility and product-intent decision;
5. keep this unit separate from default-key, hashing, proxy, and hosted-service questions.

## Selected approach

### Retire after exact prior-art confirmation

- Design: preserve the tested patch, tests, receipts, drafts, and source analysis; stop upstream preparation.
- Owning boundary: Fieldwork packet and `teamleaderleo/fieldwork#435` handoff.
- Evidence: public issue #1965, public PR #2104, commit `5a36c505...`, maintainer close comment, and current source identity.
- Advantages: avoids repeating a declined proposal; leaves a continuation-ready record if maintainer direction changes.
- Costs and risks: the baseline plaintext fallback remains; public maintainer rationale is brief.
- Remaining controls: none under current authority and product direction.

## Viable alternatives

### Maintainer-invited fail-closed omission

- Design: materialize the retained patch on an owned Context7 fork and preserve the exact two-file fence.
- Why it remains plausible: target-native tests and all ordinary package gates passed.
- What it would improve: removes plaintext fallback and exception-bearing diagnostics in the two named failure paths.
- What it would widen or complicate: changes wire behavior by removing client-IP metadata during failures.
- Exact discriminator: explicit maintainer acceptance of header omission.
- Reopening trigger: a maintainer request, accepted issue, or documented contract supporting omission.

### Document the intended fallback

- Design: explain that plaintext fallback is intentional and describe operator implications.
- Why it remains plausible: upstream rejected behavioral change and previously treated default-key concern as documentation/log clarity.
- What it would improve: reduces operator misunderstanding without changing the wire path.
- What it would widen or complicate: requires maintainers to choose precise public wording around privacy and service expectations.
- Exact discriminator: explicit request for documentation.
- Reopening trigger: user authorization plus a public documentation gap accepted by maintainers.

### Explicit-key-only metadata

- Design: omit client-IP metadata when the key is absent, empty, malformed, or unusable.
- Why it remains plausible: it creates a coherent confidentiality-oriented contract.
- What it would improve: removes reliance on the public fixed default key.
- What it would widen or complicate: broadens behavior beyond the demonstrated failure and beyond declined PR #2104.
- Exact discriminator: accepted product requirement that client-IP metadata requires an operator-supplied secret.
- Reopening trigger: maintainer direction or a replacement upstream design.

## Executed losing approaches

### Upstream fail-closed PR #2104

- Exact branch and commit: `fix/1965-fail-closed-client-ip-encryption` at `5a36c505e88da3fe74d34ae3f4dd01124031bb88`.
- What ran: author reported lint and typecheck; no target-native regression was added.
- Result: closed unmerged on 2026-04-03.
- Why it lost: maintainer stated that omission was not the intended behavior.
- Useful evidence retained: exact production diff proves the core contribution is a duplicate.

### Fieldwork omission candidate

- Exact carrier: `3360d80d8aa90e3eaafea3367ff9dcfd4dfe0345` against `upstash/context7@594a73133e14631af8c915a1b4f2c8039c964fe1`.
- What ran: focused `3/3`, complete package `49/49`, format, lint, typecheck, build, patch identity, mirrored-test identity, diff hygiene, and receipt validation.
- Result: technically accepted as a bounded source candidate.
- Why it lost: later current duplicate search found the same contract had already been declined upstream.
- Useful evidence retained: stronger tests, fixed diagnostics, exact receipt, and compatibility inventory.

### Hash fallback PR #2056

- Exact branch and commit: `fix/encryption-key-hardcoded` at `f6c401a7851f82e682f84af8fbe519996cb16622`.
- What ran: public review identified log-volume and unsalted-IP-hash reversibility concerns.
- Result: author closed the PR to maintain the change in a private mirror.
- Why it lost: broader semantics, weak privacy claim, and no upstream adoption.
- Useful evidence retained: public default-key risk and hashing pitfalls.

## Rejected easy answers

### Re-submit the Fieldwork candidate because it has better tests

- Temptation: PR #2104 lacked regression tests and retained exception text, while the Fieldwork version repairs both.
- Why it is incomplete: those improvements leave the same header-omission contract that the maintainer declined.
- Negative control or source fact: PR #2104 changes the same return type and conditional insertion points.

### File a fresh issue

- Temptation: present stronger execution evidence and privacy-bounded wording.
- Why it is incomplete: issue #1965 already described the same behavior and proposed the same option.
- Negative control or source fact: issue #1965 is closed `not planned` and directly links PR #2104.

### Treat ciphertext under the default key as confidentiality

- Temptation: a positive test shows a ciphertext-shaped value distinct from plaintext.
- Why it is incomplete: the key is fixed in public source and the IV is carried with the ciphertext.
- Negative control or source fact: PR #2056 and Fieldwork review `4830056411` identify the same limit.

### Fold listener and proxy repair into this unit

- Temptation: forwarded identity can influence the value being encrypted.
- Why it is incomplete: listener, CORS, and trusted-proxy ownership are separate code and compatibility boundaries.
- Negative control or source fact: Fieldwork PR #398 owns that lane.

## Prior upstream approaches

| Link | Approach | Status | Relationship to this unit |
| --- | --- | --- | --- |
| [issue #1366](https://github.com/upstash/context7/issues/1366) | document/default-key warning concern | closed completed | adjacent; maintainers removed warning and rejected concern framing |
| [PR #2056](https://github.com/upstash/context7/pull/2056) | remove default key and hash on failure | closed unmerged | broader alternative; author-retired |
| [issue #1965](https://github.com/upstash/context7/issues/1965) | report plaintext fallback and propose omission | closed not planned | exact duplicate issue |
| [PR #2104](https://github.com/upstash/context7/pull/2104) | return `undefined` and omit header on failure | closed unmerged | exact duplicate implementation, explicitly declined |

## Deferred adjacent work

- missing/empty key policy — broader than encryption failure;
- public default-key confidentiality — separate compatibility and product decision;
- authenticated encryption — separate wire-format redesign;
- trusted proxy and IP validation — separate parser and deployment boundary;
- hosted header consumption — requires service-side authority and execution.

## Decision history

| Date | Exact inputs | Decision | Reason | Reopening trigger |
| --- | --- | --- | --- | --- |
| 2026-07-31 | target `594a731...`, carrier `3360d80...`, run `30635777158` | accept bounded candidate | all named source and package gates passed | complete prior-art/currentness review |
| 2026-07-31 | PR #370 head `51948ee...`, review `4830056411` | narrow privacy claim | public default key defeats broad confidentiality framing | missing/empty-key policy decision |
| 2026-08-01 | issue #1965, PR #2104, commit `5a36c505...`, current master `594a731...` | `RETIRE` | exact contribution already declined and behavior remains current | new maintainer direction or explicit user-authorized challenge |
