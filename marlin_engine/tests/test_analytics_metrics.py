"""Per-parcel flag tests. Spec §5.3-§5.4, §11: absentee matching edge cases
(unit numbers, PO boxes, ST vs STREET)."""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from marlin_engine.analytics.metrics import (
    FarmAggregates,
    compute_ag_exemption_rollback,
    compute_farm_aggregates,
    compute_homestead_dropped,
    compute_over65_newly_filed,
    compute_parcel_metrics,
    fetch_prior_roll_year_snapshot,
)


def _base_row(**overrides) -> dict:
    row = {
        "parcel_id": "1",
        "situs_address": "100 MAIN ST",
        "mail_address": "100 MAIN ST",
        "mail_state": "TX",
        "owner_name": "SMITH JOHN A",
        "deed_date": date(2015, 1, 1),
        "homestead": True,
        "over65_exempt": False,
        "is_sfr": True,
        "roll_year": 2025,
    }
    row.update(overrides)
    return row


def test_absentee_false_when_mail_matches_situs() -> None:
    df = pd.DataFrame([_base_row()])
    result = compute_parcel_metrics(df)
    assert result.iloc[0]["absentee"] == False  # noqa: E712


def test_absentee_true_when_mail_differs_from_situs() -> None:
    df = pd.DataFrame([_base_row(mail_address="900 OTHER AVE")])
    result = compute_parcel_metrics(df)
    assert result.iloc[0]["absentee"] == True  # noqa: E712


def test_absentee_normalizes_st_vs_street_suffix() -> None:
    """ST/STREET-style USPS suffix normalization (spec §5.3) -- same address
    written two different ways must not falsely trigger absentee."""
    df = pd.DataFrame([_base_row(situs_address="100 MAIN ST", mail_address="100 MAIN STREET")])
    result = compute_parcel_metrics(df)
    assert result.iloc[0]["absentee"] == False  # noqa: E712


def test_absentee_strips_unit_numbers_before_comparing() -> None:
    """Unit stripping (spec §5.3) -- an owner living in their own unit shouldn't
    be flagged absentee just because the mailing address includes an APT/UNIT
    suffix the situs address doesn't repeat."""
    df = pd.DataFrame([_base_row(situs_address="210 LAVACA ST", mail_address="210 LAVACA ST APT 3402")])
    result = compute_parcel_metrics(df)
    assert result.iloc[0]["absentee"] == False  # noqa: E712


def test_absentee_true_for_po_box_mailing_address() -> None:
    """PO Box mailing address => absentee = TRUE unconditionally (spec §5.3)."""
    df = pd.DataFrame([_base_row(situs_address="100 MAIN ST", mail_address="PO BOX 4501")])
    result = compute_parcel_metrics(df)
    assert result.iloc[0]["absentee"] == True  # noqa: E712


def test_out_of_state_true_when_mail_state_not_tx() -> None:
    df = pd.DataFrame([_base_row(mail_state="CA")])
    result = compute_parcel_metrics(df)
    assert result.iloc[0]["out_of_state"] == True  # noqa: E712


def test_out_of_state_false_when_mail_state_is_tx() -> None:
    df = pd.DataFrame([_base_row(mail_state="TX")])
    result = compute_parcel_metrics(df)
    assert result.iloc[0]["out_of_state"] == False  # noqa: E712


def test_tenure_years_computed_from_deed_date_relative_to_roll_year() -> None:
    df = pd.DataFrame([_base_row(deed_date=date(2016, 1, 1), roll_year=2025)])
    result = compute_parcel_metrics(df)
    assert result.iloc[0]["tenure_years"] == pytest.approx(9.0, abs=0.05)


def test_tenure_years_null_when_deed_date_missing() -> None:
    df = pd.DataFrame([_base_row(deed_date=None)])
    result = compute_parcel_metrics(df)
    assert pd.isna(result.iloc[0]["tenure_years"])


