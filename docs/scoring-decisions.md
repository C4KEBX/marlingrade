# Marlin Grade — scoring decisions (pending implementation)

Decisions made in discussion, **not yet applied to any config**. When a
`config/scoring.yaml` is created for Marlin Grade, fold these in.

## 1. Out-of-state mailing address: flip +10 → −10

**Current (FarmSignal):** `out_of_state_additional: 10` (positive — treats a
distant owner as more likely to list).

**History:** the +10 dates to the first scaffold commit, straight from the build
spec's original table. The Jul 24 rental-direction correction (`73d53db`) flipped
`likely_rental` +10→−20 and zeroed `absentee`, but left `out_of_state` at +10 —
an oversight, not a decision.

**Decision:** out-of-state should be **negative**. An out-of-state, non-homestead
SFR owner is almost definitionally `likely_rental`; the rental-investor
interpretation (steady income, hands-off, less motivated to sell) dominates.
Today such an owner nets −20 + 10 = −10, with the +10 cancelling half the
intended penalty.

- New weight: **−10** (mirrors `owner_is_entity`; "extra damp on top of
  likely_rental — a distant landlord is even more set-and-forget than a local
  one"). −15 if it should bite harder.
- Treat as a tunable directional default pending correlation data.
- Rename key `out_of_state_additional` → `out_of_state` (no longer stacks on a
  positive `absentee`). Touches `analytics/scoring.py` (`weights[...]` lookup and
  `_SIGNAL_LABELS`).

## 2. Letter grade = fixed A–F cutoffs, NOT curved per zip

The **letter grade is the primary thing the user sees**; the 0–100 numeric score
is the deep-dive.

**Decision:** map the letter off **fixed bands on the absolute 0–100 score**. Do
not curve grades to a per-zip percentile.

Reasons:
1. Spike alerts need a stable grade meaning — a per-zip curve moves an owner's
   grade when neighbors change, manufacturing false alerts.
2. Honesty / budget guidance — a genuinely cold farm should grade low; a curve
   hides that behind a guaranteed top-10% "A" tier.
3. Comparability across farms and (later) across metros.
4. Explainability to a skeptical agent.

Handle the "my whole farm is D's" UX concern in the **UI, not the math**:
- show the area's grade distribution,
- always offer a "Top N in this area" ranked view regardless of absolute grade,
- show local percentile as *secondary* context on the deep-dive.

**Calibration:** set A/B/C/D/F boundaries only after running the model across all
~487k Travis parcels and inspecting the real score distribution. Make top grades
genuinely selective (A ≈ low single-digit %). The existing
`HOT ≥ 55 / WARM 35–54` bands were never calibrated against a full-market
distribution — only 184 parcels have ever been scored. Use A B C D F (no E).

### 2a. Calibration applied — 2026-09-09

Frozen into `marlin_engine/grades.py`: `CUTOFFS = {A: 67, B: 44, C: 35, D: 25}`
(inclusive lower bounds, boundary → higher grade). Never re-run without an
explicit re-baseline decision.

- Source: `scripts/calibrate_cutoffs.py` over the full latest-roll Travis SFR
  score distribution, **n = 349,422**. Single roll year (2025) loaded, so the
  three prior-roll diff signals contribute 0 for every parcel — pure
  standing-state signals.
- Target anchors (cumulative share from the top): **A ≈ 3% / B ≈ 15% / C ≈ 40% /
  D ≈ 75%**, F = bottom 25%.
- **A = 67** and **B = 44** are the raw anchor scores at 3% / 15% and fit the
  upper tail cleanly.
- **C = 35** and **D = 25** are placed by histogram *shape*, not the anchors. The
  distribution is zero-inflated — ~63% of the roll scores 0–9 (no tenure or
  motivation signal) — so the 40th and 75th percentiles both collapse to score 0
  and the raw anchor math yields C = 1, D = 0. Instead: **D = 25** sits on the
  `+25` "owned 9+ yrs" tenure spike (≈42k parcels in the 25–29 bin) and above the
  near-empty 10–24 valley; **C = 35** sits on the `+35` "owned 15+ yrs"
  tenure-signal cluster, above the 30–34 valley.
- Resulting whole-roll band shares ≈ A 3.4% / B 11% / C 9% / D 12.5% / F 63%.
