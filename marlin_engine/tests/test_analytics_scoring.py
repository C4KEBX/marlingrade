"""Likely-lister score tests. Spec §5.5, §11: score determinism, band boundaries."""

from __future__ import annotations

import pandas as pd
import pytest

from marlin_engine.analytics.scoring import compute_score_breakdown, compute_scores, load_scoring_config

_CONFIG = load_scoring_config()


def _row(**overrides) -> dict:
    row = {
        "tenure_years": 0.0,
        "absentee": False,
        "out_of_state": False,
        "likely_rental": False,
        "senior_longtenure": False,
        "owner_is_entity": False,
    }
    row.update(overrides)
    return row


def test_score_is_zero_for_a_parcel_with_no_signals() -> None:
    df = pd.DataFrame([_row()])
    scores, bands = compute_scores(df, _CONFIG)
    assert scores.iloc[0] == 0.0
    assert bands.iloc[0] == "STANDARD"


def test_score_stacks_tenure_9_and_15_year_weights() -> None:
    df = pd.DataFrame([_row(tenure_years=20.0)])
    scores, _ = compute_scores(df, _CONFIG)
    assert scores.iloc[0] == pytest.approx(40.0)  # 25 (>=9) + 10 (>=15, additional) + 5 (longevity bonus, floor(20-15))


def test_score_does_not_add_15_year_bonus_below_15_years() -> None:
    df = pd.DataFrame([_row(tenure_years=10.0)])
    scores, _ = compute_scores(df, _CONFIG)
    assert scores.iloc[0] == pytest.approx(25.0)


def test_score_is_capped_at_100() -> None:
    df = pd.DataFrame(
        [
            _row(
                tenure_years=25.0,  # 25 + 10 + 10 (longevity bonus, floor(25-15)) = 45
                out_of_state=True,  # +10
                senior_longtenure=True,  # +15
                homestead_dropped=True,  # +25
                tax_delinquent=True,  # +20  -- sums to 115, must clip to 100
            )
        ]
    )
    scores, _ = compute_scores(df, _CONFIG)
    assert scores.iloc[0] == 100.0


def test_owner_is_entity_subtracts_points() -> None:
    df = pd.DataFrame([_row(tenure_years=20.0, owner_is_entity=True)])
    scores, _ = compute_scores(df, _CONFIG)
    assert scores.iloc[0] == pytest.approx(30.0)  # 25 + 10 + 5 (longevity) - 10


def test_homestead_dropped_column_absent_contributes_nothing() -> None:
    """homestead_dropped only exists once >=2 roll years are loaded (spec §5.6);
    scoring must degrade gracefully rather than crash when the column is missing."""
    df = pd.DataFrame([_row(tenure_years=20.0)])
    assert "homestead_dropped" not in df.columns
    scores, _ = compute_scores(df, _CONFIG)
    assert scores.iloc[0] == pytest.approx(40.0)


def test_band_boundaries_match_spec_thresholds() -> None:
    df = pd.DataFrame(
        [
            _row(tenure_years=0.0),  # score 0 -> STANDARD
            _row(likely_rental=True),  # -20, floored to 0 -> STANDARD
            _row(tenure_years=10.0, senior_longtenure=True),  # 25 + 15 = 40 -> WARM
            _row(tenure_years=20.0, senior_longtenure=True, out_of_state=True),  # 35 + 5 (longevity) + 15 + 10 = 65 -> HOT
        ]
    )
    scores, bands = compute_scores(df, _CONFIG)
    assert bands.tolist() == ["STANDARD", "STANDARD", "WARM", "HOT"]


def test_score_is_deterministic_across_repeated_runs() -> None:
    """Spec §11 explicit requirement: score determinism."""
    df = pd.DataFrame(
        [_row(tenure_years=12.0, absentee=True, out_of_state=True, senior_longtenure=False)]
    )
    first, _ = compute_scores(df, _CONFIG)
    second, _ = compute_scores(df, _CONFIG)
    assert first.tolist() == second.tolist()


# --- Rental-scoring correction + new signals (this session) ----------------


def test_absentee_no_longer_contributes_to_score() -> None:
    """absentee alone (no likely_rental) now scores 0 -- it's still computed and
    stored, but only feeds likely_rental's definition, not the score directly."""
    df = pd.DataFrame([_row(absentee=True)])
    scores, _ = compute_scores(df, _CONFIG)
    assert scores.iloc[0] == 0.0


