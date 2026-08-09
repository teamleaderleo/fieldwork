#!/usr/bin/env python3
"""Apply the pinned SWC `instanceof` effect-analysis research candidate.

Pinned source contract: swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077.
Every edit requires exactly one match so source drift fails closed.
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


path = "crates/swc_ecma_utils/src/lib.rs"

replace_once(
    path,
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
    path,
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
