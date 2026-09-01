# Bun compatibility follow-ups: Request, builtin specifiers, and RoboBun breadcrumbs

## In simple words

This scout found two concrete compatibility seams and one worthwhile RoboBun follow-up.

The strongest result is the `Request` constructor. At Bun `52bf09cb1cdbed0fbda4cf576e5d329cf92366ef`, the constructor has no GET/HEAD-with-body rejection. Node/undici and the Fetch Standard perform that check before body extraction and before rejecting a disturbed or locked input body. RoboBun PR [#37033](https://redirect.github.com/oven-sh/bun/pull/37033) is actively repairing adjacent `Request` input-copy semantics and deliberately leaves this precedence gap for a separate change. The right disposition is **prepare-only**: retain the reference probe and regression now, then re-evaluate immediately after #37033 lands or stabilizes.

The builtin-specifier thread also found a concrete cause. Bun's runtime transpiler rewrites an import record's path text from bare `http` to `node:http` before loader-visible consumers receive it. That is appropriate for semantic resolution in some APIs, but it destroys source spelling for observer APIs. Node demonstrates the distinction: `import.meta.resolve("http")` canonicalizes to `node:http`, while a loader resolve hook sees the literal `http`. RoboBun PR [#32628](https://redirect.github.com/oven-sh/bun/pull/32628) reports the same fidelity problem in the newer `module.import` diagnostics event. The repair should preserve written spelling alongside canonical builtin identity instead of changing diagnostics output after the fact. This is also **prepare-only** while #32628 owns the diagnostics surface.

The breadcrumb miner produced several attractive leads and discarded many because RoboBun or another open Bun PR already owns them. The strongest independent survivor is the literal-IP synchronous `Bun.connect` failure called out by RoboBun PR [#37093](https://redirect.github.com/oven-sh/bun/pull/37093): current source still collapses `ConnectResult::Failed` into generic `FailedToOpenSocket`. No separate open Bun issue or PR was found for that exact literal-IP follow-up. It ranks behind the `Request` constructor because this worker cannot execute an exact-current Bun binary in the available environment, so the retained evidence is source-level plus the RoboBun breadcrumb rather than target execution.

Automated upstream contact remained false. No Bun issue, pull request, comment, reaction, branch, file, workflow, or other upstream state was created or modified.

## Assignment and source fence

- Fieldwork issue: #709
- Programme: #207 `open-source-ecosystems`
- Parent scout: #209
- Target: Bun
- Owned path: `programmes/open-source-ecosystems/scouts/bun-compat-followups/`
- Bun revision examined: `52bf09cb1cdbed0fbda4cf576e5d329cf92366ef`
- Bun `main` relation when pinned: identical to that commit, 0 ahead / 0 behind
- Fieldwork base: `98b6c064cc40ebdfad8a1dd433bd22a035b7c7c5`
- Retrieval / execution date: 2026-08-08
- Local Node: `v22.16.0`
- Local bundled undici: `6.21.2`
- Node source comparison: `nodejs/node@f538f11faf6c1f5f4bf7ecdb7fbffb15a5b67c95`, `deps/undici/src/lib/web/fetch/request.js`
- Normative reference: WHATWG Fetch Standard, `Request` constructor steps 35–41 at retrieval time
- Automated upstream contact authorized: `false`

### Execution feasibility

Node controls executed locally and their exact observations are retained in `results/node-controls.md`.

An exact-current Bun executable was unavailable in this worker environment. `bun` is absent from PATH, shell network access is blocked, and the discoverable prebuilt canary release did not correspond to the pinned Bun commit. Building or downloading an unrelated Bun revision would weaken the source fence, so this scout records an explicit feasibility limit instead of upgrading source reading to `target-executed`.

Consequences:

- Bun implementation claims below are `source-read` unless a narrower label is stated.
- The prepared Bun regression is `target-test-prepared`.
- RoboBun PR descriptions are prior upstream-reported evidence, not Fieldwork target execution.
- Node controls are `model-executed` reference evidence.

## Thread A — `Request` constructor GET/HEAD body parity

### Plain-language result

A `Request` whose final method is GET or HEAD cannot carry a body under the Fetch constructor algorithm. The important compatibility detail is the order of checks. Once URL parsing and method setup have succeeded, GET/HEAD body invalidity is diagnosed before extracting an `init.body` stream and before checking whether an inherited input body is disturbed or locked.

Current Bun's constructor never performs that GET/HEAD body check. Its separate `fetch()` path knows GET/HEAD body restrictions, which means invalid construction can survive until later use and can produce a different error ordering from Node/undici.

### Normative and Node oracle

The Fetch Standard's constructor order at retrieval time is:

```text
parse/copy input and initialize request
        ↓
apply init and final method
        ↓
if final method is GET/HEAD and init.body is non-null or inputBody exists
    throw TypeError
        ↓
extract init.body
        ↓
select initBody or inputBody
        ↓
if inheriting inputBody and it is unusable
    throw TypeError
        ↓
install final body
```

Node's vendored undici source follows the same order. In `deps/undici/src/lib/web/fetch/request.js`, the GET/HEAD-body check is performed before `extractBody()` and before `inputBody` unusability is checked.

### Node/undici control matrix

Executed with Node `v22.16.0`, undici `6.21.2`; retained probe: `probes/request-constructor-node.mjs`.

| Case | Node result |
| --- | --- |
| `new Request(url, {method:"GET", body:"x"})` | GET/HEAD body `TypeError` |
| HEAD equivalent | same |
| POST `Request` input + `{method:"GET"}` | same |
| POST input + `{method:"HEAD"}` | same |
| input + GET + overriding `body` | same |
| input + GET + `body:null` | same; null does not erase the inherited input body |
| input + GET + `body:undefined` | same |
| disturbed input + GET | GET/HEAD body error wins |
| disturbed input + POST | used-input-body error wins |
| locked input + GET | GET/HEAD body error wins |
| locked input + POST | used-input-body error wins |
| malformed URL + GET + body | URL parsing error wins |
| GET + `ReadableStream` + `keepalive:true` | GET/HEAD body error wins before stream extraction/keepalive rejection |

The multi-invalid cases are the useful discriminator. A patch that merely rejects GET/HEAD eventually can still be observably wrong if it checks after body extraction or after disturbed/locked-body rejection.

### Bun implementation map at `52bf09cb…`

Primary file: `src/runtime/webcore/Request.rs`.

The constructor currently:

1. starts with method GET and body `Null`;
2. processes `init` and then `input` through `values_to_try`;
3. reads body-like fields during object processing;
4. parses method during that same processing;
5. special-cases pristine direct `Request` wrappers for internal body copying;
6. validates the URL and returns the constructed Request;
7. contains no constructor-level GET/HEAD + body rejection.

A body supplied as a `ReadableStream` can therefore reach body-extraction checks before the constructor has a Fetch-compatible GET/HEAD body guard. The absence is also visible in the test map: existing `fetch.test.ts` covers invalid `Request` URLs and broad fetch behavior, Deno-derived `request.test.ts` covers POST body construction and clone behavior, and body tests cover consumption/clone semantics; this scout found no current constructor regression covering the required GET/HEAD precedence matrix.

Relevant files:

- `src/runtime/webcore/Request.rs`
- `src/runtime/webcore/Body.rs`
- `src/runtime/webcore/fetch.rs`
- `test/js/web/fetch/fetch.test.ts`
- `test/js/web/fetch/body.test.ts`
- `test/js/web/fetch/body-clone.test.ts`
- `test/js/web/fetch/body-mixin-errors.test.ts`
- `test/js/deno/fetch/request.test.ts`

### #37033 overlap

RoboBun PR [#37033](https://redirect.github.com/oven-sh/bun/pull/37033), currently open during this scout, repairs a neighboring constructor defect: `new Request(request)` should copy internal Request state rather than consult observable getters, and inherited body use needs correct unusable-body handling.

Its description explicitly calls out the GET/HEAD precedence case as separate work. It records that Node reports the GET/HEAD-body error before the used-body error, while Bun currently lacks the constructor-level check. That PR intentionally pins Bun's current precedence for its own scope.

This creates a clean sequencing rule:

```text
#37033: make Request-input state/body inheritance correct
                     ↓
#709 follow-up: enforce GET/HEAD body invariant at the Fetch-defined point
```

A patch authored directly against current `main` risks duplicating or conflicting with #37033's new input-body bookkeeping. A regression can be prepared now and the final implementation can stack after or rebase onto the settled #37033 code.

### Minimal repair thesis

After the constructor has the final method and knows whether a non-null `init.body` or inherited `inputBody` exists, reject GET/HEAD before:

- extracting `init.body`;
- testing stream/keepalive combinations;
- rejecting disturbed/locked inherited bodies.

Keep URL parsing earlier, matching the control where malformed URL wins over GET/HEAD body invalidity.

This scout deliberately does not prepare production code because #37033 is modifying the exact internal-body path. It does prepare `candidate-tests/request-get-head-precedence.test.ts` as `target-test-prepared` evidence.

### Recommendation

**PREPARE-ONLY**, then **PURSUE** after #37033 lands or its final constructor body model becomes stable.

Reason: high-confidence compatibility defect, crisp oracle, small behavioral boundary, excellent deterministic regression, active adjacent ownership that should settle first.

## Thread B — original builtin specifier fidelity

### Plain-language result

Bun needs two pieces of information for a builtin import:

```text
what the author wrote      semantic builtin identity
       "http"        →          node:http
```

Some APIs are supposed to answer the semantic question. `import.meta.resolve("http")` belongs there, and Node returns `node:http`.

Other APIs observe source or loader activity. Node's loader resolve hook receives the exact spellings `http` and `node:http` separately. RoboBun #32628 reports that Node 26's `module.import` diagnostics event likewise publishes the literal specifier. Bun currently discards that distinction early by replacing the import record path text itself.

### Earliest rewrite found

The hardcoded builtin alias table in `src/resolve_builtins/HardcodedModule.rs` registers both bare and prefixed Node builtins. The bare entry for `http` points at canonical target `node:http`.

Then `src/jsc/RuntimeTranspilerStore.rs` walks parsed import records and performs the destructive rewrite:

```text
parse source
   ↓
import_record.path.text == "http"
   ↓
HardcodedAlias::get(...)
   ↓
import_record.path.text = replacement.path   // "node:http"
   ↓
downstream runtime loader / observer sees canonical spelling
```

That is earlier than the diagnostics publication described by RoboBun #32628. Fixing diagnostics alone would paper over source information already lost upstream.

### Separate resolver normalization

`src/resolver/resolver.rs` independently recognizes hardcoded aliases. For Bun targets / builtin-external resolution it sets the resolved path to `alias.path`, which is the canonical builtin path. This is a semantic resolver operation and should remain free to return `node:http` where the API's contract is resolution.

Relevant files:

- `src/resolve_builtins/HardcodedModule.rs`
- `src/resolve_builtins/node_builtins.rs`
- `src/jsc/RuntimeTranspilerStore.rs`
- `src/resolver/resolver.rs`
- `src/jsc/bindings/ImportMetaObject.cpp`
- module-loader / diagnostics additions in RoboBun #32628

### Node surface matrix

Executed locally on Node `v22.16.0`; retained in `probes/builtin-specifier-node.mjs`, `probes/builtin-loader-hook-node.mjs`, and `results/node-controls.md`.

| Surface | `"http"` | `"node:http"` | Interpretation |
| --- | --- | --- | --- |
| `import.meta.resolve()` | `node:http` | `node:http` | semantic canonicalization |
| ESM loader `resolve(specifier, …)` input | `http` | `node:http` | preserves written specifier |
| `require.resolve()` | `http` | `node:http` | preserves caller spelling |
| `Module.isBuiltin()` | true | true | identity accepts both |
| `require("http") === require("node:http")` | true | true | same module identity |

Node 22 predates the exact `module.import` diagnostics event used by #32628. RoboBun #32628 compares that event against Node 26.3.0 and reports Node publishes literal `http` while Bun publishes `node:http` after the transpiler rewrite.

### Policy boundary

The evidence argues against one global rule such as “always preserve bare spelling” or “always canonicalize.” The observed contract is surface-dependent:

- semantic resolution can canonicalize;
- source/loader/diagnostic observation should retain the specifier that entered that boundary;
- module identity can treat both spellings as the same builtin.

A narrow design therefore needs to carry original spelling separately from canonical builtin identity. Possible implementation forms include retaining the parsed path text and attaching a builtin-resolution tag/target, or storing an original-specifier field before alias replacement. The smallest viable option depends on how #32628's module import hook consumes the record after review.

### Plugin / loader surface status

The runtime transpiler rewrite proves that any observer consuming the mutated runtime import record after that stage can receive canonical spelling. The ordinary resolver also canonicalizes as part of resolution. This scout did not claim every Bun plugin callback receives the rewritten spelling because exact callback ordering and target execution were unavailable; that remains a follow-up discriminator for any implementation candidate.

### #32628 overlap

RoboBun PR [#32628](https://redirect.github.com/oven-sh/bun/pull/32628) is open and introduces/expands the diagnostics machinery where the literal-specifier difference is directly observable. The PR explicitly lists the `module.import` literal URL test as a known gap and says the channel itself works.

The fidelity repair is technically adjacent but conceptually independent: the problem begins in import-record aliasing, before diagnostics. Still, implementing against a moving loader/diagnostics branch would create unnecessary overlap.

### Recommendation

**PREPARE-ONLY**.

Retain the source map and Node controls. Re-run against the settled #32628 loader path, then prepare a candidate only if original spelling can be preserved without changing semantic resolver results such as `import.meta.resolve("http") === "node:http"`.

## Thread C — RoboBun breadcrumb miner

### Method

Recent open RoboBun Bun PR descriptions were searched for explicit deferred-language cues including `known gap`, `known limitation`, `follow-up`, `out of scope`, `predates`, `not included`, and related wording. Plausible findings were checked against current source and current open Bun issues/PRs where their cost justified deeper work.

The useful property of these descriptions is that they often include a reduced reproduction, exact owning code, and a sentence saying what the current PR deliberately leaves behind. The danger is equally clear: many breadcrumbs already have an owner elsewhere. The miner therefore treats every breadcrumb as a lead, never as available work by default.

### Strongest independent survivor: literal-IP synchronous `Bun.connect` error

RoboBun PR [#37093](https://redirect.github.com/oven-sh/bun/pull/37093) fixes several places where connect failures lose errno fidelity. It explicitly leaves one case:

> a literal-IP connect that fails synchronously surfaces as a generic `FailedToOpenSocket`; the errno reaches the Rust boundary but is not carried into the thrown error.

Current Bun `52bf09cb…` still contains the generic conversion in `src/runtime/socket/socket_body.rs`: when the literal-host connect call returns `uws::ConnectResult::Failed`, the JS-facing path immediately returns `crate::Error::FailedToOpenSocket`.

The return model itself is a clue: `ConnectResult` distinguishes success/socket from failure, while this caller has no errno payload available in the failure arm. A repair likely needs to preserve error identity across the uSockets/Rust boundary instead of inventing a better string at the final throw site.

Overlap search during this scout:

- open PR search for `FailedToOpenSocket` found #37093 and unrelated fetch/TLS work;
- open issue search for `FailedToOpenSocket` + literal wording found no separate owner for this exact case;
- #37093 itself declares the case out of scope.

Evidence limit: runtime reproduction on pinned Bun remains unexecuted here. Current source confirms the generic failure mapping survives on main; #37093 supplies prior reported runtime context.

**Recommendation: PURSUE in a follow-up with exact Bun execution.** It is compact enough to warrant a targeted probe once a pinned Bun build is available. It ranks below Thread A in this scout because Thread A already has an executed reference matrix and a normative ordering oracle.

### Attractive breadcrumb rejected: WebCrypto `SyntaxError` identity

A recent RoboBun description called out WebCrypto usage-validation errors becoming native JS `SyntaxError` instead of `DOMException` named `SyntaxError`. That is real-looking and deterministic, but open RoboBun PR [#35507](https://redirect.github.com/oven-sh/bun/pull/35507) already owns exactly this repair across WebCrypto and WebSocket call sites.

**Disposition: DROP as duplicate / occupied.**

### Other breadcrumb dispositions

These were useful enough to record, yet weaker than the top three candidates or visibly occupied:

| Breadcrumb | Disposition | Reason |
| --- | --- | --- |
| macOS late-writer FIFO `Bun.file(...).text()/bytes()/json()` follow-up from #37090 | **PARK** | platform-specific; current worker cannot execute the required macOS target path |
| N-API async-work completion during terminate path | **DROP/PARK** | coupled to active general shutdown-gate work; high overlap risk |
| leading `--env-file` accepted on install-family command but env file not loaded | **PARK** | deterministic-looking CLI seam, but lower consequence/priority than A/B and current network/package-manager execution is unavailable here |
| async-stack omission for Promise combinators / module TLA | **PARK** | WebKit/JSC-scale implementation boundary, high implementation cost |
| `AggregateError` reached through `.cause` omits `.errors` in Bun error rendering | **PARK** | adjacent active error-rendering work and higher overlap risk than the retained candidates |
| JSON resolved-to-`.json` specifier identity gap | **PARK** | wider loader/JSC identity work, similar policy breadth to Thread B with weaker local controls |
| TLS 1.3 post-handshake fatal alert | **DROP** | explicitly tied to existing owner/work in the breadcrumb |
| STARTTLS / `upgradeDuplexToTLS` sibling path | **DROP** | explicitly tracked by its own existing Bun work |
| template-tag parser state follow-up | **DROP** | depends on another active parser PR introducing the relevant state |

This table is intentionally conservative. A RoboBun sentence that says “follow-up” is valuable reconnaissance; it does not erase the need for current ownership and evidence checks.

## Ranked actionable candidates across all three threads

| Rank | Candidate | Repro / oracle | Local executability | Implementation size | Overlap risk | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `Request` GET/HEAD constructor body + precedence | excellent: Fetch + Node/undici + local matrix | Node control executed; Bun target unavailable | likely small after #37033 | medium, explicit adjacent #37033 | **PREPARE-ONLY → PURSUE after #37033** |
| 2 | Preserve original bare builtin spelling on observer surfaces | strong: Node loader + Node `import.meta.resolve`; #32628 Node 26 diagnostic oracle | Node controls executed; Bun target unavailable | medium; representation/pipeline choice | medium-high while #32628 is open | **PREPARE-ONLY** |
| 3 | Literal-IP synchronous `Bun.connect` errno fidelity | strong breadcrumb, source-current; Node/net errno principle available | exact Bun run unavailable | likely small-to-medium across FFI result boundary | low current ownership found | **PURSUE with target execution** |
| 4 | macOS late-writer FIFO behavior | strong platform-specific fixture | unavailable on this worker | medium | active adjacent PR | **PARK** |
| 5 | install-family leading `--env-file` load gap | likely deterministic | package-manager target run unavailable | likely small | unknown after shallow pass | **PARK** |

## Evidence classification

| Material claim | Evidence class | Limit |
| --- | --- | --- |
| Bun current `Request.rs` lacks constructor GET/HEAD-body guard | `source-read` | exact pinned source; no Bun execution receipt |
| Bun current constructor reads body/init state in an order that can precede any GET/HEAD guard | `source-read` | source ordering |
| Node 22.16.0 produces the retained Request error matrix | `model-executed` | reference runtime, not Bun |
| WHATWG constructor puts GET/HEAD body check before body extraction and unusable-input rejection | normative source | retrieved current Fetch Standard |
| Node vendored undici follows that order | `source-read` | Node source at exact comparison revision |
| #37033 is active adjacent ownership and explicitly leaves this precedence gap | `source-read` of upstream PR | upstream-reported state; can change |
| candidate Request regression exists | `target-test-prepared` | unexecuted on Bun |
| Bun hardcoded alias maps bare `http` to canonical `node:http` | `source-read` | exact pinned source |
| runtime transpiler overwrites import-record path text with alias target | `source-read` | proves source spelling loss at that stage |
| Bun resolver separately canonicalizes hardcoded alias results | `source-read` | semantic resolver path |
| Node loader hook receives bare and prefixed spellings distinctly | `model-executed` | Node 22 loader API |
| Node `import.meta.resolve("http")` returns `node:http` | `model-executed` | Node 22 |
| Node 26 `module.import` reports literal `http` per #32628 | upstream-reported source | direct local Node 26 execution unavailable |
| current `Bun.connect` failure arm returns generic `FailedToOpenSocket` | `source-read` | exact pinned source |
| literal-IP synchronous runtime path still exhibits the breadcrumb end-to-end | `source-read` + upstream-reported | target execution required before promotion |
| WebCrypto DOMException lead is occupied by #35507 | `source-read` of current open PR | ownership can change |

## Negative results and boundaries

- No production patch is prepared for Thread A because #37033 is actively changing the exact Request-input/body path needed for a correct implementation.
- No diagnostics-only patch is prepared for Thread B because the earliest spelling loss occurs in the runtime transpiler.
- No claim is made that every Bun plugin callback sees `node:http`; callback ordering needs a focused source/execution pass before widening that statement.
- No `target-executed` claim appears in this scout. Exact-current Bun execution was unavailable.
- The breadcrumb miner discarded occupied ideas even when they looked easy or attractive. WebCrypto DOMException identity is the clearest example.
- Fieldwork exclusions #345, #457, and #705/#706 were respected; none of their occupied Bun topics were selected.

## Retained artifacts

- `report.md` — this report
- `probes/request-constructor-node.mjs` — Node/undici Request ordering control
- `probes/builtin-specifier-node.mjs` — Node builtin resolution/identity control
- `probes/builtin-loader-hook-node.mjs` — Node loader source-spelling control
- `results/node-controls.md` — retained execution observations
- `candidate-tests/request-get-head-precedence.test.ts` — prepared Bun regression candidate, unexecuted

## Recommended next actions

1. Watch #37033 only as coordination state; after it lands or stabilizes, replay the prepared Request regression on its settled constructor path and implement the guard at the Fetch-defined ordering point if the regression still fails.
2. After #32628's loader/diagnostics work settles, run a focused Bun observer matrix for `import("http")`, `import("node:http")`, `require`, plugin/loader callbacks, diagnostics, `import.meta.resolve`, and error reporting. Preserve semantic canonicalization controls while testing source spelling.
3. In a Bun-capable exact-source environment, reproduce #37093's literal-IP synchronous failure and determine whether the narrow repair belongs in `ConnectResult`/uSockets error transport or a sibling result type. Stop if another current owner appears.
4. Keep the occupied breadcrumb ledger in this report so future RoboBun mining starts with duplicate elimination instead of rediscovering the same attractive leads.

## Handoff state

State: `ready-for-synthesis`

Strongest finding: Bun's `Request` constructor at `52bf09cb…` lacks the Fetch/Node GET/HEAD body invariant, and compatibility depends on placing the check before body extraction and unusable-input rejection. The regression is prepared, while implementation should wait for adjacent #37033 to settle.

Automated upstream contact: prohibited; none attempted or performed.
