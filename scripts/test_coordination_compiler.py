#!/usr/bin/env python3
"""Regression tests for the pure static coordination compiler."""

from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent))
import coordination_compiler as compiler


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "research" / "continuous-coordination" / "fixtures"


def node(
    node_id: str,
    *,
    kind: str = "evidence",
    state: str = "current",
    generation: int = 1,
    output_key: str | None = None,
    exclusive_output: bool = False,
) -> dict[str, object]:
    value: dict[str, object] = {
        "id": node_id,
        "generation": generation,
        "kind": kind,
        "semantic_state": state,
        "input_fingerprint": f"input:{node_id}:{generation}",
        "semantic_fingerprint": f"semantic:{node_id}:{generation}",
        "evaluator_revision": "coordination-compiler/v1",
        "policy_revision": "fieldwork-review/v1",
        "authority": {},
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

    def test_duplicate_node_is_rejected(self) -> None:
        value = graph([node("same"), node("same")], [])
        with self.assertRaisesRegex(compiler.GraphError, "duplicate node id"):
            compiler.normalize_graph(value)

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

    def test_affected_descendants_do_not_include_unrelated_branch(self) -> None:
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

    def test_duplicate_exclusive_producer_requires_competes_edge(self) -> None:
        value = graph(
            [
                node("left", output_key="review-queue", exclusive_output=True),
                node("right", output_key="review-queue", exclusive_output=True),
            ],
            [],
        )
        with self.assertRaisesRegex(compiler.GraphError, "exclusive output"):
            compiler.normalize_graph(value)

        value["edges"] = [
            {"from": "left", "to": "right", "kind": "competes"}
        ]
        compiler.normalize_graph(value)

    def test_authority_defaults_false_and_cannot_be_inferred(self) -> None:
        value = compiler.normalize_graph(graph([node("evidence")], []))
        self.assertFalse(value["nodes"][0]["authority"]["upstream_contact"])

        invalid = copy.deepcopy(graph([node("evidence")], []))
        invalid["nodes"][0]["authority"]["upstream_contact"] = "yes"
        with self.assertRaisesRegex(
            compiler.GraphError, "upstream_contact must be boolean"
        ):
            compiler.normalize_graph(invalid)

    def test_unknown_fields_are_rejected_consistently(self) -> None:
        cases = []

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

    def test_empty_generation_is_rejected(self) -> None:
        value = graph([node("evidence")], [])
        value["nodes"][0]["generation"] = ""
        with self.assertRaisesRegex(compiler.GraphError, "non-empty string"):
            compiler.normalize_graph(value)


if __name__ == "__main__":
    unittest.main()
