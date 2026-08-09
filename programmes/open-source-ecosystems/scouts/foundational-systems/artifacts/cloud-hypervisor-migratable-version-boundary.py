#!/usr/bin/env python3
"""Check Cloud Hypervisor's MIGRATABLE_VERSION source boundary.

This is a no-network source probe for issue 8616. Point it at a Cloud
Hypervisor checkout. It does not run Docker, download releases, or require a
hypervisor device.

It checks whether the current dev_cli/integration path can carry a requested
previous-release version and whether the workload manifest still hard-pins the
live-upgrade binary to v39.0.

Usage:
    python3 cloud-hypervisor-migratable-version-boundary.py /path/to/cloud-hypervisor
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def read(root: Path, relative: str) -> str:
    path = root / relative
    if not path.is_file():
        raise SystemExit(f"missing required file: {path}")
    return path.read_text()


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {Path(sys.argv[0]).name} /path/to/cloud-hypervisor")

    root = Path(sys.argv[1]).resolve()
    dev_cli = read(root, "scripts/dev_cli.sh")
    x86 = read(root, "scripts/run_integration_tests_x86_64.sh")
    arm = read(root, "scripts/run_integration_tests_aarch64.sh")
    assets = read(root, "scripts/test_assets.yaml")
    fetcher = read(root, "scripts/fetch_workloads.py")

    previous_asset_urls = re.findall(
        r"url:\s*(https://github\.com/cloud-hypervisor/cloud-hypervisor/releases/download/([^/]+)/cloud-hypervisor-static(?:-aarch64)?)",
        assets,
    )
    pinned_versions = [version for _, version in previous_asset_urls]

    checks = {
        "dev_cli_forwards_migratable_version": "MIGRATABLE_VERSION" in dev_cli,
        "x86_runner_consumes_migratable_version": "MIGRATABLE_VERSION" in x86,
        "aarch64_runner_consumes_migratable_version": "MIGRATABLE_VERSION" in arm,
        "fetcher_consumes_migratable_version": "MIGRATABLE_VERSION" in fetcher,
        "previous_release_assets_found": len(previous_asset_urls) >= 2,
        "previous_release_assets_all_v39": bool(pinned_versions)
        and all(version == "v39.0" for version in pinned_versions),
    }

    for name, value in checks.items():
        print(f"{name}={value}")
    print(f"previous_release_versions={pinned_versions}")

    dynamic_path = any(
        checks[name]
        for name in (
            "dev_cli_forwards_migratable_version",
            "x86_runner_consumes_migratable_version",
            "aarch64_runner_consumes_migratable_version",
            "fetcher_consumes_migratable_version",
        )
    )
    hard_pinned = checks["previous_release_assets_all_v39"]

    print(f"dynamic_version_path_present={dynamic_path}")
    print(f"manifest_hard_pinned_v39={hard_pinned}")

    # Exit non-zero exactly for the source shape described by issue 8616:
    # no dynamic version path remains while the previous-release asset is
    # statically fixed to v39.0. This makes the script usable as a regression
    # probe for a future candidate.
    if not dynamic_path and hard_pinned:
        print("result=REGRESSION_SHAPE_PRESENT")
        return 1

    print("result=REGRESSION_SHAPE_NOT_PRESENT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
