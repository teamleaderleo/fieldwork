#!/usr/bin/env python3
"""Apply the pinned SWC `instanceof` semantic research candidate.

Pinned source contract: swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077.
The candidate has three owners:

1. shared effect classification/extraction in swc_ecma_utils;
2. the independent `instanceof` constant fold in the expression simplifier,
   which is also reused by the minifier Pure pass;
3. minifier result-discarding through `ignore_return_value`, which otherwise
   removes a direct discarded `instanceof` expression statement.

Every edit requires a unique source marker so source drift fails closed.
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
    "crates/swc_ecma_minifier/src/compress/pure/misc.rs",
    "        self.optimize_expr_in_bool_ctx(e, true);\n",
    '        if matches!(\n'
    '            e,\n'
    '            Expr::Bin(BinExpr {\n'
    '                op: op!("instanceof"),\n'
    '                ..\n'
    '            })\n'
    '        ) {\n'
    '            return;\n'
    '        }\n\n'
    '        self.optimize_expr_in_bool_ctx(e, true);\n',
)
