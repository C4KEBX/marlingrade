# Phase A — engine correctness on ZIP 78749 (spec §10.1)

Roll year: **2025** (single roll loaded — the three prior-roll diff signals
`homestead_dropped` / `over65_newly_filed` / `ag_exemption_rollback` contribute 0
for every parcel) · Cutoffs: **{A: 67, B: 44, C: 35, D: 25}** (frozen 2026-09-09,
`marlin_engine/grades.py`) · Bundle built: **2026-09-09** (`web/public/data/`,
`scripts/build_demo_bundle.py`) · Validation date: **2026-09-09**

Scope of the run: `SELECT * FROM parcels WHERE situs_zip = '78749' AND is_sfr AND
roll_year = 2025` → **10,423 SFR parcels**. Every check runs the engine fresh
(`compute_parcel_metrics` + `compute_score_breakdown` + `grades.assign_series`),
the same path `build_demo_bundle.py` uses. The DuckDB precomputed columns
(`owner_is_entity`, `tenure_years`, `out_of_state`, `score`, …) are **stale — only
184 of 486,859 rows are populated** (the original FarmSignal scored set), so all
"vs the DB column" comparisons in the skeleton are moot; the engine recomputes.

| Check | Method | Expected | Result | Notes |
|---|---|---|---|---|
| Entity owners flagged | `entity_owner_mask` on all 10,423 owner names vs. broad keyword regex `(LLC\|L L C\|LP\|LTD\|INC\|CORP\|TRUST\|TRUSTEE\|PARTNERS\|PROPERTIES\|HOMES\|INVESTMENTS\|HOLDINGS)` | every obvious entity flagged, no obvious misses | **PASS** | Engine flags 661 (6.3%). **Zero** keyword-present-but-missed. 10 flagged rows fall outside the broad list — 8 are correct (`CITY OF AUSTIN`, `HOUSING AUTHORITY OF TRAVIS COUNTY`, `… LIVING TR` trusts, `ASCENDLINK CAPITAL LIMITED`). 2 are surname false positives: `LE HOA & ANHUU` (`\bHOA\b` matches the given name "Hoa") and `CHURCH MELINDA GAYLE CURLEY` (`\bCHURCH\b` matches the surname). Not a bug — the keyword list is spec §5.2 verbatim and the word-boundary regex does exactly what it specifies; surname collisions are an inherent precision limit of keyword matching at ~0.3% (2/661). The bug bar for this row is "misses an obvious pattern" — there are none. |
| Known rentals → `likely_rental` | no operator ground-truth address list available in this task's inputs → proxy: definitional integrity + obvious investor LLCs | flagged | **PASS (proxy) — ground truth data-limited** | `likely_rental` fires for 1,514 parcels (14.5%); **0** have a homestead exemption (definition holds: `is_sfr AND NOT homestead AND (absentee OR entity)`). 1,486 absentee-driven, 381 entity-driven (overlap). Obvious rental LLCs all flagged: `KENSINGTON PEAVY LLC`, `GATEWAY ASSETS TX LLC`, `SUENO PARTNERS LLC`, `DEMARTINI PROPERTIES LLC` — and the one `KENSINGTON PEAVY LLC` parcel that carries a homestead exemption is correctly **not** flagged. Tired-landlord carve-out verified: all 459 `likely_rental` parcels with tenure ≥ 15 yr get `Tired landlord:+5` **instead of** `Likely rental:-20` (no stacking); all 1,055 with tenure < 15 get `Likely rental:-20`. The operator's own 78749 ground-truth list would make this a full PASS; the engine logic is correct. |
| Long-tenured owners → tenure + bonus | `deed_date < 2005-01-01` sample (2,586 parcels); recompute `(2025-01-01 − deed_date)/365.25` and compare to `tenure_years`; check breakdown tokens | `tenure_years` correct, +25 / +10 / per-year bonus present | **PASS** | **0** tenure math mismatches across all 2,586 (tolerance 0.05 yr). Roll date anchored at Jan 1 of `roll_year` (Tex. Tax Code §23.01), deterministic — correct. All 2,586 parcels with tenure ≥ 15 carry `Tenure 9+ yrs:+25`, `Tenure 15+ yrs:+10`, and `Tenure bonus:+N` where N = `floor(tenure − 15)`. Spot check: deed 1980-10-24 → tenure 44.2 → `Tenure bonus:+29`; deed 1999-11-05 → tenure 25.2 → `Tenure bonus:+10`. |
| `out_of_state` −10 applied | engine-direct: real 78749 parcels scored twice, once with `mail_state` forced out of TX; also 282 real non-TX parcels | score 10 lower than same profile in-state; `Out-of-state:-10` token | **PASS** | Clean end-to-end case (parcel `000000446922`, not at the score floor): in-state **36.0** → forced `CA` **26.0**, delta **−10.0**, `Out-of-state:-10` appears in the breakdown. `compute_out_of_state` = `(mail_state != '') & (mail_state != 'TX')` — NULL/blank state correctly not penalised. Across a varied 5-parcel forced-`NY` sample the raw −10 is always in the breakdown; the *observed* score delta is sometimes −5 or 0 because the documented `[0, 100]` floor clip absorbs part of it on parcels already at/near 0 (zero-inflated roll). `out_of_state_pct` for 78749 = 2.7% (282/10,423) — low but expected, TX is a large in-state market. |
| `recent_sale` de-prioritises | engine-direct + real data: `jan1_owner_name` present (1,956/10,423), tenure < 2, name mismatch via `token_set_ratio < 70` | `recent_sale` True, −25 | **PASS** | Engine fires `recent_sale` for 46 real 78749 parcels — all with tenure < 0 to ~0 and a genuinely different Jan-1 owner (e.g. `KENSINGTON PEAVY LLC` ← `SMITH TRENT MATTHEW`; `GAL DANA` ← `VIDA SKYE ACQUISITIONS INC`). The fuzzy guard correctly suppresses re-titles: `PORTNOY ANDRA SUE` ↔ `LUBIN JAN ELLEN & ANDRA SUE PORTNOY` and `KG LEASING PROPERTIES LLC` ↔ `KG LEASING LLC` both stay False. Engine-direct control/treatment on a tenure-0.2 parcel: raw contribution sum 0 → **−25** with `Recent sale:-25` token. Final clipped score stays 0 (recent-sale parcels are structurally young → no tenure points → already at the floor); the −25 is unambiguously applied to the weighted sum. |
| Zip aggregates believable | `compute_farm_aggregates` on the 10,423, cross-checked against `zips.json` | absentee ~25–35%, median tenure ~9–13 yr | **PASS (median) / PASS-with-note (absentee)** | `zips.json` 78749 matches a fresh recompute exactly: absentee **21.1%**, likely-rental 14.5%, median tenure **9.9 yr**, out-of-state 2.7%, past-9yr-threshold 53.2%. Median tenure 9.9 is inside the 9–13 band. Absentee 21.1% sits just below the skeleton's rough 25–35% guess — **not a bug**: `mail_address` is 100% populated for 78749 (no NULL-inflation artifact), absentee among rows-with-mail is the identical 21.1%, and 21% absentee for owner-occupied SW Austin is reasonable. The 25–35% figure in the skeleton was an un-anchored prior, not a measured expectation. |
| Address → parcel resolves | `situs_norm` in `parcels-78749.json`: distinct-count, collision clusters, 10 random hand-picked lookups | exact 1 match each | **PASS** | 10,409 distinct `situs_norm` over 10,423 parcels; **0 blank**. 10/10 randomly hand-picked addresses resolve to exactly one parcel. 5 collision clusters (14 parcels, 0.13%), all verified against DuckDB as genuine multi-parcel sites: `7500 SHADOWRIDGE RUN` = the 11-unit "Laurels at Legend Oaks" condominium (class A4, `UNT 51`–`UNT 61`); `6119 VALIANT CIR` = a TCAD land-only / improvement-only split; `6520 ROTAN DR` = two resubdivided lots. `normalize_address` strips unit markers by spec §5.3 design, so condo units at one street address intentionally collapse — expected tradeoff, not an engine fault. |
| Grade distribution sane | `grades.assign_series` over the 10,423; `zips.json` distribution | A single digits, F non-trivial | **PASS** | A **4.2%** (439), B 19.8% (2,061), C 11.6% (1,208), D 14.4% (1,503), F **50.0%** (5,212). A is single-digit; F is substantial. `zips.json` matches a direct `assign_series` recompute exactly. 78749 grades richer than the whole-roll projection in `grades.py` (A ≈ 3.4%) because SW Austin is long-tenured — a real signal, not a calibration error. |

