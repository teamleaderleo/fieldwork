#!/usr/bin/env python3
"""Executable lifecycle-provenance model for Fieldwork issue #35.

This fixture encodes the precedence rules observed at the pinned public Codex
revision 3725f02cf38d856bc82bb46dd68ab61bb96ec6fc and checked against owned
revision 2b7b93081361b77f8ddaceaf362a09765b4153bf.

It deliberately creates a mismatch:
- saved thread dynamic tools: ["host_old"]
- current host dynamic tools: ["host_new"]
- saved thread root: root-a at /saved/root-a
- current environment roots: root-a at /current/root-a plus root-b

Run:
    python3 lifecycle_provenance_fixture.py
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Iterable


class Transition(str, Enum):
    START = "start"
    LIVE_RECONNECT = "live_reconnect"
    COLD_RESUME = "cold_resume"
    FORK = "fork"
    RESTART = "restart"
    UPGRADE = "upgrade"


@dataclass(frozen=True)
class CapabilityRoot:
    root_id: str
    location: str
    source: str


@dataclass(frozen=True)
class Inputs:
    saved_dynamic_tools: tuple[str, ...]
    current_host_dynamic_tools: tuple[str, ...]
    live_dynamic_tools: tuple[str, ...]
    saved_thread_roots: tuple[CapabilityRoot, ...]
    current_host_thread_roots: tuple[CapabilityRoot, ...]
    current_environment_roots: tuple[CapabilityRoot, ...]
    live_thread_roots: tuple[CapabilityRoot, ...]
    current_native_tools: tuple[str, ...]
    current_mcp_tools: tuple[str, ...]
    saved_multi_agent_version: str | None
    inherited_multi_agent_version: str | None


@dataclass(frozen=True)
class EffectiveSurface:
    transition: str
    dynamic_tools: tuple[str, ...]
    thread_roots: tuple[CapabilityRoot, ...]
    effective_roots: tuple[CapabilityRoot, ...]
    native_tools: tuple[str, ...]
    mcp_tools: tuple[str, ...]
    multi_agent_version: str | None
    dynamic_outcome: str
    root_outcome: str
    lifecycle_outcome: str
    diagnostics: tuple[str, ...]


def resolve_multi_agent_version(
    transition: Transition,
    saved: str | None,
    inherited: str | None,
) -> str | None:
    # Explicit inherited Disabled wins. Saved metadata wins next. Legacy
    # resumed/forked history defaults to V1 when metadata is absent.
    if inherited == "Disabled":
        return "Disabled"
    if saved is not None:
        return saved
    if inherited is not None:
        return inherited
    if transition in {
        Transition.COLD_RESUME,
        Transition.FORK,
        Transition.RESTART,
        Transition.UPGRADE,
    }:
        return "V1"
    return None


def merge_roots(
    thread_roots: Iterable[CapabilityRoot],
    environment_roots: Iterable[CapabilityRoot],
) -> tuple[tuple[CapabilityRoot, ...], tuple[str, ...]]:
    """Thread roots come first; later roots with the same id are ignored."""
    kept: list[CapabilityRoot] = []
    locations: dict[str, str] = {}
    diagnostics: list[str] = []
    for root in (*tuple(thread_roots), *tuple(environment_roots)):
        prior = locations.get(root.root_id)
        if prior is not None:
            if prior != root.location:
                diagnostics.append(
                    f"conflicting root {root.root_id}: kept {prior}; ignored {root.location}"
                )
            continue
        locations[root.root_id] = root.location
        kept.append(root)
    return tuple(kept), tuple(diagnostics)


def evaluate(transition: Transition, inputs: Inputs) -> EffectiveSurface:
    diagnostics: list[str] = []

    if transition is Transition.START:
        # thread/start exposes dynamicTools and selectedCapabilityRoots.
        dynamic_tools = inputs.current_host_dynamic_tools
        thread_roots = inputs.current_host_thread_roots
        dynamic_outcome = "current host supplied"
        root_outcome = "current host supplied, then current environment roots merged"
        lifecycle_outcome = "new session built"
    elif transition is Transition.LIVE_RECONNECT:
        # thread/resume of a running thread rejoins the existing session.
        dynamic_tools = inputs.live_dynamic_tools
        thread_roots = inputs.live_thread_roots
        dynamic_outcome = "existing in-memory session preserved"
        root_outcome = "existing in-memory thread roots preserved"
        lifecycle_outcome = "rejoined existing session"
        diagnostics.append("resume capability overrides are unavailable")
    else:
        # Public resume/fork request types have no fresh dynamicTools or
        # selectedCapabilityRoots fields. Core passes an empty dynamic tool vec,
        # which means fallback to SessionMeta.dynamic_tools. Selected roots fall
        # back to SessionMeta unless an internal host supplies thread_extension_init.
        dynamic_tools = inputs.saved_dynamic_tools
        thread_roots = inputs.saved_thread_roots
        dynamic_outcome = "saved thread metadata preserved"
        root_outcome = "saved thread roots preserved, then current environment roots merged"
        lifecycle_outcome = "new session rebuilt from saved history plus current runtime inputs"
        diagnostics.append("current host thread capability set has no public resume/fork input")

    effective_roots, root_diagnostics = merge_roots(
        thread_roots, inputs.current_environment_roots
    )
    diagnostics.extend(root_diagnostics)

    return EffectiveSurface(
        transition=transition.value,
        dynamic_tools=dynamic_tools,
        thread_roots=thread_roots,
        effective_roots=effective_roots,
        native_tools=inputs.current_native_tools,
        mcp_tools=inputs.current_mcp_tools,
        multi_agent_version=resolve_multi_agent_version(
            transition,
            inputs.saved_multi_agent_version,
            inputs.inherited_multi_agent_version,
        ),
        dynamic_outcome=dynamic_outcome,
        root_outcome=root_outcome,
        lifecycle_outcome=lifecycle_outcome,
        diagnostics=tuple(diagnostics),
    )


def root(root_id: str, location: str, source: str) -> CapabilityRoot:
    return CapabilityRoot(root_id=root_id, location=location, source=source)


def main() -> None:
    inputs = Inputs(
        saved_dynamic_tools=("host_old",),
        current_host_dynamic_tools=("host_new",),
        live_dynamic_tools=("host_live",),
        saved_thread_roots=(root("root-a", "/saved/root-a", "saved thread metadata"),),
        current_host_thread_roots=(
            root("root-a", "/host/root-a", "current host thread start"),
            root("root-c", "/host/root-c", "current host thread start"),
        ),
        current_environment_roots=(
            root("root-a", "/current/root-a", "current environment"),
            root("root-b", "/current/root-b", "current environment"),
        ),
        live_thread_roots=(root("root-a", "/live/root-a", "live session"),),
        current_native_tools=("exec_command", "view_image"),
        current_mcp_tools=("mcp_current",),
        saved_multi_agent_version="V1",
        inherited_multi_agent_version=None,
    )

    results = [evaluate(transition, inputs) for transition in Transition]
    by_transition = {result.transition: result for result in results}

    assert by_transition["start"].dynamic_tools == ("host_new",)
    assert by_transition["live_reconnect"].dynamic_tools == ("host_live",)
    for transition in ("cold_resume", "fork", "restart", "upgrade"):
        result = by_transition[transition]
        assert result.dynamic_tools == ("host_old",)
        assert tuple(item.root_id for item in result.effective_roots) == ("root-a", "root-b")
        assert result.effective_roots[0].location == "/saved/root-a"
        assert any("conflicting root root-a" in item for item in result.diagnostics)

    assert tuple(item.root_id for item in by_transition["start"].effective_roots) == (
        "root-a",
        "root-c",
        "root-b",
    )
    assert by_transition["start"].effective_roots[0].location == "/host/root-a"

    payload = {
        "fixture": {
            "saved_dynamic_tools": inputs.saved_dynamic_tools,
            "current_host_dynamic_tools": inputs.current_host_dynamic_tools,
            "saved_thread_roots": [asdict(item) for item in inputs.saved_thread_roots],
            "current_host_thread_roots": [
                asdict(item) for item in inputs.current_host_thread_roots
            ],
            "current_environment_roots": [
                asdict(item) for item in inputs.current_environment_roots
            ],
        },
        "results": [
            {
                **asdict(result),
                "thread_roots": [asdict(item) for item in result.thread_roots],
                "effective_roots": [asdict(item) for item in result.effective_roots],
            }
            for result in results
        ],
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
