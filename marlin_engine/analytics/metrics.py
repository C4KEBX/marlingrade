"""Per-parcel flags + farm-level aggregates. Spec §5.3–§5.4. Implemented in S4 — see FARMSIGNAL_30_DAY_PLAN.md."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from rapidfuzz import fuzz

from marlin_engine.analytics.scoring import compute_score_breakdown
from marlin_engine.normalize.address import normalize_address
from marlin_engine.normalize.owners import entity_owner_mask

_TENURE_THRESHOLD_YEARS = 9  # spec §5.4: "past the typical move threshold"
_SENIOR_LONGTENURE_YEARS = 15  # spec §5.3
_RECENT_SALE_TENURE_YEARS = 2  # below this, a jan1-owner name mismatch is trusted as a real sale
_RECENT_SALE_NAME_SIMILARITY = 70  # token_set_ratio floor below which the name is "different," not just reformatted

_PO_BOX_RE = re.compile(r"\bP\.?\s*O\.?\s*BOX\b")


def compute_absentee(situs_address: pd.Series, mail_address: pd.Series) -> pd.Series:
    """mail_address normalized != situs_address normalized, OR mail_address is a PO
    Box (spec §5.3 -- PO Box mailing address is absentee unconditionally)."""
    mail_filled = mail_address.fillna("")
    is_po_box = mail_filled.str.contains(_PO_BOX_RE)
    norm_situs = situs_address.fillna("").map(normalize_address)
    norm_mail = mail_filled.map(normalize_address)
    return is_po_box | (norm_situs != norm_mail)


def compute_out_of_state(mail_state: pd.Series) -> pd.Series:
    filled = mail_state.fillna("")
    return (filled != "") & (filled != "TX")


def compute_tenure_years(deed_date: pd.Series, roll_year: pd.Series) -> pd.Series:
    """(roll_date - deed_date) / 365.25, 1 decimal (spec §5.3). roll_date is
    approximated as Jan 1 of roll_year -- Texas CADs appraise ownership as of Jan 1
    of the tax year (Tex. Tax Code §23.01), and config/counties.yaml's roll_date
    field is still an unfilled TODO (not yet captured per-roll). This keeps tenure
    -- and therefore the score -- deterministic and reproducible across report runs
    on the same roll, rather than drifting with "today"."""
    roll_date = pd.to_datetime(roll_year.astype("Int64").astype(str) + "-01-01", errors="coerce")
    deed = pd.to_datetime(deed_date, errors="coerce")
    return ((roll_date - deed).dt.days / 365.25).round(1)


def compute_senior_longtenure(over65_exempt: pd.Series, tenure_years: pd.Series) -> pd.Series:
    """over65_exempt AND tenure_years >= 15 -- classic downsizer profile (spec §5.3)."""
    return over65_exempt.fillna(False) & (tenure_years >= _SENIOR_LONGTENURE_YEARS)


def compute_likely_rental(
    is_sfr: pd.Series, homestead: pd.Series, absentee: pd.Series, owner_is_entity: pd.Series
) -> pd.Series:
    """is_sfr AND NOT homestead AND (absentee OR owner_is_entity) (spec §5.3).
    Report label: "likely non-owner-occupied"."""
    return is_sfr.fillna(False) & ~homestead.fillna(False) & (absentee | owner_is_entity)


def compute_recent_sale(owner_name: pd.Series, jan1_owner_name: pd.Series, tenure_years: pd.Series) -> pd.Series:
    """True when the owner of record changed during the current roll year --
    jan1_owner_name (TCAD's Jan-1 owner of record) differs meaningfully from the
    current owner_name. A home that just changed hands is very unlikely to sell
    again immediately (matches the "purchased <2 years" negative signal from the
    operator's research notes).

    Uses rapidfuzz's token_set_ratio rather than exact string equality: a joint
    owner being added ("SMITH JOHN" -> "SMITH JOHN & JANE") or a re-titling into a
    trust ("SMITH JOHN" -> "SMITH JOHN REVOCABLE TRUST") both keep every token of
    the shorter name as a subset of the longer one, so token_set_ratio stays high
    even though the raw strings differ -- neither should look like a sale.

    Guarded by tenure_years < _RECENT_SALE_TENURE_YEARS (or missing, i.e. no
    deed_date on file): deed_date is the more authoritative source when present,
    so a long-tenured owner whose name representation merely changed format never
    fires this just from jan1_owner_name noise. When deed_date is itself missing,
    the jan1-owner diff becomes a useful independent backstop instead of a
    redundant check."""
    jan1_filled = jan1_owner_name.fillna("")
    owner_filled = owner_name.fillna("")
    has_jan1 = jan1_filled != ""
    similarity = pd.Series(
        [fuzz.token_set_ratio(a, b) for a, b in zip(owner_filled, jan1_filled)],
        index=owner_name.index,
    )
    name_changed = has_jan1 & (similarity < _RECENT_SALE_NAME_SIMILARITY)
    tenure_ok = tenure_years.isna() | (tenure_years < _RECENT_SALE_TENURE_YEARS)
    return name_changed & tenure_ok


# TX Comptroller state class code for qualified open-space (ag-use) land. Confirmed
# against the official state class code table; spot-check against real land_state_cd
# values in an already-ingested Travis roll before trusting this in production, same
# "verify before scoring" discipline as every other enrich/ signal in this codebase.
_AG_SPECIAL_USE_LAND_STATE_PREFIX = "D1"


def compute_over65_newly_filed(over65_exempt: pd.Series, prior_over65_exempt: pd.Series) -> pd.Series:
    """True when the parcel has the Over-65 exemption this roll year but did not
    have it the prior roll year. No prior-year data (first year loaded, or a new
    parcel) yields False, not a crash -- same "not yet observable" treatment as
    homestead_dropped's existing documented behavior.

    DEVIATION FROM TASK-3 BRIEF (flagged for review): the brief's literal formula
    was `over65_exempt.fillna(False) & ~prior_over65_exempt.fillna(False)`. That
    fails the brief's own "missing prior data" test -- fillna(False) makes a
    missing prior indistinguishable from a *known* False, so ~prior.fillna(False)
    is True in both cases, producing a false positive whenever the current value
    is True and the prior is simply unobserved. homestead_dropped and
    ag_exemption_rollback don't have this problem because they require the prior
    side of the AND to be True, and fillna(False) correctly suppresses a missing
    prior there. over65_newly_filed requires the prior side to be False, so it
    needs an explicit "was prior actually observed" guard instead.

    SECOND BUG, found via a real end-to-end sample run (not caught by unit tests,
    which always passed a clean bool-dtype Series): `prior_over65_exempt` as
    produced by compute_parcel_metrics's join (result.join(prior_lookup, ...))
    is `object` dtype, not `bool` -- pandas can't represent a column mixing real
    Python bools with NaN (for unmatched parcels) as a proper bool array. Python's
    unary `~` on an object-dtype Series containing real bools does *bitwise*
    inversion (`~True == -2`, `~False == -1`), not logical NOT -- both results
    are truthy, so `~prior_over65_exempt.fillna(False)` was ALWAYS true whenever
    prior data existed, regardless of its actual value, silently defeating the
    "was it actually gained this year" check. `.astype(bool)` after `.fillna()`
    forces a real bool dtype so `~` behaves as logical NOT again."""
    prior_known = prior_over65_exempt.notna()
    prior_was_exempt = prior_over65_exempt.fillna(False).astype(bool)
    return over65_exempt.fillna(False) & prior_known & ~prior_was_exempt


def compute_homestead_dropped(homestead: pd.Series, prior_homestead: pd.Series) -> pd.Series:
    """True when the parcel had a homestead exemption the prior roll year but not
    this one -- spec §5.3/§5.6's original definition, now computable now that a
    prior roll year is actually loadable (Task 1)."""
    return prior_homestead.fillna(False) & ~homestead.fillna(False)


def compute_ag_exemption_rollback(land_state_cd: pd.Series, prior_land_state_cd: pd.Series) -> pd.Series:
    """True when the parcel's land_state_cd was under ag/wildlife special-use
    appraisal (D1) the prior roll year and is not D1 this year -- a land-use change
    that typically precedes development or sale."""
    current_ag = land_state_cd.fillna("").str.startswith(_AG_SPECIAL_USE_LAND_STATE_PREFIX)
    prior_ag = prior_land_state_cd.fillna("").str.startswith(_AG_SPECIAL_USE_LAND_STATE_PREFIX)
    return prior_ag & ~current_ag


def compute_parcel_metrics(df: pd.DataFrame, prior: pd.DataFrame | None = None) -> pd.DataFrame:
    """Computes spec §5.2-§5.3 per-parcel flags. Input df must have: situs_address,
    mail_address, mail_state, owner_name, deed_date, homestead, over65_exempt,
    is_sfr, roll_year, parcel_id. `prior`, when given, is the same parcel set's
    prior-roll-year snapshot (parcel_id, over65_exempt, homestead, land_state_cd) --
    see fetch_prior_roll_year_snapshot. Without it (no second roll year loaded
    yet), over65_newly_filed/homestead_dropped/ag_exemption_rollback are NOT
    added to the result at all -- not an error, and not present-as-False either;
    see the comment above where they're computed for why the distinction
    matters. Downstream code (scoring.py's _optional_bool_column,
    compute_farm_aggregates below) is written to treat their absence as "not
    triggered" / "not computable," not a crash."""
    result = df.copy()
    result["owner_is_entity"] = entity_owner_mask(result["owner_name"])
    result["tenure_years"] = compute_tenure_years(result["deed_date"], result["roll_year"])
    result["absentee"] = compute_absentee(result["situs_address"], result["mail_address"])
    result["out_of_state"] = compute_out_of_state(result["mail_state"])
    result["senior_longtenure"] = compute_senior_longtenure(result["over65_exempt"], result["tenure_years"])
    result["likely_rental"] = compute_likely_rental(
        result["is_sfr"], result["homestead"], result["absentee"], result["owner_is_entity"]
    )
    # jan1_owner_name may be absent entirely (test fixtures, or a DB row from
    # before the migration/ingest backfill) -- treat that the same as "no jan1
    # data available," not an error.
    jan1_owner_name = result.get("jan1_owner_name", pd.Series(pd.NA, index=result.index))
    result["recent_sale"] = compute_recent_sale(result["owner_name"], jan1_owner_name, result["tenure_years"])
    result["data_gap"] = result["deed_date"].isna()  # spec §5.5: deed_date NULL -> score from remaining signals

    # over65_newly_filed/homestead_dropped/ag_exemption_rollback are only added
    # to the result when a real prior-year snapshot was supplied. This is
    # deliberate, not an oversight: compute_farm_aggregates' "true zero vs. not
    # computable" contract for homestead_dropped_count/_pct (see FarmAggregates'
    # docstring) depends on the column being *absent* -- not present-and-False --
    # when no second roll year has ever been loaded for this county/subdivision.
    # If these were always added as all-False, a farm with zero real history
    # would look identical to a farm that genuinely has zero drops, silently
    # collapsing "not computable" into "0". scoring.py's _optional_bool_column
    # already treats "column absent" and "column present but False" the same
    # way (both contribute 0 points), so per-parcel scoring is unaffected either
    # way -- only farm-level aggregates depend on the column's presence.
    if prior is not None and not prior.empty:
        prior_lookup = prior.set_index("parcel_id")[["over65_exempt", "homestead", "land_state_cd"]]
        prior_lookup = prior_lookup.add_suffix("_prior")
        merged_prior = result[["parcel_id"]].join(prior_lookup, on="parcel_id")

        result["over65_newly_filed"] = compute_over65_newly_filed(
            result["over65_exempt"], merged_prior["over65_exempt_prior"]
        )
        result["homestead_dropped"] = compute_homestead_dropped(result["homestead"], merged_prior["homestead_prior"])
        result["ag_exemption_rollback"] = compute_ag_exemption_rollback(
            result.get("land_state_cd", pd.Series(pd.NA, index=result.index)), merged_prior["land_state_cd_prior"]
        )
    return result


def fetch_prior_roll_year_snapshot(
    con, county: str, parcel_ids: list[str], prior_roll_year: int
) -> pd.DataFrame:
    """Looks up over65_exempt/homestead/land_state_cd for `parcel_ids` at
    `prior_roll_year`, scoped to `county`. Empty frame (not an error) when
    `parcel_ids` is empty -- callers pass this straight to compute_parcel_metrics,
    which already treats a missing/empty prior frame as "no history yet"."""
    if not parcel_ids:
        return pd.DataFrame(columns=["parcel_id", "over65_exempt", "homestead", "land_state_cd"])
    placeholders = ", ".join("?" for _ in parcel_ids)
    return con.execute(
        f"""SELECT parcel_id, over65_exempt, homestead, land_state_cd FROM parcels
        WHERE county = ? AND roll_year = ? AND parcel_id IN ({placeholders})""",
        [county, prior_roll_year, *parcel_ids],
    ).fetchdf()


@dataclass(frozen=True)
class FarmAggregates:
    """Farm-level aggregates for a subdivision_canon, scoped to SFR parcels only
    (spec §5.4). homestead_dropped_count/pct are omitted entirely (not just zeroed)
    when the underlying flag isn't available -- spec §5.4: "a true zero and 'not
    computable' must never look the same to the reader" -- so callers must check
    `homestead_dropped_count is not None` before displaying that stat."""

    total_sfr_parcels: int
    owner_occupied_count: int
    owner_occupied_pct: float
    absentee_count: int
    absentee_pct: float
    out_of_state_count: int
    out_of_state_pct: float
    likely_rental_count: int
    likely_rental_pct: float
    median_tenure_years: float | None
    past_threshold_count: int
    past_threshold_pct: float
    hot_count: int
    warm_count: int
    standard_count: int
    median_assessed_value: float | None
    homestead_dropped_count: int | None
    homestead_dropped_pct: float | None
    recent_sale_count: int
    recent_sale_pct: float
    tax_delinquent_count: int | None
    tax_delinquent_pct: float | None


def compute_farm_aggregates(df: pd.DataFrame) -> FarmAggregates:
    sfr = df[df["is_sfr"].fillna(False)]
    total = len(sfr)

    def pct(n: int) -> float:
        return round(100 * n / total, 1) if total else 0.0

    absentee_count = int(sfr["absentee"].sum())
    out_of_state_count = int(sfr["out_of_state"].sum())
    likely_rental_count = int(sfr["likely_rental"].sum())
    owner_occupied_count = int((~sfr["absentee"]).sum())

    tenure = sfr["tenure_years"].dropna()
    median_tenure = float(tenure.median()) if len(tenure) else None
    past_threshold_count = int((sfr["tenure_years"] >= _TENURE_THRESHOLD_YEARS).sum())

    assessed = sfr["assessed_value"].dropna() if "assessed_value" in sfr.columns else pd.Series(dtype=float)
    median_assessed = float(assessed.median()) if len(assessed) else None

    if "score_band" in sfr.columns:
        hot_count = int((sfr["score_band"] == "HOT").sum())
        warm_count = int((sfr["score_band"] == "WARM").sum())
        standard_count = int((sfr["score_band"] == "STANDARD").sum())
    else:
        hot_count = warm_count = standard_count = 0

    if "homestead_dropped" in sfr.columns and sfr["homestead_dropped"].notna().any():
        homestead_dropped_count = int(sfr["homestead_dropped"].fillna(False).sum())
        homestead_dropped_pct = pct(homestead_dropped_count)
    else:
        homestead_dropped_count = None
        homestead_dropped_pct = None

    recent_sale_count = int(sfr["recent_sale"].fillna(False).sum()) if "recent_sale" in sfr.columns else 0

    # tax_delinquent is only populated once `farmsignal enrich tax-delinquency`
    # has run for this county -- None (not 0) when the column is absent or
    # entirely NULL, same "true zero vs not computable" rule as homestead_dropped.
    if "tax_delinquent" in sfr.columns and sfr["tax_delinquent"].notna().any():
        tax_delinquent_count = int(sfr["tax_delinquent"].fillna(False).sum())
        tax_delinquent_pct = pct(tax_delinquent_count)
    else:
        tax_delinquent_count = None
        tax_delinquent_pct = None

    return FarmAggregates(
        total_sfr_parcels=total,
        owner_occupied_count=owner_occupied_count,
        owner_occupied_pct=pct(owner_occupied_count),
        absentee_count=absentee_count,
        absentee_pct=pct(absentee_count),
        out_of_state_count=out_of_state_count,
        out_of_state_pct=pct(out_of_state_count),
        likely_rental_count=likely_rental_count,
        likely_rental_pct=pct(likely_rental_count),
        median_tenure_years=median_tenure,
        past_threshold_count=past_threshold_count,
        past_threshold_pct=pct(past_threshold_count),
        hot_count=hot_count,
        warm_count=warm_count,
        standard_count=standard_count,
        median_assessed_value=median_assessed,
        homestead_dropped_count=homestead_dropped_count,
        homestead_dropped_pct=homestead_dropped_pct,
        recent_sale_count=recent_sale_count,
        recent_sale_pct=pct(recent_sale_count),
        tax_delinquent_count=tax_delinquent_count,
        tax_delinquent_pct=tax_delinquent_pct,
    )
