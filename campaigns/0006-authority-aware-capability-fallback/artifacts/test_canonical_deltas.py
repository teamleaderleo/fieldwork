#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ARTIFACTS = Path(__file__).resolve().parent
sys.path.insert(0, str(ARTIFACTS))

from classify_fallback import classify  # noqa: E402


def main() -> None:
    review_cases = json.loads((ARTIFACTS / "review_cases.json").read_text(encoding="utf-8"))
    base = review_cases[2]

    original = classify(base)
    duplicate = copy.deepcopy(base)
    duplicate["authority_deltas"].append(copy.deepcopy(duplicate["authority_deltas"][0]))
    repeated = classify(duplicate)
    assert repeated.to_json() == original.to_json(), (
        "duplicate identical deltas must produce the same decision, named codes, and digest"
    )

    conflicting = copy.deepcopy(base)
    conflicting["authority_deltas"].append(
        {
            "field": conflicting["authority_deltas"][0]["field"],
            "relation": "changed",
        }
    )
    try:
        classify(conflicting)
    except ValueError as error:
        assert "conflicting authority relations" in str(error)
    else:
        raise AssertionError("conflicting authority relations must be rejected")


if __name__ == "__main__":
    main()
