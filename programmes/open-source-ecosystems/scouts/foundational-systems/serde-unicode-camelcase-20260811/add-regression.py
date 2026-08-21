from __future__ import annotations

import pathlib
import sys

path = pathlib.Path(sys.argv[1])
source = path.read_text()

if "fn unicode_camel_case_field" in source:
    raise SystemExit("regression tests already present")

source += r'''

#[test]
fn unicode_camel_case_field() {
    assert_eq!(CamelCase.apply_to_field("项目名称"), "项目名称");
    assert_eq!(CamelCase.apply_to_field("Éclair"), "éclair");
    assert_eq!(CamelCase.apply_to_field("İ_value"), "i\u{307}Value");
    assert_eq!(CamelCase.apply_to_field("foo_éclair"), "fooÉclair");
    assert_eq!(CamelCase.apply_to_field("foo_σigma"), "fooΣigma");
    assert_eq!(CamelCase.apply_to_field("foo_ßeta"), "fooSSeta");
}

#[test]
fn unicode_camel_case_variant() {
    assert_eq!(CamelCase.apply_to_variant("项目名称"), "项目名称");
    assert_eq!(CamelCase.apply_to_variant("Éclair"), "éclair");
    assert_eq!(CamelCase.apply_to_variant("Σigma"), "σigma");
}

#[test]
fn unicode_camel_case_does_not_widen_pascal_case() {
    assert_eq!(PascalCase.apply_to_field("foo_éclair"), "Fooéclair");
    assert_eq!(PascalCase.apply_to_field("foo_σigma"), "Fooσigma");
}
'''

path.write_text(source)
