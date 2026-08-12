#!/usr/bin/env python3
"""
Dependency-free model for the VDFL uv-tool state proposal.

This is a filesystem state-machine experiment, not production code.
It models:
- an explicitly claimed tool root;
- immutable complete generations;
- one atomic active-generation pointer per tool;
- stable public launcher metadata;
- rollback;
- unexpected-child findings and reversible quarantine;
- preservation of foreign public executables.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

PACKAGE_NAME = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$")


@dataclass(frozen=True)
class Finding:
    code: str
    subject: str
    summary: str
    confidence: str
    safety: str
    repair: str | None = None


class ToolRoot:
    def __init__(self, root: Path):
        self.root = root
        self.internal = root / ".uv"

    @classmethod
    def init(cls, root: Path) -> "ToolRoot":
        root.mkdir(parents=True, exist_ok=True)
        internal = root / ".uv"
        for path in [
            internal / "catalog",
            internal / "generations",
            internal / "active",
            internal / "public",
            internal / "quarantine",
            internal / "staging",
        ]:
            path.mkdir(parents=True, exist_ok=True)
        marker = internal / "root.json"
        if not marker.exists():
            marker.write_text(json.dumps({"schema": 1, "kind": "uv-tool-root", "id": "R1"}) + "\n")
        return cls(root)

    def claimed(self) -> bool:
        try:
            marker = json.loads((self.internal / "root.json").read_text())
        except (OSError, json.JSONDecodeError):
            return False
        return marker.get("kind") == "uv-tool-root" and marker.get("schema") == 1

    def spec_path(self, tool: str) -> Path:
        return self.internal / "catalog" / f"{tool}.json"

    def active_path(self, tool: str) -> Path:
        return self.internal / "active" / tool

    def generation_dir(self, tool: str, generation: int) -> Path:
        return self.internal / "generations" / tool / f"{generation:06d}"

    def stage_dir(self, tool: str, generation: int) -> Path:
        return self.internal / "staging" / f"{tool}-{generation:06d}"

    def public_path(self, entrypoint: str) -> Path:
        return self.internal / "public" / entrypoint

    def write_spec(self, tool: str, requirement: str) -> None:
        self.spec_path(tool).write_text(
            json.dumps({"schema": 1, "tool": tool, "requirement": requirement}, sort_keys=True) + "\n"
        )

    def active_generation(self, tool: str) -> int | None:
        try:
            return int(self.active_path(tool).read_text().strip())
        except (OSError, ValueError):
            return None

    def _atomic_set_active(self, tool: str, generation: int) -> None:
        target = self.active_path(tool)
        tmp = target.with_name(target.name + ".tmp")
        tmp.write_text(f"{generation}\n")
        os.replace(tmp, target)

    def prepare_generation(
        self,
        tool: str,
        generation: int,
        version: str,
        entrypoints: Iterable[str],
        *,
        fail_before_complete: bool = False,
    ) -> Path:
        stage = self.stage_dir(tool, generation)
        shutil.rmtree(stage, ignore_errors=True)
        (stage / "bin").mkdir(parents=True)
        eps = sorted(set(entrypoints))
        for ep in eps:
            (stage / "bin" / ep).write_text(f"{tool} {version} via {ep}\n")
        (stage / "generation.json").write_text(
            json.dumps(
                {"schema": 1, "tool": tool, "generation": generation, "version": version, "entrypoints": eps},
                sort_keys=True,
            )
            + "\n"
        )
        if fail_before_complete:
            raise RuntimeError("injected failure before generation completion")
        (stage / "complete").write_text("complete\n")
        return stage

    def publish_generation(self, tool: str, generation: int, stage: Path) -> None:
        if not (stage / "complete").is_file():
            raise RuntimeError("refusing to publish incomplete generation")
        dest = self.generation_dir(tool, generation)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            raise RuntimeError(f"generation already exists: {generation}")
        os.replace(stage, dest)

    def generation_manifest(self, tool: str, generation: int) -> dict:
        path = self.generation_dir(tool, generation)
        if not (path / "complete").is_file():
            raise RuntimeError("generation is incomplete")
        return json.loads((path / "generation.json").read_text())

    def ensure_public_launchers(self, tool: str, generation: int) -> list[Finding]:
        manifest = self.generation_manifest(tool, generation)
        findings: list[Finding] = []
        desired = set(manifest["entrypoints"])
        for ep in desired:
            path = self.public_path(ep)
            payload = {"schema": 1, "root_id": "R1", "tool": tool, "entrypoint": ep}
            if path.exists():
                try:
                    existing = json.loads(path.read_text())
                except (OSError, json.JSONDecodeError):
                    findings.append(
                        Finding(
                            "F3101",
                            str(path),
                            f"foreign public executable blocks `{ep}`",
                            "certain",
                            "destructive",
                            None,
                        )
                    )
                    continue
                if existing != payload:
                    findings.append(
                        Finding(
                            "F3102",
                            str(path),
                            f"public executable `{ep}` is owned by different managed identity",
                            "certain",
                            "destructive",
                            None,
                        )
                    )
                    continue
            else:
                path.write_text(json.dumps(payload, sort_keys=True) + "\n")
        return findings

    def reconcile_retired_launchers(
        self, tool: str, generation: int, *, dry_run: bool = True
    ) -> list[str]:
        manifest = self.generation_manifest(tool, generation)
        desired = set(manifest["entrypoints"])
        actions: list[str] = []
        for path in (self.internal / "public").iterdir():
            if not path.is_file():
                continue
            try:
                launcher = json.loads(path.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            if launcher.get("root_id") != "R1" or launcher.get("tool") != tool:
                continue
            entrypoint = launcher.get("entrypoint")
            if entrypoint in desired:
                continue
            actions.append(f"remove retired launcher {path}")
            if not dry_run:
                path.unlink()
        return actions

    def install(
        self,
        tool: str,
        generation: int,
        version: str,
        entrypoints: Iterable[str],
        *,
        fail_before_switch: bool = False,
    ) -> None:
        if not self.claimed():
            raise RuntimeError("tool root is not claimed")
        stage = self.prepare_generation(tool, generation, version, entrypoints)
        self.publish_generation(tool, generation, stage)
        collisions = self.ensure_public_launchers(tool, generation)
        if collisions:
            raise RuntimeError(collisions[0].summary)
        if fail_before_switch:
            raise RuntimeError("injected failure before active pointer switch")
        self._atomic_set_active(tool, generation)

    def resolve(self, entrypoint: str) -> Path:
        launcher = json.loads(self.public_path(entrypoint).read_text())
        if launcher.get("root_id") != "R1":
            raise RuntimeError("launcher root identity mismatch")
        tool = launcher["tool"]
        generation = self.active_generation(tool)
        if generation is None:
            raise RuntimeError(f"tool `{tool}` has no active generation")
        manifest = self.generation_manifest(tool, generation)
        if entrypoint not in manifest["entrypoints"]:
            raise RuntimeError(f"entrypoint `{entrypoint}` is retired in active generation")
        target = self.generation_dir(tool, generation) / "bin" / entrypoint
        if not target.is_file():
            raise RuntimeError(f"active generation missing entrypoint: {target}")
        return target

    def rollback(self, tool: str, generation: int) -> None:
        self.generation_manifest(tool, generation)
        self._atomic_set_active(tool, generation)

    def doctor(self) -> list[Finding]:
        findings: list[Finding] = []
        if not self.claimed():
            return [
                Finding(
                    "F0001",
                    str(self.root),
                    "configured tool directory is not initialized for this manager",
                    "certain",
                    "unknown",
                    None,
                )
            ]

        for child in self.root.iterdir():
            if child.name == ".uv":
                continue
            if child.is_dir() and not PACKAGE_NAME.fullmatch(child.name):
                findings.append(
                    Finding(
                        "F1001",
                        str(child),
                        "invalid tool directory name",
                        "certain",
                        "reversible",
                        "quarantine",
                    )
                )

        for spec_file in (self.internal / "catalog").glob("*.json"):
            spec = json.loads(spec_file.read_text())
            tool = spec["tool"]
            active = self.active_generation(tool)
            if active is None:
                findings.append(
                    Finding(
                        "F2101",
                        tool,
                        "tool has recorded desired state but no active generation",
                        "certain",
                        "reversible",
                        "rebuild",
                    )
                )
                continue
            gen = self.generation_dir(tool, active)
            if not (gen / "complete").is_file():
                findings.append(
                    Finding(
                        "F2102",
                        str(gen),
                        "active generation is incomplete",
                        "certain",
                        "reversible",
                        "rollback-or-rebuild",
                    )
                )

        return findings

    def repair(self, *, dry_run: bool = True) -> list[str]:
        actions: list[str] = []
        for finding in self.doctor():
            if finding.code == "F1001" and finding.repair == "quarantine":
                src = Path(finding.subject)
                dest = self.internal / "quarantine" / src.name
                actions.append(f"quarantine {src} -> {dest}")
                if not dry_run:
                    if dest.exists():
                        raise RuntimeError(f"quarantine destination exists: {dest}")
                    os.replace(src, dest)
        return actions


def run_scenarios() -> dict:
    with tempfile.TemporaryDirectory() as td:
        root = ToolRoot.init(Path(td) / "tools")
        root.write_spec("black", "black>=25")

        # Initial complete generation.
        root.install("black", 1, "25.0", ["black", "blackd"])
        assert root.active_generation("black") == 1
        assert "25.0" in root.resolve("black").read_text()
        assert "25.0" in root.resolve("blackd").read_text()

        # A failed candidate may be complete on disk but never becomes active.
        try:
            root.install("black", 2, "25.1", ["black", "blackd"], fail_before_switch=True)
        except RuntimeError as err:
            assert "before active pointer switch" in str(err)
        assert root.active_generation("black") == 1
        assert "25.0" in root.resolve("black").read_text()

        # Retrying as generation 3 commits through one pointer change.
        root.install("black", 3, "25.1", ["black", "blackd"])
        assert root.active_generation("black") == 3
        assert "25.1" in root.resolve("black").read_text()
        assert "25.1" in root.resolve("blackd").read_text()

        # Rollback requires no rebuild.
        root.rollback("black", 1)
        assert "25.0" in root.resolve("black").read_text()
        root.rollback("black", 3)

        # Unexpected root child becomes a reversible finding.
        bad = root.root / "tool backup"
        bad.mkdir()
        findings = root.doctor()
        assert any(f.code == "F1001" and f.subject == str(bad) for f in findings)
        plan = root.repair(dry_run=True)
        assert plan and bad.exists()
        applied = root.repair(dry_run=False)
        assert applied == plan
        assert not bad.exists()
        assert (root.internal / "quarantine" / "tool backup").exists()

        # A later generation may retire an entrypoint without making cleanup the commit point.
        root.install("black", 4, "25.2", ["black"])
        assert root.active_generation("black") == 4
        assert "25.2" in root.resolve("black").read_text()
        try:
            root.resolve("blackd")
        except RuntimeError as err:
            assert "retired" in str(err)
        else:
            raise AssertionError("retired entrypoint unexpectedly resolved old code")
        cleanup_plan = root.reconcile_retired_launchers("black", 4, dry_run=True)
        assert cleanup_plan and root.public_path("blackd").exists()
        root.reconcile_retired_launchers("black", 4, dry_run=False)
        assert not root.public_path("blackd").exists()

        # A foreign public file is preserved and blocks publication.
        foreign = root.public_path("black-beta")
        foreign.write_text("FOREIGN\n")
        stage = root.prepare_generation("black", 5, "26.0", ["black", "black-beta"])
        root.publish_generation("black", 5, stage)
        findings = root.ensure_public_launchers("black", 5)
        assert any(f.code == "F3101" for f in findings)
        assert foreign.read_text() == "FOREIGN\n"
        assert root.active_generation("black") == 4

        # An unclaimed custom root gets diagnosis only: no quarantine action is offered.
        unclaimed_dir = Path(td) / "wrong-root"
        unclaimed_dir.mkdir()
        (unclaimed_dir / "tool backup").mkdir()
        unclaimed = ToolRoot(unclaimed_dir)
        unclaimed_findings = unclaimed.doctor()
        assert [f.code for f in unclaimed_findings] == ["F0001"]
        assert unclaimed.repair(dry_run=True) == []
        assert (unclaimed_dir / "tool backup").exists()

        return {
            "active_generation": root.active_generation("black"),
            "black_target": str(root.resolve("black")),
            "quarantine_exists": (root.internal / "quarantine" / "tool backup").exists(),
            "foreign_preserved": foreign.read_text() == "FOREIGN\n",
            "retired_launcher_removed": not root.public_path("blackd").exists(),
            "unclaimed_root_preserved": (unclaimed_dir / "tool backup").exists(),
            "findings": [f.code for f in findings],
        }


if __name__ == "__main__":
    print(json.dumps(run_scenarios(), indent=2, sort_keys=True))
