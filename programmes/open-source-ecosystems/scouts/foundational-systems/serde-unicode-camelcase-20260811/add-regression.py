from __future__ import annotations

import pathlib
import sys

path = pathlib.Path(sys.argv[1])
source = path.read_text()

required = [
    'CamelCase => variant[..1].to_ascii_lowercase() + &variant[1..],',
    'pascal[..1].to_ascii_lowercase() + &pascal[1..]',
]
for needle in required:
    if needle not in source:
        raise SystemExit(f"expected exact baseline source missing: {needle}")

if "fn unicode_camel_case_field" in source:
    raise SystemExit("regression tests already present")

source += r'''

#[test]
fn unicode_camel_case_field() {
    assert_eq!(CamelCase.apply_to_field("项目名称"), "项目名称");
    assert_eq!(CamelCase.apply_to_field("Éclair"), "éclair");
    assert_eq!(CamelCase.apply_to_field("İ_value"), "i\u{307}Value");
}

#[test]
fn unicode_camel_case_variant() {
    assert_eq!(CamelCase.apply_to_variant("项目名称"), "项目名称");
    assert_eq!(CamelCase.apply_to_variant("Éclair"), "éclair");
    assert_eq!(CamelCase.apply_to_variant("Σigma"), "σigma");
}
'''

path.write_text(source)
