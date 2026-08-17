# SWC long-concat scaling — 2026-08-11

## In simple words

The old SWC failure where long `+` chains became very slow and then crashed around a few thousand terms does not reproduce on current source at the old scale.

On exact SWC source `6c778430811853d4feee2ab3af1473669deb7b2a`, every left-deep mixed, literal-only, and variable-only case through 4,000 generated repetitions completed with an 8 MiB stack. A balanced mixed-expression control also completed. Selected 3,000, 4,000, and 6,000 cases completed with a 32 MiB stack. No stage timed out or exited unsuccessfully.

The old mixed-variable/string failure pattern is therefore not a current defect at this tested scale. Literal-only folding is now the slowest family: at 4,000 repetitions its compressor step took about 51 ms versus about 13 ms for mixed and variable-only chains and about 8 ms for the balanced mixed control. At 6,000 repetitions with the larger stack, literal-only compression took about 140 ms versus roughly 30–40 ms for the left-deep mixed/variable families and about 20 ms for balanced mixed. That is measurable shape/content sensitivity, but the absolute cost and tested range do not justify a new optimization campaign yet.

Disposition: retain this as a target-executed negative result for the historical crash/slowdown premise. Do not open implementation work from it. Revisit only if a larger realistic input, profile, or downstream workload demonstrates consequential current cost.

## Assignment

