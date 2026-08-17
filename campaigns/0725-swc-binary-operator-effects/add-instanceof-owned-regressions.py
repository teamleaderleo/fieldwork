#!/usr/bin/env python3
"""Add SWC-owned regression fixtures for the pinned `instanceof` repair.

Pinned source contract: swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077.

These fixtures deliberately live under tests/fixture rather than tests/terser.
SWC's minifier-local instructions say new regression coverage belongs in
SWC-owned fixture roots; imported Terser snapshots are compatibility surfaces,
not the sole semantic contract.
"""

from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
fixture = root / "crates/swc_ecma_minifier/tests/fixture/operator-effects/instanceof-pure-func-value"

if fixture.exists():
    raise SystemExit(f"fixture already exists: {fixture}")

fixture.mkdir(parents=True)

(fixture / "config.json").write_text(
    '''{
    "defaults": false,
    "pure_funcs": ["foo"],
    "side_effects": true
}
'''
)

(fixture / "input.js").write_text(
    '''function callback() {
    foo() instanceof bar();
}

function invalid() {
    foo() instanceof 2;
}

function control() {
    foo() === bar();
}
'''
)

(fixture / "output.js").write_text(
    '''function callback() {
    foo() instanceof bar();
}
function invalid() {
    foo() instanceof 2;
}
function control() {
    bar();
}
'''
)
