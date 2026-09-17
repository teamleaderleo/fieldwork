# Postmortem: SWC remote-first validation loop

Date: 2026-08-10  
Status: process lesson recorded; upstream pull request remains an open draft

Upstream pull request:  
https://redirect.github.com/swc-project/swc/pull/12110

Reviewed candidate head:  
`a8ee1a6def602867739fc4427b992f90c9bfefe5`

## In simple words

The SWC `instanceof` correction had a sound semantic thesis: an optimizer must preserve the operator when it can invoke `Symbol.hasInstance`, throw because of an invalid right operand, or produce a result that operand types alone cannot prove.

The painful part came afterward. Fieldwork treated remote GitHub CI as the inner development loop. Several deterministic repository checks therefore arrived one push at a time: test-placement policy, a DCE fixture whose enclosing functions were themselves removable, downstream TSC golden outputs, and a minifier size baseline.

A complete local checkout plus the owning test targets would have exposed nearly all of this before the first review cycle. The reusable rule is simple: use source and AST reasoning to design the change, then use the target repository's own local harnesses to discover every consequence before pushing.

## Work class and evidence

Work class: upstream-fork research with an already-existing human-performed upstream submission.

- **Observed — semantic defect:** SWC could erase or fold complete `instanceof` evaluations even though the operator can invoke user code, throw, or return a value that operand categories do not establish.
- **Observed — repository feedback:** the same candidate changed optimizer fixtures, TSC minified references, and the minifier size table.
- **Observed — platform behavior:** Linux, macOS, and Windows reported the same four TSC reference mismatches, showing one deterministic golden-output change rather than separate platform defects.
- **Inferred — local prevention:** the owning optimizer fixture target and downstream TSC target would have produced these failures on one local checkout before the candidate was pushed.
- **Boundary:** this postmortem records the validation-loop failure. It does not claim the entire SWC CI matrix can be reproduced economically on one workstation.

Automated upstream contact remained prohibited. Fieldwork records an upstream pull request created and updated by the human submitter.

## Failure sequence

### 1. Repository policy arrived through review

The first regression coverage used an ad-hoc Rust test module. SWC's repository instructions explicitly direct new coverage into the existing fixture suites. Reading the nearest `AGENTS.md` before implementation would have selected the correct test owner immediately.

An IDE could help navigate the AST types and fixture harness. The repository instruction supplied the decisive placement rule.

### 2. The first DCE fixture deleted its own test container

The replacement fixture wrapped each unused local in an unreferenced top-level function. DCE correctly removed the entire functions, leaving empty output. Exporting the functions retained the containers while allowing DCE to optimize the unused locals inside them.

This was a fixture-design error. The focused optimizer fixture target would have reported it locally:

```sh
cargo test -p swc_ecma_transforms_optimization --test fixture
```

### 3. Downstream TSC references still encoded the old optimizer behavior

Four `.2.minified.js` reference files expected SWC to discard or reduce the affected `instanceof` expressions. The corrected optimizer preserved those expressions, so the golden outputs needed intentional updates.

Every operating-system job found the same four mismatches. One local downstream target would have enumerated the complete set:

```sh
cargo test -p swc --test tsc
```

The upstream pull-request validation list covered the optimization and minifier crates but omitted this downstream consumer target. That gap let a predictable output change reach the OS matrix.

### 4. The minifier benchmark reference moved

Preserving an additional operator changed the displayed Terser compressed and gzip results by `0.01 KiB`. The source behavior was expected; the checked-in size table still required an intentional reference update through its repository-owned script.

## Root cause

Fieldwork had enough source information to reason about the AST change and too little local repository feedback to finish the candidate coherently.

The workflow looked like this:

```text
inspect remote source
      ↓
edit owned fork
      ↓
push
      ↓
wait for broad CI or review
      ↓
discover one local consequence
      ↓
rewrite and push again
```

That loop delegated ordinary development feedback to a remote matrix. CI then acted as an expensive fixture runner and golden-file enumerator.

The better loop is:

```text
full local checkout at exact candidate base
      ↓
read repository instructions and locate test owners
      ↓
implement the smallest semantic change
      ↓
run focused owner test
      ↓
run downstream output consumers
      ↓
inspect intentional golden and size differences
      ↓
push one coherent candidate
      ↓
use CI for platform, feature, and integration breadth
```

## What an IDE provides and misses

An IDE would improve navigation through `Expr`, `BinExpr`, effect analysis, simplifier call sites, and references to `instanceof` handling. It could reveal multiple owners of the same semantic decision.

The IDE alone would rarely infer all of these repository facts:

- SWC requires fixture-suite placement for this coverage;
- unexported fixture functions disappear under DCE;
- the `swc` TSC harness consumes optimizer output through checked-in references;
- a benchmark table is a reviewed generated artifact;
- each changed output is intentional under the semantic correction.

Repository search, contribution instructions, and executable harnesses answer those questions. AST navigation and tests serve different jobs.

## Preventive rule

For compiler, bundler, formatter, parser, code-generator, and minifier work, Fieldwork will use a complete local checkout before the first candidate push whenever the target can be built locally.

The pre-push gate is:

1. Read the target's nearest agent and contribution instructions.
2. Map the implementation owner, test owner, generated-output consumers, snapshots, benchmarks, and size references touched by the behavior.
3. Run the smallest discriminating test while iterating.
4. Run the complete owning test target before pushing.
5. When emitted text or AST output changes, run downstream golden and snapshot suites and review every difference.
6. Run repository-owned generators for intentional references; avoid hand-approving unexplained output.
7. Run the relevant format, lint, and size gates.
8. Push only after the local gate is clean or after recording a concrete local execution blocker.
9. Let CI cover the remaining operating systems, feature combinations, and expensive integrations.

Remote-only editing remains appropriate for tiny repository-file changes whose validation is fully visible. A cross-crate compiler semantics repair requires the local target harness.

## Durable lesson

Correct AST reasoning selects the repair. The local repository harness reveals the repair's full review surface.

Use CI as the final breadth check. Use the local checkout as the development loop.
