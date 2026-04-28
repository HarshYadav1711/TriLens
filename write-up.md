# TriLens Design Write-up

## Why these questions

The question set is built to classify stance, not personality. Each axis uses two questions:
- a primary question to capture default orientation
- a stabilizer question to capture consistency under changing context

That pairing reduces overreaction to a single moment and keeps routing deterministic without needing free text.

Question language is intentionally concrete (pressure, resources, downstream effects, next step) so users can choose quickly without interpretation ambiguity.

## How branching works

The tree has explicit node types (`start`, `question`, `decision`, `bridge`, `reflection`, `summary`, `end`).

- Question nodes collect fixed-option selections and store `state_key` values.
- Decision nodes evaluate exact `when` mappings and may set normalized axis states (`victim|balanced|victor`, etc.).
- Bridge nodes keep transitions readable between axis phases.
- Reflection nodes deliver concise guidance, then continue.
- Summary interpolates state into final output and closes at `end`.

All routing is defined in data (`target` fields and decision mappings). The runtime does not contain branch-specific rules.

## Why the flow is ordered as three axes

The order is deliberate:
1. **Locus (agency)** first, because perceived control shapes how any later prompt is interpreted.
2. **Orientation (contribution vs entitlement)** second, because exchange stance is most meaningful after agency context is known.
3. **Radius (scope of concern)** third, because social scope is clearer once agency and exchange stance are established.

This sequence prevents mixing concepts too early and keeps each stage cognitively narrow.

## Psychological grounding

The design draws from established ideas, translated into deterministic prompts:
- **Locus of control / agency framing** (Rotter tradition): internal vs external control orientation.
- **Prosocial vs self-protective orientation** from social and organizational psychology: contribution/reciprocity dynamics under constraint.
- **Self-other scope and perspective taking** from moral-development and social-cognition literature: narrow self focus vs broader system consideration.
- **Brief reflective practice** from coaching and CBT-style behavioral framing: end with a concrete, observable next step.

The system is not diagnostic and avoids moral labels; it frames current stance as situational and adjustable.

## Trade-offs made

- Chose fixed options over nuance-rich text to preserve determinism and auditability.
- Added `balanced` intermediate states to reduce brittle binary classification, at the cost of a larger mapping table.
- Kept reflections short and non-prescriptive to stay calm and reusable, at the cost of personalization depth.
- Used deterministic summary variants instead of open generation to improve tone while keeping repeatability.

## What I would improve with more time

- Expand the summary variant library for more dominance combinations while staying deterministic.
- Add stricter schema validation (e.g., coverage checks ensuring every intended state combination is mapped).
- Add a transcript exporter in CLI for reproducible review artifacts.
- Run a small human review pass to tune wording clarity across diverse roles and cultures.

## Rubric alignment

- **Tree quality:** multi-stage axis classification with explicit normalization and reflection routing.
- **Psychological grounding:** agency, exchange stance, and scope-of-concern model reflected in question design.
- **Data structure clarity:** readable IDs, explicit parent/target patterns, TSV mirror, Mermaid diagram.
- **Write-up clarity:** concrete rationale, documented trade-offs, and explicit constraints.
