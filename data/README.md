# Marlin Grade — data

## `farmsignal.duckdb` (282 MB)

Copied **verbatim** from the FarmSignal project on 2026-09-07:

- Source: `/Users/justinmason/Claude Code/FarmSignal/data/farmsignal.duckdb`
- Verified byte-identical to source at copy time (`cmp`).
- Kept the original filename. Rename later if desired.

This is a straight lift of the existing dataset so the Marlin Grade build has
real data to work against. No transformation, no schema cleanup, no re-export.

### Origin of the underlying data

Ingested by FarmSignal's Travis CAD adapter from the TCAD bulk export
`travis_SUPP 318_2025_WEBSITE EXPORT` (fixed-width, ~470-field TP/True Prodigy
CAMA layout). Subdivision names were then canonicalized (regex + fuzzy + manual
alias file) and GIS-backfilled by spatial-joining parcel centroids against the
City of Austin recorded-plat polygon layer.

## Contents

One table: **`parcels`** — 486,859 rows, **Travis County, 2025 roll only**.
(FarmSignal's Williamson and Hays adapters were never implemented; no data
exists for those counties.)

- 16,004 distinct `subdivision_canon` values
- 349,422 rows with `is_sfr = true`

### Columns that are populated and useful (fill rate)

| Group | Columns |
|---|---|
| Identity / location | `county`, `parcel_id` (100%), `roll_year`, `situs_address` (100%), `situs_zip` (96%), `situs_city` (43%) |
| Owner | `owner_name` (100%), `mail_address` / `mail_city` / `mail_state` / `mail_zip` (~100%), `jan1_owner_name` (46%) |
| Records | `legal_description` (100%), `subdivision_raw` / `subdivision_canon` (91.5%), `deed_date` (86%), `homestead` (100%), `over65_exempt` (100%), `property_class` (92%), `is_sfr` (100%), `assessed_value` (100%), `geo_id` (92%) |

### Columns present in the schema but effectively empty

Computed by FarmSignal's analytics/enrichment stages, which only ever ran
against **one ~184-parcel farm** — so these are populated for 184 rows out of
486,859:

`score`, `score_band`, `score_breakdown`, `tenure_years`, `absentee`,
`out_of_state`, `likely_rental`, `senior_longtenure`, `recent_sale`,
`recent_permit_activity`, `tax_delinquent`, `has_code_violation`

Fully empty (0 rows): `year_built`, `living_sqft`, `land_state_cd`,
`homestead_dropped`, `over65_newly_filed`, `ag_exemption_rollback`,
`flood_zone`, `in_special_flood_hazard_area`.

## Gotchas for whatever consumes this next

1. **`parcel_id` is a zero-padded string** (e.g. `000000100041`). FarmSignal's
   GIS geometry file (`travis_centroids.json`, not copied here) keys parcel
   polygons by **integer `PROP_ID`** (e.g. `177373`). Any join needs an
   int-cast / leading-zero strip on one side.
2. **The scoring engine is essentially unrun.** Treat every `score*` and flag
   column as needing a full recompute across all 486,859 rows. The per-parcel
   scoring logic itself lives in the FarmSignal repo
   (`src/farmsignal/analytics/`), tuned against a single subdivision.
3. **Single roll year.** Multi-year diff signals (`homestead_dropped`,
   `over65_newly_filed`, `ag_exemption_rollback`) require a prior roll year
   loaded; none is. They are empty by design, not by bug.
   → **Action (build-spec [GAP-15], §6.1):** download + load the **Travis 2024
   certified roll** alongside this 2025 data so those signals activate. Same
   fixed-width family; verify byte offsets against the 2024 layout doc.
