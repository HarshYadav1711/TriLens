# TriLens Design Write-up

## Intent
TriLens is designed as a deterministic reflection system where the tree is the product.  
The runtime agent is only a traversal layer over tree data.

## Deterministic Design
- Fixed traversal order: `locus -> orientation -> radius`.
- Fixed choices per question; no free text input.
- Every complete 3-axis path maps to exactly one leaf profile.
- Same answers always produce the same profile and reflection output.

## Source of Truth
The authoritative definition is `tree/reflection-tree.json`, which includes:
- axis order
- question prompts
- option IDs and labels
- path-to-profile mapping
- output template

The CLI and web UI both read this file and do not embed branch-specific business logic.

## Psychological Grounding Approach
The three axes are framed as reflective stances rather than moral categories:
- **Locus** captures perceived agency under pressure.
- **Orientation** captures give-first vs owed-first focus in shared work.
- **Radius** captures scope of concern from self-protection to broader impact.

Leaf profile language is intentionally calm and practical:
- descriptive, not diagnostic
- non-moralizing
- action-oriented with a small, concrete next step

## Auditability and Readability
- `tree/reflection-tree.tsv` provides a tabular, review-friendly mirror of the tree.
- `tree/tree-diagram.md` provides a visual Mermaid map of all branches.
- Deterministic outputs are traceable by option IDs and path keys.

## Runtime Constraints Compliance
- No LLM calls at runtime.
- No external APIs.
- No cloud dependency.
- Python agent uses only the standard library.
- Web agent uses single-file vanilla HTML/CSS/JS.
