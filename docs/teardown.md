# FarmSignal → Marlin Grade teardown

Subsystem-by-subsystem verdict on the existing FarmSignal codebase
(`/Users/justinmason/Claude Code/FarmSignal`). Legend:

- **KEEP** — port roughly as-is, it already does the right thing
- **ADAPT** — the logic is good, the shape/scope/trigger changes
- **CUT** — does not exist in the Marlin model
- **NEW** — Marlin needs this and FarmSignal has no antecedent

---

## The core reframe

| | FarmSignal | Marlin Grade |
|---|---|---|
| Unit of work | one subdivision "farm" (`subdivision_canon`, ≤1,500 SFR) | one **address** (A–F grade) + one **zip / farm area** (monitoring) |
| Delivery | operator runs a CLI, emails a PDF | self-serve multi-tenant web app + API + alerts |
| Cadence | annual manual CAD roll download | "daily" refresh + change/spike alerts |
| Money | $49 one-time / $29 watch / $79–199 exclusive | $99 / $199 / $499 per month, metered |
| Geography | Travis only (real); WCAD/Hays stubs | Travis + Williamson + Hays at launch → TX metros |
| Score shown | 0–100 + HOT/WARM/STANDARD | **A–F letter** (primary) → 0–100 (deep dive) |
| Infra | $0, local, no paid APIs | hosted; paid APIs/infra funded by MRR |

---

## 1. `db.py` — canonical `parcels` schema + DuckDB — **ADAPT**

