# Tests and receipts — Unit 07 `backgroundFetchSize` snapshot

## Exact identity

- base: `16b3a916662ab449d496b7b4b4f04132565d1d28`;
- canonical one-commit candidate: `1191f6607d4df62bf302ce86cdc3287f9e2c57e0`;
- reviewed identical-tree head: `5dce70a1765b6985244cd46325e011c19920dd80`;
- changed files: `src/index.ts`, `test/background-fetch-size.ts`.

History collapse changed no bytes in the two-file fence:

- `src/index.ts`: `c3549a638b84ce096b13ebd7e3f71496dbe5afd5` on both heads;
- `test/background-fetch-size.ts`: `ce5f70eac6ed995361fe55ddc9b445f85fcbd07a` on both heads.

## Baseline characterization

Released `lru-cache@11.5.2` probes on Node 22/24/26 established:

- `NaN` poisons calculated size;
- negative and fractional values enter live accounting;
- positive infinity prevents provisional caching and breaks same-key coalescing;
- runtime string `'2'` reaches string arithmetic, entry loss, negative count, and `Invalid array length` rejections;
- zero remains coherent and coalesced.

Receipt: Fieldwork run `30491292307`.

## Focused candidate gate

Run `30754588900`, job `91514469959`, Ubuntu 24.04 ARM, Node 24.18.0, on accepted predecessor tree:

- dependency install and repository build: success;
- focused `test/background-fetch-size.ts`: 95/95 assertions;
- OXLint on both changed files: zero warnings/errors;
- Prettier on both changed files: success;
- diff and tracked-worktree hygiene: success.

The focused matrix covered invalid primitive values, hostile non-coercion, constructor/default versus mutated `undefined`, pre-dispatch rejection, callback re-entry, next-operation mutation, zero coalescing, stale/no-size behavior, settlement, internal receipt corruption, and one unrelated TTL-autopurge control.

The final reviewed tree removed only that unrelated TTL-autopurge control. Product source and every `backgroundFetchSize` assertion are unchanged.

## Exact reviewed-tree native matrix

At `5dce70a1765b6985244cd46325e011c19920dd80`:

Benchmarks `31010354657`: success.

CI `31010353969`:

| Lane | Result |
| --- | --- |
| Ubuntu Node 24 | success |
| Ubuntu Node 25 | success |
| macOS Node 24 | success |
| macOS Node 25 | success |
| Windows Node 24 Bash | harness failure before product tests |
| Windows Node 24 PowerShell | harness failure before product tests |
| Windows Node 25 Bash | harness failure before product tests |
| Windows Node 25 PowerShell | harness failure before product tests |

All Windows failures occur after install/build and before product test collection:

```text
'@tapjs/clock' does not appear to be a tap plugin.
Cannot find module '@tapjs/clock'
```

The public-base `.taprc` requests the plugin while the clean repository dependency graph does not install it. Exact-version base/candidate comparison showed both can execute without coverage after temporary plugin injection, while both remain red under the native coverage command. No dependency or lockfile repair belongs in this candidate.

The canonical one-commit head reuses this execution receipt by exact changed-file blob identity, not by pretending the commit SHA itself ran those jobs.

## Reversing controls

- invalid constructor and mutated values are rejected without coercion;
- provider dispatch remains zero on invalid missing-key consumption;
- synchronous provider mutation cannot change the current operation’s captured charge;
- valid mutation applies to the next operation;
- zero remains cached and coalesced;
- stale refresh and no-size caches ignore the irrelevant field;
- corrupted internal receipt fails at the accounting boundary;
- pending provisional size becomes the resolved value’s calculated size on settlement.

## Final judgment

`TARGET-EXECUTED / TECHNICALLY READY`, with a declared unchanged-base Windows coverage-harness limit and exact-tree carry-forward to the one-commit canonical source. No public upstream interaction occurred or is authorized.
