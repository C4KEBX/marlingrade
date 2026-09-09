# Session log — 2026-09-08 — Marlin Grade spec + app-build brainstorm

Saved to hand off to a fresh session. Project: **Marlin Grade**
(`/Users/justinmason/Claude Code/Marlin Grade/`).

---

## What Marlin Grade is

FarmSignal (a local Python CLI that produced one-time PDF farm reports per
subdivision) is being rebuilt as **Marlin Grade** — a hosted, multi-tenant B2B
SaaS that grades every Texas residential address **A–F** for listing propensity,
monitors zip codes, and pushes spike / legal-trigger alerts. Subscription model,
monthly data refresh, Austin (Travis/Williamson/Hays) launch → Texas metros.

## Artifacts produced (all under `Marlin Grade/`)

| File | What it is |
|---|---|
| `MARLIN_GRADE_BUILD_SPEC.md` | **The spec. v0.2, 8 of 21 gaps resolved.** Product, brand, tiers, 3-cadence data model, architecture, canonical data model, scoring, alert engine, zip exclusivity, month-1 baseline. |
| `docs/teardown.md` | FarmSignal → Marlin subsystem-by-subsystem KEEP / ADAPT / CUT / NEW. |
| `docs/scoring-decisions.md` | `out_of_state` +10 → −10; letter grade = fixed A–F cutoffs (not curved per zip). |
| `data/farmsignal.duckdb` | Copied verbatim from FarmSignal. 486,859 Travis 2025 parcels, `parcels` table only. |
| `data/README.md` | Inventory + gotchas (zero-padded `parcel_id` vs int `PROP_ID`; scoring effectively unrun; single roll year — need Travis 2024). |

**FarmSignal (frozen reference):** `/Users/justinmason/Claude Code/FarmSignal`.
Key modules to port: `src/farmsignal/{normalize,analytics,ingest,enrich,gis}/`,
`config/scoring.yaml`, `config/subdivision_aliases.yaml`,
`config/travis_property_layout.json`.

## Decisions locked this session

- **Scoring:** `out_of_state` weight +10 → **−10** (rental-investor = less
  motivated); rename `out_of_state_additional` → `out_of_state`. Letter grade =
  **fixed A–F cutoffs on the 0–100 score**, NOT curved per zip. Grades A B C D F.
- **[GAP-9] backend:** **all Python** — FastAPI · Dramatiq/arq + Redis · Postgres
  · SQLAlchemy/SQLModel + Alembic. Frontend React + TypeScript, separate SPA.
- **[GAP-16] repo:** **new Marlin repo**; FarmSignal engine modules lifted into an
  importable `marlin_engine` package; FarmSignal frozen.
- **[GAP-1] tiers:** gate **which signal streams reach the subscriber** (monthly
  CAD / weekly warm-lead / daily legal-trigger) + capacity (zips, lookups, seats)
  + integrations — **never data freshness**. Monthly refresh only, no daily CAD
  scraping. Monthly report is a feature. "Citywide Exclusive" → "Citywide".
- **[GAP-2] zip exclusivity:** per-zip **add-on**, Market Leader+ only, price =
  **+100% of effective per-zip rate**. One holder/zip; claimable only on a zip
  with ≤1 active monitor; waitlist first-reply-wins; 3-mo min hold, no
  auto-renew. MVP = enforce at zip-add + manual operator grant (Stripe line
  item); self-serve + demand-banded pricing = Phase 2.
- **[GAP-8] computed-spike rule:** urgent spike = grade now **A/B** + movement
  driven by an **event signal** (`homestead_dropped`, `ag_exemption_rollback`,
  new `tax_delinquent`, deed/owner change) + score **Δ ≥ N** + **6-mo cooldown**.
  Passive A/B crossings, "warming" (still C/D), downgrades, new parcels =
  **report-only, no push**. Cutoff recalibration / new roll → silent re-baseline.
- **[GAP-15] baseline:** load **current + one prior certified roll per county**
  (Travis: add **2024**). First monthly run = baseline: **zero computed spikes**;
  multi-year signals + **~90-day backfill** of warm-lead/legal streams give the
  first report content. Computed spikes start month 2.
- **[GAP-11] cutoffs — methodology only:** Phase A = one-zip engine validation
  (zip **78749**) against ground truth; Phase B = full-roll distribution run →
  distribution-anchored-then-frozen cutoffs. Anchors A≈top 3%, B≈next 12%,
  C≈25%, D≈35%, F≈25%. `N` provisional **10**.
- **[GAP-21]** (from coherence review) logged: do external-event alerts respect
  the grade? Recommendation: legal triggers alert regardless of grade; permit
  stream grade-gated (≥C); violations/delinquency any grade. Unconfirmed.

## Open gaps

3 (report format) · 4 (CRM sync scope) · 5 (quiet-month report — narrowed) ·
6 (tri-county enrichment parity) · 7 (scraping ToS) · 10 (teams/seats —
effort-gated) · 12 (alert/postcard copy) · 13 (trial/freemium) · 14 (lookup
definition) · 17 (MLS access) · 18 (W'son/Hays legal sourcing) · 19 (permit
thesis validation) · 20 (foreclosure/probate outreach legal) · 21 (above).

