#!/usr/bin/env python3
"""Small model of a Serde internally tagged unit-variant boundary.

This models the control flow read from serde-rs/serde at
747814f7d5fbab872df3b02f070c165b91bde062. It is intentionally a model,
not target-native Serde execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class BufferedMap:
    tag: Any
    content: tuple[tuple[Any, Any], ...]


def tagged_content_visitor(
    entries: Iterable[tuple[Any, Any]], tag_name: str
) -> BufferedMap:
    """Model TaggedContentVisitor::visit_map.

    The tag entry is separated from every other pair. Duplicate or missing tag
    entries fail before variant dispatch.
    """

    tag = None
    have_tag = False
    content: list[tuple[Any, Any]] = []

    for key, value in entries:
        if key == tag_name:
            if have_tag:
                raise ValueError(f"duplicate field {tag_name!r}")
            tag = value
            have_tag = True
        else:
            content.append((key, value))

    if not have_tag:
        raise ValueError(f"missing field {tag_name!r}")

    return BufferedMap(tag=tag, content=tuple(content))


def current_bare_unit_visit_map(content: tuple[tuple[Any, Any], ...]) -> str:
    """Model InternallyTaggedUnitVisitor::visit_map.

    Current source drains every pair as IgnoredAny and returns success.
    """

    for _key, _value in content:
        pass
    return "ok"


def empty_struct_variant_with_deny(
    content: tuple[tuple[Any, Any], ...]
) -> str:
    """Model the behavioral control used by the upstream issue report.

    A generated empty struct variant with deny_unknown_fields rejects the first
    remaining field after the tag has been removed.
    """

    if content:
        return f"unknown field {content[0][0]!r}"
    return "ok"


def main() -> None:
    tagged_only = tagged_content_visitor([("type", "A")], "type")
    assert tagged_only.tag == "A"
    assert tagged_only.content == ()
    assert current_bare_unit_visit_map(tagged_only.content) == "ok"
    assert empty_struct_variant_with_deny(tagged_only.content) == "ok"

    with_extra = tagged_content_visitor(
        [("type", "A"), ("token", "testToken")], "type"
    )
    assert with_extra.tag == "A"
    assert with_extra.content == (("token", "testToken"),)

    bare = current_bare_unit_visit_map(with_extra.content)
    empty_struct = empty_struct_variant_with_deny(with_extra.content)

    print(f"buffered after tag removal: {with_extra.content!r}")
    print(f"bare unit variant: {bare}")
    print(f"empty struct variant + deny_unknown_fields: {empty_struct}")

    assert bare == "ok"
    assert empty_struct == "unknown field 'token'"

    try:
        tagged_content_visitor([("type", "A"), ("type", "B")], "type")
    except ValueError as error:
        print(f"duplicate tag control: {error}")
    else:
        raise AssertionError("duplicate tag should fail")


if __name__ == "__main__":
    main()
