#!/usr/bin/env python3
"""Measure Codex rollout growth without retaining transcript content or identities."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any


TYPE_RE = re.compile(br'"type":"([^"]+)"')
PAYLOAD_TYPE_RE = re.compile(br'"payload":\{"type":"([^"]+)"')
REPLACEMENT_HISTORY_FIELD = b'"replacement_history":'
RETAINED_SOURCE_CLASSES = {"subagent", "vscode"}


def percentile(values: list[int], fraction: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = round((len(ordered) - 1) * fraction)
    return ordered[index]


def session_source_class(line: bytes) -> str:
    """Return only an allow-listed coarse class from the canonical metadata line."""
    try:
        value = json.loads(line)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return "unknown"
    payload = value.get("payload")
    source = payload.get("source") if isinstance(payload, dict) else None
    if isinstance(source, str) and source in RETAINED_SOURCE_CLASSES:
        return source
    if isinstance(source, dict):
        retained = RETAINED_SOURCE_CLASSES.intersection(source)
        if len(retained) == 1:
            return retained.pop()
    return "other"


def scan_rollout(path: Path) -> dict[str, Any]:
    bytes_by_record_type: Counter[str] = Counter()
    records_by_record_type: Counter[str] = Counter()
    compacted_lengths: list[int] = []
    compacted_replacement_history_lengths: list[int] = []
    total_bytes = 0
    total_records = 0
    source_class = "unknown"

    with path.open("rb") as rollout:
        for line in rollout:
            line_bytes = len(line)
            total_bytes += line_bytes
            total_records += 1

            # Current rollout JSON puts the top-level type before payload. Looking only at
            # this bounded prefix avoids parsing or retaining private transcript values.
            prefix = line[:4096]
            type_match = TYPE_RE.search(prefix)
            record_type = (
                type_match.group(1).decode("ascii", errors="replace")
                if type_match
                else "unknown"
            )
            payload_match = PAYLOAD_TYPE_RE.search(prefix)
            payload_type = (
                payload_match.group(1).decode("ascii", errors="replace")
                if payload_match
                else "-"
            )
            type_key = f"{record_type}/{payload_type}"
            bytes_by_record_type[type_key] += line_bytes
            records_by_record_type[type_key] += 1

            if record_type == "compacted":
                compacted_lengths.append(line_bytes)
                if REPLACEMENT_HISTORY_FIELD in line:
                    compacted_replacement_history_lengths.append(line_bytes)
            elif record_type == "session_meta" and source_class == "unknown":
                source_class = session_source_class(line)

    compacted_bytes = sum(compacted_lengths)
    return {
        "file_bytes": total_bytes,
        "records": total_records,
        "compacted_records": len(compacted_lengths),
        "compacted_bytes": compacted_bytes,
        "compacted_share": compacted_bytes / total_bytes if total_bytes else 0.0,
        "source_class": source_class,
        "compacted_record_bytes": compacted_lengths,
        "compacted_replacement_history_record_bytes": (
            compacted_replacement_history_lengths
        ),
        "bytes_by_record_type": bytes_by_record_type,
        "records_by_record_type": records_by_record_type,
    }


def parse_utc_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise argparse.ArgumentTypeError("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def discover_rollouts(root: Path, modified_before: datetime | None) -> list[Path]:
    paths = (path for path in root.rglob("*.jsonl") if path.is_file())
    if modified_before is not None:
        cutoff = modified_before.timestamp()
        paths = (path for path in paths if path.stat().st_mtime <= cutoff)
    return sorted(paths)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--largest", type=int, default=12)
    parser.add_argument("--modified-before", type=parse_utc_timestamp)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    paths = discover_rollouts(args.root, args.modified_before)
    scans = [scan_rollout(path) for path in paths]
    scans.sort(key=lambda result: result["file_bytes"], reverse=True)

    total_bytes = sum(result["file_bytes"] for result in scans)
    total_records = sum(result["records"] for result in scans)
    compacted_lengths = [
        length
        for result in scans
        for length in result.pop("compacted_record_bytes")
    ]
    compacted_replacement_history_lengths = [
        length
        for result in scans
        for length in result.pop("compacted_replacement_history_record_bytes")
    ]
    compacted_bytes = sum(compacted_lengths)
    bytes_by_record_type: Counter[str] = Counter()
    records_by_record_type: Counter[str] = Counter()
    for result in scans:
        bytes_by_record_type.update(result.pop("bytes_by_record_type"))
        records_by_record_type.update(result.pop("records_by_record_type"))

    largest_files = []
    for rank, result in enumerate(scans[: max(args.largest, 0)], start=1):
        largest_files.append(
            {
                "rank": rank,
                **result,
            }
        )

    output = {
        "schema_version": 1,
        "privacy": {
            "paths_retained": False,
            "filenames_retained": False,
            "thread_ids_retained": False,
            "transcript_content_parsed": False,
            "transcript_content_retained": False,
            "session_metadata_source_class_parsed": True,
            "unrecognized_source_classes_retained": False,
        },
        "input": {
            "rollout_files": len(scans),
            "modified_before_utc": (
                args.modified_before.isoformat().replace("+00:00", "Z")
                if args.modified_before
                else None
            ),
        },
        "totals": {
            "file_bytes": total_bytes,
            "records": total_records,
            "compacted_records": len(compacted_lengths),
            "compacted_bytes": compacted_bytes,
            "compacted_share": compacted_bytes / total_bytes if total_bytes else 0.0,
            "compacted_with_replacement_history_records": len(
                compacted_replacement_history_lengths
            ),
            "compacted_with_replacement_history_bytes": sum(
                compacted_replacement_history_lengths
            ),
            "files_at_least_1_gib": sum(
                result["file_bytes"] >= 1024**3 for result in scans
            ),
        },
        "compacted_record_size_bytes": {
            "minimum": min(compacted_lengths, default=0),
            "median": percentile(compacted_lengths, 0.5),
            "p90": percentile(compacted_lengths, 0.9),
            "p99": percentile(compacted_lengths, 0.99),
            "maximum": max(compacted_lengths, default=0),
        },
        "bytes_by_record_type": dict(bytes_by_record_type.most_common()),
        "records_by_record_type": dict(records_by_record_type.most_common()),
        "largest_files": largest_files,
    }
    rendered = json.dumps(output, indent=2, sort_keys=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
