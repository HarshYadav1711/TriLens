# Reflection Tree Notes

This file is the commentary companion to `tree/reflection-tree.json`.  
It adds human-readable intent without changing JSON behavior.

## Axis Sections

- **Prelude (`Q0_CHECKIN`)**
  - Captures initial pacing context before axis classification begins.
  - Routes to one of three bridge tones, then converges into Axis 1.

- **Axis 1: Locus (`Q1_LOCUS_PRIMARY`, `Q1B_LOCUS_WINDOW`)**
  - Detects where agency attention starts (`outside_forces`, `shared_influence`, `next_action`).
  - Stabilizer question checks whether stance is stable or shifting.
  - Normalized by `D1_LOCUS_CLASSIFIER` into `locus_state`.

- **Axis 2: Orientation (`Q2_ORIENTATION_PRIMARY`, `Q2B_ORIENTATION_BALANCE`)**
  - Captures exchange stance under shared work constraints.
  - Distinguishes contribution-first, fairness-balancing, and owed-first patterns.
  - Normalized by `D2_ORIENTATION_CLASSIFIER` into `orientation_state`.

- **Axis 3: Radius (`Q3_RADIUS_PRIMARY`, `Q3B_RADIUS_HORIZON`)**
  - Captures scope of concern (self, near circle, broader system).
  - Horizon question measures immediate vs multi-step impact window.
  - Normalized by `D3_RADIUS_CLASSIFIER` into `radius_state`.

- **Closure (`Q4_CLOSE_STEP`)**
  - Chooses an implementation style for the next 24 hours.
  - Does not alter core axis states; it shapes closing summary language.

## Decision Nodes (Purpose)

- **`D0_CHECKIN_ROUTER`**
  - Maps prelude pace to one of three bridge messages.

- **`D1_LOCUS_CLASSIFIER`**
  - Converts two locus answers into a normalized `locus_state`.
  - Grouped in JSON by `locus_primary` value.

- **`D2_ORIENTATION_CLASSIFIER`**
  - Converts two orientation answers into `orientation_state`.
  - Grouped in JSON by `orientation_primary` value.

- **`D3_RADIUS_CLASSIFIER`**
  - Converts radius/scope + horizon into `radius_state`.
  - Grouped in JSON by `radius_primary` value.

- **`D4_REFLECTION_SELECTOR` (core routing decision)**
  - Takes the normalized axis triple:
    - `locus_state`
    - `orientation_state`
    - `radius_state`
  - Resolves to exactly one reflection node (`R1`..`R6`).
  - JSON mapping rows are visually grouped by:
    1. `locus_state` (`victim`, `balanced`, `victor`)
    2. then `orientation_state` (`entitlement`, `balanced`, `contribution`)
    3. then `radius_state` (`self_centrism`, `balanced`, `altrocentrism`)
  - This grouping improves scanability while preserving deterministic outcomes.

- **`D5_CLOSING_ROUTE`**
  - Sends all closing styles to `SUMMARY`.
  - Exists to keep final routing explicit and auditable.