def test_senior_longtenure_requires_over65_and_15_plus_years() -> None:
    df = pd.DataFrame(
        [
            _base_row(over65_exempt=True, deed_date=date(2005, 1, 1), roll_year=2025),  # 20yr, over65 -> True
            _base_row(over65_exempt=True, deed_date=date(2020, 1, 1), roll_year=2025),  # 5yr, over65 -> False
            _base_row(over65_exempt=False, deed_date=date(2005, 1, 1), roll_year=2025),  # 20yr, not over65 -> False
        ]
    )
    result = compute_parcel_metrics(df)
    assert result["senior_longtenure"].tolist() == [True, False, False]


def test_likely_rental_requires_sfr_not_homestead_and_absentee_or_entity() -> None:
    df = pd.DataFrame(
        [
            _base_row(is_sfr=True, homestead=False, mail_address="900 OTHER AVE"),  # SFR, absentee, not homestead
            _base_row(is_sfr=True, homestead=True, mail_address="900 OTHER AVE"),  # homestead -> not rental
            _base_row(is_sfr=False, homestead=False, mail_address="900 OTHER AVE"),  # not SFR -> not rental
            _base_row(is_sfr=True, homestead=False, owner_name="ACME HOLDINGS LLC"),  # entity, not homestead
        ]
    )
    result = compute_parcel_metrics(df)
    assert result["likely_rental"].tolist() == [True, False, False, True]


def test_owner_is_entity_flag_set_on_metrics_output() -> None:
    df = pd.DataFrame([_base_row(owner_name="ACME HOLDINGS LLC"), _base_row(owner_name="SMITH JOHN A")])
    result = compute_parcel_metrics(df)
    assert result["owner_is_entity"].tolist() == [True, False]


def test_compute_recent_sale_true_when_jan1_owner_name_differs_and_tenure_short() -> None:
    df = pd.DataFrame(
        [_base_row(owner_name="JONES MARY", jan1_owner_name="SMITH JOHN A", deed_date=date(2025, 6, 1), roll_year=2025)]
    )
    result = compute_parcel_metrics(df)
    assert result.iloc[0]["recent_sale"] == True  # noqa: E712


def test_compute_recent_sale_false_when_jan1_owner_name_matches_current_owner() -> None:
    df = pd.DataFrame([_base_row(owner_name="SMITH JOHN A", jan1_owner_name="SMITH JOHN A")])
    result = compute_parcel_metrics(df)
    assert result.iloc[0]["recent_sale"] == False  # noqa: E712


def test_compute_recent_sale_false_when_joint_owner_added() -> None:
    """A joint owner being added ('SMITH JOHN A' -> 'SMITH JOHN A & JANE') keeps
    every jan1-owner token as a subset of the current name -- token_set_ratio
    stays high, so this must not look like a sale."""
    df = pd.DataFrame(
        [
            _base_row(
                owner_name="SMITH JOHN A & JANE",
                jan1_owner_name="SMITH JOHN A",
                deed_date=date(2025, 6, 1),
                roll_year=2025,
            )
        ]
    )
    result = compute_parcel_metrics(df)
    assert result.iloc[0]["recent_sale"] == False  # noqa: E712


def test_compute_recent_sale_false_when_retitled_to_trust() -> None:
    df = pd.DataFrame(
        [
            _base_row(
                owner_name="SMITH JOHN A REVOCABLE TRUST",
                jan1_owner_name="SMITH JOHN A",
                deed_date=date(2025, 6, 1),
                roll_year=2025,
            )
        ]
    )
    result = compute_parcel_metrics(df)
    assert result.iloc[0]["recent_sale"] == False  # noqa: E712


def test_compute_recent_sale_guarded_by_long_tenure() -> None:
    """Name differs (a real format change, not a sale) but tenure is long --
    deed_date is the more authoritative source, so this must not fire."""
    df = pd.DataFrame(
        [_base_row(owner_name="JONES MARY", jan1_owner_name="SMITH JOHN A", deed_date=date(2010, 1, 1), roll_year=2025)]
    )
    result = compute_parcel_metrics(df)
    assert result.iloc[0]["recent_sale"] == False  # noqa: E712


def test_compute_recent_sale_false_when_jan1_owner_name_missing() -> None:
    df = pd.DataFrame([_base_row(jan1_owner_name=None, deed_date=date(2025, 6, 1), roll_year=2025)])
    result = compute_parcel_metrics(df)
    assert result.iloc[0]["recent_sale"] == False  # noqa: E712