def test_likely_rental_now_subtracts_points() -> None:
    """Rental-scoring correction: a landlord earning passive income is less
    motivated to sell, not more -- likely_rental flipped from +10 to -20."""
    df = pd.DataFrame([_row(tenure_years=10.0, likely_rental=True)])
    scores, _ = compute_scores(df, _CONFIG)
    assert scores.iloc[0] == pytest.approx(5.0)  # 25 - 20


def test_recent_sale_subtracts_25_points() -> None:
    df = pd.DataFrame([_row(tenure_years=20.0, recent_sale=True)])
    scores, _ = compute_scores(df, _CONFIG)
    assert scores.iloc[0] == pytest.approx(15.0)  # 25 + 10 + 5 (longevity) - 25


def test_recent_permit_activity_subtracts_15_points() -> None:
    df = pd.DataFrame([_row(tenure_years=10.0, recent_permit_activity=True)])
    scores, _ = compute_scores(df, _CONFIG)
    assert scores.iloc[0] == pytest.approx(10.0)  # 25 - 15


def test_tax_delinquent_adds_20_points() -> None:
    df = pd.DataFrame([_row(tax_delinquent=True)])
    scores, _ = compute_scores(df, _CONFIG)
    assert scores.iloc[0] == pytest.approx(20.0)


def test_new_signal_columns_absent_contribute_nothing() -> None:
    """recent_sale/recent_permit_activity/tax_delinquent may not exist yet
    (ingest/enrichment steps not run) -- graceful degradation, same rule as
    homestead_dropped."""
    df = pd.DataFrame([_row(tenure_years=20.0)])
    assert "recent_sale" not in df.columns
    assert "tax_delinquent" not in df.columns
    scores, _ = compute_scores(df, _CONFIG)
    assert scores.iloc[0] == pytest.approx(40.0)


def test_score_floor_is_zero_not_negative() -> None:
    """Stacking negative weights (owner_is_entity + likely_rental + recent_sale
    = -10 - 20 - 25 = -55) must floor at 0, not go negative -- the spec and
    report both describe a 0-100 score throughout."""
    df = pd.DataFrame([_row(owner_is_entity=True, likely_rental=True, recent_sale=True)])
    scores, bands = compute_scores(df, _CONFIG)
    assert scores.iloc[0] == 0.0
    assert bands.iloc[0] == "STANDARD"


def test_compute_score_breakdown_returns_sorted_nonzero_signals_only() -> None:
    df = pd.DataFrame([_row(tenure_years=20.0, tax_delinquent=True, likely_rental=True)])
    scores, bands, breakdown = compute_score_breakdown(df, _CONFIG)
    # tenure_years=20 -> +25 (9plus), +10 (15plus), +5 (longevity bonus); tax_delinquent -> +20; likely_rental with tenure 20yr -> +5 (tired landlord)
    assert scores.iloc[0] == pytest.approx(65.0)
    factors = breakdown.iloc[0].split("|")
    # +25 first (largest magnitude); the +20 is next; then +10, then two +5s ordered by column-definition (tenure_bonus before tired_landlord)
    assert factors == [
        "Tenure 9+ yrs:+25",
        "Tax delinquent:+20",
        "Tenure 15+ yrs:+10",
        "Tenure bonus:+5",
        "Tired landlord:+5",
    ]
    # zero-contribution signals (out_of_state, senior_longtenure, etc.) never appear
    assert not any("Out-of-state" in f for f in factors)


def test_compute_score_breakdown_empty_string_when_no_signals_fire() -> None:
    df = pd.DataFrame([_row()])
    _scores, _bands, breakdown = compute_score_breakdown(df, _CONFIG)
    assert breakdown.iloc[0] == ""


def test_compute_scores_matches_compute_score_breakdown_score_and_band() -> None:
    """compute_scores is a thin wrapper -- must return identical score/band to
    unpacking compute_score_breakdown directly."""
    df = pd.DataFrame([_row(tenure_years=20.0, tax_delinquent=True), _row(likely_rental=True)])
    scores_a, bands_a = compute_scores(df, _CONFIG)
    scores_b, bands_b, _breakdown = compute_score_breakdown(df, _CONFIG)
    assert scores_a.tolist() == scores_b.tolist()
    assert bands_a.tolist() == bands_b.tolist()


# --- Tenure longevity bonus (this session) ---------------------------------


def test_tenure_longevity_bonus_is_zero_at_exactly_15_years() -> None:
    df = pd.DataFrame([_row(tenure_years=15.0)])
    scores, _ = compute_scores(df, _CONFIG)
    assert scores.iloc[0] == pytest.approx(35.0)  # 25 (>=9) + 10 (>=15) + 0 (bonus starts past 15)


