# SWC continuation — 2026-08-09

## In simple words

This continuation moved one SWC finding from source theory to real target reproduction and sharpened two other branches without creating unnecessary implementation work.

The `instanceof` effect-analysis finding is now target-executed RED in the shared utility layer and both known extraction consumers. The candidate GREEN did not run because the temporary carrier's source-edit script was brittle; that harness failure is recorded separately from the valid target REDs.

The deep-expression resource branch split into two very different cases. Arbitrarily nested parser syntax is explicitly outside the guarantee SWC maintainers currently want to provide, so that case is a policy-bounded negative branch. The older minifier string-concatenation issue remains more interesting: maintainers identified a real time-complexity problem, a later performance change reduced several recursive costs, and subsequent reporter data still showed segmentation faults for large mixed variable/string concatenation. Current-revision behavior remains unmeasured, so this stays a bounded performance probe rather than a defect claim.

A separate open minifier issue about removing function-local `"use strict"` directives while `arguments` is observed looks like a stronger next semantics discriminator. Strict mode changes parameter/`arguments` aliasing, and that behavior is not among the minifier assumptions found during the operator campaign.

The Wasmtime cache campaign also gained stronger source precedent: the Wasmer sibling explicitly removes rejected serialized cache files, while Wasmtime currently turns rejection into a cache miss and leaves the artifact in place. Its execution carrier was prepared but remained unexecuted after a connector control-plane block.

No third-party upstream mutation occurred.

## 1. `instanceof` — target defect reproduced

Campaign: #725

Execution carrier: `teamleaderleo/fieldwork#756`

Workflow run: `31290088187`

The three exact owned-fork contracts all reached their intended Rust test assertions and failed:

- `teamleaderleo/swc#2` — shared `may_have_side_effects` / `extract_side_effects_to` contract;
- `teamleaderleo/swc#4` — expression-simplifier selected-array consumer;
- `teamleaderleo/swc#7` — minifier literal-member extraction consumer.

The shared helper classified inert-operand `instanceof` as effect-free and extracted no whole operator effect. The expression simplifier reduced invalid-RHS `instanceof` to `42` and callback-capable `instanceof` to operand evaluation. The minifier literal-member fixture reproduced the same semantic loss through the other known extractor consumer.

Evidence class for the defect claims: `target-executed` RED.

The candidate was not disproved. The carrier's runner-only exact-string patch failed after RED and before GREEN. Full details are in `campaigns/0725-swc-binary-operator-effects/execution-2026-08-09.md`.

## 2. Deep parser nesting — policy-bounded stop

Upstream issue `swc-project/swc#12024` reported stack overflow on roughly 5000 nested parentheses.

The issue was closed `not_planned`. Maintainer reasoning is explicit:

- SWC does not intend to guarantee graceful handling of arbitrarily deep syntax trees;
- recursion spans ASTs, parser, visitors, transforms and minifier, so a parser-only guard would not establish an end-to-end guarantee;
- applications needing unusually deep inputs can increase stack size;
- untrusted-input applications should apply isolation/resource limits;
- a practical real-world need would be required to revisit the policy.

Disposition: **STOP as a standalone Fieldwork defect branch.**

This is useful policy evidence for future resource investigations. A synthetic depth bomb alone does not clear the target's current bar.

Evidence class: `source-read` plus maintainer policy.

## 3. Long mixed string/binary expressions — retained performance probe

Upstream issue `swc-project/swc#10219` remains open. The reporter generated long left-associated concatenation chains and observed rapidly increasing compression time followed by segmentation faults.

A maintainer explicitly described the original problem as a time-complexity bug in string-concat logic and pointed investigators at:

- `crates/swc_ecma_minifier/src/compress/pure/strings.rs`;
- `crates/swc_ecma_minifier/src/compress/optimize/strings.rs`.

Commit `1434571477f5f8576a268a2bd32631eb9ce77229` (`perf(es/minifier): Avoid calling some costly function when optimizing deep nested binary expr`) profiled four expensive mechanisms:

1. recursive expression visiting;
2. `compress::pure::misc::remove_invalid` recursion;
3. `compress::optimize::remove_invalid_bin` recursion;
4. `swc_ecma_utils::is_str` recursion.

That change reduced one profiled case from about 2.17s to 0.77s by calling several recursive helpers less often. The commit explicitly said recursive expression visiting was especially hard to eliminate.

Later reporter data on SWC 1.12.3 showed much lower normal runtimes but still produced segmentation faults at the larger mixed cases. Pure literal-string concatenation reached the 3000-size case, while variable+string and variable+variable patterns still failed around the larger input.

