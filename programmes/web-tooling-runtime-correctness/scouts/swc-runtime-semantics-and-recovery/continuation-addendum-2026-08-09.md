# SWC continuation addendum — 2026-08-09

## In simple words

The next research sweep produced one target-executed negative result, one sharper mapped-`arguments` discriminator now running, one parser source defect candidate, and two deliberate non-branches where target policy or active upstream ownership already answers the coordination question.

Function-local strict-directive issue #9238 does not reproduce under the isolated current `directives` compressor pass: pinned SWC retained the directive and preserved sloppy/strict `arguments` behavior. That carrier is retired with a durable receipt.

Open issue #12032 initially looked like the next aliasing defect, but its published configuration is an ES module. JavaScript modules are strict, so its stated expectation that a parameter assignment should update `arguments[0]` is not valid in module semantics. A new execution-only probe removes that ambiguity by comparing an ordinary sloppy function with an otherwise identical function-local strict control under current default compression.

The parser sweep found an unusually direct source candidate for JSX surrogate numeric entities: `read_jsx_entity` still converts numeric entity values with `char::from_u32(...).expect(...)`, accompanied by a TODO to replace the unwrap with an error. Surrogate code units are outside Rust `char`'s scalar-value domain, which directly explains the panic reported by #11802. This deserves a no-panic parser discriminator after the mapped-arguments probe resolves.

Resolver issue #11607 has active upstream ownership in open PR #11872 against the same current base, so Fieldwork will observe rather than duplicate that implementation. `with`-statement issue #9856 is similarly held as a policy/documentation seam because maintainers explicitly said they prefer to assume `with` is absent even though current optimizer code carries `InWithStmt` context in several paths.

No third-party upstream mutation occurred.

## 1. Strict directive / `arguments` — target-executed negative

Execution carrier: `teamleaderleo/fieldwork#764`  
Carrier head: `a5ec3b004c68eceed10cf5cf272a875131a1928b`  
Workflow run: `31291282856`  
Job: `93188782308`  
Pinned SWC: `5bf27fd72e4667bac6cc86888b8facb8b91f8077`

The temporary fixture used only:

```json
{
  "defaults": false,
  "directives": true
}
```

and compared:

```js
function sloppy(o) {
    o = 1;
    return [o, arguments[0]];
}

function strict(o) {
    "use strict";
    o = 1;
    return [o, arguments[0]];
}
```

Runtime oracle:

```text
1,1
1,0
```

Both snapshot generation and the second no-UPDATE fixture run passed. Generated output retained:

```js
function strict(o) {
    "use strict";
    ...
}
```

The carrier explicitly found the directive at generated-output line 9.

Evidence class: `target-executed` negative discriminator.

Exact receipt: `strict-arguments-probe-2026-08-09.md`.

Disposition: **RETIRE #9238 as a minimal current-path lead.** Broader historical configurations can be revisited only if current evidence reproduces a runtime mismatch.

## 2. Open #12032 — distinguish sloppy mapped arguments from module strictness

Upstream issue #12032 reports:

```js
function run(f) {
    f();
}

function foo(b) {
    run(() => {
        b = 2;
    });
    console.log(arguments[0]);
}

foo(1);
```

with expected `2` and actual `1`.

The published configuration sets `isModule: true` and ES module output. That is a semantic complication: ES module code is strict, so simple parameters are not mapped to the `arguments` object.

A dependency-free Node mechanism probe confirmed the distinction:

```text
script/sloppy:  b becomes 2, arguments[0] becomes 2
module/strict:  b becomes 2, arguments[0] remains 1
```

Evidence class: `model-executed`.

Current minifier source initializes `ExprCtx.in_strict` from the compressor's `options.module`, confirming that module mode is a first-class semantic input to optimizer reasoning.

### Source hypothesis for a genuine sloppy bug

The usage analyzer does see both relevant pieces:

- assignment to the outer parameter `b` inside the nested arrow;
- an identifier use named `arguments`, which calls `scope.mark_used_arguments()`.

What is not obvious in the analyzed source is an explicit dependency edge that says: in a sloppy function with a simple parameter list, `arguments[0]` aliases the first parameter, so writes to that parameter remain observable through the `arguments` object.

That implicit alias is a plausible missing relation for default unused/reduction logic. The dedicated `optimize_usage_of_arguments` pass is gated behind the separate `arguments` compressor option and is not assumed to own the reported default-compression behavior.

### Current target probe