def test_tenure_longevity_bonus_is_zero_just_under_15_years() -> None:
    df = pd.DataFrame([_row(tenure_years=14.9)])
    scores, _ = compute_scores(df, _CONFIG)
    assert scores.iloc[0] == pytest.approx(25.0)


def test_tenure_longevity_bonus_adds_one_point_per_year_past_15_floored() -> None:
    df = pd.DataFrame([_row(tenure_years=25.7)])
    scores, _ = compute_scores(df, _CONFIG)
    assert scores.iloc[0] == pytest.approx(45.0)  # 25 + 10 + floor(25.7-15)=10


def test_tenure_longevity_bonus_is_zero_when_tenure_years_is_nan() -> None:
    """No deed_date on file -> tenure_years is NaN (spec §5.5 data_gap case).
    Must contribute 0, not crash the int() cast in the breakdown string."""
    df = pd.DataFrame([_row(tenure_years=float("nan"))])
    scores, bands, breakdown = compute_score_breakdown(df, _CONFIG)
    assert scores.iloc[0] == 0.0
    assert bands.iloc[0] == "STANDARD"
    assert breakdown.iloc[0] == ""


def test_tenure_longevity_bonus_applies_regardless_of_senior_exemption() -> None:
    df = pd.DataFrame(
        [
            _row(tenure_years=25.0),  # non-senior: 25 + 10 + floor(25-15)=10 -> 45
            _row(tenure_years=25.0, senior_longtenure=True),  # + 15 -> 60
        ]
    )
    scores, _ = compute_scores(df, _CONFIG)
    assert scores.tolist() == pytest.approx([45.0, 60.0])


def test_tenure_longevity_bonus_appears_in_breakdown_with_correct_label() -> None:
    df = pd.DataFrame([_row(tenure_years=25.0)])
    _scores, _bands, breakdown = compute_score_breakdown(df, _CONFIG)
    factors = breakdown.iloc[0].split("|")
    assert "Tenure bonus:+10" in factors


# --- Multi-year roll diff signals (this session) ----------------------------


def test_over65_newly_filed_contributes_configured_weight() -> None:
    df = pd.DataFrame([_row(over65_newly_filed=True)])
    _scores, _bands, breakdown = compute_score_breakdown(df, _CONFIG)
    assert "Newly 65+:+15" in breakdown.iloc[0]


def test_ag_exemption_rollback_contributes_configured_weight() -> None:
    df = pd.DataFrame([_row(ag_exemption_rollback=True)])
    _scores, _bands, breakdown = compute_score_breakdown(df, _CONFIG)
    assert "Ag exemption dropped:+20" in breakdown.iloc[0]


# --- Tenure-gated likely_rental (tired landlord, this session) ---------------


def test_long_tenure_rental_gets_tired_landlord_label_not_full_rental_penalty() -> None:
    df = pd.DataFrame([_row(tenure_years=20.0, likely_rental=True)])
    _, _, breakdown = compute_score_breakdown(df, _CONFIG)
    assert "Tired landlord:+5" in breakdown.iloc[0]
    assert "Likely rental:" not in breakdown.iloc[0]


def test_short_tenure_rental_keeps_likely_rental_label_and_full_penalty() -> None:
    df = pd.DataFrame([_row(tenure_years=10.0, likely_rental=True)])
    _, _, breakdown = compute_score_breakdown(df, _CONFIG)
    assert "Likely rental:-20" in breakdown.iloc[0]
    assert "Tired landlord:" not in breakdown.iloc[0]


def test_rental_with_unknown_tenure_defaults_to_likely_rental_not_tired_landlord() -> None:
    df = pd.DataFrame([_row(tenure_years=float("nan"), likely_rental=True)])
    _, _, breakdown = compute_score_breakdown(df, _CONFIG)
    assert "Likely rental:-20" in breakdown.iloc[0]
    assert "Tired landlord:" not in breakdown.iloc[0]


def test_long_tenure_rental_score_reflects_tired_landlord_bonus() -> None:
    df = pd.DataFrame([_row(tenure_years=20.0, likely_rental=True)])
    scores, _ = compute_scores(df, _CONFIG)
    # 25 (9+ yrs) + 10 (15+ yrs) + 5 (longevity bonus, floor(20-15)) + 5 (tired landlord) = 45
    assert scores.iloc[0] == pytest.approx(45.0)
