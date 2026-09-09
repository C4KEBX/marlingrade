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
