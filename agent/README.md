# TriLens CLI Runner

This folder contains the offline deterministic CLI runtime and validator.

## Requirements
- Python 3.9+ (standard library only)
- No API keys
- No network calls

## Commands

From repository root:

```bash
python agent/validate_tree.py
```

Run the CLI with default canonical tree:

```bash
python agent/main.py
```

Run the CLI with an explicit tree path:

```bash
python agent/main.py tree/reflection-tree.json
```

## Behavior
- Auto-advances `start`, `decision`, and `bridge` nodes
- Prompts only on `question` nodes and reflection continue prompts
- Tracks answers by node ID
- Applies decision `set` values into runtime state
- Interpolates summary template placeholders from accumulated state
- Computes and prints dominant states for `locus`, `orientation`, and `radius`

## Troubleshooting
- If the runtime prints `ERROR:` with a node ID, inspect that node for missing `target`, malformed `mappings`, or unresolved placeholders.
- Run `python agent/validate_tree.py` first to catch structural issues early.
