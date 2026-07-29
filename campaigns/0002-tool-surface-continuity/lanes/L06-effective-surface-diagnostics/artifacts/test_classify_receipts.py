import json
import tempfile
import unittest
from pathlib import Path

from classify_receipts import classify, run, validate_privacy


class ReceiptClassifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(Path("fixtures.json").read_text(encoding="utf-8"))
        cls.by_id = {receipt["receipt_id"]: receipt for receipt in cls.document["receipts"]}

    def test_all_fixture_expectations(self):
        for receipt in self.document["receipts"]:
            with self.subTest(receipt=receipt["receipt_id"]):
                result = classify(receipt)
                expected = receipt["expected"]
                self.assertEqual(expected["first_divergent_layer"], result["first_divergent_layer"])
                self.assertEqual(expected["typed_reason"], result["typed_reason"])

    def test_privacy_allowlist(self):
        for receipt in self.document["receipts"]:
            with self.subTest(receipt=receipt["receipt_id"]):
                self.assertEqual([], validate_privacy(receipt))

    def test_privacy_rejects_arguments(self):
        receipt = dict(self.document["receipts"][0])
        receipt["arguments"] = {"secret": "value"}
        self.assertIn("arguments", validate_privacy(receipt))

    def test_unavailable_views_do_not_create_false_divergence(self):
        result = classify(self.by_id["l08-healthy-coexistence-after-context-summary"])
        self.assertEqual("no_observed_divergence", result["classification"])
        self.assertIn("router", result["unavailable_views"])

    def test_request_divergence_precedes_later_unavailable_layers(self):
        result = classify(self.by_id["l02-clean-prewarm-lite"])
        self.assertEqual("wire_request", result["first_divergent_layer"])

    def test_catalogue_divergence_precedes_router_and_execution(self):
        result = classify(self.by_id["l04-stub-real-ordinary-refresh"])
        self.assertEqual("binding", result["first_divergent_layer"])

    def test_run_writes_zero_mismatch_summary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "result.json"
            summary = run(Path("fixtures.json"), output)
            self.assertEqual([], summary["expectation_mismatches"])
            self.assertEqual(8, summary["receipt_count"])
            self.assertTrue(output.exists())


if __name__ == "__main__":
    unittest.main()
