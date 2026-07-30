# lru-cache background fetch size accounting

State: `candidate-executing`

Fieldwork lane: #132  
Programme: data-durable-workflows  
Target package: `lru-cache@11.5.2`  
Source pin: `isaacs/node-lru-cache@16b3a916662ab449d496b7b4b4f04132565d1d28`  
Owned implementation: `teamleaderleo/node-lru-cache#1`  
Owned branch: `fieldwork/background-fetch-size-validation`  
Current owned head: `1dcfd7e07cc8b961c2aae38da37e2e148f92e6a9`  
Upstream contact authorized: `false`

## In simple words

`backgroundFetchSize` is provisional size accounting for an asynchronous cache fill. Released `lru-cache@11.5.2` accepts invalid runtime values into arithmetic that assumes a finite nonnegative integer.

The defect is not limited to construction. The option remains a mutable public field, and `fetchMethod` runs synchronously inside the Promise executor before the provisional entry is inserted. A callback can therefore mutate the field after an earlier validation but before `#requireSize()` consumes it.

The current candidate validates at the relevant public boundaries and carries one immutable validated snapshot through the internal background-fetch object.

## Confirmed released behavior

Workflow `30491292307` passed on Node 22, 24, and 26 against exact `lru-cache@11.5.2`.

Observed:

- `NaN` permanently poisoned `calculatedSize`;
- negative and fractional values entered live accounting;
- positive infinity prevented provisional insertion and broke same-key fetch coalescing;
- runtime string `'2'` changed arithmetic into string concatenation, drove cache entry count negative, removed entries, and rejected both waiting fetches with `Invalid array length`.

`backgroundFetchSize: 0` remained coherent: the pending entry contributed zero provisional size but stayed cached and coalesced. Zero is a required compatibility control.

## Source ownership

### Construction

The constructor defaults the option to `1` and assigns it directly to the public mutable field. The candidate requires a primitive finite nonnegative integer before assignment.

### Missing-key background fetch

For a missing key under active size tracking, `#backgroundFetch()`:

1. checks whether a fetch already exists;
2. creates a Promise whose executor invokes user `fetchMethod` synchronously;
3. inserts the resulting internal background-fetch promise through `#set()`;
4. `#requireSize()` reads the provisional size for accounting.

A check performed only before step 2 is insufficient if step 4 re-reads the public field.

### Stale refresh and no-size controls

A stale-entry refresh reuses the existing entry size and does not call `#set()` for a new provisional entry. A cache without size tracking ignores provisional size. The repair does not widen those paths.

## Candidate contract

The owned patch now:

1. introduces `isNonNegativeInt()`;
2. validates the constructor value;
3. before missing-key provider dispatch under active size tracking, validates and stores one local snapshot;
4. attaches that snapshot as internal `BackgroundFetch.__size`;
5. makes size accounting consume and revalidate only that snapshot;
6. never re-reads `this.backgroundFetchSize` after user code runs for the current operation.

The public field remains mutable and enumerable. Mutation affects later operations, not the already-dispatched operation.

## Candidate tests

The native focused suite covers:

- negative, fractional, `NaN`, positive/negative infinity;
- strings, booleans, bigint, symbols, null, objects, and arrays;
- valid zero and positive integer controls;
- invalid public-property mutation before dispatch, with zero provider calls and unchanged cache state;
- public-property mutation inside synchronous `fetchMethod` to string, `NaN`, and negative values;
- snapshot accounting remains `2` while pending despite that mutation;
- same-key calls remain coalesced;
- settlement transitions to the resolved value's size `5`;
- mutated irrelevant values remain ignored without size tracking;
- stale-entry and existing eviction controls remain present.

## Policy consistency

Construction rejects an explicitly supplied invalid option even when the chosen cache configuration would not use size tracking. Later public-field mutation is validated only when an operation consumes the value.

That distinction is deliberate:

- constructor options are validated as a declared configuration contract;
- runtime mutable state is checked at actual consumption;
- irrelevant later mutation does not retroactively make an otherwise valid no-size cache unusable.

## Evidence state

- released-package defect: `target-executed`;
- source mechanism and TOCTOU: `source-read`;
- revised candidate patch and native tests: prepared on owned head `1dcfd7e...`;
- clean-checkout Node 22/24/26 execution: pending on the revised exact head;
- direct source-only implementation branch: absent;
- public upstream packet: unauthorized.

## Next gate

1. exact clean checkout applies `.fieldwork/background-fetch-size-validation.patch` with `git apply --check`;
2. Node 22/24/26 focused suite passes;
3. formatting, type, and ordinary relevant repository gates run on a direct source head;
4. complete-diff review confirms no alternate background-fetch construction lacks `__size`;
5. only then promote implementation beyond R1.

## Boundary

- synthetic local values only;
- no public upstream issue, pull request, comment, reaction, or message;
- no claim that validating this one option repairs unrelated size or fetch lifecycle behavior.
