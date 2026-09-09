"""Fixed A–F letter grade from the absolute 0–100 Marlin score.

Decision (docs/scoring-decisions.md §2): fixed cutoffs on the absolute score,
never curved per zip. Grades are exactly A, B, C, D, F — no plus, no E.

CUTOFFS are FROZEN 2026-09-09 from scripts/calibrate_cutoffs.py, run over the
full latest-roll Travis SFR score distribution (n = 349,422, single-roll so the
prior-roll diff signals contribute 0). Target anchors are cumulative-from-top
A≈3% / B≈15% / C≈40% / D≈75% (F = bottom 25%).

A (67) and B (44) are the raw anchor scores at 3% / 15% and fit the tail well.
C and D are placed by histogram SHAPE, not the anchors: the distribution is
zero-inflated — ~63% of the roll scores 0-9 (no tenure/motivation signal) — so
the 40th and 75th percentiles both land at score 0 and the raw anchor math
collapses to C=1, D=0. Instead: D=25 sits exactly on the "+25 = owned 9-14 yrs"
tenure spike (42k parcels) and above the empty 10-24 valley; C=35 sits on the
"+35 = owned 15+ yrs" cluster edge, above the 30-34 valley. Resulting whole-roll
band shares ≈ A 3.4% / B 11% / C 9% / D 12.5% / F 63%. See docs/scoring-decisions.md §2.
"""
from __future__ import annotations

import pandas as pd

# Lower-bound score for each band. F is the implicit floor (anything below D).
CUTOFFS: dict[str, int] = {"A": 67, "B": 44, "C": 35, "D": 25}

_ORDER = ("A", "B", "C", "D")


def assign(score: float) -> str:
    s = max(0.0, min(100.0, float(score)))
    for letter in _ORDER:
        if s >= CUTOFFS[letter]:
            return letter
    return "F"


def assign_series(scores: pd.Series) -> pd.Series:
    return scores.map(assign)


def cutoffs_for_display() -> list[tuple[str, str]]:
    a, b, c, d = (CUTOFFS[k] for k in _ORDER)
    return [
        ("A", f"≥ {a}"),
        ("B", f"{b}–{a - 1}"),
        ("C", f"{c}–{b - 1}"),
        ("D", f"{d}–{c - 1}"),
        ("F", f"< {d}"),
    ]
