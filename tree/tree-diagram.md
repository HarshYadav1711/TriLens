# TriLens Tree Diagram

```mermaid
flowchart TD
    START([START]) --> Q0[Q0_CHECKIN<br/>Question: prelude]
    Q0 -->|compressed| D0{D0_CHECKIN_ROUTER}
    Q0 -->|steady| D0
    Q0 -->|open| D0

    D0 --> B0G[B0_GROUNDING]
    D0 --> B0S[B0_STABILITY]
    D0 --> B0E[B0_EXPANSION]
    B0G --> Q1
    B0S --> Q1
    B0E --> Q1

    Q1[Q1_LOCUS_PRIMARY<br/>Axis 1: LOCUS] --> Q1B[Q1B_LOCUS_WINDOW]
    Q1B --> D1{D1_LOCUS_CLASSIFIER<br/>sets locus_state}
    D1 --> B1[B1_LOCUS_TO_ORIENTATION]

    B1 --> Q2[Q2_ORIENTATION_PRIMARY<br/>Axis 2: ORIENTATION]
    Q2 --> Q2B[Q2B_ORIENTATION_BALANCE]
    Q2B --> D2{D2_ORIENTATION_CLASSIFIER<br/>sets orientation_state}
    D2 --> B2[B2_ORIENTATION_TO_RADIUS]

    B2 --> Q3[Q3_RADIUS_PRIMARY<br/>Axis 3: RADIUS]
    Q3 --> Q3B[Q3B_RADIUS_HORIZON]
    Q3B --> D3{D3_RADIUS_CLASSIFIER<br/>sets radius_state}
    D3 --> D4{D4_REFLECTION_SELECTOR}
    NOTE_D4["Enumerates 3-axis combinations (locus, orientation, radius)<br/>to preserve deterministic routing."]
    D4 --- NOTE_D4

    D4 --> R1[R1_STABILIZE_AGENCY]
    D4 --> R2[R2_RECIPROCAL_RESET]
    D4 --> R3[R3_GROUNDED_BOUNDARIES]
    D4 --> R4[R4_SHARED_STEADINESS]
    D4 --> R5[R5_SYSTEMS_RECIPROCITY]
    D4 --> R6[R6_GENERATIVE_STEWARDSHIP]

    R1 --> Q4[Q4_CLOSE_STEP<br/>Question: closure]
    R2 --> Q4
    R3 --> Q4
    R4 --> Q4
    R5 --> Q4
    R6 --> Q4

    Q4 --> D5{D5_CLOSING_ROUTE}
    D5 --> SUMMARY[[SUMMARY]]
    SUMMARY --> END([END])
```

Traversal is fixed and deterministic.  
Axis order is preserved as `locus -> orientation -> radius`, with bridge/decision nodes providing explicit, auditable routing.

## Complex Node Notes

- `D1_LOCUS_CLASSIFIER`: normalizes two locus answers into one `locus_state`.
- `D2_ORIENTATION_CLASSIFIER`: normalizes two orientation answers into one `orientation_state`.
- `D3_RADIUS_CLASSIFIER`: normalizes scope+horizon into one `radius_state`.
- `D4_REFLECTION_SELECTOR`: central lookup that maps the normalized axis triple to exactly one reflection node (`R1`..`R6`).
