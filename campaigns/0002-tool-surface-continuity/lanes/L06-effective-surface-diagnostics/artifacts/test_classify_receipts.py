import json
import tempfile
import unittest
from pathlib import Path

from classify_receipts import (
    classify,
    run,
    validate_document,
    validate_privacy,
    validate_receipt_schema,
)


class ReceiptClassifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(Path("fixtures.json").read_text(encoding="utf-8"))
        cls.by_id = {
            receipt["receipt_id"]: receipt for receipt in cls.document["receipts"]
        }

    def test_all_fixture_expectations(self):
        for receipt in self.document["receipts"]:
            with self.subTest(receipt=receipt["receipt_id"]):
                result = classify(receipt)
                expected = receipt["expected"]
                self.assertEqual(
                    expected["first_divergent_layer"],
                    result["first_divergent_layer"],
                )
                self.assertEqual(expected["typed_reason"], result["typed_reason"])

    def test_schema_accepts_all_retained_fixtures(self):
        validate_document(self.document)
        for receipt in self.document["receipts"]:
            with self.subTest(receipt=receipt["receipt_id"]):
                validate_receipt_schema(receipt)

    def test_schema_rejects_missing_required_receipt_field(self):
        receipt = dict(self.document["receipts"][0])
        del receipt["transition"]
        with self.assertRaisesRegex(ValueError, "missing required field 'transition'"):
            validate_receipt_schema(receipt)

    def test_schema_rejects_unknown_receipt_field(self):
        receipt = dict(self.document["receipts"][0])
        receipt["unexpected"] = True
        with self.assertRaisesRegex(ValueError, "unknown field 'unexpected'"):
            validate_receipt_schema(receipt)

    def test_schema_rejects_unknown_view_and_view_field(self):
        receipt = json.loads(json.dumps(self.document["receipts"][0]))
        receipt["views"]["unknown_view"] = {"state": "present"}
        with self.assertRaisesRegex(ValueError, "unknown view 'unknown_view'"):
            validate_receipt_schema(receipt)

        receipt = json.loads(json.dumps(self.document["receipts"][0]))
        receipt["views"]["router"] = {
            "state": "present",
            "tool_name": "retained-sensitive-name",
        }
        with self.assertRaisesRegex(ValueError, "unknown field 'tool_name'"):
            validate_receipt_schema(receipt)

    def test_schema_rejects_wrong_enums_and_primitive_types(self):
        receipt = json.loads(json.dumps(self.document["receipts"][0]))
        receipt["operation_kind"] = "unknown"
        with self.assertRaisesRegex(ValueError, "operation_kind"):
            validate_receipt_schema(receipt)

        receipt = json.loads(json.dumps(self.document["receipts"][0]))
        receipt["views"]["saved_host"]["state"] = "maybe"
        with self.assertRaisesRegex(ValueError, "saved_host.*state"):
            validate_receipt_schema(receipt)

        receipt = json.loads(json.dumps(self.document["receipts"][0]))
        receipt["views"]["saved_host"]["count"] = True
        with self.assertRaisesRegex(
            ValueError, "count must be a nonnegative integer"
        ):
            validate_receipt_schema(receipt)

    def test_schema_rejects_empty_observation_set(self):
        receipt = dict(self.document["receipts"][0])
        receipt["views"] = {}
        with self.assertRaisesRegex(ValueError, "views must contain an observation"):
            validate_receipt_schema(receipt)

    def test_document_contract_is_bounded(self):
        invalid = dict(self.document)
        invalid["unexpected"] = True
        with self.assertRaisesRegex(ValueError, "document has unknown field"):
            validate_document(invalid)

        invalid = dict(self.document)
        invalid["receipts"] = {}
        with self.assertRaisesRegex(
            ValueError, "document.receipts must be an array"
        ):
            validate_document(invalid)

    def test_privacy_allowlist(self):
        for receipt in self.document["receipts"]:
            with self.subTest(receipt=receipt["receipt_id"]):
                self.assertEqual([], validate_privacy(receipt))

    def test_privacy_rejects_arguments(self):
        receipt = dict(self.document["receipts"][0])
        receipt["arguments"] = {"secret": "value"}
        self.assertIn("arguments", validate_privacy(receipt))

    def test_unavailable_views_do_not_create_false_divergence(self):
        result = classify(
            self.by_id["l08-healthy-coexistence-after-context-summary"]
        )
        self.assertEqual("no_observed_divergence", result["classification"])
        self.assertIn("router", result["unavailable_views"])

    def test_request_divergence_precedes_later_unavailable_layers(self):
        result = classify(self.by_id["l02-clean-prewarm-lite"])
        self.assertEqual("wire_request", result["first_divergent_layer"])

    def test_catalogue_divergence_precedes_router_and_execution(self):
        result = classify(self.by_id["l04-stub-real-ordinary-refresh"])
        self.assertEqual("binding", result["first_divergent_layer"])

    def test_run_rejects_schema_drift_before_classification(self):
        document = json.loads(json.dumps(self.document))
        document["receipts"][0]["views"]["router"] = {
            "state": "present",
            "tool_name": "retained-sensitive-name",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "invalid.json"
            output_path = Path(temp_dir) / "result.json"
            input_path.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unknown field 'tool_name'"):
                run(input_path, output_path)
            self.assertFalse(output_path.exists())

    def test_run_writes_identical_zero_mismatch_summary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "result.json"
            summary = run(Path("fixtures.json"), output)
            self.assertEqual([], summary["expectation_mismatches"])
            self.assertEqual(8, summary["receipt_count"])
            self.assertEqual(
                Path("results/latest.json").read_text(encoding="utf-8"),
                output.read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
