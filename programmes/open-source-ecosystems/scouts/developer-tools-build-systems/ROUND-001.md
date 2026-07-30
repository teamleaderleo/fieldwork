# Developer Tools and Build Systems Scout — Round 001

Date: 2026-07-30  
Programme: [Open-Source Ecosystems](../../STATUS.md)  
Scout issue: [#210](https://github.com/teamleaderleo/fieldwork/issues/210)

## In simple words

Automatic-fix bugs are unusually productive targets because the issue can preserve source before the fix, source after the fix, and runtime behavior before and after. This round found a dense Ruff queue where several fixes alter execution, syntax, or convergence. pip also exposes resolver and integrity boundaries, though some require maintainer policy decisions before code.

## Ruff first wave

Repository: `astral-sh/ruff`

### Deep dive — RUF038 runtime mutation

Issue: [#27026](https://github.com/astral-sh/ruff/issues/27026)  
Owning file: `crates/ruff_linter/src/rules/ruff/rules/redundant_bool_literal.rs`  
Related stabilization: [PR #26919](https://github.com/astral-sh/ruff/pull/26919)

The rule documentation says it checks `Literal[True, False]` **type annotations**. The implementation receives a general `literal_expr`, traverses its members, and can replace the entire expression range with `bool` when it believes only `True` and `False` were seen.

The issue demonstrates two separate defects:

1. runtime calls such as `get_args(Literal[True, False])` are diagnosed and rewritten even though the expression is executed;
2. a mixed expression containing `values[0]` can be traversed in a way that loses the subscripted member and its evaluation.

Observed change:

```python
print(get_args(Literal[True, False]))
values = ["sentinel"]
print(get_args(Literal[True, False, values[0]]))
```

becomes runtime uses of `bool`, changing output and dropping `values[0]`.

### Likely owning boundaries

```text
crates/ruff_linter/src/rules/ruff/rules/redundant_bool_literal.rs
crates/ruff_linter/src/checkers/ast/analyze/expression.rs
RUF038 fixtures and snapshots
semantic helpers that determine annotation context
```

### First executable probe

Add fixtures covering:

- a variable annotation where replacement is permitted;
- `typing.get_args()` runtime use where no diagnostic should appear;
- a mixed `Literal[True, False, values[0]]` annotation where the rule must preserve the third member;
- postponed annotations and quoted annotations;
- nested subscripts and unions;
- a shadowed `Literal` binding.

Then trace the rule invocation to decide whether annotation context belongs at the caller or inside the rule. Keep the member traversal conservative: any unsupported member must prevent whole-expression replacement.

### Promotion signal

A focused patch should prevent runtime diagnostics, preserve all unsupported members, and retain expected annotation fixes. Because PR #26919 proposes stabilization, coordinate the regression with that review path before upstream submission.

## Other Ruff candidates

1. [#27022](https://github.com/astral-sh/ruff/issues/27022) — B006 preview fix changes the contents of a multiline string by introducing indentation. Preserve exact runtime value.
2. [#27024](https://github.com/astral-sh/ruff/issues/27024) — RUF055 is classified safe but changes bytes-regex behavior for buffer-protocol objects. Reassess fix safety or constrain the transformation.
3. [#27008](https://github.com/astral-sh/ruff/issues/27008) — PEP 695 fixes remove unpacked `TypeVar` keyword arguments.
4. [#26954](https://github.com/astral-sh/ruff/issues/26954) — PEP 695 fixes introduce syntax errors for starred constraints.
5. [#27028](https://github.com/astral-sh/ruff/issues/27028) — EXE001 treats a nested ordinary `#!` comment as a shebang.
6. [#25418](https://github.com/astral-sh/ruff/issues/25418) and [#26450](https://github.com/astral-sh/ruff/issues/26450) — conflicting lazy-import fixes fail to converge after 100 iterations.

The PEP 695 cases could form a bounded batch because they share TypeVar-to-type-parameter transformation code and require runtime/syntax preservation matrices.

## pip first wave

Repository: `pypa/pip`

### Integrity boundary

Issue [#13984](https://github.com/pypa/pip/issues/13984) reports that `--require-hashes` does not enforce hashes for build-system dependencies. This is consequential, but it crosses policy and compatibility boundaries. The first packet should use a fully local package index and sdist so the behavior can be demonstrated without network or registry variability, then ask maintainers which contract they want before implementation.

Required fixture:

```text
local index
├── top-level sdist with hashes
├── pyproject build-system requirement
├── unhashed build dependency
└── offline install command with --require-hashes
```

Record whether pip documents or reports the bypass and which resolver/install phase owns enforcement.

### Diagnostic candidate

Issue [#14193](https://github.com/pypa/pip/issues/14193) reports a “no matching distributions” hint for a package version that installs independently. Reduce the resolver state and environment marker combination before considering code.

### Duplicate stop

Issue #14177 already has [PR #14178](https://github.com/pypa/pip/pull/14178), fixing a `Version == str` comparison that made the `(latest)` output branch unreachable. Retain as a compact tool-correctness example.

## Test packet standard for developer tools

Every automatic-fix candidate should include:

1. original source;
2. fixed source;
3. parser success for both when expected;
4. runtime output before and after when executable;
5. fix-safety classification before and after;
6. idempotence and convergence result;
7. neighboring negative cases.

## Return

- **Promote first:** Ruff #27026.
- **Parallel candidates:** Ruff #27022 and #27024.
- **Batch candidate:** Ruff #27008 and #26954 around PEP 695 transformations.
- **Issue-first:** pip #13984.
- **Retain for reduction:** pip #14193 and Ruff convergence issues.
- **Stop duplicate implementation:** pip #14177.