#!/usr/bin/env python3
"""Create a minimal fork-free Fieldwork experiment directory."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys

SLUG_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*$")
ROOT = Path("playgrounds")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", help="lowercase words separated by hyphens")
    parser.add_argument("--question", required=True, help="one bounded question")
    parser.add_argument("--owner", default="unassigned")
    parser.add_argument("--date", dest="created_at", default=date.today().isoformat())
    parser.add_argument("--command", default="python3 run.py")
    parser.add_argument(
        "--network-policy",
        choices=["disabled", "loopback-only", "public-read-only", "explicit"],
        default="disabled",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not SLUG_PATTERN.fullmatch(args.slug):
        print("slug must contain lowercase letters, digits, and single hyphens", file=sys.stderr)
        return 2

    try:
        date.fromisoformat(args.created_at)
    except ValueError:
        print("--date must use YYYY-MM-DD", file=sys.stderr)
        return 2

    compact_date = args.created_at.replace("-", "")
    experiment_id = f"EXP-{compact_date}-{args.slug}"
    directory = ROOT / experiment_id
    if directory.exists():
        print(f"experiment already exists: {directory}", file=sys.stderr)
        return 1

    directory.mkdir(parents=True)
    metadata = {
        "schema_version": 1,
        "id": experiment_id,
        "question": args.question,
        "owner": args.owner,
        "created_at": args.created_at,
        "state": "draft",
        "sources": [],
        "command": args.command,
        "environment": {
            "runtime": "",
            "platform": "",
            "dependencies": [],
        },
        "distinguishing_outcomes": [],
        "stop_condition": "Stop after the bounded question is answered or cannot be tested safely.",
        "network_policy": args.network_policy,
        "upstream_contact_authorized": False,
        "result_paths": [],
        "promoted_to": None,
    }
    (directory / "experiment.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    readme = f"""# Experiment: {args.slug.replace('-', ' ').title()}

Experiment ID: `{experiment_id}`

State: `draft`

## Question

{args.question}

## Distinguishing outcomes

| Observation | Interpretation |
|---|---|
| | |

## Command

```text
{args.command}
```

## Result

Not run.

## Uncertainty

Not assessed.

## Disposition

Pending.

## Boundaries

- Upstream contact is not authorized.
- Network policy: `{args.network_policy}`.
"""
    (directory / "README.md").write_text(readme, encoding="utf-8")

    run_py = '''#!/usr/bin/env python3
"""Implement the bounded experiment described in experiment.json."""

from __future__ import annotations

import sys


def main() -> int:
    print("Experiment adapter not implemented.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
'''
    (directory / "run.py").write_text(run_py, encoding="utf-8")

    print(directory)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