Current pinned source still has recursive tree walking and string-addition transforms, including `Pure::eval_str_addition` and shared string/value analysis. Historical evidence alone cannot identify which current recursion boundary, if any, fails first.

### Required current-revision probe

Before implementation work:

1. generate left-associated size series with at least three families:
   - variable + string;
   - string + string;
   - variable + variable;
2. run parse-only, transform-with-compress-off, and compress-on stages separately;
3. record wall time, process result, output size and peak memory where available;
4. use a controlled runner stack size so stack exhaustion can be distinguished from heap growth;
5. if failure remains, bisect the pass family by minifier options or a focused Rust harness;
6. stop if current growth is ordinary and the historical crash no longer reproduces.

Disposition: **RETAIN as a performance probe, not yet a campaign.**

Evidence class: `source-read` / historical target reports; current pinned target behavior `Unknown`.

## 4. Function-local strict directive and `arguments` aliasing — next semantics candidate

Open upstream issue `swc-project/swc#9238` reports that compression can remove a function-local `"use strict"` directive even when the function observes `arguments`.

The semantic discriminator is small:

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

In sloppy mode, a simple parameter and its corresponding `arguments` entry can remain mapped. In strict mode they are not mapped. Removing only the strict directive can therefore change the returned second element after `o = 1`.

The issue remains open on the current repository. During the operator campaign, SWC's documented minifier assumptions were read carefully; no assumption was found that permits changing parameter/`arguments` synchronization by deleting a strict directive.

### Next question

Does pinned current main still remove the directive under the issue's relevant minifier configuration, and if so, which directive-removal decision lacks function-level `arguments`/parameter context?

A useful owned-fork discriminator should:

- execute both sloppy and strict functions before and after minification;
- use runtime output as the oracle;
- include a function with strict mode but no parameter/`arguments` alias dependence as the removable/control case if the optimizer intentionally removes redundant directives;
- map the directive-removal owner before proposing a repair.

Disposition: **HIGH-PRIORITY next scout lane after current campaign evidence is synchronized.**

Evidence class now: `source-read`; target current behavior unexecuted.

## 5. Nested-control-flow visitor precedent

Closed upstream issue `swc-project/swc#10885` is useful precedent even though it is already fixed.

The minifier once emitted an illegal `break` after compressing nested switches. The recorded root cause was a `BreakFinder` visitor that skipped traversal of nested `switch` statements. The fix made nested-switch traversal context-aware.

This is a recurring compiler-review lesson: AST visitor bugs often arise because a pass carries an incomplete notion of its current control-flow context across a nesting boundary. That pattern is worth checking when triaging current minifier failures involving loops, switches, labels, functions or conditional branches.

Disposition: reference pattern only; no active branch.

## 6. Wasmtime rejected-cache recovery — stronger sibling precedent, execution pending

Campaign: #719

Current Wasmtime cache loading reads the final file and returns a cache miss if `wasmtime::Module::deserialize` rejects it, leaving the file in place.

The Wasmer sibling explicitly performs best-effort `remove_file(path)` when deserialization rejects its cached module.

This narrows the Wasmtime rejected-cache candidate to a simple lifecycle parity rule: rejected serialized cache artifacts should be removed so later compilation can republish a fresh final entry.

Owned-fork PR #3 pins this expectation as a test-only discriminator. A temporary Fieldwork carrier (#761) was prepared to run both Wasmtime cache cases but remained unexecuted after a connector safety/control-plane block. No target evidence upgrade is claimed.

Disposition: keep #719 on HOLD/EXECUTE.

## Ranked next work

1. **Finish `instanceof` GREEN execution.** The defect is now target-reproduced; the highest-value next evidence is an exact owned-fork candidate head and GREEN receipts, not another theory branch.
2. **Strict directive / `arguments` semantics.** Small runtime oracle, open bug, ordinary language semantics, no discovered assumption exception.
3. **Wasmtime cache RED/GREEN.** Source evidence is strong; target execution remains the missing gate.
4. **Long mixed-concat resource series.** Current-revision measurement first; no implementation work until the failure boundary is known.
5. **Deep arbitrary syntax nesting.** Stop unless practical real-world evidence changes the target policy.

## Research discipline from this pass

Three different kinds of evidence must remain separate:

- JavaScript or filesystem semantics can establish what the mechanism *would* do;
- SWC target tests establish what the current implementation *does*;
- target policy and documented assumptions establish which differences SWC promises to preserve.

The operator campaign only became clean after all three were compared. The same rule should govern the next branches.
