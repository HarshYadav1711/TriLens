#!/usr/bin/env python3
"""TriLens deterministic CLI reflection agent.

Uses tree/reflection-tree.json as the single source of truth.
No free text responses are accepted during traversal.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Dict, List, Tuple


def load_tree() -> Dict:
    here = os.path.dirname(os.path.abspath(__file__))
    tree_path = os.path.normpath(os.path.join(here, "..", "tree", "reflection-tree.json"))
    with open(tree_path, "r", encoding="utf-8") as f:
        return json.load(f)


def index_leaf_profiles(tree: Dict) -> Dict[Tuple[str, str, str], Dict]:
    indexed: Dict[Tuple[str, str, str], Dict] = {}
    for profile in tree["leaf_profiles"]:
        p = profile["path"]
        key = (p["locus"], p["orientation"], p["radius"])
        indexed[key] = profile
    return indexed


def choose_option(question: Dict) -> Dict:
    print()
    print(f"{question['axis'].upper()}: {question['prompt']}")
    for idx, option in enumerate(question["options"], start=1):
        print(f"  {idx}. {option['label']} [{option['id']}]")

    while True:
        raw = input("Choose an option number: ").strip()
        if not raw.isdigit():
            print("Please enter a number from the listed options.")
            continue
        choice = int(raw)
        if 1 <= choice <= len(question["options"]):
            return question["options"][choice - 1]
        print("Invalid choice. Pick one of the shown option numbers.")


def traverse(tree: Dict) -> Dict[str, str]:
    node_map = {node["id"]: node for node in tree["nodes"]}
    current_id = tree["start_node_id"]
    answers: Dict[str, str] = {}

    while True:
        node = node_map[current_id]
        selected = choose_option(node)
        answers[node["axis"]] = selected["id"]
        if selected["next"] == "END":
            return answers

        # Deterministic linear axis progression from source tree order.
        axis_order: List[str] = tree["axes_order"]
        current_axis_i = axis_order.index(node["axis"])
        next_axis = axis_order[current_axis_i + 1]
        next_node = next(n for n in tree["nodes"] if n["axis"] == next_axis)
        current_id = next_node["id"]


def render_output(tree: Dict, answers: Dict[str, str]) -> None:
    leaf_index = index_leaf_profiles(tree)
    key = (answers["locus"], answers["orientation"], answers["radius"])
    profile = leaf_index[key]

    print("\n--- TriLens Reflection Output ---")
    print(f"Path: locus={answers['locus']} -> orientation={answers['orientation']} -> radius={answers['radius']}")
    print(f"Profile: {profile['title']} ({profile['id']})")
    print(f"Reflection: {profile['reflection']}")
    print("Suggested next micro-step: Choose one concrete action in the next 24 hours that matches this stance.")


def main() -> int:
    tree = load_tree()
    print("TriLens Deterministic Reflection")
    print("Fixed choices only. No free text. Offline traversal.\n")
    answers = traverse(tree)
    render_output(tree, answers)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
