from __future__ import annotations

import pathlib
import sys

path = pathlib.Path(sys.argv[1])
source = path.read_text()

insert_after = "use self::RenameRule::*;\nuse std::fmt::{self, Debug, Display};\n"
helpers = r'''

fn lowercase_first(value: &str) -> String {
    let mut chars = value.chars();
    if let Some(first) = chars.next() {
        first.to_lowercase().chain(chars).collect()
    } else {
        String::new()
    }
}

fn camel_case_field(field: &str) -> String {
    let mut camel = String::new();
    let mut capitalize = false;

    for ch in field.chars() {
        if ch == '_' {
            capitalize = true;
        } else if capitalize {
            camel.extend(ch.to_uppercase());
            capitalize = false;
        } else {
            camel.push(ch);
        }
    }

    lowercase_first(&camel)
}
'''

variant_old = '            CamelCase => variant[..1].to_ascii_lowercase() + &variant[1..],'
variant_new = '            CamelCase => lowercase_first(variant),'

field_old = '''            CamelCase => {
                let pascal = PascalCase.apply_to_field(field);
                pascal[..1].to_ascii_lowercase() + &pascal[1..]
            }'''
field_new = '            CamelCase => camel_case_field(field),'

for needle in (insert_after, variant_old, field_old):
    if source.count(needle) != 1:
        raise SystemExit(f"expected exact source occurrence once: {needle!r}")

source = source.replace(insert_after, insert_after + helpers, 1)
source = source.replace(variant_old, variant_new, 1)
source = source.replace(field_old, field_new, 1)
path.write_text(source)
