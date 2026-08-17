#!/usr/bin/env python3
"""Apply the pinned SWC `instanceof` semantic research candidate.

Pinned source contract: swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077.
The candidate has four confirmed owners:

1. shared effect classification/extraction in swc_ecma_utils;
2. the independent `instanceof` constant fold in the expression simplifier,
   which is also reused by the minifier Pure pass;
3. the main minifier Optimizer's independent ignored-result binary reducer,
   which otherwise replaces every discarded binary operation with child effects;
4. the optimization dead-branch remover's local `ignore_result`, which also
   decomposes every non-short-circuit binary expression to child effects.

It also updates the three broad-test expectation surfaces that encode the old
operator-dropping behavior. Every edit requires a unique source marker so source
drift fails closed.
"""

from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()


def replace_once(path: str, old: str, new: str) -> None:
    p = root / path
    text = p.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one match, found {count}")
    p.write_text(text.replace(old, new, 1))


def remove_braced_match_arm(path: str, marker: str) -> None:
    p = root / path
    text = p.read_text()
    count = text.count(marker)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one arm marker, found {count}")

    start = text.index(marker)
    brace = text.index("{", start + len(marker) - 1)
    depth = 0
    end = None
    for index in range(brace, len(text)):
        ch = text[index]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = index + 1
                break

    if end is None:
        raise SystemExit(f"{path}: unterminated match arm for {marker!r}")

    if end < len(text) and text[end] == ",":
        end += 1
    if end < len(text) and text[end] == "\n":
        end += 1

    p.write_text(text[:start] + text[end:])


utils_path = "crates/swc_ecma_utils/src/lib.rs"

replace_once(
    utils_path,
    '        Expr::Unary(UnaryExpr { arg, .. }) => arg.may_have_side_effects(ctx),\n'
    '        Expr::Bin(BinExpr { left, right, .. }) => {\n'
    '            left.may_have_side_effects(ctx) || right.may_have_side_effects(ctx)\n'
    '        }\n',
    '        Expr::Unary(UnaryExpr { arg, .. }) => arg.may_have_side_effects(ctx),\n'
    '        Expr::Bin(BinExpr {\n'
    '            op: op!("instanceof"),\n'
    '            ..\n'
    '        }) => true,\n'
    '        Expr::Bin(BinExpr { left, right, .. }) => {\n'
    '            left.may_have_side_effects(ctx) || right.may_have_side_effects(ctx)\n'
    '        }\n',
)

replace_once(
    utils_path,
    '            Expr::Bin(BinExpr { op, .. }) if op.may_short_circuit() => {\n'
    '                to.push(Box::new(expr));\n'
    '            }\n'
    '            Expr::Bin(BinExpr { left, right, .. }) => {\n'
    '                self.extract_side_effects_to(to, *left);\n'
    '                self.extract_side_effects_to(to, *right);\n'
    '            }\n',
    '            Expr::Bin(BinExpr { op, .. }) if op.may_short_circuit() => {\n'
    '                to.push(Box::new(expr));\n'
    '            }\n'
    '            Expr::Bin(BinExpr {\n'
    '                op: op!("instanceof"),\n'
    '                ..\n'
    '            }) => {\n'
    '                to.push(Box::new(expr));\n'
    '            }\n'
    '            Expr::Bin(BinExpr { left, right, .. }) => {\n'
    '                self.extract_side_effects_to(to, *left);\n'
    '                self.extract_side_effects_to(to, *right);\n'
    '            }\n',
)

remove_braced_match_arm(
    "crates/swc_ecma_transforms_optimization/src/simplify/expr/mod.rs",
    '        op!("instanceof") => {',
)

replace_once(
    "crates/swc_ecma_minifier/src/compress/optimize/mod.rs",
    '            Expr::Bin(BinExpr {\n'
    '                span,\n'
    '                left,\n'
    '                right,\n'
    '                #[cfg(feature = "debug")]\n'
    '                op,\n'
    '                ..\n'
    '            }) => {\n',
    '            Expr::Bin(BinExpr {\n'
    '                op: op!("instanceof"),\n'
    '                ..\n'
    '            }) => {\n'
    '                return Some(e.take());\n'
    '            }\n\n'
    '            Expr::Bin(BinExpr {\n'
    '                span,\n'
    '                left,\n'
    '                right,\n'
    '                #[cfg(feature = "debug")]\n'
    '                op,\n'
    '                ..\n'
    '            }) => {\n',
)

