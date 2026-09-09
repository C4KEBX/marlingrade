"""Fixed A–F letter grade from the absolute 0–100 Marlin score.

Decision (docs/scoring-decisions.md §2): fixed cutoffs on the absolute score,
never curved per zip. Grades are exactly A, B, C, D, F — no plus, no E.

CUTOFFS below are PLACEHOLDERS. Task 8 (scripts/calibrate_cutoffs.py) replaces
them with values read off the full-Travis-roll score histogram at the anchors
A≈top 3%, B≈next 12%, C≈next 25%, D≈next 35%, F≈bottom 25%.
"""
from __future__ import annotations

import pandas as pd

# Lower-bound score for each band. F is the implicit floor (anything below D).
CUTOFFS: dict[str, int] = {"A": 75, "B": 55, "C": 35, "D": 18}

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
