# Campaign 0010 Decision

## In simple words

The receiver-aware declaration direction is worth retaining and testing. It is not ready to publish as a Cloudflare pull request today. The local application protection is already complete. The remaining work is a narrow evidence and review pass on the owned-fork candidate, not more broad runtime or TypeScript research.

## Decision

**Disposition: HOLD upstream publication; EXECUTE the bounded final gate.**

The canonical implementation candidate is:

- repository: `teamleaderleo/workerd`
- pull request: `teamleaderleo/workerd#1`
- branch: `research/issue-474-receiver-aware-types`
- materialized head: `e7b15f8014e8ed49255d2f0c6774f0b3bfe1714a`
- base pin: `6aa890be9fa547e3907c805b312e39917a274221`

The exact candidate head may move during the final gate. Any prior review expires on movement unless semantic identity is explicitly proved.

## Clearing conditions

1. **Small exact-head receipt**
   - construct synthetic RTTI;
   - run generator, override merge, global extraction, and receiver cleanup;
   - compile the resulting declaration text with TypeScript against legal and illegal receiver cases;
   - retain command, environment, exact head, output, and runtime.

2. **Target-native receipt**
   - complete the named focused workerd targets at the same exact head; or
   - record a clear feasibility limit and explain why the small receipt plus source review is the strongest practical evidence.

3. **Independent exact-head review**
   - inspect the complete current diff;
   - verify static, explicit receiver, override, overload, generic, inheritance, and context-global paths;
   - use `ACCEPT`, `REPAIR`, `HOLD`, `EXECUTE`, or `REJECT` with an exact next transition.

4. **Compatibility boundary**
   - inspect representative generated APIs or a complete generated diff;
   - identify intentional detachable operations, declaration breaks, recursive aliases, and owner-type changes;
   - do not claim broad compatibility from the synthetic fixture alone.

5. **Upstream packet hygiene**
   - update the issue/PR narrative to the final design;
   - remove temporary workflow machinery from the canonical contribution diff;
   - record contribution and AI-assistance policy;
   - preserve rejected alternatives and rollback.

## Actions that do not need repeating

- no more Bun or Node receiver research;
- no TypeScript language issue;
- no typescript-eslint issue;
- no broad lint-rule proposal;
- no Chromium rerun unless a later workerd result conflicts with browser behaviour;
- no change to Stensibly's arrow wrapper or native-workerd regression.

## Human decisions reserved

Only the human owner may authorize:

- a new comment on the existing workerd issue;
- opening a workerd upstream pull request;
- merging or closing owned candidate and archival pull requests;
- changing the campaign from `submitted` to another upstream state.

## Retention decisions

- retain `teamleaderleo/stensibly#474` as the original research thread;
- retain merged `teamleaderleo/stensibly#482` as the owned production safeguard;
- retain `teamleaderleo/workerd#1` as the canonical upstream-fork research branch;
- retain `teamleaderleo/stensibly#483` only until this Fieldwork campaign and its source links are accepted, then close it as superseded rather than merge it.