def test_compute_recent_sale_defaults_false_when_column_entirely_absent() -> None:
    """jan1_owner_name may not exist at all on the input df (older test
    fixtures, or a DB row from before the ingest backfill) -- graceful
    degradation, not a KeyError."""
    df = pd.DataFrame([_base_row()])
    assert "jan1_owner_name" not in df.columns
    result = compute_parcel_metrics(df)
    assert result.iloc[0]["recent_sale"] == False  # noqa: E712


def test_data_gap_true_when_deed_date_missing() -> None:
    df = pd.DataFrame([_base_row(deed_date=None), _base_row(deed_date=date(2015, 1, 1))])
    result = compute_parcel_metrics(df)
    assert result["data_gap"].tolist() == [True, False]


def test_compute_farm_aggregates_basic_counts() -> None:
    df = pd.DataFrame(
        [
            _base_row(is_sfr=True, homestead=True, deed_date=date(2010, 1, 1), roll_year=2025),
            _base_row(is_sfr=True, homestead=False, mail_address="900 OTHER AVE", mail_state="CA"),
            _base_row(is_sfr=True, homestead=True, deed_date=date(2020, 1, 1), roll_year=2025),
        ]
    )
    metrics = compute_parcel_metrics(df)
    agg = compute_farm_aggregates(metrics)

    assert isinstance(agg, FarmAggregates)
    assert agg.total_sfr_parcels == 3
    assert agg.absentee_count == 1
    assert agg.out_of_state_count == 1


def test_compute_farm_aggregates_homestead_dropped_none_when_no_prior_year_loaded() -> None:
    """Regression test: compute_parcel_metrics(df) with no `prior` must not
    cause compute_farm_aggregates to report a real 0 for homestead_dropped --
    that would be indistinguishable from a farm that genuinely has zero drops.
    'Not computable' (None) and 'computed, and it's zero' must stay distinct
    (FarmAggregates' documented contract)."""
    df = pd.DataFrame(
        [
            _base_row(is_sfr=True, homestead=True, deed_date=date(2010, 1, 1), roll_year=2025),
            _base_row(is_sfr=True, homestead=False, deed_date=date(2020, 1, 1), roll_year=2025),
        ]
    )
    metrics = compute_parcel_metrics(df)  # no prior -- no second roll year loaded
    agg = compute_farm_aggregates(metrics)

    assert agg.homestead_dropped_count is None
    assert agg.homestead_dropped_pct is None


def test_over65_newly_filed_true_when_exemption_gained_this_year() -> None:
    current = pd.Series([True, True, False])
    prior = pd.Series([False, True, False])
    result = compute_over65_newly_filed(current, prior)
    assert list(result) == [True, False, False]


def test_over65_newly_filed_false_when_prior_data_missing() -> None:
    current = pd.Series([True])
    prior = pd.Series([pd.NA], dtype="boolean")
    result = compute_over65_newly_filed(current, prior)
    assert list(result) == [False]  # no prior-year history means "not yet observed," not a false positive


def test_homestead_dropped_true_when_exemption_lost_this_year() -> None:
    current = pd.Series([False, True, False])
    prior = pd.Series([True, True, False])
    result = compute_homestead_dropped(current, prior)
    assert list(result) == [True, False, False]


def test_ag_exemption_rollback_true_when_land_state_cd_leaves_d1() -> None:
    current = pd.Series(["A1", "D1", "C1"])
    prior = pd.Series(["D1", "D1", "C1"])
    result = compute_ag_exemption_rollback(current, prior)
    assert list(result) == [True, False, False]


def test_ag_exemption_rollback_false_when_land_state_cd_missing() -> None:
    current = pd.Series([pd.NA], dtype="object")
    prior = pd.Series([pd.NA], dtype="object")
    result = compute_ag_exemption_rollback(current, prior)
    assert list(result) == [False]