---

## IN PROGRESS — the app build (brainstorming skill active, mid-process)

**Path:** architectural (new app, greenfield). Brainstorming skill was invoked
and is NOT finished — no design doc written, `writing-plans` not yet invoked.

**Two build targets:** (1) MVP for launch; (2) a **navigable demo for Wednesday
2026-09-10 afternoon**. Treat as one design, two increments — the demo is the
real frontend running ahead of the backend, not throwaway.

### Demo parameters (all confirmed with operator)

- **Reviewer:** Palmer — trusted industry veteran; broker & team lead, advisor,
  potential investor, close friend. **Remote, in DFW** — needs a shareable URL.
  Goal: **wow on look + current capability + potential**; gut-check on idea
  soundness and execution credibility.
- **Demo type = B, "thin real slice":** real `marlin_engine` scoring the real
  Travis zip; alerts + monthly report staged.
- **Zip: 78749** (SW Austin — Legend Oaks / Maple Run / Village at Western Oaks).
- **Hosting: standalone Cloudflare deploy** — its own `*.workers.dev` (or point
  `marlin.grade` at it if grabbed). **NOT** a `parlyr.site` subdomain (operator
  reversed that). Must be a public URL (Palmer is remote).
- **Data architecture = Approach A (static bundle, no runtime backend):** score
  78749 + ~5 neighbouring SW-Austin zips (candidates: 78748, 78745, 78739,
  78735, 78736, 78652) **offline** with `marlin_engine`, export JSON, bundle in
  a static SPA on Cloudflare. Address search filters the bundled set. Staged
  alerts / monthly report = fixture JSON.

### Demo narrative (approved)

| # | Screen | Wednesday state |
|---|---|---|
| 1 | Landing page (real copy, spec §14) | staged marketing page |
| 2 | Sign in | faked — one click into a seeded agent session |
| 3 | Pick your farm — Travis zip picker + exclusivity availability | real zip list, staged availability |
| 4 | **Zip dashboard** — grade distribution (A–F %), ranked prospect list, filters | **REAL** — `marlin_engine` from the DuckDB |
| 5 | **Address detail** — letter grade, 0–100 score, per-signal breakdown, ownership/tenure/exemption facts, history sparkline | **REAL** grade + breakdown; staged sparkline |
| 6 | **Address search** — any bundled-zip address → grade card | **REAL** |
| 7 | Alerts feed — staged spikes + a foreclosure event | staged data, real UI |
| 8 | Monthly report — zip aggregates, movers, top A/B | semi-real (aggregates real, movers staged) |
| 9 | Roadmap screens — Citywide, CRM sync, `/dfw` waitlist | static mockups, if time |

**Wednesday cut:** 1, 3, 4, 5, 6 fully functional; 7 + 8 polished staged; 9 only
if time.

### parlyr.site tech context (for stack consistency)

Vite + React 18 SPA, Cloudflare Workers static-assets (`wrangler.jsonc`,
`assets.directory: dist`), fonts **Space Grotesk + IBM Plex Mono**, repo
`C4KEBX/parlyr-website`. Marlin brand: dark, matte black + deep ocean blue,
**Signal Cyan** primary accent, "apex predator" voice.

### NEXT STEP for the fresh session

Resume the brainstorming design phase. Operator had just been **offered the
visual companion** for the screen-layout work (answer pending — re-offer).

Then present design sections, approval after each:
1. **Repo structure + frontend stack** (Vite + React + TS to match parlyr.site;
   where the new repo lives; how `marlin_engine` sits alongside).
2. **`marlin_engine` extraction scope** — minimum modules to score 78749 from
   the DuckDB: `normalize/` (subdivision, owners, address), `analytics/`
   (metrics, scoring), the `parcels` read. Apply the `out_of_state` −10 change.
   Decide whether to load Travis 2024 for the demo (activates `homestead_dropped`
   etc.) or ship single-roll for Wednesday.
3. **Screen-by-screen layout** — wireframe each of screens 1,3,4,5,6 (+7,8);
   real-vs-staged data contract per screen; the JSON bundle shape.
4. **Design language** — dark premium SaaS, type scale, grade color system
   (A–F on Signal Cyan → red ramp), component inventory.
5. **2.5-day build sequence** + explicit MVP-deferred list.

Then: write the design to `docs/` (a demo build spec), spec self-review, operator
review, then invoke `writing-plans`.

### Watch-outs

- `parcel_id` is zero-padded string; GIS/`PROP_ID` is int — only matters if we
  pull geometry (not needed for Approach A).
- Scoring is effectively unrun at scale — expect the Phase A validation on 78749
  to surface bugs / weight issues. Budget time for it.
- A–F cutoffs are unset — for the demo, either freeze provisional cutoffs from
  the 78749 + neighbours distribution, or run the full Travis roll once (also
  serves [GAP-11]). Full roll is the better call if time allows.
- Only 1 roll year loaded → no `homestead_dropped` etc. unless Travis 2024 is
  ingested. Decide per screen 5 (the breakdown looks thinner without them).
