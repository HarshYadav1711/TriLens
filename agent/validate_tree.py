#!/usr/bin/env python3
"""Lightweight validator for TriLens reflection tree."""

from __future__ import annotations

import json
import sys
from collections import Counter, deque
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple


REQUIRED_AXIS_SEQUENCE = ["locus", "orientation", "radius"]


def load_tree(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def node_edges(node: Dict) -> Iterable[str]:
    if "target" in node and node["target"]:
        yield node["target"]
    for opt in node.get("options", []):
        if opt.get("target"):
            yield opt["target"]
    for mapping in node.get("mappings", []):
        if mapping.get("target"):
            yield mapping["target"]


def fail(errors: List[str], message: str) -> None:
    errors.append(message)


def validate(tree: Dict) -> List[str]:
    errors: List[str] = []
    nodes = tree.get("nodes", [])
    if not isinstance(nodes, list) or not nodes:
        return ["nodes must be a non-empty list"]

    # Unique IDs + index
    ids = [n.get("id") for n in nodes]
    if any(not i for i in ids):
        fail(errors, "every node must have a non-empty id")
    duplicates = [k for k, v in Counter(ids).items() if v > 1]
    if duplicates:
        fail(errors, f"duplicate node ids found: {duplicates}")
    node_map = {n["id"]: n for n in nodes if "id" in n}

    # Minimum structure requirements
    type_counts = Counter(n.get("type") for n in nodes)
    if len(nodes) < 25:
        fail(errors, f"node count must be >= 25 (found {len(nodes)})")
    if type_counts.get("question", 0) < 8:
        fail(errors, f"question node count must be >= 8 (found {type_counts.get('question', 0)})")
    if type_counts.get("decision", 0) < 4:
        fail(errors, f"decision node count must be >= 4 (found {type_counts.get('decision', 0)})")
    if type_counts.get("reflection", 0) < 4:
        fail(errors, f"reflection node count must be >= 4 (found {type_counts.get('reflection', 0)})")
    if type_counts.get("bridge", 0) < 2:
        fail(errors, f"bridge node count must be >= 2 (found {type_counts.get('bridge', 0)})")
    if type_counts.get("start", 0) < 1:
        fail(errors, "a start node is required")
    if type_counts.get("summary", 0) < 1:
        fail(errors, "a summary node is required")
    if type_counts.get("end", 0) < 1:
        fail(errors, "an end node is required")

    # Questions must have 3-5 fixed options
    for q in [n for n in nodes if n.get("type") == "question"]:
        options = q.get("options")
        if not isinstance(options, list):
            fail(errors, f"question {q['id']} is missing options list")
            continue
        if not (3 <= len(options) <= 5):
            fail(errors, f"question {q['id']} must have 3-5 options (found {len(options)})")
        for opt in options:
            if not opt.get("id") or not opt.get("label") or not opt.get("target"):
                fail(errors, f"question {q['id']} has option missing id/label/target")

    # Presence of required axes and order
    question_axes = [n.get("axis") for n in nodes if n.get("type") == "question"]
    for axis in REQUIRED_AXIS_SEQUENCE:
        if axis not in question_axes:
            fail(errors, f"missing required axis in question nodes: {axis}")
    try:
        positions = [question_axes.index(axis) for axis in REQUIRED_AXIS_SEQUENCE]
        if positions != sorted(positions):
            fail(errors, "axes are not ordered locus -> orientation -> radius")
    except ValueError:
        pass

    # Decision deterministic mappings
    for d in [n for n in nodes if n.get("type") == "decision"]:
        mappings = d.get("mappings")
        if not isinstance(mappings, list) or not mappings:
            fail(errors, f"decision {d['id']} must include non-empty mappings")
            continue
        seen: Set[Tuple[Tuple[str, str], ...]] = set()
        for m in mappings:
            when = m.get("when")
            target = m.get("target")
            if not isinstance(when, dict) or not when:
                fail(errors, f"decision {d['id']} has mapping missing non-empty when")
                continue
            if not target:
                fail(errors, f"decision {d['id']} has mapping missing target")
            signature = tuple(sorted((str(k), str(v)) for k, v in when.items()))
            if signature in seen:
                fail(errors, f"decision {d['id']} has duplicate mapping condition: {dict(signature)}")
            seen.add(signature)

    # Validate all targets exist
    for n in nodes:
        for tgt in node_edges(n):
            if tgt not in node_map:
                fail(errors, f"node {n['id']} points to missing target: {tgt}")

    # Reachability to END from START
    start_id = tree.get("start_node_id")
    if not start_id:
        fail(errors, "start_node_id is required")
        return errors
    if start_id not in node_map:
        fail(errors, f"start_node_id points to unknown node: {start_id}")
        return errors
    end_ids = [n["id"] for n in nodes if n.get("type") == "end"]
    if not end_ids:
        return errors
    end_set = set(end_ids)

    visited: Set[str] = set()
    q: deque[str] = deque([start_id])
    while q:
        cur = q.popleft()
        if cur in visited:
            continue
        visited.add(cur)
        for tgt in node_edges(node_map[cur]):
            if tgt not in visited:
                q.append(tgt)

    if not any(e in visited for e in end_set):
        fail(errors, "no end node is reachable from start_node_id")

    if "SUMMARY" not in node_map:
        fail(errors, "SUMMARY node id is required for reporting consistency")

    return errors


def main() -> int:
    default_path = Path(__file__).resolve().parents[1] / "tree" / "reflection-tree.json"
    path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else default_path
    tree = load_tree(path)
    errors = validate(tree)
    if errors:
        print("FAILED")
        for e in errors:
            print(f"- {e}")
        return 1
    print("PASSED")
    print(f"Validated: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
