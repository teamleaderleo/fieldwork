#!/usr/bin/env python3
"""Deterministic DuckDB boundary probes for Fieldwork issue 28."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from typing import Any, Callable

import duckdb

ROWS = 50_000
INTERRUPT_RANGE = 100_000
SPILL_ROWS = 1_500_000


def error_record(exc: BaseException) -> dict[str, str]:
    return {"type": type(exc).__name__, "message": str(exc)}


def row_dicts(cursor: duckdb.DuckDBPyConnection) -> list[dict[str, Any]]:
    columns = [item[0] for item in cursor.description]
    return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]


def run_with_timed_interrupt(
    connection: duckdb.DuckDBPyConnection,
    sql: str,
    delay_seconds: float = 0.25,
) -> dict[str, Any]:
    timer = threading.Timer(delay_seconds, connection.interrupt)
    started = time.monotonic()
    timer.start()
    try:
        value = connection.execute(sql).fetchone()
        return {"value": value, "elapsed_seconds": time.monotonic() - started}
    except BaseException as exc:
        return {"error": error_record(exc), "elapsed_seconds": time.monotonic() - started}
    finally:
        timer.cancel()
        timer.join(timeout=5)


def probe_explicit_transaction_interrupt(root: Path) -> dict[str, Any]:
    database = root / "explicit_interrupt.duckdb"
    connection = duckdb.connect(str(database))
    connection.execute("CREATE TABLE facts(id BIGINT PRIMARY KEY)")
    connection.execute("INSERT INTO facts VALUES (0)")
    connection.execute("BEGIN TRANSACTION")
    connection.execute("INSERT INTO facts SELECT i FROM range(1, 101) t(i)")
    outcome = run_with_timed_interrupt(
        connection,
        f"SELECT sum(a.i * b.i) FROM range({INTERRUPT_RANGE}) a(i), "
        f"range({INTERRUPT_RANGE}) b(i)",
    )
    try:
        post_interrupt: dict[str, Any] = {
            "value": connection.execute("SELECT count(*) FROM facts").fetchone()[0]
        }
    except BaseException as exc:
        post_interrupt = {"error": error_record(exc)}
    try:
        connection.execute("ROLLBACK")
        rollback: dict[str, Any] = {"ok": True}
    except BaseException as exc:
        rollback = {"ok": False, "error": error_record(exc)}
    connection.close()
    verification = duckdb.connect(str(database), read_only=True)
    persisted_count = verification.execute("SELECT count(*) FROM facts").fetchone()[0]
    verification.close()
    return {
        "query_outcome": outcome,
        "post_interrupt": post_interrupt,
        "rollback": rollback,
        "persisted_count": persisted_count,
        "invariants": {
            "interrupt_raised": "error" in outcome,
            "transaction_requires_rollback": "error" in post_interrupt,
            "rollback_succeeds": rollback.get("ok") is True,
            "uncommitted_rows_absent": persisted_count == 1,
        },
    }


def probe_autocommit_insert_interrupt(root: Path) -> dict[str, Any]:
    database = root / "autocommit_interrupt.duckdb"
    connection = duckdb.connect(str(database))
    connection.execute("CREATE TABLE atomic_target(id BIGINT)")
    connection.execute("INSERT INTO atomic_target VALUES (-1)")
    outcome = run_with_timed_interrupt(
        connection,
        f"INSERT INTO atomic_target "
        f"SELECT a.i * {INTERRUPT_RANGE} + b.i "
        f"FROM range({INTERRUPT_RANGE}) a(i), range({INTERRUPT_RANGE}) b(i)",
    )
    count_after = connection.execute("SELECT count(*) FROM atomic_target").fetchone()[0]
    reusable_value = connection.execute("SELECT 42").fetchone()[0]
    connection.close()
    return {
        "query_outcome": outcome,
        "count_after": count_after,
        "reusable_value": reusable_value,
        "invariants": {
            "interrupt_raised": "error" in outcome,
            "statement_atomic": count_after == 1,
            "connection_reusable": reusable_value == 42,
        },
    }


def child_crash(database: Path, commit: bool) -> None:
    connection = duckdb.connect(str(database))
    connection.execute("BEGIN TRANSACTION")
    connection.execute(f"INSERT INTO durable SELECT i FROM range(1, {ROWS + 1}) t(i)")
    if commit:
        connection.execute("COMMIT")
    os._exit(18 if commit else 17)


def wal_state(database: Path) -> dict[str, Any]:
    wal = Path(str(database) + ".wal")
    return {"exists": wal.exists(), "size": wal.stat().st_size if wal.exists() else 0}


def run_crash_case(root: Path, name: str, commit: bool) -> dict[str, Any]:
    database = root / f"{name}.duckdb"
    connection = duckdb.connect(str(database))
    connection.execute("CREATE TABLE durable(id BIGINT PRIMARY KEY)")
    connection.execute("INSERT INTO durable VALUES (0)")
    connection.close()
    completed = subprocess.run(
        [sys.executable, __file__, "--child", str(database), "commit" if commit else "uncommitted"],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    before_reopen = wal_state(database)
    verification = duckdb.connect(str(database))
    count = verification.execute("SELECT count(*) FROM durable").fetchone()[0]
    checksum = verification.execute("SELECT sum(id) FROM durable").fetchone()[0]
    verification.close()
    after_reopen = wal_state(database)
    expected_count = ROWS + 1 if commit else 1
    expected_checksum = ROWS * (ROWS + 1) // 2 if commit else 0
    return {
        "child_returncode": completed.returncode,
        "wal_before_reopen": before_reopen,
        "wal_after_reopen": after_reopen,
        "count": count,
        "checksum": checksum,
        "invariants": {
            "child_exited_abruptly": completed.returncode in {17, 18},
            "visibility_matches_commit": count == expected_count,
            "checksum_matches_commit": checksum == expected_checksum,
        },
    }


def probe_crash_recovery(root: Path) -> dict[str, Any]:
    return {
        "uncommitted": run_crash_case(root, "crash_uncommitted", False),
        "committed": run_crash_case(root, "crash_committed", True),
    }


def directory_snapshot(path: Path) -> dict[str, Any]:
    files = []
    total = 0
    if path.exists():
        for entry in sorted(path.rglob("*")):
            if entry.is_file():
                size = entry.stat().st_size
                total += size
                files.append({"path": str(entry.relative_to(path)), "size": size})
    return {"total_bytes": total, "files": files}


def run_sort_case(root: Path, name: str, memory_limit: str) -> dict[str, Any]:
    database = root / f"{name}.duckdb"
    temp_directory = root / f"{name}_temp"
    output = root / f"{name}.parquet"
    temp_directory.mkdir()
    connection = duckdb.connect(str(database))
    connection.execute("SET threads = 1")
    connection.execute(f"SET memory_limit = '{memory_limit}'")
    connection.execute("SET preserve_insertion_order = false")
    connection.execute(f"SET temp_directory = '{str(temp_directory).replace("'", "''")}'")
    extension_before = row_dicts(
        connection.execute(
            "SELECT extension_name, loaded, installed, install_mode, installed_from "
            "FROM duckdb_extensions() WHERE extension_name = 'parquet'"
        )
    )
    stop_monitor = threading.Event()
    observations: list[dict[str, Any]] = []

    def monitor() -> None:
        while not stop_monitor.is_set():
            observations.append(directory_snapshot(temp_directory))
            time.sleep(0.005)
        observations.append(directory_snapshot(temp_directory))

    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()
    query_error: dict[str, str] | None = None
    try:
        connection.execute(
            f"COPY (SELECT i, md5(i::VARCHAR) AS payload "
            f"FROM range({SPILL_ROWS}) t(i) ORDER BY hash(i)) "
            f"TO '{str(output).replace("'", "''")}' (FORMAT PARQUET, COMPRESSION ZSTD)"
        )
    except BaseException as exc:
        query_error = error_record(exc)
    finally:
        stop_monitor.set()
        monitor_thread.join(timeout=10)
    peak = max(
        observations,
        key=lambda item: item["total_bytes"],
        default={"total_bytes": 0, "files": []},
    )
    extension_after = row_dicts(
        connection.execute(
            "SELECT extension_name, loaded, installed, install_mode, installed_from "
            "FROM duckdb_extensions() WHERE extension_name = 'parquet'"
        )
    )
    connection_reusable = connection.execute("SELECT 7").fetchone()[0]
    if output.exists():
        count, checksum = connection.execute(
            f"SELECT count(*), sum(i) FROM read_parquet('{str(output).replace("'", "''")}')"
        ).fetchone()
    else:
        count, checksum = None, None
    after_query = directory_snapshot(temp_directory)
    connection.close()
    after_close = directory_snapshot(temp_directory)
    return {
        "memory_limit": memory_limit,
        "query_error": query_error,
        "row_count": count,
        "checksum": checksum,
        "output_exists": output.exists(),
        "connection_reusable_value": connection_reusable,
        "peak_temp": peak,
        "temp_after_query": after_query,
        "temp_after_close": after_close,
        "extension_before": extension_before,
        "extension_after": extension_after,
    }


def probe_memory_pressure_and_parquet(root: Path) -> dict[str, Any]:
    baseline = run_sort_case(root, "baseline_128mb", "128MB")
    pressure = run_sort_case(root, "pressure_24mb", "24MB")
    expected_checksum = SPILL_ROWS * (SPILL_ROWS - 1) // 2
    second = duckdb.connect(str(root / "baseline_128mb.duckdb"))
    extension_second_before = row_dicts(
        second.execute(
            "SELECT extension_name, loaded, installed, install_mode, installed_from "
            "FROM duckdb_extensions() WHERE extension_name = 'parquet'"
        )
    )
    second_count = second.execute(
        f"SELECT count(*) FROM read_parquet('{str(root / "baseline_128mb.parquet").replace("'", "''")}')"
    ).fetchone()[0]
    second.close()
    return {
        "baseline": baseline,
        "pressure": pressure,
        "extension_second_connection_before": extension_second_before,
        "second_connection_count": second_count,
        "invariants": {
            "baseline_succeeds": baseline["query_error"] is None,
            "baseline_count": baseline["row_count"] == SPILL_ROWS,
            "baseline_checksum": baseline["checksum"] == expected_checksum,
            "pressure_spills": pressure["peak_temp"]["total_bytes"] > 0,
            "pressure_reports_oom": pressure["query_error"] is not None
            and pressure["query_error"]["type"] == "OutOfMemoryException",
            "pressure_leaves_no_output": pressure["output_exists"] is False,
            "pressure_connection_reusable": pressure["connection_reusable_value"] == 7,
            "pressure_temp_cleaned": pressure["temp_after_close"]["total_bytes"] == 0,
            "parquet_reopens": second_count == SPILL_ROWS,
        },
    }


def probe_connection_visibility(root: Path) -> dict[str, Any]:
    database = root / "connections.duckdb"
    first = duckdb.connect(str(database))
    second = duckdb.connect(str(database))
    first.execute("CREATE TABLE shared(id BIGINT)")
    first.execute("INSERT INTO shared VALUES (0)")
    first.execute("BEGIN TRANSACTION")
    first.execute("INSERT INTO shared SELECT i FROM range(1, 101) t(i)")
    first_local = first.execute("SELECT count(*) FROM shared").fetchone()[0]
    second_before = second.execute("SELECT count(*) FROM shared").fetchone()[0]
    first.execute("COMMIT")
    second_after = second.execute("SELECT count(*) FROM shared").fetchone()[0]

    started = threading.Event()
    outcome: dict[str, Any] = {}

    def long_query() -> None:
        started.set()
        try:
            outcome["value"] = first.execute(
                f"SELECT sum(a.i * b.i) FROM range({INTERRUPT_RANGE}) a(i), "
                f"range({INTERRUPT_RANGE}) b(i)"
            ).fetchone()
        except BaseException as exc:
            outcome["error"] = error_record(exc)

    thread = threading.Thread(target=long_query, daemon=True)
    thread.start()
    if not started.wait(timeout=5):
        raise RuntimeError("long query thread failed to start")
    time.sleep(0.25)
    sibling_value = second.execute("SELECT 84").fetchone()[0]
    first.interrupt()
    thread.join(timeout=30)
    if thread.is_alive():
        raise RuntimeError("manual interrupt failed to stop query")
    second_after_interrupt = second.execute("SELECT count(*) FROM shared").fetchone()[0]
    first.close()
    second.close()
    return {
        "first_local_count": first_local,
        "second_before_commit": second_before,
        "second_after_commit": second_after,
        "interrupted_query": outcome,
        "sibling_value_during_query": sibling_value,
        "second_after_interrupt": second_after_interrupt,
        "invariants": {
            "uncommitted_changes_connection_local": first_local == 101 and second_before == 1,
            "commit_visible_to_sibling": second_after == 101,
            "interrupt_targets_connection": "error" in outcome and sibling_value == 84,
            "sibling_remains_reusable": second_after_interrupt == 101,
        },
    }


def all_invariants(value: Any) -> list[bool]:
    checks: list[bool] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "invariants" and isinstance(child, dict):
                checks.extend(bool(item) for item in child.values())
            else:
                checks.extend(all_invariants(child))
    elif isinstance(value, list):
        for child in value:
            checks.extend(all_invariants(child))
    return checks


def run(output: Path) -> int:
    with tempfile.TemporaryDirectory(prefix="fieldwork-duckdb-28-") as temp:
        root = Path(temp)
        version_connection = duckdb.connect(":memory:")
        library_version = version_connection.execute(
            "SELECT library_version FROM pragma_version()"
        ).fetchone()[0]
        version_connection.close()
        results: dict[str, Any] = {
            "environment": {
                "duckdb_python_version": duckdb.__version__,
                "duckdb_library_version": library_version,
                "python": sys.version,
                "platform": platform.platform(),
                "processor": platform.processor(),
                "constants": {
                    "rows": ROWS,
                    "interrupt_range": INTERRUPT_RANGE,
                    "spill_rows": SPILL_ROWS,
                    "threads": 1,
                },
            },
            "probes": {},
        }
        probes: list[tuple[str, Callable[[Path], dict[str, Any]]]] = [
            ("explicit_transaction_interrupt", probe_explicit_transaction_interrupt),
            ("autocommit_insert_interrupt", probe_autocommit_insert_interrupt),
            ("crash_recovery", probe_crash_recovery),
            ("memory_pressure_and_parquet", probe_memory_pressure_and_parquet),
            ("connection_visibility", probe_connection_visibility),
        ]
        for name, probe in probes:
            try:
                results["probes"][name] = probe(root)
            except BaseException as exc:
                results["probes"][name] = {
                    "probe_error": error_record(exc),
                    "traceback": traceback.format_exc(),
                    "invariants": {"probe_completed": False},
                }
        checks = all_invariants(results["probes"])
        results["summary"] = {
            "invariant_count": len(checks),
            "invariant_pass_count": sum(checks),
            "all_invariants_passed": bool(checks) and all(checks),
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(output.read_text(encoding="utf-8"))
        return 0 if results["summary"]["all_invariants_passed"] else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("fieldwork/results/issue28-latest.json"),
    )
    parser.add_argument("--child", type=Path)
    parser.add_argument("child_mode", nargs="?", choices=["commit", "uncommitted"])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.child is not None:
        child_crash(args.child, args.child_mode == "commit")
        return 99
    return run(args.output)


if __name__ == "__main__":
    raise SystemExit(main())
