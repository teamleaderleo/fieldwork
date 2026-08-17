#!/usr/bin/env python3
"""Apply the SWC mapped-arguments explicit-ownership research candidate.

Pinned source contract: swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077.
The script intentionally requires exactly one match for every replacement so
source drift fails closed instead of silently applying a different patch.
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


replace_once(
    "crates/swc_ecma_minifier/src/program_data.rs",
    "        const LAZY_INIT                 = 1 << 25;\n",
    "        const LAZY_INIT                 = 1 << 25;\n"
    "\n"
    "        /// Parameter of an ordinary function whose lexical `arguments` is used.\n"
    "        /// This flag follows cloned/remapped bindings with `VarUsageInfo`.\n"
    "        const FN_PARAM_OF_ARGUMENTS_FN  = 1 << 26;\n",
)

replace_once(
    "crates/swc_ecma_minifier/src/program_data.rs",
    "                    *e_flags |= var_info_flags & VarUsageInfoFlags::USED_IN_NON_CHILD_FN;\n",
    "                    *e_flags |= var_info_flags & VarUsageInfoFlags::USED_IN_NON_CHILD_FN;\n"
    "                    *e_flags |= var_info_flags & VarUsageInfoFlags::FN_PARAM_OF_ARGUMENTS_FN;\n",
)

replace_once(
    "crates/swc_ecma_minifier/src/program_data.rs",
    "    fn mark_declared_as_fn_param(&mut self) {\n"
    "        self.flags.insert(VarUsageInfoFlags::DECLARED_AS_FN_PARAM);\n"
    "    }\n",
    "    fn mark_declared_as_fn_param(&mut self) {\n"
    "        self.flags.insert(VarUsageInfoFlags::DECLARED_AS_FN_PARAM);\n"
    "    }\n"
    "\n"
    "    fn mark_fn_param_of_arguments_fn(&mut self) {\n"
    "        self.flags\n"
    "            .insert(VarUsageInfoFlags::FN_PARAM_OF_ARGUMENTS_FN);\n"
    "    }\n",
)

replace_once(
    "crates/swc_ecma_minifier/src/usage_analyzer/analyzer/storage.rs",
    "    fn mark_declared_as_fn_param(&mut self);\n\n"
    "    fn mark_as_lazy_init(&mut self);\n",
    "    fn mark_declared_as_fn_param(&mut self);\n\n"
    "    fn mark_fn_param_of_arguments_fn(&mut self);\n\n"
    "    fn mark_as_lazy_init(&mut self);\n",
)

replace_once(
    "crates/swc_ecma_minifier/src/usage_analyzer/analyzer/mod.rs",
    "                if let Some(body) = &n.body {\n"
    "                    // We use visit_children_with instead of visit_with to bypass block scope\n"
    "                    // handler.\n"
    "                    body.visit_children_with(child);\n"
    "                }\n"
    "            })\n",
    "                if let Some(body) = &n.body {\n"
    "                    // We use visit_children_with instead of visit_with to bypass block scope\n"
    "                    // handler.\n"
    "                    body.visit_children_with(child);\n"
    "                }\n"
    "\n"
    "                if child.scope.used_arguments() {\n"
    "                    for param in &n.params {\n"
    "                        for id in find_pat_ids::<_, Id>(&param.pat) {\n"
    "                            child\n"
    "                                .data\n"
    "                                .var_or_default(id)\n"
    "                                .mark_fn_param_of_arguments_fn();\n"
    "                        }\n"
    "                    }\n"
    "                }\n"
    "            })\n",
)

replace_once(
    "crates/swc_ecma_minifier/src/compress/optimize/unused.rs",
    "                    && (!var.flags.contains(VarUsageInfoFlags::DECLARED_AS_FN_PARAM)\n"
    "                        || !self.data.used_arguments(self.ctx.scope)\n"
    "                        || self.ctx.expr_ctx.in_strict)\n",
    "                    && (!var.flags.contains(VarUsageInfoFlags::DECLARED_AS_FN_PARAM)\n"
    "                        || !var\n"
    "                            .flags\n"
    "                            .contains(VarUsageInfoFlags::FN_PARAM_OF_ARGUMENTS_FN))\n",
)
