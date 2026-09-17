#!/usr/bin/env python3
"""Exhaustive interruption-point model for uv self-update recovery.

This is a dependency-free architecture model. It does not claim package execution.
It compares the observed public candidate ordering with a journaled rollback protocol.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Callable, Optional

FILES = ("uv", "uvx", "uvw", "receipt")
Generation = Optional[str]


@dataclass
class State:
    live: dict[str, Generation] = field(
        default_factory=lambda: {name: "old" for name in FILES}
    )
    staged: dict[str, Generation] = field(
        default_factory=lambda: {name: None for name in FILES}
    )
    backups: dict[str, Generation] = field(
        default_factory=lambda: {name: None for name in FILES}
    )
    temporary: dict[str, Generation] = field(
        default_factory=lambda: {name: None for name in FILES}
    )
    journal: Optional[str] = None


def invariants(state: State) -> tuple[bool, bool, bool]:
    canonical_uv_available = state.live["uv"] in {"old", "new"}
    generations = [state.live[name] for name in FILES]
    coherent_generation = (
        generations[0] in {"old", "new"}
        and all(value == generations[0] for value in generations)
    )
    no_partial_live_file = all(value != "partial" for value in generations)
    return canonical_uv_available, coherent_generation, no_partial_live_file


def candidate_steps() -> list[tuple[str, Callable[[State], None]]]:
    def stage(state: State) -> None:
        for name in FILES:
            state.staged[name] = "new"

    return [
        ("stage complete release", stage),
        ("interrupt during direct uvx copy", lambda state: state.live.__setitem__("uvx", "partial")),
        ("finish direct uvx copy", lambda state: state.live.__setitem__("uvx", "new")),
        ("interrupt during direct uvw copy", lambda state: state.live.__setitem__("uvw", "partial")),
        ("finish direct uvw copy", lambda state: state.live.__setitem__("uvw", "new")),
        (
            "rename canonical uv to backup",
            lambda state: (
                state.backups.__setitem__("uv", state.live["uv"]),
                state.live.__setitem__("uv", None),
            ),
        ),
        ("interrupt during new uv temporary copy", lambda state: state.temporary.__setitem__("uv", "partial")),
        ("finish new uv temporary copy", lambda state: state.temporary.__setitem__("uv", "new")),
        (
            "rename new uv to canonical",
            lambda state: (
                state.live.__setitem__("uv", state.temporary["uv"]),
                state.temporary.__setitem__("uv", None),
            ),
        ),
    ]


def recover_precommit(state: State) -> State:
    recovered = deepcopy(state)
    if recovered.journal == "committed":
        for name in FILES:
            recovered.backups[name] = None
        recovered.journal = None
        return recovered

    for name in FILES:
        if recovered.backups[name] == "old":
            recovered.live[name] = "old"
            recovered.backups[name] = None
    recovered.staged = {name: None for name in FILES}
    recovered.temporary = {name: None for name in FILES}
    recovered.journal = None
    return recovered


def journaled_steps() -> list[tuple[str, Callable[[State], None]]]:
    steps: list[tuple[str, Callable[[State], None]]] = []
    for name in FILES:
        steps.append(
            (
                f"rename old {name} to backup",
                lambda state, name=name: (
                    state.backups.__setitem__(name, state.live[name]),
                    state.live.__setitem__(name, None),
                ),
            )
        )
        steps.append(
            (
                f"rename staged new {name} to canonical",
                lambda state, name=name: (
                    state.live.__setitem__(name, state.staged[name]),
                    state.staged.__setitem__(name, None),
                ),
            )
        )
    steps.append(("mark journal committed", lambda state: setattr(state, "journal", "committed")))
    return steps


def report_candidate() -> None:
    state = State()
    print("CURRENT CANDIDATE")
    print("step|canonical_uv|coherent_generation|no_partial_live_file|live")
    print(f"before start|{*invariants(state),}|{state.live}")
    for label, operation in candidate_steps():
        operation(state)
        print(f"{label}|{*invariants(state),}|{state.live}")


def report_journaled() -> None:
    state = State()
    for name in FILES:
        state.staged[name] = "new"
    state.journal = "prepared"

    print("\nJOURNALED ROLLBACK PROTOCOL")
    print("interruption point|recovered canonical_uv|recovered coherent_generation|recovered no_partial|recovered live")
    recovered = recover_precommit(state)
    print(f"prepared|{*invariants(recovered),}|{recovered.live}")
    for label, operation in journaled_steps():
        operation(state)
        recovered = recover_precommit(state)
        print(f"{label}|{*invariants(recovered),}|{recovered.live}")
        assert invariants(recovered) == (True, True, True)


if __name__ == "__main__":
    report_candidate()
    report_journaled()
