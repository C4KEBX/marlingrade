from __future__ import annotations
import pandas as pd
from marlin_engine.grades import assign, assign_series, CUTOFFS, cutoffs_for_display

def test_each_band_returns_its_letter() -> None:
    assert assign(CUTOFFS["A"]) == "A"
    assert assign(CUTOFFS["A"] - 1) == "B"
    assert assign(CUTOFFS["B"]) == "B"
    assert assign(CUTOFFS["C"]) == "C"
    assert assign(CUTOFFS["D"]) == "D"
    assert assign(CUTOFFS["D"] - 1) == "F"

def test_boundary_takes_higher_grade() -> None:
    assert assign(CUTOFFS["B"]) == "B"      # exactly on B's floor -> B, not C

def test_clip_range() -> None:
    assert assign(0) == "F"
    assert assign(100) == "A"
    assert assign(-5) == "F"                # defensive: below 0
    assert assign(150) == "A"               # defensive: above 100

def test_assign_series_matches_scalar() -> None:
    s = pd.Series([0, 40, 70, 95])
    assert list(assign_series(s)) == [assign(v) for v in s]

def test_display_has_five_bands_in_order() -> None:
    disp = cutoffs_for_display()
    assert [d[0] for d in disp] == ["A", "B", "C", "D", "F"]
