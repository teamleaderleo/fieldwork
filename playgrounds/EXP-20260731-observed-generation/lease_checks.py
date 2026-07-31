#!/usr/bin/env python3
"""Repository-scoped writer-lease collision checks for issue #325."""

from __future__ import annotations

from typing import Any


def evaluate_writer_leases(leases: list[dict[str, Any]]) -> dict[str, Any]:
    """Detect active collisions using (repository, resource_kind, resource)."""

    seen: dict[tuple[str, str, str], str] = {}
    collisions: list[dict[str, str]] = []
    for lease in leases:
        if lease.get("state") != "active":
            continue
        identity = (
            str(lease.get("repository")),
            str(lease.get("resource_kind")),
            str(lease.get("resource")),
        )
        previous = seen.get(identity)
        if previous is None:
            seen[identity] = str(lease.get("holder"))
            continue
        collisions.append(
            {
                "repository": identity[0],
                "resource_kind": identity[1],
                "resource": identity[2],
                "first_holder": previous,
                "second_holder": str(lease.get("holder")),
            }
        )
    return {
        "status": "False" if collisions else "True",
        "reason": "DuplicateActiveLease" if collisions else "RepositoryScopedLeasesUnique",
        "collisions": collisions,
    }
