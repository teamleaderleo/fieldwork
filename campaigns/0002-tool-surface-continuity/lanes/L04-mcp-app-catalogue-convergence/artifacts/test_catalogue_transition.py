from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from catalogue_transition_probe import run_probe


class CatalogueTransitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory(prefix="fieldwork-l04-test-")
        cls.output = Path(cls.temp.name) / "latest.json"
        cls.payload = run_probe(cls.output)
        cls.checkpoints = {item["label"]: item for item in cls.payload["checkpoints"]}

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_stub_baseline_agrees_and_executes(self) -> None:
        point = self.checkpoints["01-stub-baseline"]
        self.assertEqual(point["global"]["tools"], ["offline_status"])
        self.assertEqual(point["binding"]["tools"], point["global"]["tools"])
        self.assertEqual(point["router"]["registered"], point["model"]["advertised"])
        self.assertTrue(point["execution"]["router_smoke"]["offline_status"].endswith(":ok"))

    def test_server_transition_first_leaves_binding_stale(self) -> None:
        point = self.checkpoints["02-server-became-real-before-refresh"]
        self.assertEqual(point["global"]["tools"], ["catalogue_version", "echo", "health"])
        self.assertEqual(point["binding"]["tools"], ["offline_status"])
        self.assertEqual(point["router"]["registered"], ["offline_status"])
        self.assertEqual(point["model"]["advertised"], ["offline_status"])
        self.assertTrue(point["execution"]["router_smoke"]["offline_status"].startswith("ERROR:"))
        self.assertTrue(point["execution"]["raw_control_plane_smoke"]["echo"].endswith(":ok"))

    def test_ordinary_refresh_reuses_stale_client(self) -> None:
        point = self.checkpoints["03-ordinary-refresh-same-config"]
        self.assertEqual(point["refresh_action"], "reused")
        self.assertNotEqual(point["global"]["catalogue_digest"], point["binding"]["catalogue_digest"])

    def test_reconnect_fresh_thread_and_restart_converge(self) -> None:
        for label in ("04-fresh-thread", "05-explicit-reconnect", "06-full-restart"):
            point = self.checkpoints[label]
            self.assertEqual(point["global"]["tools"], point["binding"]["tools"], label)
            self.assertEqual(point["binding"]["tools"], point["router"]["registered"], label)
            self.assertEqual(point["router"]["registered"], point["model"]["advertised"], label)

    def test_identity_only_change_is_invisible_to_ordinary_refresh(self) -> None:
        point = self.checkpoints["07-identity-only-ordinary-refresh"]
        self.assertEqual(point["refresh_action"], "reused")
        self.assertNotEqual(
            point["global"]["server_identity_digest"],
            point["binding"]["server_identity_digest"],
        )
        self.assertEqual(point["global"]["tools"], point["binding"]["tools"])

    def test_catalogue_only_change_is_invisible_to_ordinary_refresh(self) -> None:
        point = self.checkpoints["08-catalogue-only-ordinary-refresh"]
        self.assertEqual(point["refresh_action"], "reused")
        self.assertEqual(
            point["global"]["server_identity_digest"],
            point["binding"]["server_identity_digest"],
        )
        self.assertNotEqual(point["global"]["catalogue_digest"], point["binding"]["catalogue_digest"])

    def test_connection_identity_change_forces_convergence(self) -> None:
        point = self.checkpoints["09-connection-config-change"]
        self.assertEqual(point["refresh_action"], "reconnected")
        self.assertEqual(point["global"]["catalogue_digest"], point["binding"]["catalogue_digest"])
        self.assertEqual(
            point["global"]["server_identity_digest"],
            point["binding"]["server_identity_digest"],
        )


if __name__ == "__main__":
    unittest.main()