- Worker: GPT-5.6 Sol
- Programme: `web-tooling-runtime-correctness` (#15)
- Target hub: #717
- Parent scout: #718
- Target: `target:swc`
- Exact target source: `6c778430811853d4feee2ab3af1473669deb7b2a`
- Retrieval and execution date: 2026-08-11
- Claim scope: mechanism
- Execution carrier: Fieldwork #842
- Workflow run: `31489088182`
- Job: `93771096892`
- Upstream-contact authorization: `false`

No third-party upstream mutation occurred.

## Question

Does current SWC still show the historical nonlinear slowdown or process failure on long left-deep binary `+` chains, and if a failure remains, which stage and expression shape own it?

## Why this was worth measuring

The earlier SWC scout retained this only as a performance probe because the historical report predated a targeted performance repair.

That repair identified four expensive mechanisms on deep binary expressions:

1. recursive expression visiting;
2. recursive `compress::pure::misc::remove_invalid`;
3. recursive `compress::optimize::remove_invalid_bin`;
4. recursive string/type analysis.

The repair reduced calls to several recursive helpers but explicitly left recursive AST visiting as a hard remaining cost. Later historical measurements still distinguished mixed/variable chains from literal-only chains. Current behavior therefore needed a fresh shape/stage measurement rather than another source-only guess.

## Current source map

Exact source: `6c778430811853d4feee2ab3af1473669deb7b2a`.

Relevant current paths:

- `crates/swc_ecma_minifier/src/compress/pure/mod.rs`
  - `visit_mut_expr` recursively visits expression children before local rewrites;
  - binary expressions can pass through the expression simplifier and `eval_str_addition`;
  - invalid-expression cleanup is now guarded by actual invalid children rather than applied unconditionally.
- `crates/swc_ecma_minifier/src/compress/pure/strings.rs`
  - `eval_str_addition` performs string-addition simplification and queries expression type/string values.
- `crates/swc_ecma_minifier/src/compress/optimize/mod.rs`
  - `remove_invalid_bin` remains recursive and is explicitly documented as costly on very long binary expressions, but current callers avoid unnecessary invocation.
- `crates/swc_ecma_minifier/src/compress/optimize/strings.rs`
  - string-context optimization can materialize pure string values.

This leaves two useful competing explanations before execution:

- **H1 — left-deep AST depth still owns the failure:** left-deep families should fail or degrade while balanced expressions remain healthy, and increasing stack should move the failure boundary.
- **H2 — string-concat analysis still owns a content-specific failure:** mixed or literal families should degrade independently of equivalent variable-only tree depth.
- **H3 — the historical failure is no longer present at the reported scale:** all families and stages should complete with modest growth.

The measurements support H3 at the tested scale. They also expose a smaller literal-only cost difference worth recording without promoting it.

## Execution design

The execution carrier checked out the owned fork at the exact target source and materialized a measurement-only Rust example in the runner. No measurement source was committed to the SWC fork.

Environment:

- Ubuntu 24.04 Azure runner, x86-64;
- Rust `1.96.0-nightly`, toolchain date 2026-04-10;
- normal probe stack explicitly set to 8,192 KiB;
- extension probe stack explicitly set to 32,768 KiB;
- 30-second timeout per process.

The generated families were:

1. `mixed` — repeated variable plus string literal;
2. `literals` — repeated string literal plus string literal;
3. `vars` — repeated variable plus variable;
4. `balanced_mixed` — the same mixed terms arranged into a balanced parenthesized tree instead of the parser's ordinary left-deep chain.

Each normal case was split into four stages:

- `parse` — parse only;
- `prepare` — parse, resolver, and parenthesis removal;
- `compress` — preparation plus SWC compression, without mangling or emission;
- `full` — compression plus top-level mangling, fixer, and code generation.

Normal sizes: 100, 500, 1,000, 1,500, 2,000, 2,500, 3,000, and 4,000 repetitions at 8 MiB stack.

Extension sizes: 3,000, 4,000, and 6,000 repetitions for `compress` and `full` at 32 MiB stack.

The runner retained process status, external wall time, maximum resident set size, internal stage timings, output size, environment identity, and raw logs.

Evidence class: `target-executed`.

## Result

### Process outcome

All 152 measured processes exited with status `0`.

At 8 MiB stack:

- every family passed every stage through size 4,000;
- no parse-only or preparation failure appeared;
- no compression-only failure appeared;
- no additional full/minify failure appeared.

At 32 MiB stack:

- selected compression and full cases passed through size 6,000 for all four families.

Because the 8 MiB series never reached a failure, the larger-stack extension does **not** establish that additional stack fixes anything. It only extends the observed-success range. A stack-sensitive current defect was not demonstrated.

### Compressor timing

Internal compressor time in milliseconds:

| repetitions | balanced mixed | literal-only | mixed | variables |
| ---: | ---: | ---: | ---: | ---: |
| 100 | 0.57 | 0.58 | 0.56 | 0.52 |
| 500 | 1.14 | 1.92 | 2.32 | 2.41 |
| 1,000 | 2.14 | 6.95 | 3.93 | 4.17 |
| 1,500 | 2.87 | 12.07 | 7.74 | 7.01 |
| 2,000 | 4.40 | 18.00 | 8.42 | 5.61 |
| 2,500 | 7.19 | 22.08 | 8.27 | 6.79 |
| 3,000 | 8.67 | 31.58 | 9.37 | 11.46 |
| 4,000 | 7.78 | 51.47 | 12.86 | 12.91 |

The 32 MiB extension at size 6,000 recorded approximately:

- balanced mixed: 20 ms;
- literal-only: 140 ms;
- mixed: 30 ms;
- variables: 40 ms.

The timings are single-run measurements and small enough that scheduler noise is visible, so they should not be treated as a benchmark-quality complexity fit. They are sufficient to distinguish the old seconds-plus/crash behavior from current behavior at the same order of input size.

### Memory

At 8 MiB stack and size 4,000, maximum RSS was approximately:

- balanced mixed: 16 MiB;
- mixed: 19 MiB compressor-only / 21 MiB full;
- variables: 19 MiB compressor-only / 21 MiB full;
- literal-only: 24 MiB.

At size 6,000 with the 32 MiB stack, maximum RSS remained below about 30 MiB for the measured processes.

No runaway memory pattern was demonstrated in this range.

## Interpretation

### Established

**Observed:** the historical crash threshold does not reproduce on current source through 4,000 repetitions with an 8 MiB stack.

**Observed:** the historical mixed variable/string family is not uniquely pathological in current measurements. Mixed and variable-only compression are similar at the upper normal sizes, while the balanced mixed control is generally cheaper.

**Observed:** literal-only left-deep chains cost substantially more compressor time than the other families at 3,000–6,000 repetitions.

### Inferred

The literal-only result is consistent with cumulative work while folding progressively larger constant strings, but this probe did not profile allocations or individual functions. It therefore does not assign the extra cost to `eval_str_addition`, expression simplification, string materialization, or another helper.

The balanced control being cheaper supports tree depth as one contributor to ordinary traversal cost, but there is no current failure to attribute to depth.

### Not established

This probe does not establish:

- asymptotic complexity from benchmark-quality repeated samples;
- behavior at tens or hundreds of thousands of terms;
- behavior on a different operating system, native Node binding, or smaller thread stack;
- an ecosystem or production consequence;
- that literal-only scaling is worth changing.

## Negative result and stop condition

The scout's stop condition was to stop implementation work if current growth was ordinary and the historical crash did not reproduce.

That condition is met for the old reported scale.

Do **not** create a repair branch from the historical issue on this evidence. The current source has moved the old failure boundary beyond the tested range and reduced the relevant workload from historical seconds/process failure to tens of milliseconds in the mixed/variable cases.

The literal-only cost should remain a note, not a campaign. Reopen only if one of these occurs:

1. a realistic generated workload reaches a materially larger chain and shows consequential latency or memory cost;
2. a repeated benchmark demonstrates clearly superlinear scaling with a useful optimization target;
3. profiling identifies avoidable repeated string materialization or traversal with a bounded repair;
4. current source fails at a reachable size under a declared stack/runtime configuration.

## Adjacent source note: unary effects

The original scout retained unary coercion as a separate semantics lead. Current source search still places shared expression-effect classification in `swc_ecma_utils` and several consumers in minifier/optimization code, but this continuation did not promote or patch that lead. The previous language-level probe is not enough by itself; the next useful step would be the same discipline learned from `instanceof`: identify a concrete destructive consumer, compare against SWC/Terser policy, and execute a target-native discriminator before proposing a global purity change.

Disposition: retained lead only.

## Handoff

Strongest supported finding: current SWC no longer reproduces the historical long mixed-concat crash/slowdown at the previously interesting few-thousand-term scale.

Retained artifact: this report plus execution receipt from Fieldwork carrier #842, run `31489088182`, job `93771096892`.

Failed/retired hypothesis: mixed variable/string concatenation remains a current special crash trigger around 2,000–4,000 repetitions.

Unresolved uncertainty: larger literal-only left-deep chains show measurably higher compression cost, but no consequential boundary or owning function has been established.

Recommendation: close the performance probe as a negative result for now and spend SWC research effort on the already-target-proven semantic/recovery campaigns or a newly bounded source-backed question.

Automated upstream contact remained prohibited and no third-party upstream mutation occurred.