def test_fetch_prior_roll_year_snapshot_selects_scoped_columns() -> None:
    import duckdb

    con = duckdb.connect(":memory:")
    con.execute("""
        CREATE TABLE parcels (
            county TEXT, parcel_id TEXT, roll_year INTEGER,
            over65_exempt BOOLEAN, homestead BOOLEAN, land_state_cd TEXT
        )
    """)
    con.execute("""INSERT INTO parcels VALUES
        ('travis','A1',2024,TRUE,FALSE,'D1'),
        ('travis','A2',2024,FALSE,TRUE,NULL),
        ('travis','A1',2025,FALSE,FALSE,NULL),
        ('hays','A1',2024,TRUE,TRUE,'D1')
    """)
    out = fetch_prior_roll_year_snapshot(con, "travis", ["A1", "A2"], 2024)
    assert set(out.columns) == {"parcel_id", "over65_exempt", "homestead", "land_state_cd"}
    assert sorted(out["parcel_id"]) == ["A1", "A2"]          # 2025 row + hays row excluded
    empty = fetch_prior_roll_year_snapshot(con, "travis", [], 2024)
    assert list(empty.columns) == ["parcel_id", "over65_exempt", "homestead", "land_state_cd"]
    assert len(empty) == 0
    con.close()


def test_compute_parcel_metrics_diff_signals_absent_when_no_prior_given() -> None:
    """Without a prior snapshot, the three diff columns must be entirely absent
    from the result -- not present-and-False -- so compute_farm_aggregates can
    tell "no prior year loaded" apart from "loaded, and genuinely zero drops"
    (see the FarmAggregates docstring's true-zero-vs-not-computable contract)."""
    df = pd.DataFrame([_base_row()])
    result = compute_parcel_metrics(df)
    assert "over65_newly_filed" not in result.columns
    assert "homestead_dropped" not in result.columns
    assert "ag_exemption_rollback" not in result.columns


def test_compute_parcel_metrics_diff_signals_computed_from_prior() -> None:
    df = pd.DataFrame(
        [_base_row(parcel_id="1", over65_exempt=True, homestead=False, land_state_cd="A1")]
    )
    prior = pd.DataFrame(
        [{"parcel_id": "1", "over65_exempt": False, "homestead": True, "land_state_cd": "D1"}]
    )
    result = compute_parcel_metrics(df, prior)
    row = result.iloc[0]
    assert row["over65_newly_filed"] == True  # noqa: E712
    assert row["homestead_dropped"] == True  # noqa: E712
    assert row["ag_exemption_rollback"] == True  # noqa: E712


def test_compute_parcel_metrics_over65_newly_filed_false_when_prior_also_true_with_mixed_batch() -> None:
    """Regression test: found via a real end-to-end sample run against Park West
    At Circle C data, not by any prior unit test. The existing
    ...computed_from_prior test above uses a single row where every parcel_id
    matches between df and prior, so the join never needs to introduce NaN and
    the joined prior column stays a clean bool dtype -- it can't catch this bug.
    A real farm has a MIX of parcels with and without prior-year data, which
    forces pandas to represent the joined prior column as `object` dtype (to
    hold real bools alongside NaN for unmatched parcels). Python's unary `~` on
    an object-dtype Series containing real bools does bitwise inversion, not
    logical NOT (`~True == -2`, `~False == -1`, both truthy) -- so a naive
    `~prior.fillna(False)` was always true whenever ANY prior data existed,
    regardless of its actual value, incorrectly firing over65_newly_filed for a
    parcel whose exemption status didn't change at all."""
    df = pd.DataFrame(
        [
            _base_row(parcel_id="1", over65_exempt=True),  # has prior data, prior=True -> must NOT fire
            _base_row(parcel_id="2", over65_exempt=True),  # has prior data, prior=False -> must fire
            _base_row(parcel_id="3", over65_exempt=True),  # no prior data at all -> must NOT fire
        ]
    )
    prior = pd.DataFrame(
        [
            {"parcel_id": "1", "over65_exempt": True, "homestead": True, "land_state_cd": None},
            {"parcel_id": "2", "over65_exempt": False, "homestead": True, "land_state_cd": None},
        ]
    )
    result = compute_parcel_metrics(df, prior)

    by_parcel = result.set_index("parcel_id")["over65_newly_filed"]
    assert by_parcel["1"] == False  # noqa: E712 -- unchanged (already had it), must not fire
    assert by_parcel["2"] == True  # noqa: E712 -- genuinely newly gained
    assert by_parcel["3"] == False  # noqa: E712 -- no prior data, must not fire
