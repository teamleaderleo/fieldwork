# SWC long mixed-concat source review

## In simple words

The open long-concatenation performance issue still has a current source reason to investigate after the 2025 speedup: SWC reduced several expensive recursive helpers, but the core recursive AST visit over a deep binary `+` tree remains.

The useful next experiment is therefore a current-revision size/depth series, with stack-depth behavior separated from repeated string/template copying. No implementation should be proposed before that measurement.

Target issue: `swc-project/swc#10219`  
Pinned/current Fieldwork target: `swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077`  
Evidence: `source-read`, historical upstream benchmark/commentary  
Upstream contact authorized: `false`

## Historical fix boundary

Merged commit `1434571477f5f8576a268a2bd32631eb9ce77229` (`perf(es/minifier): Avoid calling some costly function when optimizing deep nested binary expr (#10611)`) profiled four expensive contributors:

1. recursive expression visiting;
2. recursive `compress::pure::misc::remove_invalid`;
3. recursive `compress::optimize::remove_invalid_bin`;
4. recursive `swc_ecma_utils::is_str`.

The commit description explicitly says the recursive expression visit was hard to eliminate and that the patch only decreased calls to items 2–4. Its reported benchmark improved from 2.17s to 0.77s on that sample.

Later issue discussion says the original all-literal case became much faster, while a mixed variable/string case could still crash with a segmentation fault; the maintainer replied that the issue was not fully fixed.

## Current source boundary A — recursive binary traversal remains

Current `Pure::visit_mut_bin_expr` does:

```rust
if !Self::is_expr_leaf(&e.left) {
    self.visit_mut_expr(&mut e.left);
}
if !Self::is_expr_leaf(&e.right) {
    self.visit_mut_expr(&mut e.right);
}
...
if e.op == op!(bin, "+") {
    self.concat_tpl(&mut e.left, &mut e.right);
}
```

A normal source expression such as:

```js
x + "a" + x + "a" + x + "a"
```

is represented as nested binary additions. The pure pass recursively descends the non-leaf child before handling the current `+`, so traversal call depth grows with binary-tree depth.

This is the exact cost class the 2025 commit said it did not eliminate.

## Current source boundary B — template/string append copies accumulated text

`Pure::concat_tpl` also has an independent repeated-copy possibility. When appending a string literal to a template literal it rebuilds cooked and raw text:

```rust
let mut c = Wtf8Buf::from(&*cooked);
c.push_wtf8(&Cow::Borrowed(&rs.value));
*cooked = c.into();

l_last.raw = format!("{}{}", l_last.raw, ...).into();
```

Repeated template-plus-string folding can therefore copy already-accumulated text again. This is a different axis from recursive AST depth and should be measured separately.

The open issue's mixed variable/string reproducer may exercise primarily traversal depth, repeated copying, or both depending on the exact rewrites reached on current SWC.

## Required measurement matrix

Use one current-revision execution carrier later, after active correctness carriers retire. Keep generation deterministic and record source bytes, AST-chain count, wall time, peak RSS if available, exit status, and output size.

### Series A — mixed left-deep binary chain

Generate increasing `N` for:

```js
let out = value + "x" + value + "x" + ...;
```

Suggested sizes: 1k, 2k, 4k, 8k, 16k, then continue only while the previous run remains comfortably bounded.

Purpose: expose recursion/stack and superlinear traversal behavior without giant literal payloads.

### Series B — template/string accumulation

Generate a chain whose intermediate form reaches template-plus-string folding, with small pieces and increasing count.

Purpose: distinguish repeated accumulated-text copying from generic binary depth.

### Series C — balanced control

Generate the same number of `+` nodes as a balanced expression tree.

Purpose: hold node count roughly constant while reducing maximum recursion depth. A large left-deep/balanced gap would strongly implicate traversal depth rather than total work alone.

### Series D — literal-only historical control

Retain a smaller all-literal chain similar to the original report.

Purpose: confirm that the historical #10611 improvement still behaves differently from the mixed case on the pinned revision.

## Stop conditions

Stop size escalation on the first of:

- process crash / stack overflow / segmentation fault;
- repository or runner timeout boundary;
- memory growth that makes the next doubling unsafe for the shared runner;
- enough points to identify a clear depth-sensitive or superlinear trend.

A crash should be preserved as a bounded target receipt rather than repeated at larger sizes.

## Current disposition

**MEASURE, do not implement yet.**

The historical optimization deliberately left recursive expression traversal in place, and current source still has a depth-proportional binary visit. That is sufficient to justify a current-revision benchmark series, but not sufficient to choose a repair. The balanced-tree control is the most important discriminator because it separates recursion depth from total binary-node count.

No third-party upstream mutation occurred.
