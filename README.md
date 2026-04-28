# TriLens

TriLens is an offline, deterministic reflection system built around a structured decision tree.  
The tree is the product; the CLI is a thin runtime that traverses it.

## Why this exists

Most reflection tools hide logic inside prompts or model behavior, which makes them hard to audit.  
TriLens does the opposite:
- keeps branching logic in plain data
- uses fixed options only (no free-text interpretation)
- guarantees that the same path always returns the same outcome

## Repository layout

- `tree/reflection-tree.json` - canonical source of truth
- `tree/reflection-tree.tsv` - tabular mirror for inspection/review
- `tree/tree-diagram.md` - full Mermaid flowchart
- `agent/main.py` - offline CLI runtime (Python standard library only)
- `agent/validate_tree.py` - structural validator for tree integrity
- `agent/README.md` - runner-specific commands
- `transcripts/persona-1.md` - low-agency/entitlement/self-centric sample run
- `transcripts/persona-2.md` - high-agency/contribution/altrocentric sample run
- `write-up.md` - design rationale and trade-offs

## Core guarantees

- Offline execution only
- No runtime LLM/API calls
- No external services, billing, or keys
- Deterministic routing through explicit node targets and decision mappings
- No hardcoded branch-specific logic in runtime code

## Quick start

From repo root:

```bash
python agent/validate_tree.py
python agent/main.py
```

Optional explicit tree path:

```bash
python agent/main.py tree/reflection-tree.json
```

## Updating the system

To change behavior, edit tree data in `tree/reflection-tree.json`.  
`agent/main.py` should remain generic: it handles node types, routing, and summary interpolation, not domain rules.
