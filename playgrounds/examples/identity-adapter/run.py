#!/usr/bin/env python3
"""Read one JSON value from stdin and write the same value to stdout."""

from __future__ import annotations

import json
import sys


def main() -> int:
    value = json.load(sys.stdin)
    json.dump(value, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