- **Keep:** the canonical parcel column set (§4) is well-designed and portable —
  it's the contract every adapter maps into. The `ALTER TABLE ... ADD COLUMN IF
  NOT EXISTS` migration list shows the schema already evolved cleanly.
- **Change:**
  - **Storage engine.** DuckDB is a single-file embedded analytical DB — no
    concurrent writers, no network. Fine for a batch CLI, wrong for a
    multi-tenant web app. Move the system-of-record to **Postgres** (parcels,
    users, orgs, subscriptions, saved farms, alert configs, score history).
    Keep DuckDB (or Postgres + a columnar extension) as the **batch
    scoring/analytics layer** that recomputes grades over the full roll.
  - **PK.** `(county, parcel_id, roll_year)` stays for the roll table, but Marlin
    needs a stable **address/parcel identity** that survives re-ingest and
    powers lookups + alert history. Add a surrogate `parcel_uid`.
  - **Score history.** New table `parcel_score_history(parcel_uid, as_of_date,
    score, grade, breakdown)` — required for spike alerts and the
    "score changed" diff. Today only a single roll year exists and scores are
    overwritten in place.
  - `parcel_id` is a zero-padded string; GIS sources key on integer `PROP_ID` —
    normalize this at ingest, don't leave it for every consumer.

## 2. `ingest/` — county adapters — **ADAPT (and finish)**

- **Keep:** the adapter pattern (`CountyAdapter` ABC: `download / parse /
  map_to_canonical`). Correct abstraction — CAD schemas are not standardized.
- **Keep:** `ingest/travis.py` — real, working, parses the 470-field TCAD
  fixed-width layout from `config/travis_property_layout.json`. This is weeks of
  fiddly work; carry it over intact.
- **Build:** `williamson.py` and `hays.py` are **empty stub classes**. They must
  actually be implemented for the tri-county launch. `config/counties.yaml`
  already has the recon notes (deed-date availability confirmed for all three,
  formats documented).
- **Change:** cadence. Today: operator manually downloads a Cloudflare-protected
  zip and runs `ingest`. Marlin's "daily scraping" promise needs a scheduled,
  unattended refresh per county with change detection between pulls. **Open
  question flagged below** — whether "daily" is literal or aspirational.
- **Change:** ingest currently `DELETE`s + re-`INSERT`s a roll year. Marlin needs
  ingest to *diff* against the prior snapshot and emit change events (owner
  changed, exemption dropped, new deed) that feed the alert engine.

## 3. `normalize/` — **KEEP (near-wholesale)**

The most reusable code in the repo. All three modules carry over with minimal
change.

- `subdivision.py` — deterministic strip → alias override → conservative fuzzy
  near-duplicate proposals (never auto-merged). Hardened against real TCAD
  boilerplate over many commits (`JOSEPH`→`JOSE`, `THE VISTAS OF AUSTIN`→`""`
  bugs already fixed). **Keep the code and `config/subdivision_aliases.yaml`
  (45 KB of manual merge decisions).** Still needed: zip/farm-area monitoring is
  defined over `subdivision_canon` OR zip, and address search benefits from
  clean subdivision grouping.
- `owners.py` — entity detection (LLC/TRUST/LP/… word-boundary regex). **Keep.**
  This *is* the "data quality filter" the Marlin brief calls out ("auto-downgrade
  corporate rentals") — just needs to be surfaced as a named product feature.
- `address.py` — USPS-style suffix/unit normalization, shared by absentee-match
  and enrichment-match. **Keep, and lean on it harder** — Marlin's address search
  needs fuzzy address→parcel resolution, which is this module's job scaled up
  (typo tolerance, missing unit, `ST` vs `STREET`, etc.).

## 4. `analytics/metrics.py` — per-parcel flags — **KEEP (unblock the dormant signals)**

- **Keep** every flag computation: `absentee`, `out_of_state`, `tenure_years`,
  `senior_longtenure`, `likely_rental`, `recent_sale`, `owner_is_entity`, and the
  multi-year diffs (`homestead_dropped`, `over65_newly_filed`,
  `ag_exemption_rollback`). The "blank vs False vs not-computable" discipline
  throughout is correct and worth preserving.
- **Unblock:** the three multi-year diff signals need a prior roll year loaded.
  Marlin should load ≥2 roll years per county from day one so these are live —
  and they're also the model for score history / alerting.
- **Scope change:** `compute_farm_aggregates` / `FarmAggregates` is subdivision-
  scoped reporting. Keep it for the zip/farm-area monitoring report, but the
  primary path becomes **single-parcel scoring** (already supported — the
  functions are vectorized over any DataFrame).

## 5. `analytics/scoring.py` + `config/scoring.yaml` — the engine — **KEEP + relabel**

- **This is the IP.** `compute_score_breakdown()` — weighted sum, clipped 0–100,
  per-signal explainability string, deterministic tie-breaking. Port as-is.
- **Keep** the tuned weights and the research behind them
  (`docs/superpowers/specs/`, the operator sign-offs in the yaml comments).
- **Change (already decided — see `scoring-decisions.md`):**
  1. `out_of_state` +10 → −10 (+ rename from `out_of_state_additional`).
  2. Replace the `bands: {hot_min, warm_min}` structure + `_band_for()` with
     **fixed A–F cutoffs** on the 0–100 score. Not curved per zip.
  3. Recalibrate all cutoffs against the real score distribution once the model
     runs across the full ~487k-parcel roll (only 184 parcels have ever scored).
- **New surface:** the letter is primary in the UI; the number + breakdown is the
  deep-dive. Add per-area grade-distribution + local-percentile views (UI, not a
  change to the math).

## 6. `enrich/` — tax delinquency / permits / code violations — **ADAPT**

- **Keep** the signal concepts and the match logic (`geo_id` primary, address
  fallback; legal-description match for tax delinquency; the full-scope
  blank-vs-False mapping).
- **Change scope:** every source is Travis/Austin-specific
  (Travis Tax Office CSV, City of Austin Socrata permits/violations). For
  tri-county, either find WCAD/Hays/other-city equivalents or let the signal
  degrade gracefully (`_optional_bool_column` already does this).
- **Change trigger:** today enrichment runs per-farm, on demand, from the CLI.
  Marlin needs it to run **county-wide on the refresh schedule** so every parcel
  carries current enrichment before a lookup, not just parcels in a purchased
  farm.
- **Cache hygiene:** `data/enrich_cache/` mixes a static bulk snapshot (tax
  delinquency) with live data (permits/violations, currently scoped to a single
  zip `78739`). Marlin's scheduler owns freshness; the ad-hoc cache files go.

## 7. `gis/` — plats / centroids / spatial join / flood zone — **ADAPT**

- **Keep:** `spatial_join.py` (centroid-in-polygon), `austin_plats.py`
  (`is_likely_clean_plat_name` — hard-won heuristic that stopped GIS backfill
  from *worsening* the canonical-name count). The GIS-sourced subdivision backfill
  is genuinely better data than flat-file parsing.
- **Keep the data:** `travis_centroids.json` (parcel geometry) is the basis for
  any map view and for point-in-zip / point-in-polygon queries. Not copied into
  Marlin yet — pull it when the map/'draw a farm area' work starts. (Custom
  polygon drawing is explicitly post-MVP per the brief, but zip↔parcel
  resolution needs geometry now.)
- **Change:** `flood_zone.py` is informational-only and unscored — low priority
  for Marlin MVP; keep the module, don't prioritize wiring it.
- **Change:** GIS is Travis-only (only county with a validated plat source).
  Same tri-county generalization problem as enrichment.

## 8. `report/` — PDF builder + Jinja template — **CUT as primary, KEEP as export**

- The 6–8 page branded PDF-per-farm was *the* FarmSignal deliverable. In Marlin
  it's demoted to an **optional export/attachment** off the zip-monitoring
  report. The product surface is the app UI + CSV + CRM sync + alerts.
- **Keep** `report/builder.py`'s Playwright/Chromium render path and the font-
  embedding approach if a branded PDF export is still wanted (agents like a
  leave-behind). Otherwise CUT the whole module.
- **CUT** the FarmSignal brand tokens in `config/brand.yaml` — Marlin has its own
  identity (matte black, deep ocean blue, signal cyan / data green;
  "apex predator" voice).

## 9. `export/csv_export.py` — prospect CSV — **KEEP (rework columns)**

- **Keep:** the export itself — the ranked CSV is a real deliverable (feeds
  mailer vendors + CRMs) and survives into Marlin as "export this farm / this
  zip". `QUOTE_NONNUMERIC` zip-safety and the blank-vs-False discipline stay.
- **Change:** column set. Drop FarmSignal-tier framing, add `grade` (letter) as
  the lead column, `local_percentile`, `as_of_date`, and a stable `parcel_uid`.
  Gate columns by subscription tier if needed.

## 10. `cli.py` — Typer command surface — **CUT (becomes an API)**

- The CLI *is* the FarmSignal product interface. In Marlin it's replaced by:
  - a **service API** (`POST /score`, `GET /parcels/{uid}`,
    `GET /areas/{id}/report`, alert/subscription CRUD),
  - a **web frontend**,
  - **background jobs** (ingest, county-wide rescore, alert evaluation, report
    delivery).
- **Keep as internal tooling:** `ingest`, `subdivisions`, `gis backfill-subdivisions`,
  `enrich *` are useful as ops/admin commands or job entrypoints — keep the
  `run_*()` functions (they're already factored out of the Typer layer for
  testability), drop the `@app.command` decorators as the primary interface.
- **CUT outright:** `generate`, `preview`, `sample` (subdivision-report workflow),
  all `registry *` commands.

## 11. `leads/agent_leads.py` — **CUT**

- TREC-license parsing + email-permutation generation was tooling for the
  operator's **manual cold-outreach sales motion**. A self-serve SaaS with
  landing-page waitlists doesn't need it. (Retain privately for founder-led
  sales if desired, but it's not a platform component.) Module is a 3-line stub
  anyway — nothing to port.

## 12. Business model — farm registry / waitlist / tiers / scope cap — **CUT (registry: ADAPT)**

- **ADAPT, not cut:** the single-holder exclusivity mechanic **stays** — operator
  decision — but **re-scoped from subdivision to zip code**. `farm_registry` →
  `zip_claims`, `farm_waitlist` → `zip_waitlist`; keep the one-holder-per-unit +
  waitlist + `min_hold_until` shape. `registry` CLI commands become
  subscription/claim API + admin tooling. See build spec §7.
- **CUT** the $49 one-time and $29 Farm Watch tiers, and the "refuse, don't
  truncate" **1,500-parcel scope cap** in `generate` (spec §6.1). Marlin's
  constraint is **usage metering**, not a hard per-farm size ceiling:
  active-zip count, monthly lookup count, alert frequency, CRM-sync access.
- **CUT** the operator-in-the-loop SOP (spec §10) and the manual QA checklist
  (§11) — replaced by automated pipeline + monitoring. The **listing-status
  disclaimer** language (§6.1/§6.2) should survive verbatim in the app and any
  export: CAD data still has no live-MLS field.

## 13. `config/` — **MIXED**

| File | Verdict |
|---|---|
| `travis_property_layout.json`, `travis_abstract_subdv_layout.json` | **KEEP** — the TCAD field map, essential for re-ingest |
| `subdivision_aliases.yaml` | **KEEP** — 45 KB of manual merge decisions |
| `scoring.yaml` | **KEEP + edit** — see `scoring-decisions.md` |
| `counties.yaml` | **KEEP + extend** — recon notes for all 3 launch counties; add WCAD/Hays layout maps |
| `brand.yaml` | **CUT** — Marlin has its own identity |

## 14. `tests/` — **KEEP (the analytics/normalize/enrich half)**

- **Keep:** `test_normalize*`, `test_analytics_*`, `test_metrics`, `test_enrich_*`,
  `test_gis_*`, `test_export_csv`, the `travis_row_builder` fixture. These pin
  the engine's behavior and carry over with the code they test.
- **CUT / rewrite:** `test_cli_*`, `test_report_builder`, registry tests — tied
  to the CLI/report/registry surfaces that are going away.

## 15. Hard constraints — **CUT**

`$0 infrastructure`, `no paid APIs`, `runs locally`, `operator has ~1 hr/day`,
`every workflow ≤15 min` — all products of the bootstrap CLI model. Marlin is a
funded (by MRR) hosted platform: it will have a hosting bill, a job scheduler, a
transactional-email/SMS provider, CRM API integrations, and possibly paid data
sources. Don't carry these constraints into Marlin's architecture decisions.

---

## NEW — no FarmSignal antecedent, must be built

1. **Multi-tenancy** — auth, users, orgs/teams, per-user saved addresses + farm
   areas, roles.
2. **Billing + metering** — Stripe subscriptions for the 3 tiers; meter active
   zips, monthly lookups, alert cadence, CRM-sync entitlement; enforce limits.
3. **Address lookup** — fuzzy address → `parcel_uid` resolution, single-parcel
   score + breakdown response, sub-second. (Engine supports it; the resolution +
   API layer is new.)
4. **Zip / farm-area monitoring** — subscribe an area, scheduled report
   generation, delivery, diff-since-last-run ("12 ownership changes, 3 new
   absentee owners").
5. **Score history + spike-alert engine** — per-parcel time series, threshold /
   delta config, spike detection, notification fan-out (email / SMS / push).
   Fixed A–F cutoffs (decision #2) are what make "grade changed" a real event.
6. **CRM API sync** — kvCORE, LionDesk (tier 3). Outbound integrations, field
   mapping, sync scheduling.
7. **"Daily" ingest pipeline** — unattended per-county refresh + change events.
   *Depends on the open question below.*
8. **Regional expansion mechanics** — `/dfw`, `/houston` landing pages, waitlist
   capture, and the "gamified" scrape-priority-by-waitlist-density feature.
9. **Web frontend** — premium enterprise-SaaS UI in the Marlin identity; letter
   grade primary, numeric + breakdown on drill-in, per-area grade distributions.
10. **Hosting / infra** — app hosting, Postgres, object storage, a job
    queue/scheduler, transactional email/SMS.

---

## Open questions

1. ~~**"Daily scraping" — literal or aspirational?**~~ **RESOLVED (operator):**
   **monthly refresh only**, no daily/real-time scraping. The monthly updated
   report is a subscription feature; spike alerts fire on changes between the
   monthly cycles. Batch/scheduled pipeline, monthly cadence.
2. ~~**Backend language.**~~ **RESOLVED (operator):** all Python — FastAPI +
   Dramatiq/arq + Redis + Postgres, engine ported as an importable package;
   React/TS frontend. See build spec §8.
3. **A–F cutoff values.** Pending a full-roll score-distribution run (decision #2
   in `scoring-decisions.md`).
4. ~~**Rewrite vs. evolve.**~~ **RESOLVED (operator):** new Marlin repo; engine
   modules imported as a packaged `marlin_engine` library; FarmSignal frozen as
   reference.
5. **Enrichment/GIS tri-county parity** — build county equivalents, or ship
   Austin-rich / WCAD+Hays-degraded at launch and backfill?
