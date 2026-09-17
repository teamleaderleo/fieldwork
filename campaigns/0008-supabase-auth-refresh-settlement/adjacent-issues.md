# Adjacent Supabase issue map

State: `exploration-complete`

Campaign: #78

Parent scout: #21

Exploration date: `2026-07-30`

Upstream contact authorized: `false`

Upstream contact performed: `false`

## Purpose

This pass checks whether nearby public Supabase reports strengthen, duplicate, supersede, or distract from the auth refresh settlement campaign.

It does not promote every open issue. Each item is classified by current owner, evidence gap, and the smallest useful next action.

## Ranked adjacent candidates

### 1. Realtime persisted-session authentication in React Native

Public report: [React Native Realtime persisted-session report](https://redirect.github.com/supabase/supabase-js/issues/1730)

Reported behavior:

- React Native restores a persisted session;
- Realtime reports a successful subscription;
- RLS-dependent changes do not arrive;
- a fresh sign-in or manual `realtime.setAuth()` helped at least some reporters;
- the original report used Supabase JS `2.39.8`.

Current source state:

- the Supabase wrapper listens for `INITIAL_SESSION`, `SIGNED_IN`, and `TOKEN_REFRESHED`;
- those events call `realtime.setAuth()` when the token changes;
- current unit tests explicitly assert that `INITIAL_SESSION` updates Realtime auth;
- current Realtime also receives an async access-token provider backed by `auth.getSession()`.

Assessment:

**Current-version characterization candidate, not a confirmed current defect.**

The issue remains open and was updated in 2026, but the source and unit contract now cover the reported missing initialization step. The remaining possibilities include:

- React Native or AsyncStorage notification timing;
- channel subscription before initial auth propagation;
- foreground/background socket recovery;
- a stale report spanning multiple mechanisms;
- a current regression outside the unit fixture.

Smallest useful trial:

1. current released Supabase JS;
2. React Native-compatible async storage;
3. persisted authenticated session before client creation;
4. RLS policy dependent on a JWT claim;
5. subscribe immediately and after `INITIAL_SESSION`;
6. record socket join payload token, `setAuth` timing, and first delivered change;
7. include manual `setAuth` and fresh-sign-in controls.

Keep separate from campaign #78. The settlement patch may prevent auth-dependent calls from hanging, but it does not establish Realtime's persisted-session ordering.

### 2. `getSession()` performance after lockless coordination

Public report: [`getSession()` performance report](https://redirect.github.com/supabase/supabase-js/issues/970)

Reported behavior:

- local `getSession()` can take tens of milliseconds during rendering;
- the original reporter suspected the old auth lock;
- later reporters continued to observe delays;
- the issue remains open.

Current source state:

- the default navigator/process lock path was removed by the lockless coordination refactor;
- `getSession()` still waits for initialization and may trigger refresh near expiry;
- storage adapters, session parsing, callback initialization, and active refresh joining remain possible latency owners.

Assessment:

**Recheck candidate with a changed mechanism hypothesis.**

The old lock explanation cannot be carried forward without measurement. A useful matrix should separate:

- before and after initialization;
- empty storage, valid session, near-expiry session, and expired session;
- synchronous local storage and asynchronous storage;
- idle execution and render/task contention;
- direct auth-js and the public Supabase wrapper;
- current release and a pre-lockless control.

The private-storage workaround posted in the issue bypasses supported auth behavior and trust warnings. It should not become the expected public contract.

### 3. Generated zero-argument function types collide with table columns

Public report: [zero-argument function type collision report](https://redirect.github.com/supabase/postgres-meta/issues/1039)

Active upstream patch: [zero-argument and computed-field type correction](https://redirect.github.com/supabase/postgres-meta/pull/1035)

Reported mechanism:

- zero-argument functions are generated with `Args: never`;
- TypeScript conditional types treat `never extends T` as true;
- a function sharing a name with a table column can be classified as a computed field;
- the column is then omitted from the inferred result of `select('*')`.

Assessment:

**High-confidence generated-contract issue with active upstream ownership.**

The existing PR changes zero-argument `Args` to `Record<PropertyKey, never>` and also addresses scalar computed-field generation. Fieldwork should avoid a duplicate implementation.

Useful independent review:

1. run the reported schema through current type generation;
2. compile the generated type with current postgrest-js select parsing;
3. prove the colliding column is omitted before the patch and retained after;
4. test non-colliding zero-argument functions;
5. test genuine computed fields with unnamed row parameters;
6. check whether changing `Args` affects RPC call ergonomics or generated compatibility.

This is a stronger candidate for independent review than a new branch.

### 4. Bigint runtime and generated-type representation

Public report: [Bigint runtime and generated-types report](https://redirect.github.com/supabase/postgres-meta/issues/1078)

The issue combines several contracts:

- JSON response precision for values above `Number.MAX_SAFE_INTEGER`;
- PostgREST casting syntax in the select parser;
- row output representation;
- insert and update acceptance of strings or JavaScript `bigint`;
- generated database types.

Assessment:

**Consequential but too broad for one campaign.**

Split before investigation:

1. wire/runtime precision from PostgREST JSON to JavaScript;
2. select-cast type inference;
3. generated `Row` output type;
4. generated `Insert` and `Update` accepted-input types;
5. migration guidance for applications already storing large identifiers.

A source-only type change cannot repair a wire response that has already lost precision. Conversely, changing all `bigint` columns to strings may be a broad compatibility change. The first useful artifact is a contract table using values below, at, and above the safe-integer boundary.

### 5. Reopened session-user warning behavior

Public report: [session-user warning report](https://redirect.github.com/supabase/supabase-js/issues/1709)

Merged prior fix: [session-user warning proxy correction](https://redirect.github.com/supabase/supabase-js/pull/1817)

History:

- the original warning proxy produced false positives during serialization and internal access;
- the merged correction moved the warning boundary from the session object to the user object;
- the issue was later reopened and remained active in July 2026.

Assessment:

**Current reproduction required.**

The next pass should identify which exact access now triggers warnings and whether it is:

- application access to unverified stored user data;
- framework serialization;
- auth-js internal access;
- initialization or refresh notification;
- a custom storage adapter;
- a regression after the merged proxy change.

This is a trust and diagnostics contract, separate from refresh settlement.

### 6. Refresh outage and retry lifecycle

Public issue: [refresh outage and repeated-retry report](https://redirect.github.com/supabase/supabase-js/issues/1680)

Current open work:

- [offline-aware refresh and reconnect proposal](https://redirect.github.com/supabase/supabase-js/pull/2568);
- [bounded automatic refresh failures proposal](https://redirect.github.com/supabase/supabase-js/pull/2573).

Assessment:

**Active upstream lifecycle area; monitor and rebase, do not duplicate.**

These changes touch retry, failure cooldown, online events, auto-refresh tickers, initialization, and disposal. They do not change the order between committed session storage, listener completion, and shared refresh settlement.

Any production branch from campaign #78 must retain their accepted behavior if either lands.

### 7. Refresh diagnostic headers

Current service behavior:

- the Auth service emits response headers for refresh-token counter, reuse, and reuse cause;
- successful auth-js requests parse JSON and return the transformed body;
- those response headers are not exposed on the success path.

Assessment:

**Bounded observability candidate.**

Potential value:

- distinguish normal rotation from convergence after a lost response;
- identify close-concurrency reuse without logging token material;
- improve support diagnostics for refresh storms and cross-tab recovery.

Risks:

- accidental public API expansion;
- browser header-exposure/CORS requirements;
- leaking internal security signals into ordinary logs;
- coupling the client to service implementation headers.

Keep outside the settlement patch. A separate design should decide whether diagnostics remain internal debug events, become an optional hook, or stay service-only.

## Rejected or narrowed reports

### Storage multipart/upsert report

Public report: [Storage multipart and upsert authorization report](https://redirect.github.com/supabase/storage/issues/1241)

The reporter initially isolated multipart requests and `x-upsert` as apparent backend failures with misleading RLS errors.

Maintainer review established:

- delete requires `SELECT` plus `DELETE` policy permission;
- upsert requires `SELECT` plus `UPDATE` permission;
- the reporter was missing the required scoped `SELECT` policy;
- adding it repaired delete and upsert;
- the reporter explicitly withdrew the backend-defect conclusion.

Assessment:

**Rejected as a Storage correctness defect.**

A narrower diagnostics question remains: how much policy detail can Storage safely expose without revealing security-sensitive information. Do not use this report as evidence of token propagation failure.

### JSONB `NOT NULL` generated type includes `null`

Public report: [JSONB nullability type report](https://redirect.github.com/supabase/postgres-meta/issues/1055)

The report expects `NonNullable<Json>` for a `jsonb NOT NULL` column.

Assessment:

**Representation question, not yet a simple generator defect.**

The shared TypeScript `Json` type represents values inside JSON, including JSON `null`, while column nullability represents SQL NULL. One TypeScript `null` spelling can conflate those layers. A useful investigation must first define:

- how PostgREST serializes SQL NULL versus JSON null;
- how inserts express JSON null versus SQL NULL;
- whether row, insert, and update types need distinct wrappers;
- whether `NonNullable<Json>` would incorrectly reject valid JSON values.

Do not promote a one-line type substitution without that contract.

## Functions and Storage client boundary

The public Supabase wrapper obtains an auth token for PostgREST, Storage, and Functions through one shared `fetchWithAuth` path. Current unit tests assert the same session token reaches all three clients.

This pass found no separate Functions-client settlement owner. A hang in `auth.getSession()` can delay a Functions, Storage, or PostgREST call before its own client sends a request, but that remains propagation of auth lifecycle behavior.

The Storage authorization report also demonstrates why a successful token-control request does not prove every operation has sufficient policy permissions.

## Recommended next actions

1. **Run the Realtime persisted-session current-version matrix.** Highest-value adjacent runtime check.
2. **Rebenchmark `getSession()` on current lockless code.** Determine whether the open issue is resolved, changed, or still reproducible.
3. **Review the active zero-argument function type correction independently.** Avoid duplicate generated-types work.
4. **Split Bigint into wire, parser, and generated-type contracts before claiming one fix.**
5. **Reproduce the session-user warning report on the current release and identify the exact warning access.**
6. **Keep outage and reconnect proposals as rebase constraints for campaign #78.**
7. **Retain refresh headers as a separate observability design.**

## Boundary

No upstream issue, pull request, comment, review, reaction, or message was created or changed during this exploration.