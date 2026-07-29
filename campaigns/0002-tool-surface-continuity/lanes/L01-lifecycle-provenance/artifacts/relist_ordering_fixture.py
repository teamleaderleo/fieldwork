#!/usr/bin/env python3
"""Source-derived invariant fixture for MCP catalogue ordering.

This is not a full Codex or rmcp binary test. It models two observed source
contracts:

1. rmcp can reject a stale response-cache write while still returning the raw
   relist result to its caller.
2. Codex can advertise cached catalogue A, wait for server startup, and execute
   against the later live binding B.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Optional

Tool = tuple[str, str]


@dataclass(frozen=True)
class Catalogue:
    label: str
    tools: tuple[Tool, ...]

    def digest(self) -> tuple[Tool, ...]:
        return tuple(sorted(self.tools))

    def tool_revision(self, name: str) -> Optional[str]:
        for tool_name, revision in self.tools:
            if tool_name == name:
                return revision
        return None


class SdkCache:
    def __init__(self, initial: Catalogue) -> None:
        self.generation = 0
        self.cached: Optional[Catalogue] = initial

    def invalidate(self) -> int:
        self.generation += 1
        self.cached = None
        return self.generation

    def complete_relist(self, captured_generation: int, result: Catalogue) -> bool:
        accepted = captured_generation == self.generation
        if accepted:
            self.cached = result
        return accepted


class ApplicationPublisher:
    def __init__(self, initial: Catalogue) -> None:
        self.published = initial

    def publish_naive(self, result: Catalogue) -> None:
        self.published = result

    def publish_if_current(
        self,
        captured_generation: int,
        current_generation: int,
        result: Catalogue,
    ) -> bool:
        if captured_generation != current_generation:
            return False
        self.published = result
        return True


def sdk_relist_ordering() -> dict[str, object]:
    catalogue_a = Catalogue("A", (("search", "v1"),))
    catalogue_b = Catalogue("B", (("search", "v2"),))
    catalogue_c = Catalogue("C", (("search", "v3"),))

    cache = SdkCache(catalogue_a)
    naive = ApplicationPublisher(catalogue_a)
    ticketed = ApplicationPublisher(catalogue_a)

    relist_1_generation = cache.invalidate()
    relist_2_generation = cache.invalidate()

    relist_2_cache_accepted = cache.complete_relist(relist_2_generation, catalogue_c)
    naive.publish_naive(catalogue_c)
    relist_2_app_accepted = ticketed.publish_if_current(
        relist_2_generation,
        cache.generation,
        catalogue_c,
    )

    relist_1_cache_accepted = cache.complete_relist(relist_1_generation, catalogue_b)
    naive.publish_naive(catalogue_b)
    relist_1_app_accepted = ticketed.publish_if_current(
        relist_1_generation,
        cache.generation,
        catalogue_b,
    )

    assert relist_2_cache_accepted is True
    assert relist_2_app_accepted is True
    assert relist_1_cache_accepted is False
    assert relist_1_app_accepted is False
    assert cache.cached == catalogue_c
    assert naive.published == catalogue_b
    assert ticketed.published == catalogue_c

    return {
        "cache_catalogue": cache.cached.label if cache.cached else None,
        "naive_application_catalogue": naive.published.label,
        "ticketed_application_catalogue": ticketed.published.label,
        "late_cache_write_accepted": relist_1_cache_accepted,
        "late_application_publish_accepted": relist_1_app_accepted,
    }


def codex_call(
    advertised: Catalogue,
    live: Catalogue,
    tool_name: str,
) -> dict[str, object]:
    advertised_revision = advertised.tool_revision(tool_name)
    live_revision = live.tool_revision(tool_name)

    if advertised_revision is None:
        return {"outcome": "not_advertised"}

    if live_revision is None:
        return {
            "outcome": "unavailable_after_startup_wait",
            "diagnostic": "advertisement_execution_revision_mismatch",
            "advertised_catalogue": advertised.label,
            "live_catalogue": live.label,
        }

    if advertised.digest() == live.digest():
        return {
            "outcome": "execute_live_binding",
            "diagnostic": "verified_equal_catalogue",
            "tool_revision": live_revision,
        }

    return {
        "outcome": "execute_live_binding",
        "diagnostic": "advertisement_execution_revision_mismatch",
        "advertised_tool_revision": advertised_revision,
        "live_tool_revision": live_revision,
    }


def codex_late_binding() -> dict[str, object]:
    catalogue_a = Catalogue(
        "A",
        (("search", "schema-v1/approval-prompt"),),
    )
    catalogue_b_removed = Catalogue("B-removed", (("other", "v1"),))
    catalogue_b_changed = Catalogue(
        "B-changed",
        (("search", "schema-v2/approval-auto"),),
    )
    catalogue_b_equal = Catalogue(
        "B-equal",
        (("search", "schema-v1/approval-prompt"),),
    )

    results = {
        "removed": codex_call(catalogue_a, catalogue_b_removed, "search"),
        "same_name_changed": codex_call(catalogue_a, catalogue_b_changed, "search"),
        "same_digest": codex_call(catalogue_a, catalogue_b_equal, "search"),
    }

    assert results["removed"]["outcome"] == "unavailable_after_startup_wait"
    assert (
        results["same_name_changed"]["diagnostic"]
        == "advertisement_execution_revision_mismatch"
    )
    assert results["same_digest"]["diagnostic"] == "verified_equal_catalogue"
    return results


def main() -> None:
    result = {
        "sdk_relist_ordering": sdk_relist_ordering(),
        "codex_late_binding": codex_late_binding(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
