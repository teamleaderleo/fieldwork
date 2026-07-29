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
CLAIM_SCOPES = ["mechanism", "interface", "integration", "operational", "ecosystem"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", help="lowercase words separated by hyphens")
    parser.add_argument("--question", required=True, help="one bounded question")
    parser.add_argument("--owner", default="unassigned")
    parser.add_argument("--date", dest="created_at", default=date.today().isoformat())
    parser.add_argument("--command", default="python3 run.py")
    parser.add_argument(
        "--claim-scope",
        choices=CLAIM_SCOPES,
        default="mechanism",
        help="widest claim this experiment is intended to support",
    )
    parser.add_argument(
        "--integration-context",
        help="repository-relative context dossier, for example contexts/patterns/retry-idempotency.md",
    )
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

    if args.integration_context:
        context_path = Path(args.integration_context)
        if context_path.is_absolute() or ".." in context_path.parts:
            print("--integration-context must be a repository-relative path without '..'", file=sys.stderr)
            return 2
    elif args.claim_scope in {"integration", "operational", "ecosystem"}:
        print(
            f"--claim-scope {args.claim_scope!r} requires --integration-context",
            file=sys.stderr,
        )
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
        "claim_scope": args.claim_scope,
        "integration_context": args.integration_context,
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

    context_line = args.integration_context or "none"
    readme = f"""# Experiment: {args.slug.replace('-', ' ').title()}

Experiment ID: `{experiment_id}`

State: `draft`

Claim scope: `{args.claim_scope}`

Integration context: `{context_line}`

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

## Wider context

Record only the claim scope supported by the evidence. Use `INTEGRATION_CONTEXT.md` when asserting integration, operational, or ecosystem consequences.

## Uncertainty

Not assessed.

## Disposition

Pending.

## Boundaries

- Upstream contact is not authorized.
- Network policy: `{args.network_policy}`.
- Mechanism evidence does not establish wider use without supporting context.
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
