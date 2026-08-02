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

    @staticmethod
    def minimal_document() -> dict:
        return {
            "schema_version": 1,
            "source_boundary": {
                "public_codex_revision": "a" * 40,
                "campaign_issue": 31,
                "fixture_sources": [35],
            },
            "receipts": [
                {
                    "schema_version": 1,
                    "receipt_id": "minimal",
                    "transition": "test",
                    "request_kind": "test",
                    "operation_kind": "read",
                    "views": {"router": {"state": "unavailable"}},
                    "expected": {
                        "first_divergent_layer": None,
                        "typed_reason": None,
                    },
                }
            ],
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

    def test_schema_rejects_boolean_schema_versions(self):
        document = json.loads(json.dumps(self.document))
        document["schema_version"] = True
        with self.assertRaisesRegex(ValueError, "document schema_version must be"):
            validate_document(document)

        receipt = json.loads(json.dumps(self.document["receipts"][0]))
        receipt["schema_version"] = True
        with self.assertRaisesRegex(ValueError, "unsupported schema_version"):
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

    def test_document_rejects_duplicate_receipt_ids(self):
        document = json.loads(json.dumps(self.document))
        document["receipts"][1]["receipt_id"] = document["receipts"][0][
            "receipt_id"
        ]
        with self.assertRaisesRegex(ValueError, "duplicate receipt_id"):
            validate_document(document)

    def test_source_boundary_is_strict_and_typed(self):
        document = self.minimal_document()
        document["source_boundary"]["unexpected"] = True
        with self.assertRaisesRegex(ValueError, "source_boundary has unknown field"):
            validate_document(document)

        document = self.minimal_document()
        document["source_boundary"]["campaign_issue"] = True
        with self.assertRaisesRegex(ValueError, "campaign_issue must be a positive"):
            validate_document(document)

        document = self.minimal_document()
        document["source_boundary"]["fixture_sources"] = [35, 35]
        with self.assertRaisesRegex(ValueError, "fixture_sources must be unique"):
            validate_document(document)

        document = self.minimal_document()
        document["source_boundary"]["public_codex_revision"] = "not-a-sha"
        with self.assertRaisesRegex(ValueError, "lowercase 40-hex"):
            validate_document(document)

    def test_expected_contract_rejects_unknown_fields(self):
        receipt = json.loads(json.dumps(self.document["receipts"][0]))
        receipt["expected"]["unexpected"] = True
        with self.assertRaisesRegex(ValueError, "expected has unknown field"):
            validate_receipt_schema(receipt)

    def test_privacy_allowlist(self):
        self.assertEqual([], validate_privacy(self.document))
        for receipt in self.document["receipts"]:
            with self.subTest(receipt=receipt["receipt_id"]):
                self.assertEqual([], validate_privacy(receipt))

    def test_privacy_rejects_arguments_and_source_boundary_prompt(self):
        receipt = dict(self.document["receipts"][0])
        receipt["arguments"] = {"secret": "value"}
        self.assertIn("arguments", validate_privacy(receipt))

        document = self.minimal_document()
        document["source_boundary"]["prompt"] = "retained"
        self.assertIn("source_boundary.prompt", validate_privacy(document))

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

    def test_run_rejects_privacy_violation_before_output(self):
        document = self.minimal_document()
        document["source_boundary"]["prompt"] = "retained"
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "invalid.json"
            output_path = Path(temp_dir) / "result.json"
            input_path.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "document privacy violations"):
                run(input_path, output_path)
            self.assertFalse(output_path.exists())

    def test_strict_loader_rejects_duplicate_members_at_every_depth(self):
        base = self.minimal_document()
        valid = json.dumps(base, separators=(",", ":"))
        duplicate_inputs = {
            "document": valid.replace(
                '{"schema_version":1,',
                '{"schema_version":1,"schema_version":1,',
                1,
            ),
            "source_boundary": valid.replace(
                '"campaign_issue":31,',
                '"campaign_issue":31,"campaign_issue":31,',
                1,
            ),
            "receipt": valid.replace(
                '"receipt_id":"minimal",',
                '"receipt_id":"minimal","receipt_id":"minimal",',
                1,
            ),
            "view": valid.replace(
                '"router":{"state":"unavailable"}',
                '"router":{"state":"unavailable","state":"unavailable"}',
                1,
            ),
            "expected": valid.replace(
                '"typed_reason":null',
                '"typed_reason":null,"typed_reason":null',
                1,
            ),
        }
        for depth, raw in duplicate_inputs.items():
            with self.subTest(depth=depth):
                with tempfile.TemporaryDirectory() as temp_dir:
                    input_path = Path(temp_dir) / "invalid.json"
                    output_path = Path(temp_dir) / "result.json"
                    input_path.write_text(raw, encoding="utf-8")
                    with self.assertRaisesRegex(
                        ValueError, "duplicate JSON object member"
                    ):
                        run(input_path, output_path)
                    self.assertFalse(output_path.exists())

    def test_strict_loader_rejects_nonstandard_constants_without_output(self):
        valid = json.dumps(self.minimal_document(), separators=(",", ":"))
        for constant in ("NaN", "Infinity", "-Infinity"):
            raw = valid.replace('"campaign_issue":31', f'"campaign_issue":{constant}')
            with self.subTest(constant=constant):
                with tempfile.TemporaryDirectory() as temp_dir:
                    input_path = Path(temp_dir) / "invalid.json"
                    output_path = Path(temp_dir) / "result.json"
                    input_path.write_text(raw, encoding="utf-8")
                    with self.assertRaisesRegex(
                        ValueError, "non-standard JSON constant"
                    ):
                        run(input_path, output_path)
                    self.assertFalse(output_path.exists())

    def test_raw_and_canonical_identities_are_distinct(self):
        document = self.minimal_document()
        compact = json.dumps(document, separators=(",", ":"))
        pretty = json.dumps(document, indent=2)
        with tempfile.TemporaryDirectory() as temp_dir:
            compact_input = Path(temp_dir) / "compact.json"
            pretty_input = Path(temp_dir) / "pretty.json"
            compact_output = Path(temp_dir) / "compact-result.json"
            pretty_output = Path(temp_dir) / "pretty-result.json"
            compact_input.write_text(compact, encoding="utf-8")
            pretty_input.write_text(pretty, encoding="utf-8")
            compact_summary = run(compact_input, compact_output)
            pretty_summary = run(pretty_input, pretty_output)

        self.assertNotEqual(
            compact_summary["raw_input_sha256"],
            pretty_summary["raw_input_sha256"],
        )
        self.assertEqual(
            compact_summary["canonical_input_sha256"],
            pretty_summary["canonical_input_sha256"],
        )
        self.assertEqual(
            compact_summary["input_digest"],
            pretty_summary["input_digest"],
        )
        self.assertEqual(64, len(compact_summary["raw_input_sha256"]))
        self.assertEqual(64, len(compact_summary["canonical_input_sha256"]))

    def test_run_writes_semantically_identical_zero_mismatch_summary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "result.json"
            summary = run(Path("fixtures.json"), output)
            self.assertEqual([], summary["expectation_mismatches"])
            self.assertEqual(8, summary["receipt_count"])
            actual = json.loads(output.read_text(encoding="utf-8"))
            legacy_actual = {
                key: value
                for key, value in actual.items()
                if key not in {"raw_input_sha256", "canonical_input_sha256"}
            }
            self.assertEqual(
                json.loads(Path("results/latest.json").read_text(encoding="utf-8")),
                legacy_actual,
            )
            self.assertEqual(64, len(actual["raw_input_sha256"]))
            self.assertEqual(64, len(actual["canonical_input_sha256"]))


if __name__ == "__main__":
    unittest.main()
