"""Score every Travis SFR parcel (latest roll) and propose A–F cutoffs at the
spec §10.1 anchors. Run once; copy the printed values into marlin_engine/grades.py.

Usage:  python -m scripts.calibrate_cutoffs
"""
from __future__ import annotations

from pathlib import Path

import duckdb
import numpy as np

from marlin_engine.analytics.metrics import compute_parcel_metrics
from marlin_engine.analytics.scoring import compute_score_breakdown, load_scoring_config

# anchors: cumulative share from the TOP. A = top 3%, B = next 12% (top 15), etc.
ANCHORS = {"A": 0.03, "B": 0.15, "C": 0.40, "D": 0.75}  # F = remainder


def main(db_path: Path = Path("data/farmsignal.duckdb")) -> None:
    con = duckdb.connect(str(db_path), read_only=True)
    df = con.execute(
        "SELECT * FROM parcels WHERE is_sfr = TRUE "
        "AND roll_year = (SELECT MAX(roll_year) FROM parcels)"
    ).fetchdf()
    con.close()

    metrics = compute_parcel_metrics(df, prior=None)          # single-roll: diff signals = 0
    score, _, _ = compute_score_breakdown(metrics, load_scoring_config())
    s = np.sort(score.to_numpy())[::-1]                        # descending

    print(f"n = {len(s)}   min={s.min():.0f}  median={np.median(s):.0f}  max={s.max():.0f}")
    # histogram
    hist, edges = np.histogram(s, bins=range(0, 105, 5))
    for h, lo in zip(hist, edges[:-1]):
        print(f"{lo:>3}-{lo+4:<3} | {'#' * (h * 60 // hist.max())} {h}")

    cut = {}
    for letter, top_share in ANCHORS.items():
        idx = int(top_share * len(s)) - 1
        cut[letter] = int(round(s[idx]))
    # snap so bands strictly decrease
    for a, b in (("A", "B"), ("B", "C"), ("C", "D")):
        if cut[a] <= cut[b]:
            cut[a] = cut[b] + 1
    print("\nproposed CUTOFFS =", cut)
    print("copy into marlin_engine/grades.py, then re-run build_demo_bundle + update test_grades expectations")


if __name__ == "__main__":
    main()