replace_once(
    "crates/swc_ecma_transforms_optimization/src/simplify/branch/mod.rs",
    '        Expr::Bin(BinExpr {\n'
    '            span,\n'
    '            left,\n'
    '            op,\n'
    '            right,\n'
    '        }) if !op.may_short_circuit() => {\n',
    '        Expr::Bin(bin) if bin.op == op!("instanceof") => Some(bin.into()),\n\n'
    '        Expr::Bin(BinExpr {\n'
    '            span,\n'
    '            left,\n'
    '            op,\n'
    '            right,\n'
    '        }) if !op.may_short_circuit() => {\n',
)

replace_once(
    "crates/swc_ecma_transforms_optimization/src/simplify/expr/tests.rs",
    '''fn test_fold_instance_of() {
    // Non object types are never instances of anything.
    fold("64 instanceof Object", "false");
    fold("64 instanceof Number", "false");
    fold("'' instanceof Object", "false");
    fold("'' instanceof String", "false");
    fold("true instanceof Object", "false");
    fold("true instanceof Boolean", "false");
    fold("!0 instanceof Object", "false");
    fold("!0 instanceof Boolean", "false");
    fold("false instanceof Object", "false");
    fold("null instanceof Object", "false");
    fold("undefined instanceof Object", "false");
    fold("NaN instanceof Object", "false");
    fold("Infinity instanceof Object", "false");

    // Array and object literals are known to be objects.
    fold("[] instanceof Object", "true");
    fold("({}) instanceof Object", "true");

    // These cases is foldable, but no handled currently.
    fold("new Foo() instanceof Object", "new Foo(), true;");

    // These would require type information to fold.
    fold_same("[] instanceof Foo");
    fold_same("({}) instanceof Foo");

    fold("(function() {}) instanceof Object", "true");

    // An unknown value should never be folded.
    fold_same("x instanceof Foo");
    fold_same("x instanceof Object");
}
''',
    '''fn test_fold_instance_of() {
    // `instanceof` may invoke an own or inherited `Symbol.hasInstance` hook,
    // and invalid right operands may throw. Keep the operator unless a future
    // proof establishes the complete operator semantics, not just operand types.
    fold_same("64 instanceof Object");
    fold_same("64 instanceof Number");
    fold_same("'' instanceof Object");
    fold_same("'' instanceof String");
    fold_same("true instanceof Object");
    fold_same("true instanceof Boolean");
    fold_same("!0 instanceof Object");
    fold_same("!0 instanceof Boolean");
    fold_same("false instanceof Object");
    fold_same("null instanceof Object");
    fold_same("undefined instanceof Object");
    fold_same("NaN instanceof Object");
    fold_same("Infinity instanceof Object");
    fold_same("[] instanceof Object");
    fold_same("({}) instanceof Object");
    fold_same("new Foo() instanceof Object");
    fold_same("[] instanceof Foo");
    fold_same("({}) instanceof Foo");
    fold_same("(function() {}) instanceof Object");
    fold_same("x instanceof Foo");
    fold_same("x instanceof Object");
}
''',
)

replace_once(
    "crates/swc_ecma_minifier/tests/terser/compress/comparing/dont_change_in_or_instanceof_expressions/output.js",
    "1 in 1;\nnull in null;\n",
    "1 in 1;\nnull in null;\n1 instanceof 1;\nnull instanceof null;\n",
)

replace_once(
    "crates/swc_ecma_minifier/tests/terser/compress/pure_funcs/relational/output.js",
    "bar();\nbar();\nbar(), bar();\nbar();\nbar();\n",
    "foo() instanceof bar();\nbar();\nbar(), bar();\nbar();\nbar();\n",
)