## Engine bugs found and fixed

**None.** All eight rows pass on engine logic. Two rows are constrained on the
*ground-truth* side rather than the engine side:

- **Known rentals** — no operator 78749 rental-address list was available in this
  task's inputs. The definitional-integrity + obvious-investor-LLC proxy passes;
  a full pass needs the operator's list.
- **`out_of_state` / `recent_sale` end-to-end score movement** — the documented
  `[0, 100]` floor clip masks part of the negative delta on parcels that already
  sit at 0 (the roll is zero-inflated: ~63% of parcels have no tenure/motivation
  signal). This is intended behaviour — the raw weighted contribution (`−10`,
  `−25`) is always applied and always shown in the breakdown; only the *final
  clipped* score can fail to move. A clean, non-floored end-to-end demonstration
  exists for `out_of_state` (36.0 → 26.0).

No `marlin_engine/` module was modified. `.venv/bin/python -m pytest -q` →
**82 passed**, zero warnings (unchanged from the pre-validation baseline).

## Minor observations (not acted on — no change to engine or data)

- **Entity keyword precision:** `\bHOA\b` / `\bCHURCH\b` / `\bTR\b` in the spec
  §5.2 verbatim list collide with real person names at ~0.3% of flagged rows in
  78749 (`LE HOA & ANHUU`, `CHURCH MELINDA GAYLE CURLEY`). Faithful to spec;
  worth a note if a future pass tightens entity precision.
- **DuckDB precomputed columns are stale** (`owner_is_entity`, `score`,
  `tenure_years`, … populated for only 184/486,859 rows). Harmless — the bundle
  build recomputes everything — but any future check that reads those columns
  directly instead of running the engine will be wrong.
