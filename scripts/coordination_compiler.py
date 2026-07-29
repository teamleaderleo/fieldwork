#!/usr/bin/env python3
"""Pure static evaluator for Fieldwork coordination graph fixtures."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys
from typing import Any, Iterable

SCHEMA_VERSION = "fieldwork.coordination/v1"
MAX_NODES = 1_000
MAX_EDGES = 5_000
MAX_ID_LENGTH = 160

NODE_KINDS = {
    "evidence",
    "execution-receipt",
    "technical-review",
    "human-decision",
    "authority-gate",
    "queue-entry",
}
SEMANTIC_STATES = {
    "current",
    "ready",
    "blocked",
    "execution-gated",
    "stale-input",
    "missing-receipt",
    "incomplete-input-set",
    "policy-drift",
    "authority-mismatch",
}
READINESS_EDGE_KINDS = {
    "requires",
    "consumes-evidence",
    "requires-review",
    "requires-decision",
    "requires-authority",
    "produces",
}
NON_READINESS_EDGE_KINDS = {
    "supersedes",
    "causal",
    "history",
    "related",
    "competes",
}
EDGE_KINDS = READINESS_EDGE_KINDS | NON_READINESS_EDGE_KINDS
INTRINSICALLY_SATISFIED = {"current", "ready"}
GRAPH_KEYS = {"schema_version", "nodes", "edges"}
NODE_KEYS = {
    "id",
    "generation",
    "kind",
    "semantic_state",
    "input_fingerprint",
    "semantic_fingerprint",
    "evaluator_revision",
    "policy_revision",
    "authority",
    "output_key",
    "exclusive_output",
}
EDGE_KEYS = {"from", "to", "kind"}
AUTHORITY_KEYS = {"upstream_contact"}


class GraphError(ValueError):
    """Raised when a static coordination graph is structurally invalid."""


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise GraphError(f"{label} must be an object")
    return value


def _require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise GraphError(f"{label} must be an array")
    return value


def _reject_unknown_keys(
    value: dict[str, Any], allowed: set[str], label: str
) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise GraphError(f"{label} has unknown field {unknown[0]!r}")


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GraphError(f"{label} must be a non-empty string")
    if len(value) > MAX_ID_LENGTH:
        raise GraphError(f"{label} exceeds {MAX_ID_LENGTH} characters")
    return value


def _canonical_node(raw: Any, index: int) -> dict[str, Any]:
    label = f"nodes[{index}]"
    node = _require_mapping(raw, label)
    _reject_unknown_keys(node, NODE_KEYS, label)
    node_id = _require_text(node.get("id"), f"{label}.id")
    generation = node.get("generation")
    if isinstance(generation, str):
        generation = _require_text(generation, f"node {node_id!r} generation")
    elif not isinstance(generation, int) or isinstance(generation, bool):
        raise GraphError(f"node {node_id!r} generation must be a string or integer")

    kind = _require_text(node.get("kind"), f"node {node_id!r} kind")
    if kind not in NODE_KINDS:
        raise GraphError(f"node {node_id!r} has unknown kind {kind!r}")

    semantic_state = _require_text(
        node.get("semantic_state"), f"node {node_id!r} semantic_state"
    )
    if semantic_state not in SEMANTIC_STATES:
        raise GraphError(
            f"node {node_id!r} has unknown semantic_state {semantic_state!r}"
        )

    authority = _require_mapping(node.get("authority"), f"node {node_id!r} authority")
    _reject_unknown_keys(authority, AUTHORITY_KEYS, f"node {node_id!r} authority")
    upstream_contact = authority.get("upstream_contact", False)
    if not isinstance(upstream_contact, bool):
        raise GraphError(
            f"node {node_id!r} authority.upstream_contact must be boolean"
        )

    canonical = {
        "id": node_id,
        "generation": generation,
        "kind": kind,
        "semantic_state": semantic_state,
        "input_fingerprint": _require_text(
            node.get("input_fingerprint"), f"node {node_id!r} input_fingerprint"
        ),
        "semantic_fingerprint": _require_text(
            node.get("semantic_fingerprint"),
            f"node {node_id!r} semantic_fingerprint",
        ),
        "evaluator_revision": _require_text(
            node.get("evaluator_revision"), f"node {node_id!r} evaluator_revision"
        ),
        "policy_revision": _require_text(
            node.get("policy_revision"), f"node {node_id!r} policy_revision"
        ),
        "authority": {"upstream_contact": upstream_contact},
    }

    if "output_key" in node:
        canonical["output_key"] = _require_text(
            node["output_key"], f"node {node_id!r} output_key"
        )
        exclusive = node.get("exclusive_output", False)
        if not isinstance(exclusive, bool):
            raise GraphError(f"node {node_id!r} exclusive_output must be boolean")
        canonical["exclusive_output"] = exclusive
    elif "exclusive_output" in node:
        raise GraphError(f"node {node_id!r} exclusive_output requires an output_key")

    return canonical


def _canonical_edge(raw: Any, index: int) -> dict[str, str]:
    label = f"edges[{index}]"
    edge = _require_mapping(raw, label)
    _reject_unknown_keys(edge, EDGE_KEYS, label)
    source = _require_text(edge.get("from"), f"{label}.from")
    target = _require_text(edge.get("to"), f"{label}.to")
    kind = _require_text(edge.get("kind"), f"{label}.kind")
    if kind not in EDGE_KINDS:
        raise GraphError(f"edge {source!r}->{target!r} has unknown kind {kind!r}")
    return {"from": source, "to": target, "kind": kind}


def _readiness_adjacency(
    node_ids: Iterable[str], edges: list[dict[str, str]]
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    outgoing = {node_id: [] for node_id in node_ids}
    incoming = {node_id: [] for node_id in node_ids}
    for edge in edges:
        if edge["kind"] not in READINESS_EDGE_KINDS:
            continue
        outgoing[edge["from"]].append(edge["to"])
        incoming[edge["to"]].append(edge["from"])
    for neighbors in outgoing.values():
        neighbors.sort()
    for dependencies in incoming.values():
        dependencies.sort()
    return outgoing, incoming


def _find_readiness_cycle(
    node_ids: Iterable[str], outgoing: dict[str, list[str]]
) -> list[str] | None:
    state: dict[str, int] = {node_id: 0 for node_id in node_ids}
    stack: list[str] = []
    stack_index: dict[str, int] = {}

    def visit(node_id: str) -> list[str] | None:
        state[node_id] = 1
        stack_index[node_id] = len(stack)
        stack.append(node_id)
        for target in outgoing[node_id]:
            if state[target] == 0:
                cycle = visit(target)
                if cycle:
                    return cycle
            elif state[target] == 1:
                start = stack_index[target]
                return stack[start:] + [target]
        stack.pop()
        stack_index.pop(node_id)
        state[node_id] = 2
        return None

    for node_id in sorted(state):
        if state[node_id] == 0:
            cycle = visit(node_id)
            if cycle:
                return cycle
    return None


def _topological_order(
    node_ids: Iterable[str],
    outgoing: dict[str, list[str]],
    incoming: dict[str, list[str]],
) -> list[str]:
    ready = sorted(node_id for node_id in node_ids if not incoming[node_id])
    order: list[str] = []
    indegree = {node_id: len(incoming[node_id]) for node_id in node_ids}
    while ready:
        node_id = ready.pop(0)
        order.append(node_id)
        for target in outgoing[node_id]:
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
                ready.sort()
    if len(order) != len(indegree):
        raise GraphError("readiness graph contains a cycle")
    return order


def _validate_exclusive_outputs(
    nodes: list[dict[str, Any]], edges: list[dict[str, str]]
) -> None:
    competitors = {
        frozenset((edge["from"], edge["to"]))
        for edge in edges
        if edge["kind"] == "competes"
    }
    producers: dict[str, list[str]] = defaultdict(list)
    for node in nodes:
        if node.get("exclusive_output"):
            producers[node["output_key"]].append(node["id"])
    for output_key, node_ids in sorted(producers.items()):
        node_ids.sort()
        for index, left in enumerate(node_ids):
            for right in node_ids[index + 1 :]:
                if frozenset((left, right)) not in competitors:
                    raise GraphError(
                        f"exclusive output {output_key!r} has competing producers "
                        f"{left!r} and {right!r} without a competes edge"
                    )


def normalize_graph(raw: Any) -> dict[str, Any]:
    """Validate and canonicalize one bounded graph document."""
    graph = _require_mapping(raw, "graph")
    _reject_unknown_keys(graph, GRAPH_KEYS, "graph")
    if graph.get("schema_version") != SCHEMA_VERSION:
        raise GraphError(f"schema_version must be {SCHEMA_VERSION!r}")

    raw_nodes = _require_list(graph.get("nodes"), "nodes")
    raw_edges = _require_list(graph.get("edges"), "edges")
    if len(raw_nodes) > MAX_NODES:
        raise GraphError(f"nodes exceeds bounded limit {MAX_NODES}")
    if len(raw_edges) > MAX_EDGES:
        raise GraphError(f"edges exceeds bounded limit {MAX_EDGES}")

    nodes = [_canonical_node(node, index) for index, node in enumerate(raw_nodes)]
    edges = [_canonical_edge(edge, index) for index, edge in enumerate(raw_edges)]

    node_ids: set[str] = set()
    for node in nodes:
        node_id = node["id"]
        if node_id in node_ids:
            raise GraphError(f"duplicate node id {node_id!r}")
        node_ids.add(node_id)

    seen_edges: set[tuple[str, str, str]] = set()
    for edge in edges:
        source, target, kind = edge["from"], edge["to"], edge["kind"]
        if source not in node_ids:
            raise GraphError(f"edge source {source!r} does not exist")
        if target not in node_ids:
            raise GraphError(f"edge target {target!r} does not exist")
        identity = (source, target, kind)
        if identity in seen_edges:
            raise GraphError(f"duplicate edge {source!r}->{target!r} ({kind})")
        seen_edges.add(identity)
        if source == target and kind in READINESS_EDGE_KINDS:
            raise GraphError(f"readiness self-dependency at node {source!r}")

    _validate_exclusive_outputs(nodes, edges)
    outgoing, _ = _readiness_adjacency(node_ids, edges)
    cycle = _find_readiness_cycle(node_ids, outgoing)
    if cycle:
        raise GraphError(f"readiness cycle detected: {' -> '.join(cycle)}")

    nodes.sort(key=lambda item: item["id"])
    edges.sort(key=lambda item: (item["kind"], item["from"], item["to"]))
    return {"schema_version": SCHEMA_VERSION, "nodes": nodes, "edges": edges}


def evaluate_graph(
    graph: dict[str, Any], changed_nodes: Iterable[str] = ()
) -> dict[str, Any]:
    """Evaluate readiness and affected descendants over a normalized graph."""
    nodes_by_id = {node["id"]: node for node in graph["nodes"]}
    outgoing, incoming = _readiness_adjacency(nodes_by_id, graph["edges"])
    order = _topological_order(nodes_by_id, outgoing, incoming)

    evaluations: dict[str, dict[str, Any]] = {}
    for node_id in order:
        node = nodes_by_id[node_id]
        if node["semantic_state"] not in INTRINSICALLY_SATISFIED:
            evaluations[node_id] = {
                "state": node["semantic_state"],
                "first_blocker_path": [node_id],
            }
            continue

        blocker = next(
            (
                dependency
                for dependency in incoming[node_id]
                if evaluations[dependency]["state"] != "ready"
            ),
            None,
        )
        if blocker is None:
            evaluations[node_id] = {"state": "ready", "first_blocker_path": []}
        else:
            evaluations[node_id] = {
                "state": "blocked",
                "first_blocker_path": [
                    node_id,
                    *evaluations[blocker]["first_blocker_path"],
                ],
            }

    changed = sorted(set(changed_nodes))
    unknown_changed = [node_id for node_id in changed if node_id not in nodes_by_id]
    if unknown_changed:
        raise GraphError(f"changed node does not exist: {unknown_changed[0]!r}")

    affected = set(changed)
    queue = list(changed)
    while queue:
        source = queue.pop(0)
        for target in outgoing[source]:
            if target not in affected:
                affected.add(target)
                queue.append(target)

    return {
        "schema_version": graph["schema_version"],
        "canonical_graph": graph,
        "topological_order": order,
        "evaluations": [
            {"id": node_id, **evaluations[node_id]} for node_id in sorted(evaluations)
        ],
        "changed_nodes": changed,
        "affected_nodes": sorted(affected),
    }


def load_and_evaluate(path: Path, changed_nodes: Iterable[str] = ()) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return evaluate_graph(normalize_graph(raw), changed_nodes)


def canonical_json(value: Any, pretty: bool = False) -> str:
    if pretty:
        return json.dumps(value, indent=2, sort_keys=True) + "\n"
    return json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and evaluate a static Fieldwork coordination graph."
    )
    parser.add_argument("graph", type=Path)
    parser.add_argument("--changed", action="append", default=[])
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Evaluate from the supplied graph only; accepted for clean-build receipts.",
    )
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        result = load_and_evaluate(args.graph, args.changed)
    except (OSError, json.JSONDecodeError, GraphError) as error:
        print(f"coordination graph invalid: {error}", file=sys.stderr)
        return 2
    sys.stdout.write(canonical_json(result, args.pretty))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
