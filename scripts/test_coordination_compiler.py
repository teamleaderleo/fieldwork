#!/usr/bin/env python3
"""Regression tests for the pure static coordination compiler."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent))
import coordination_compiler as compiler


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "research" / "continuous-coordination" / "fixtures"
SCHEMA = ROOT / "research" / "continuous-coordination" / "schema" / "graph-v1.schema.json"


def node(
    node_id: str,
    *,
    kind: str = "evidence",
    state: str = "current",
    generation: int = 1,
    output_key: str | None = None,
    exclusive_output: bool = False,
    upstream_contact: bool | None = None,
) -> dict[str, object]:
    authority: dict[str, object] = {}
    if upstream_contact is not None:
        authority["upstream_contact"] = upstream_contact
    value: dict[str, object] = {
        "id": node_id,
        "generation": generation,
        "kind": kind,
        "semantic_state": state,
        "input_fingerprint": f"input:{node_id}:{generation}",
        "semantic_fingerprint": f"semantic:{node_id}:{generation}",
        "evaluator_revision": "coordination-compiler/v1",
        "policy_revision": "fieldwork-review/v1",
        "authority": authority,
    }
    if output_key is not None:
        value["output_key"] = output_key
        value["exclusive_output"] = exclusive_output
    return value


def graph(
    nodes: list[dict[str, object]], edges: list[dict[str, str]]
) -> dict[str, object]:
    return {
        "schema_version": compiler.SCHEMA_VERSION,
        "nodes": nodes,
        "edges": edges,
    }


class CoordinationCompilerTests(unittest.TestCase):
    def test_simple_chain_is_ready_and_deterministic(self) -> None:
        first = compiler.load_and_evaluate(FIXTURES / "simple-chain.json")
        second = compiler.load_and_evaluate(FIXTURES / "simple-chain.json")
        self.assertEqual(first, second)
        self.assertEqual(
            first["topological_order"],
            ["evidence", "receipt", "review", "queue"],
        )
        self.assertTrue(
            all(item["state"] == "ready" for item in first["evaluations"])
        )
        digest = hashlib.sha256(
            compiler.canonical_json(first).encode("utf-8")
        ).hexdigest()
        self.assertEqual(len(digest), 64)

    def test_blocked_queue_has_first_blocker_trace(self) -> None:
        result = compiler.load_and_evaluate(FIXTURES / "blocked-chain.json")
        evaluations = {item["id"]: item for item in result["evaluations"]}
        self.assertEqual(evaluations["receipt"]["state"], "missing-receipt")
        self.assertEqual(evaluations["queue"]["state"], "blocked")
        self.assertEqual(
            evaluations["queue"]["first_blocker_path"],
            ["queue", "receipt"],
        )

    def test_causal_history_loop_is_not_a_readiness_cycle(self) -> None:
        result = compiler.load_and_evaluate(FIXTURES / "causal-loop.json")
        self.assertEqual(result["topological_order"], ["attempt-1", "attempt-2"])

    def test_readiness_edges_are_prerequisite_to_dependent(self) -> None:
        value = compiler.normalize_graph(
            graph(
                [node("review"), node("queue")],
                [{"from": "review", "to": "queue", "kind": "requires-review"}],
            )
        )
        result = compiler.evaluate_graph(value, ["review"])
        self.assertEqual(result["topological_order"], ["review", "queue"])
        self.assertEqual(result["affected_nodes"], ["queue", "review"])

    def test_duplicate_node_is_rejected(self) -> None:
        with self.assertRaisesRegex(compiler.GraphError, "duplicate node id"):
            compiler.normalize_graph(graph([node("same"), node("same")], []))

    def test_missing_endpoint_is_rejected(self) -> None:
        value = graph(
            [node("evidence")],
            [{"from": "evidence", "to": "missing", "kind": "requires"}],
        )
        with self.assertRaisesRegex(compiler.GraphError, "does not exist"):
            compiler.normalize_graph(value)

    def test_readiness_self_cycle_is_rejected(self) -> None:
        value = graph(
            [node("evidence")],
            [{"from": "evidence", "to": "evidence", "kind": "requires"}],
        )
        with self.assertRaisesRegex(compiler.GraphError, "self-dependency"):
            compiler.normalize_graph(value)

    def test_multi_node_readiness_cycle_is_rejected(self) -> None:
        value = graph(
            [node("a"), node("b"), node("c")],
            [
                {"from": "a", "to": "b", "kind": "requires"},
                {"from": "b", "to": "c", "kind": "requires"},
                {"from": "c", "to": "a", "kind": "requires"},
            ],
        )
        with self.assertRaisesRegex(compiler.GraphError, "readiness cycle"):
            compiler.normalize_graph(value)

    def test_maximum_depth_chain_does_not_depend_on_python_recursion(self) -> None:
        nodes = [node(f"n-{index:04d}") for index in range(compiler.MAX_NODES)]
        edges = [
            {
                "from": f"n-{index:04d}",
                "to": f"n-{index + 1:04d}",
                "kind": "requires",
            }
            for index in range(compiler.MAX_NODES - 1)
        ]
        normalized = compiler.normalize_graph(graph(nodes, edges))
        result = compiler.evaluate_graph(normalized, ["n-0000"])
        self.assertEqual(len(result["topological_order"]), compiler.MAX_NODES)
        self.assertEqual(len(result["affected_nodes"]), compiler.MAX_NODES)
        self.assertEqual(result["topological_order"][0], "n-0000")
        self.assertEqual(
            result["topological_order"][-1],
            f"n-{compiler.MAX_NODES - 1:04d}",
        )

    def test_affected_descendants_exclude_unrelated_branch(self) -> None:
        value = compiler.normalize_graph(
            graph(
                [node("a"), node("b"), node("c"), node("unrelated")],
                [
                    {"from": "a", "to": "b", "kind": "requires"},
                    {"from": "b", "to": "c", "kind": "requires"},
                ],
            )
        )
        result = compiler.evaluate_graph(value, ["a"])
        self.assertEqual(result["affected_nodes"], ["a", "b", "c"])

    def test_exclusive_producers_are_rejected_without_selection(self) -> None:
        producers = [
            node("left", output_key="review-contract", exclusive_output=True),
            node("right", output_key="review-contract", exclusive_output=True),
        ]
        with self.assertRaisesRegex(compiler.GraphError, "unresolved producers"):
            compiler.normalize_graph(graph(producers, []))

        with self.assertRaisesRegex(compiler.GraphError, "unresolved producers"):
            compiler.normalize_graph(
                graph(
                    producers,
                    [{"from": "left", "to": "right", "kind": "competes"}],
                )
            )

    def test_authority_defaults_false_and_is_typed_input(self) -> None:
        defaulted = compiler.normalize_graph(graph([node("evidence")], []))
        self.assertFalse(defaulted["nodes"][0]["authority"]["upstream_contact"])

        explicit = compiler.normalize_graph(
            graph([node("decision", upstream_contact=True)], [])
        )
        self.assertTrue(explicit["nodes"][0]["authority"]["upstream_contact"])

        invalid = copy.deepcopy(graph([node("evidence")], []))
        invalid["nodes"][0]["authority"]["upstream_contact"] = "yes"
        with self.assertRaisesRegex(
            compiler.GraphError, "upstream_contact must be boolean"
        ):
            compiler.normalize_graph(invalid)

    def test_authority_gate_blocks_dependent_action(self) -> None:
        value = compiler.normalize_graph(
            graph(
                [
                    node(
                        "authority",
                        kind="authority-gate",
                        state="authority-mismatch",
                    ),
                    node("action", kind="queue-entry", upstream_contact=True),
                ],
                [
                    {
                        "from": "authority",
                        "to": "action",
                        "kind": "requires-authority",
                    }
                ],
            )
        )
        result = compiler.evaluate_graph(value)
        evaluations = {item["id"]: item for item in result["evaluations"]}
        self.assertEqual(evaluations["action"]["state"], "blocked")
        self.assertEqual(
            evaluations["action"]["first_blocker_path"],
            ["action", "authority"],
        )

    def test_unknown_fields_are_rejected_consistently(self) -> None:
        cases: list[dict[str, object]] = []

        top_level = graph([node("evidence")], [])
        top_level["unexpected"] = True
        cases.append(top_level)

        node_field = graph([node("evidence")], [])
        node_field["nodes"][0]["unexpected"] = True
        cases.append(node_field)

        authority_field = graph([node("evidence")], [])
        authority_field["nodes"][0]["authority"]["unexpected"] = True
        cases.append(authority_field)

        edge_field = graph(
            [node("a"), node("b")],
            [{"from": "a", "to": "b", "kind": "requires", "unexpected": True}],
        )
        cases.append(edge_field)

        for value in cases:
            with self.subTest(value=value):
                with self.assertRaisesRegex(compiler.GraphError, "unknown field"):
                    compiler.normalize_graph(value)

    def test_schema_and_compiler_contracts_match(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        node_schema = schema["$defs"]["node"]
        node_fields = node_schema["properties"]
        edge_fields = schema["$defs"]["edge"]["properties"]
        text_fields = [
            node_fields["id"],
            node_fields["input_fingerprint"],
            node_fields["semantic_fingerprint"],
            node_fields["evaluator_revision"],
            node_fields["policy_revision"],
            node_fields["output_key"],
            node_fields["generation"]["oneOf"][0],
            edge_fields["from"],
            edge_fields["to"],
        ]
        self.assertTrue(all(field.get("pattern") == "\\S" for field in text_fields))
        self.assertIn(
            {
                "if": {"required": ["exclusive_output"]},
                "then": {"required": ["output_key"]},
            },
            node_schema["allOf"],
        )

        with self.assertRaisesRegex(compiler.GraphError, "non-empty string"):
            compiler.normalize_graph(graph([node("   ")], []))

        invalid = node("producer")
        invalid["exclusive_output"] = False
        with self.assertRaisesRegex(compiler.GraphError, "requires an output_key"):
            compiler.normalize_graph(graph([invalid], []))


if __name__ == "__main__":
    unittest.main()
