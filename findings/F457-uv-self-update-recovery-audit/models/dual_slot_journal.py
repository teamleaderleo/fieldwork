"""Crash-order model for a two-slot Windows update journal.

The journal alternates monotonically increasing generations between two files. A phase write may
leave its target slot torn, but the other slot still contains the preceding durable generation.
Recovery selects the highest valid generation.

This model deliberately abstracts file operations to their authority effects. It checks every
publication and cleanup boundary used by the proposed ordering.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Optional


class Phase(str, Enum):
    PREPARED = "prepared"
    OLD_BACKED_UP = "old-backed-up"
    NEW_LIVE = "new-live"
    COMMITTED = "committed"


@dataclass(frozen=True)
class Record:
    generation: int
    phase: Phase
    valid: bool = True


@dataclass(frozen=True)
class State:
    canonical: Optional[str]
    staged: Optional[str]
    backup: Optional[str]
    slots: tuple[Optional[Record], Optional[Record]]


def latest_valid(state: State) -> Optional[Record]:
    records = [record for record in state.slots if record is not None and record.valid]
    return max(records, key=lambda record: record.generation) if records else None


def durable_write(state: State, record: Record) -> State:
    slots = list(state.slots)
    slots[record.generation % 2] = record
    return replace(state, slots=tuple(slots))


def torn_write(state: State, record: Record) -> State:
    slots = list(state.slots)
    slots[record.generation % 2] = replace(record, valid=False)
    return replace(state, slots=tuple(slots))


def recover(state: State) -> State:
    record = latest_valid(state)
    if record is None:
        # No transaction record means normal live state is authoritative.
        return state

    if record.phase is Phase.COMMITTED:
        if state.canonical != "new":
            raise AssertionError("committed journal lacks new canonical authority")
        return State("new", None, None, (None, None))

    # Every non-committed phase conservatively chooses the old generation.
    if state.backup == "old":
        return State("old", None, None, (None, None))
    if state.canonical == "old":
        return State("old", None, None, (None, None))
    raise AssertionError("uncommitted journal lacks old canonical or backup authority")


def assert_recovery(name: str, state: State, expected: str) -> None:
    recovered = recover(state)
    assert recovered.canonical == expected, (
        name,
        latest_valid(state),
        recovered,
        expected,
    )


def main() -> None:
    checks: list[tuple[str, State, str]] = []
    state = State("old", "new", None, (None, None))
    checks.append(("before prepared publication", state, "old"))

    prepared = Record(0, Phase.PREPARED)
    checks.append(("prepared slot torn", torn_write(state, prepared), "old"))
    state = durable_write(state, prepared)
    checks.append(("prepared durable", state, "old"))

    state = replace(state, canonical=None, backup="old")
    checks.append(("old moved before phase publication", state, "old"))
    old_backed_up = Record(1, Phase.OLD_BACKED_UP)
    checks.append(("old-backed-up slot torn", torn_write(state, old_backed_up), "old"))
    state = durable_write(state, old_backed_up)
    checks.append(("old-backed-up durable", state, "old"))

    state = replace(state, canonical="new", staged=None)
    checks.append(("new live before phase publication", state, "old"))
    new_live = Record(2, Phase.NEW_LIVE)
    checks.append(("new-live slot torn", torn_write(state, new_live), "old"))
    state = durable_write(state, new_live)
    checks.append(("new-live durable", state, "old"))

    committed = Record(3, Phase.COMMITTED)
    checks.append(("committed slot torn", torn_write(state, committed), "old"))
    state = durable_write(state, committed)
    checks.append(("committed durable", state, "new"))

    # Cleanup ordering is part of the protocol. Remove the older uncommitted slot first, then
    # backup/stage, and remove the committed slot last.
    slots = list(state.slots)
    slots[0] = None
    state = replace(state, slots=tuple(slots))
    checks.append(("older slot removed", state, "new"))
    state = replace(state, backup=None)
    checks.append(("backup removed with committed slot retained", state, "new"))
    state = replace(state, staged=None)
    checks.append(("stage removed with committed slot retained", state, "new"))
    slots = list(state.slots)
    slots[1] = None
    state = replace(state, slots=tuple(slots))
    checks.append(("committed slot removed last", state, "new"))

    for name, crash_state, expected in checks:
        assert_recovery(name, crash_state, expected)

    # Counterexample: deleting committed evidence before the old backup creates an unsafe window.
    bad = State(
        canonical="new",
        staged=None,
        backup=None,
        slots=(Record(2, Phase.NEW_LIVE), None),
    )
    try:
        recover(bad)
    except AssertionError:
        pass
    else:
        raise AssertionError("wrong cleanup ordering unexpectedly remained recoverable")

    print(f"passed {len(checks)} intended crash boundaries and rejected bad cleanup ordering")


if __name__ == "__main__":
    main()
