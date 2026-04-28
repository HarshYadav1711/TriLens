#!/usr/bin/env python3
"""TriLens deterministic offline CLI runner.

Generic node handling only:
- Loads canonical tree JSON
- Traverses by node type and explicit targets/mappings
- Stores answers by node id
- Stores state assignments from decisions
- Computes dominant axis state and interpolates summary template
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class TreeRuntimeError(RuntimeError):
    """Raised when tree data is malformed or cannot be routed."""


def load_tree(path: Optional[Path] = None) -> Dict[str, Any]:
    if path is None:
        path = Path(__file__).resolve().parents[1] / "tree" / "reflection-tree.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_node_map(tree: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    nodes = tree.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        raise TreeRuntimeError("Tree must contain a non-empty 'nodes' list.")
    node_map: Dict[str, Dict[str, Any]] = {}
    for node in nodes:
        node_id = node.get("id")
        if not node_id or not isinstance(node_id, str):
            raise TreeRuntimeError("Every node must have a string 'id'.")
        if node_id in node_map:
            raise TreeRuntimeError(f"Duplicate node id found: {node_id}")
        node_map[node_id] = node
    return node_map


def choose_option(node: Dict[str, Any]) -> Dict[str, Any]:
    prompt = node.get("prompt")
    options = node.get("options")
    if not isinstance(prompt, str) or not prompt.strip():
        raise TreeRuntimeError(f"Question node '{node['id']}' is missing a valid 'prompt'.")
    if not isinstance(options, list) or not options:
        raise TreeRuntimeError(f"Question node '{node['id']}' is missing options.")

    print()
    axis = node.get("axis", "question")
    print(f"[{axis.upper()}] {prompt}")
    for i, opt in enumerate(options, start=1):
        label = opt.get("label")
        opt_id = opt.get("id")
        target = opt.get("target")
        if not label or not opt_id or not target:
            raise TreeRuntimeError(
                f"Question node '{node['id']}' has option missing id/label/target."
            )
        print(f"  {i}. {label} [{opt_id}]")

    while True:
        raw = input("Select option number: ").strip()
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return options[idx]
        print("Invalid choice. Enter one of the listed option numbers.")


def match_mapping(mapping: Dict[str, Any], state: Dict[str, str]) -> bool:
    when = mapping.get("when")
    if not isinstance(when, dict) or not when:
        raise TreeRuntimeError("Decision mapping requires a non-empty 'when' dictionary.")
    for key, expected in when.items():
        if state.get(key) != expected:
            return False
    return True


def apply_set(mapping: Dict[str, Any], state: Dict[str, str], axis_signals: Dict[str, List[str]]) -> None:
    assigned = mapping.get("set", {})
    if not assigned:
        return
    if not isinstance(assigned, dict):
        raise TreeRuntimeError("Decision mapping 'set' must be an object when present.")
    for key, value in assigned.items():
        state[key] = value
        axis_name = key.split("_", 1)[0]
        axis_signals[axis_name].append(str(value))


def next_from_decision(node: Dict[str, Any], state: Dict[str, str], axis_signals: Dict[str, List[str]]) -> str:
    mappings = node.get("mappings")
    if not isinstance(mappings, list) or not mappings:
        raise TreeRuntimeError(f"Decision node '{node['id']}' requires non-empty 'mappings'.")

    hits: List[Dict[str, Any]] = [m for m in mappings if match_mapping(m, state)]
    if len(hits) != 1:
        raise TreeRuntimeError(
            f"Decision node '{node['id']}' expected exactly 1 matching mapping, found {len(hits)}."
        )

    hit = hits[0]
    apply_set(hit, state, axis_signals)
    target = hit.get("target")
    if not target:
        raise TreeRuntimeError(f"Decision node '{node['id']}' mapping missing 'target'.")
    return target


def pause_continue(message: str = "Press Enter to continue...") -> None:
    input(message)


def interpolate(text: str, values: Dict[str, str]) -> str:
    pattern = re.compile(r"\{([a-zA-Z0-9_]+)\}")

    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        return values.get(key, f"<missing:{key}>")

    return pattern.sub(repl, text)


def polish_summary_closing(line: str) -> str:
    """Keep summary closing specific and human, without changing logic."""
    if line.strip() == "Choose one concrete action in the next day and keep it observable.":
        return "Keep it small enough to complete, and visible enough to matter."
    return line


def dominant_value(candidates: List[str]) -> str:
    if not candidates:
        return "unknown"
    counts = Counter(candidates)
    max_count = max(counts.values())
    top = {v for v, c in counts.items() if c == max_count}
    for v in candidates:
        if v in top:
            return v
    return candidates[0]


def compute_axis_dominance(tree: Dict[str, Any], state: Dict[str, str], axis_signals: Dict[str, List[str]]) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for axis in tree.get("axis_sequence", []):
        direct_key = f"{axis}_state"
        if direct_key in state:
            result[axis] = state[direct_key]
        else:
            result[axis] = dominant_value(axis_signals.get(axis, []))
    return result


def choose_summary_variant(axis_dominant: Dict[str, str]) -> List[str]:
    """Return deterministic summary lines from dominant axis pattern."""
    locus = axis_dominant.get("locus", "unknown")
    orientation = axis_dominant.get("orientation", "unknown")
    radius = axis_dominant.get("radius", "unknown")
    pattern = (locus, orientation, radius)

    variants = {
        ("victim", "entitlement", "self_centrism"): [
            "You are carrying pressure while protecting your own footing.",
            "A stabilizing next step is one concrete action that restores agency before negotiating expectations."
        ],
        ("victim", "balanced", "balanced"): [
            "You seem to be navigating constraints while still trying to keep things fair.",
            "A useful move now is to make one practical request and pair it with one concrete contribution."
        ],
        ("victim", "contribution", "altrocentrism"): [
            "You are still showing up for others even while things feel constrained.",
            "Protect durability by sharing load explicitly and choosing one bounded action for today."
        ],
        ("balanced", "entitlement", "self_centrism"): [
            "You are balancing context carefully, with strong attention to reciprocity and self-protection.",
            "Clarity can help here: name what you need, then state what you will contribute next."
        ],
        ("balanced", "balanced", "altrocentrism"): [
            "You are holding multiple perspectives without losing practical focus.",
            "Keep momentum by turning that perspective into one visible agreement with clear ownership."
        ],
        ("balanced", "contribution", "balanced"): [
            "Your stance combines steadiness with a bias toward contribution.",
            "To keep it sustainable, set a clear boundary around scope and timeline."
        ],
        ("victor", "entitlement", "balanced"): [
            "You are action-oriented and clear about exchange, with awareness beyond your own position.",
            "A strong next step is to make expectations explicit and commit to one shared milestone."
        ],
        ("victor", "contribution", "altrocentrism"): [
            "You are pairing initiative with a contribution mindset and a broad field of view.",
            "Sustain this by keeping one visible commitment and one clear boundary in the same window."
        ],
    }
    if pattern in variants:
        return variants[pattern]

    fallback_by_locus = {
        "victim": "Agency feels tight right now; begin with one controllable move you can complete today.",
        "balanced": "You are working in a mixed-agency zone; clear priorities and pacing will help.",
        "victor": "You have forward momentum; channel it into a steady, observable next step.",
    }
    fallback_by_orientation = {
        "entitlement": "State expectations clearly so the exchange remains workable.",
        "balanced": "Keep reciprocity and contribution visible at the same time.",
        "contribution": "Your contribution mindset works best when paired with sustainable limits.",
    }
    return [
        fallback_by_locus.get(locus, "Use a small concrete step to create traction."),
        fallback_by_orientation.get(orientation, "Keep the next step observable and time-bounded."),
    ]


def export_transcript(
    question_log: List[Dict[str, str]],
    summary_lines: List[str],
    axis_dominant: Dict[str, str],
) -> Path:
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "transcripts"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = out_dir / f"run-{stamp}.md"

    lines: List[str] = [
        "# TriLens Run Transcript",
        "",
        f"- Timestamp: {datetime.now().isoformat(timespec='seconds')}",
        f"- Dominant axis states: locus={axis_dominant.get('locus', 'unknown')}, "
        f"orientation={axis_dominant.get('orientation', 'unknown')}, "
        f"radius={axis_dominant.get('radius', 'unknown')}",
        "",
        "## Questions and selections",
        "",
    ]
    for idx, item in enumerate(question_log, start=1):
        lines.extend(
            [
                f"{idx}. **{item['axis'].upper()}** `{item['node_id']}`",
                f"   - Question: {item['prompt']}",
                f"   - Selected: {item['option_label']} (`{item['option_id']}`)",
                "",
            ]
        )

    lines.extend(["## Final summary", ""])
    for line in summary_lines:
        lines.append(f"- {line}")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def run(tree: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str], List[Dict[str, str]], List[str]]:
    node_map = build_node_map(tree)
    start_id = tree.get("start_node_id")
    if not start_id or start_id not in node_map:
        raise TreeRuntimeError("Tree must provide valid 'start_node_id'.")

    answers_by_node: Dict[str, str] = {}
    state: Dict[str, str] = {}
    axis_signals: Dict[str, List[str]] = defaultdict(list)
    question_log: List[Dict[str, str]] = []
    summary_output: List[str] = []

    current_id = start_id
    visited_count = 0
    max_steps = 1000

    while True:
        visited_count += 1
        if visited_count > max_steps:
            raise TreeRuntimeError("Traversal exceeded safe step limit; possible cycle in tree.")

        node = node_map.get(current_id)
        if node is None:
            raise TreeRuntimeError(f"Route points to unknown node '{current_id}'.")
        node_type = node.get("type")
        if not node_type:
            raise TreeRuntimeError(f"Node '{current_id}' is missing 'type'.")

        if node_type == "start":
            print("\nTriLens Reflection (offline deterministic mode)")
            print("- Fixed options only")
            print("- No runtime AI calls\n")
            target = node.get("target")
            if not target:
                raise TreeRuntimeError(f"Start node '{current_id}' is missing 'target'.")
            current_id = target
            continue

        if node_type == "question":
            selected = choose_option(node)
            answers_by_node[node["id"]] = selected["id"]
            question_log.append(
                {
                    "node_id": node["id"],
                    "axis": str(node.get("axis", "question")),
                    "prompt": str(node.get("prompt", "")),
                    "option_id": str(selected.get("id", "")),
                    "option_label": str(selected.get("label", "")),
                }
            )
            if node.get("state_key"):
                state[node["state_key"]] = selected["id"]
                axis = node.get("axis")
                if isinstance(axis, str):
                    axis_signals[axis].append(selected["id"])
            current_id = selected["target"]
            continue

        if node_type == "decision":
            current_id = next_from_decision(node, state, axis_signals)
            continue

        if node_type == "bridge":
            text = node.get("text")
            if not isinstance(text, str):
                raise TreeRuntimeError(f"Bridge node '{current_id}' is missing 'text'.")
            print(f"\n{interpolate(text, state)}")
            target = node.get("target")
            if not target:
                raise TreeRuntimeError(f"Bridge node '{current_id}' is missing 'target'.")
            current_id = target
            continue

        if node_type == "reflection":
            text = node.get("text")
            if not isinstance(text, str):
                raise TreeRuntimeError(f"Reflection node '{current_id}' is missing 'text'.")
            print(f"\nReflection:\n{interpolate(text, state)}")
            pause_continue("Press Enter to continue...")
            target = node.get("target")
            if not target:
                raise TreeRuntimeError(f"Reflection node '{current_id}' is missing 'target'.")
            current_id = target
            continue

        if node_type == "summary":
            axis_dominant = compute_axis_dominance(tree, state, axis_signals)
            for axis, value in axis_dominant.items():
                state[f"dominant_{axis}_state"] = value
                state.setdefault(f"{axis}_state", value)

            template = node.get("template", {})
            lines = template.get("lines", [])
            closing = template.get("closing", "")
            if not isinstance(lines, list):
                raise TreeRuntimeError(f"Summary node '{current_id}' has invalid template lines.")

            print("\nSummary:")
            for line in choose_summary_variant(axis_dominant):
                rendered = interpolate(line, state)
                summary_output.append(rendered)
                print(f"- {rendered}")
            for line in lines:
                if not isinstance(line, str):
                    raise TreeRuntimeError(f"Summary node '{current_id}' includes non-string line.")
                rendered = interpolate(line, state)
                summary_output.append(rendered)
                print(f"- {rendered}")
            if isinstance(closing, str) and closing.strip():
                rendered = polish_summary_closing(interpolate(closing, state))
                summary_output.append(rendered)
                print(f"- {rendered}")

            target = node.get("target")
            if not target:
                raise TreeRuntimeError(f"Summary node '{current_id}' is missing 'target'.")
            current_id = target
            continue

        if node_type == "end":
            axis_dominant = compute_axis_dominance(tree, state, axis_signals)
            print("\nEnd of reflection.")
            print(
                "Dominant axis states: "
                + ", ".join(f"{k}={v}" for k, v in axis_dominant.items())
            )
            return answers_by_node, state, axis_dominant, question_log, summary_output

        raise TreeRuntimeError(f"Unsupported node type '{node_type}' in node '{current_id}'.")


def main() -> int:
    try:
        tree_path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None
        tree = load_tree(tree_path)
        _, _, axis_dominant, question_log, summary_output = run(tree)
        transcript_path = export_transcript(question_log, summary_output, axis_dominant)
        print(f"Transcript saved: {transcript_path}")
        return 0
    except FileNotFoundError as exc:
        print(f"ERROR: tree file not found: {exc}")
        return 1
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON in tree file: {exc}")
        return 1
    except TreeRuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1
    except EOFError:
        print("ERROR: input stream ended before traversal completed.")
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
