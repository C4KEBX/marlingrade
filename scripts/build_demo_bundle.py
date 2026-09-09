"""Offline: score the 7 demo zips from the FarmSignal DuckDB into a static JSON
bundle for the SPA. Approach A — no runtime backend. Idempotent; no DB writes.

Usage:  python -m scripts.build_demo_bundle
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import duckdb
import pandas as pd

from marlin_engine.analytics.metrics import (
    compute_parcel_metrics,
    compute_farm_aggregates,
    fetch_prior_roll_year_snapshot,
)
from marlin_engine.analytics.scoring import compute_score_breakdown, load_scoring_config
from marlin_engine import grades

DEMO_ZIPS = ["78749", "78748", "78745", "78739", "78735", "78736", "78652"]
FOCUS_ZIP = "78749"

# Static area labels (situs_city is only 43% populated). Subdivisions are read
# live from the data (top N by parcel count).
ZIP_AREA = {
    "78749": "Southwest Austin",
    "78748": "Far South Austin",
    "78745": "South Austin",
    "78739": "Circle C Ranch",
    "78735": "West Oak Hill",
    "78736": "Oak Hill",
    "78652": "Manchaca",
}
# Staged for the demo (spec §5.2). 78749 is the monitored/exclusivity-available one.
ZIP_EXCLUSIVITY = {z: ("available" if z == FOCUS_ZIP else "held") for z in DEMO_ZIPS}
ZIP_EXCLUSIVITY[FOCUS_ZIP] = "available"

_DEFAULT_DB = Path("data/farmsignal.duckdb")
_DEFAULT_OUT = Path("web/public/data")
_FIXTURES = Path("fixtures")


def _parse_breakdown(s: str | None) -> list[dict]:
    """'Tenure 9+ yrs:+25|Likely rental:-20' -> [{'label':..., 'points':int}]."""
    if not s:
        return []
    out = []
    for chunk in s.split("|"):
        label, _, pts = chunk.rpartition(":")
        out.append({"label": label, "points": int(pts)})
    return out


def _load_demo_parcels(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    placeholders = ", ".join("?" for _ in DEMO_ZIPS)
    df = con.execute(
        f"""
        SELECT * FROM parcels
        WHERE situs_zip IN ({placeholders})
          AND is_sfr = TRUE
          AND roll_year = (SELECT MAX(roll_year) FROM parcels)
        """,
        DEMO_ZIPS,
    ).fetchdf()
    return df


def _score(df: pd.DataFrame, con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    # Prior roll year (Task 10): if a second roll_year exists, diff against it so
    # homestead_dropped / over65_newly_filed / ag_exemption_rollback activate.
    years = con.execute("SELECT DISTINCT roll_year FROM parcels ORDER BY roll_year DESC").fetchall()
    prior = None
    if len(years) >= 2:
        prior_year = years[1][0]
        prior = fetch_prior_roll_year_snapshot(
            con, "travis", df["parcel_id"].tolist(), prior_year
        )
    metrics = compute_parcel_metrics(df, prior)
    score, band, breakdown = compute_score_breakdown(metrics, load_scoring_config())
    metrics = metrics.assign(score=score, score_breakdown=breakdown)
    metrics["grade"] = grades.assign_series(score)
    return metrics


def _zip_record(zip_code: str, g: pd.DataFrame) -> dict:
    agg = compute_farm_aggregates(g.assign(score_band=None))
    n = len(g)
    dist = {}
    for letter in ("A", "B", "C", "D", "F"):
        c = int((g["grade"] == letter).sum())
        dist[letter] = {"count": c, "pct": round(100 * c / n, 1) if n else 0.0}
    subs = (
        g["subdivision_canon"].dropna().value_counts().head(4).index.tolist()
    )
    return {
        "zip": zip_code,
        "area": ZIP_AREA[zip_code],
        "subdivisions": subs,
        "sfr_count": n,
        "distribution": dist,
        "aggregates": {
            "absentee_pct": agg.absentee_pct,
            "rental_pct": agg.likely_rental_pct,
            "median_tenure": round(agg.median_tenure_years, 1) if agg.median_tenure_years else None,
            "out_of_state_pct": agg.out_of_state_pct,
        },
        "exclusivity": ZIP_EXCLUSIVITY[zip_code],
    }


def _parcel_record(row: pd.Series) -> dict:
    from marlin_engine.normalize.address import normalize_address

    situs = row["situs_address"] if pd.notna(row["situs_address"]) else None
    return {
        "parcel_uid": f"travis-{row['parcel_id']}",
        "situs_address": situs,
        "situs_norm": normalize_address(situs or ""),
        "owner_name": row["owner_name"] if pd.notna(row["owner_name"]) else None,
        "owner_type": "entity" if bool(row["owner_is_entity"]) else "occupant",
        "grade": row["grade"],
        "score": float(row["score"]),
        "breakdown": _parse_breakdown(row["score_breakdown"]),
        "facts": {
            "deed_date": str(row["deed_date"]) if pd.notna(row["deed_date"]) else None,
            "tenure_years": round(float(row["tenure_years"]), 1) if pd.notna(row["tenure_years"]) else None,
            "homestead": bool(row["homestead"]),
            "over65": bool(row["over65_exempt"]),
            "subdivision": row["subdivision_canon"] if pd.notna(row["subdivision_canon"]) else None,
            "assessed_value": int(row["assessed_value"]) if pd.notna(row["assessed_value"]) else None,
            "mail_state": row["mail_state"] if pd.notna(row["mail_state"]) else None,
            "out_of_state": bool(row["out_of_state"]),
        },
    }


def build(db_path: Path = _DEFAULT_DB, out_dir: Path = _DEFAULT_OUT) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        scored = _score(_load_demo_parcels(con), con)
    finally:
        con.close()

    zips = []
    for zip_code in DEMO_ZIPS:
        g = scored[scored["situs_zip"] == zip_code]
        zips.append(_zip_record(zip_code, g))
        # Secondary key parcel_id (unique within a roll year) makes tie ordering
        # deterministic so the bundle is byte-identical across rebuilds — ~1200
        # parcels can share one score, and a bare score sort would reshuffle them
        # every run and churn the committed JSON.
        ordered = g.sort_values(["score", "parcel_id"], ascending=[False, True])
        parcels = [_parcel_record(r) for _, r in ordered.iterrows()]
        (out_dir / f"parcels-{zip_code}.json").write_text(json.dumps(parcels, allow_nan=False))
    (out_dir / "zips.json").write_text(json.dumps(zips, indent=2, allow_nan=False))
    (out_dir / "grades.json").write_text(
        json.dumps({"cutoffs": grades.cutoffs_for_display()}, indent=2, allow_nan=False)
    )

    for fx in ("alerts.json", "report-78749.json"):
        src = _FIXTURES / fx
        if src.exists():
            shutil.copy(src, out_dir / fx)

    print(f"wrote bundle for {len(DEMO_ZIPS)} zips to {out_dir}")


if __name__ == "__main__":
    build()