Fieldwork carrier `teamleaderleo/fieldwork#765`, head `2581d9c1627ecea8af0cca1ff0d7ec14ef7446f4`, is running an unambiguous script fixture under `{ "defaults": true }`:

```js
function run(f) {
    f();
}

function sloppy(b) {
    run(() => { b = 2; });
    return arguments[0];
}

function strict(b) {
    "use strict";
    run(() => { b = 2; });
    return arguments[0];
}

console.log(sloppy(1), strict(1));
```

Runtime oracle:

```text
2 1
```

Interpretation:

- `1 1` would reproduce a real sloppy mapped-arguments optimizer defect independently of the issue's module configuration;
- `2 1` would show that the core sloppy/strict distinction is correct on current default compression and make the upstream issue primarily a mode/configuration question.

Evidence remains `target-test-running` until the job is inspected; do not upgrade it yet.

## 3. JSX numeric surrogate entity panic — strong parser source candidate

Open upstream issue #11802 reports `RuntimeError: unreachable` while parsing JSX containing numeric entities such as:

```text
&#xD83E;&#xDD80;
```

Current pinned parser source still contains:

```rust
fn from_code(s: &str, radix: u32) -> LexResult<char> {
    // TODO(kdy1): unwrap -> Err
    let c = char::from_u32(
        u32::from_str_radix(s, radix).expect("failed to parse string as number"),
    )
    .expect("failed to parse number as char");

    Ok(c)
}
```

Rust `char` represents Unicode scalar values and excludes surrogate code units `0xD800..=0xDFFF`. Therefore a numeric JSX entity representing `0xD83E` reaches a value for which `char::from_u32` returns `None`, and the current `expect` can panic.

The surrounding lexer already has explicit `UnicodeEscape::LoneSurrogate` support for JavaScript escape handling, so this is specifically an entity-decoding boundary rather than a repository-wide inability to represent WTF-8/surrogates.

### Required discriminator

Prepare a parser-only target test with:

1. valid scalar numeric entity control, e.g. `&#x1F980;`;
2. high-surrogate numeric entity `&#xD83E;`;
3. low-surrogate numeric entity `&#xDD80;`;
4. paired consecutive JSX entities, matching the report;
5. out-of-range numeric entity above `0x10FFFF`.

The first invariant is **no panic**. The follow-up semantic decision is whether surrogate-pair entities should combine into one scalar, be preserved through WTF-8, or produce a syntax error; that should be settled from JSX/HTML entity semantics and project precedent before implementation.

Disposition: **HIGH-PRIORITY parser discriminator after #765 resolves.**

Evidence now: `source-read`; upstream historical reproduction at 1.15.26; current target execution pending.

## 4. Resolver namespace re-open #11607 — active upstream ownership

Issue #11607 is open, but upstream PR #11872 is also open against current base `5bf27fd...` and explicitly says it closes #11607 / unblocks #11514.

The PR identifies the mechanism as fresh resolver scopes for each re-opened TypeScript namespace body. Its proposed repair caches merged namespace-body scope state keyed by `(parent_scope.mark, namespace_name)`, allowing later namespace declarations to see earlier bindings.

The PR reports a new exact repro fixture and the full `swc_ecma_transforms_base` suite passing.

Disposition: **OBSERVE ONLY.** Do not create a competing owned-fork implementation while a concrete upstream PR has active review ownership. Fieldwork may revisit only if that PR stalls/rejects or exposes a distinct uncovered invariant.

## 5. `with` statement optimization #9856 — policy/documentation seam

The issue reports optimization behavior affected by `with` dynamic name lookup. Maintainer discussion says they would prefer to assume `with` is not used, and the reporter accepted that policy direction.

Current source nevertheless contains an `InWithStmt` optimizer context flag in multiple files, showing that SWC partially models the construct even while maintainers may decline full semantic guarantees.

Disposition: **DO NOT PROMOTE AS CODE DEFECT.** Retain as a policy/documentation seam: future findings involving `with` need an explicit support-policy decision before implementation work.

## Updated ranking

1. Finish `instanceof` exact-candidate GREEN when a safe narrow source-head write path is available.
2. Inspect mapped-arguments carrier #765 and either promote a genuine sloppy aliasing defect or retire #12032 as mode-confused/currently-correct.
3. Run the JSX surrogate-entity no-panic parser discriminator.
4. Obtain Wasmtime cache target execution when a clean execution carrier transition is available.
5. Run current-revision mixed-concat size series before any performance implementation work.
6. Observe resolver PR #11872; no competing branch.
7. Keep arbitrary-depth parser and `with` findings policy-bounded.
