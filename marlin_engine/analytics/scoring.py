"""Likely-lister score (0-100) + band assignment. Spec §5.5, config/scoring.yaml.
Implemented in S4 — see FARMSIGNAL_30_DAY_PLAN.md."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

# scoring.yaml sits at the package root: marlin_engine/scoring.yaml
_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "scoring.yaml"

_TENURE_9PLUS_YEARS = 9
_TENURE_15PLUS_YEARS = 15
_TIRED_LANDLORD_TENURE_YEARS = 15

# Human-readable labels for the score_breakdown explainability string (report +
# CSV). One entry per weights.yaml key. Kept short deliberately -- these render
# as report table pills two-per-row (HOT List Preview), and the original longer
# phrasing ("Long-tenured senior exemption", "Likely non-owner-occupied
# (rental)") forced one pill per line, which overflowed the 15-row table onto a
# second page (verified against a real Park West At Circle C report render).
_SIGNAL_LABELS = {
    "tenure_years_9plus": "Tenure 9+ yrs",
    "tenure_years_15plus_additional": "Tenure 15+ yrs",
    "tenure_longevity_bonus": "Tenure bonus",
    "absentee": "Absentee mailing",
    "out_of_state": "Out-of-state",
    "likely_rental": "Likely rental",
    "likely_rental_long_tenure": "Tired landlord",
    "senior_longtenure": "Long-tenured senior",
    "homestead_dropped": "Homestead dropped",
    "over65_newly_filed": "Newly 65+",
    "ag_exemption_rollback": "Ag exemption dropped",
    "owner_is_entity": "Entity/investor",
    "recent_sale": "Recent sale",
    "recent_permit_activity": "Recent permit",
    "tax_delinquent": "Tax delinquent",
}


def load_scoring_config(path: Path = _DEFAULT_CONFIG_PATH) -> dict:
    return yaml.safe_load(path.read_text())


def _band_for(score: float, bands: dict) -> str:
    if score >= bands["hot_min"]:
        return "HOT"
    if score >= bands["warm_min"]:
        return "WARM"
    return "STANDARD"


def _optional_bool_column(df: pd.DataFrame, name: str) -> pd.Series:
    """Signals that may not exist yet (homestead_dropped needs >=2 roll years;
    recent_sale/recent_permit_activity/tax_delinquent need ingest/enrichment
    steps that may not have run) contribute 0, not an error, when absent."""
    return df[name].fillna(False) if name in df.columns else pd.Series(False, index=df.index)


def compute_score_breakdown(df: pd.DataFrame, config: dict | None = None) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Single source of truth for the weighted-sum score formula (spec §5.5).
    Returns (scores, bands, breakdown): breakdown[i] is a pipe-delimited,
    Excel-safe string like "Property tax delinquent:+20|Tenure 9+ yrs:+25|Likely
    non-owner-occupied (rental):-20", restricted to signals with a nonzero point
    contribution for that row, sorted by magnitude descending -- the
    "explainability" goal (score + top contributing factors, not a black-box
    number).

    Score is clipped to [0, 100]. The lower clip is new this session: with
    likely_rental/recent_sale/recent_permit_activity now negative, a parcel can
    stack well below 0 (e.g. owner_is_entity + likely_rental + recent_sale =
    -10-20-25 = -55) -- the spec and report copy both describe a 0-100 score
    throughout, so the floor preserves that contract. The clip is applied to the
    final score only; each contribution in the breakdown reflects its raw
    (unclipped) weight, which can only matter at the 100-ceiling edge (spec
    already treats 100 as a hard cap, not a claim about the "true" sum).

    tenure_longevity_bonus adds 1 point (tenure_bonus_per_year) per whole year
    of tenure past 15, uncapped except by the 100 ceiling -- fixes score
    clustering where every long-tenured home tied at the same flat total.
    Applies regardless of senior_longtenure status.

    likely_rental_long_tenure replaces likely_rental's contribution (not
    stacked on top of it) once tenure_years >= 15 -- see config/scoring.yaml
    for the full rationale."""
    config = config or load_scoring_config()
    weights = config["weights"]
    bands = config["bands"]

    tenure = df["tenure_years"]
    tenure_years_past_15 = (tenure - _TENURE_15PLUS_YEARS).clip(lower=0).fillna(0).astype(int)
    is_long_tenure = tenure >= _TIRED_LANDLORD_TENURE_YEARS
    contributions = pd.DataFrame(
        {
            "tenure_years_9plus": weights["tenure_years_9plus"] * (tenure >= _TENURE_9PLUS_YEARS),
            "tenure_years_15plus_additional": weights["tenure_years_15plus_additional"]
            * (tenure >= _TENURE_15PLUS_YEARS),
            "tenure_longevity_bonus": weights.get("tenure_bonus_per_year", 0) * tenure_years_past_15,
            "absentee": weights.get("absentee", 0) * df["absentee"],
            "out_of_state": weights["out_of_state"] * df["out_of_state"],
            "likely_rental": weights["likely_rental"] * (df["likely_rental"] & ~is_long_tenure),
            "likely_rental_long_tenure": weights.get("likely_rental_long_tenure", weights["likely_rental"])
            * (df["likely_rental"] & is_long_tenure),
            "senior_longtenure": weights["senior_longtenure"] * df["senior_longtenure"],
            "homestead_dropped": weights.get("homestead_dropped", 0) * _optional_bool_column(df, "homestead_dropped"),
            "over65_newly_filed": weights.get("over65_newly_filed", 0) * _optional_bool_column(df, "over65_newly_filed"),
            "ag_exemption_rollback": weights.get("ag_exemption_rollback", 0)
            * _optional_bool_column(df, "ag_exemption_rollback"),
            "owner_is_entity": weights["owner_is_entity"] * df["owner_is_entity"],
            "recent_sale": weights.get("recent_sale", 0) * _optional_bool_column(df, "recent_sale"),
            "recent_permit_activity": weights.get("recent_permit_activity", 0)
            * _optional_bool_column(df, "recent_permit_activity"),
            "tax_delinquent": weights.get("tax_delinquent", 0) * _optional_bool_column(df, "tax_delinquent"),
        },
        index=df.index,
    )

    score = contributions.sum(axis=1).clip(lower=0, upper=100).round(1)
    band = score.map(lambda s: _band_for(s, bands))
    breakdown = contributions.apply(
        lambda row: "|".join(
            f"{_SIGNAL_LABELS[key]}:{int(points):+d}"
            # kind="stable" so ties in |points| break by column-definition order,
            # not sort-algorithm implementation details -- otherwise two signals
            # with the same magnitude (e.g. a +20 and a -20) could swap order
            # between runs, which would fail the score-determinism guarantee.
            for key, points in row.sort_values(key=abs, ascending=False, kind="stable").items()
            if points != 0
        ),
        axis=1,
    )
    return score, band, breakdown


def compute_scores(df: pd.DataFrame, config: dict | None = None) -> tuple[pd.Series, pd.Series]:
    """Thin wrapper over compute_score_breakdown for callers that only need
    score+band (e.g. existing tests, any future caller uninterested in the
    per-signal breakdown)."""
    scores, bands, _breakdown = compute_score_breakdown(df, config)
    return scores, bands
