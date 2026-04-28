# TriLens

TriLens is a deterministic reflection-tree submission.  
The tree is the primary product; interfaces are lightweight traversal clients.

## Deliverables
- `tree/reflection-tree.json` - source-of-truth structured tree
- `tree/reflection-tree.tsv` - auditable table view
- `tree/tree-diagram.md` - Mermaid visualization
- `agent/main.py` - Python CLI agent (standard library only)
- `agent/web.html` - single-file browser UI (vanilla HTML/CSS/JS)
- `transcripts/persona-1.md` - sample path transcript
- `transcripts/persona-2.md` - sample path transcript
- `write-up.md` - short design rationale

## Constraints Satisfied
- No LLM/API calls at runtime
- No external APIs or paid services
- No API keys, no billing dependencies
- No free-text user input
- Fully deterministic path traversal
- Same answer path always returns same output
- Tree data remains source of truth
- No hardcoded branch logic in the agent

## Run CLI
From repo root:

```bash
python agent/main.py
```

## Run Web UI
Serve locally from the repository root (example using Python):

```bash
python -m http.server 8000
```

Then open:
- [http://localhost:8000/agent/web.html](http://localhost:8000/agent/web.html)

The page loads `../tree/reflection-tree.json` and traverses fixed options only.

## Notes
- This repository is intentionally minimal for auditability.
- To update behavior, modify tree data files, not agent branching logic.
