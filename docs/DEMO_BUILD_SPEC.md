# Marlin Grade — Demo Build Specification (v1.0)

**Status:** approved design, ready for implementation planning.
**Author session:** `docs/session-2026-09-08-app-build-brainstorm.md` (brainstorm) → this doc.
**Parent spec:** `MARLIN_GRADE_BUILD_SPEC.md` (the full product/MVP spec — v0.2). This
document is the **demo increment** of that spec, not a replacement.

---

## 1. Purpose & context

Build a **navigable, public web demo** of Marlin Grade for review by **Palmer
Holland** — a broker/team-lead, advisor, and potential investor, remote in DFW —
on the **afternoon of Wednesday 2026-09-10**. The demo must:

- **wow on look** — clean, dynamic, professional dark SaaS;
- **show current capability** — real A–F grades on real Southwest Austin
  addresses, scored by the ported engine;
- **show potential** — the alert and monthly-report surfaces staged convincingly.

It doubles as the **real MVP frontend running ahead of the backend**. Nothing
here is throwaway: the SPA, the design system, and the extracted `marlin_engine`
package all carry forward into the MVP build.

### Demo parameters (locked)

| Parameter | Value |
|---|---|
| Reviewer | Palmer Holland — remote (DFW), needs a shareable public URL |
| Demo type | "Thin real slice" — real engine, real Travis data; alerts + report staged |
| Focus zip | **78749** (SW Austin — Legend Oaks / Maple Run / Village at Western Oaks / Sendera) |
| Bundled zips | 78749 + 78748, 78745, 78739, 78735, 78736, 78652 (7 total, ~57.6k scored SFR parcels) |
| Hosting | Standalone Cloudflare Workers static-assets deploy — its own `*.workers.dev`; point `marlin.grade` at it later if secured. **Not** a `parlyr.site` subdomain. |
| Data architecture | **Approach A** — score offline with `marlin_engine`, export JSON, bundle in a static SPA. No runtime backend. |
| Phase A validation zip | 78749 (operator has ground-truth knowledge) |
| Seeded account | **Palmer Holland**, shown in a persistent identity block (upper-left app shell) — this is the real build's layout too, not demo-only |

---

## 2. Scope

### In scope (Wednesday)

- Extracted `marlin_engine` Python package (scoring path only).
- Offline scoring + JSON bundle build script.
- Full-roll single-year score run → frozen A–F cutoffs (real [GAP-11] Phase B).
- Phase A engine-correctness validation on 78749.
- Time-boxed Travis 2024 roll ingest (with hard fallback to single-roll).
- React + TypeScript SPA, 9 screens (cut line below), deployed to a public URL.

### Out of scope (explicitly deferred to MVP)

FastAPI backend · Postgres · Redis · workers (Dramatiq/arq) · real auth,
multi-tenancy, Stripe billing, metering · WCAD + Hays adapters, any tri-county
work · all weekly/daily stream pullers (permits, code violations, tax
delinquency, foreclosure/probate) · diff engine, `signal_events`, Event
Generator, Subscription Matcher, notification queue · `parcel_score_history` and
real grade history / sparkline · real monthly-report generation, PDF, object
storage · CRM sync, CSV export, SMS/email delivery · `normalize/subdivision.py`
+ alias file · zip-exclusivity enforcement + waitlist · custom polygon farm
areas · cutoff outcome-anchoring.

### Wednesday cut line

| Priority | Screens |
|---|---|
| **Must** | 1 Landing · 2 Sign-in (fake) · 3 Farm picker · 4 Zip dashboard · 5 Address drawer · sticky-header address search |
| **Strong want** | 6 Alerts feed (staged) · 7 Monthly report (semi-real) |
| **Only if ahead** | 8 Roadmap screens (Citywide, CRM sync, `/dfw` waitlist) |

---

## 3. Repo structure + frontend stack

`Marlin Grade/` becomes the canonical Marlin git repo (`git init` in place — the
spec, teardown, and DuckDB are already the project's center of gravity).

```
Marlin Grade/                      # git repo root (new)
├── marlin_engine/                 # extracted FarmSignal engine — importable package
│   ├── normalize/                 # address.py, owners.py
│   ├── analytics/                 # metrics.py, scoring.py
│   ├── scoring.yaml               # Marlin config — out_of_state −10 applied here
│   ├── grades.py                  # NEW — 0–100 → A–F, fixed frozen cutoffs
│   └── tests/                     # lifted analytics/ + normalize/ tests, repointed
├── scripts/
│   └── build_demo_bundle.py       # offline: DuckDB → score 7 zips → emit web/public/data/*.json
├── web/                           # Vite + React 18 + TS SPA
│   ├── src/
│   ├── public/data/               # generated JSON bundle + fixtures
│   └── wrangler.jsonc             # Cloudflare Workers static-assets (assets.directory: dist)
├── fixtures/                      # hand-authored staged JSON (alerts, monthly report movers)
├── data/                          # farmsignal.duckdb (gitignored — already is)
├── docs/                          # this spec, parent spec, teardown, scoring decisions
├── pyproject.toml                 # marlin_engine + script deps: duckdb, pandas, pyyaml, rapidfuzz
└── .gitignore                     # + .superpowers/, web/node_modules, web/dist
```

The MVP backend (`api/`, `workers/`) is **not scaffolded now** — it lands in this
same repo later.

### Frontend stack

Build tooling mirrors parlyr.site (Vite + React + Cloudflare Workers
static-assets); the visual identity follows the Marlin brand brief (§6), not
parlyr.site.

- **Vite + React 18 + TypeScript**, single SPA.
- **Cloudflare Workers static-assets** (`wrangler.jsonc`, `assets.directory: dist`).
- Fonts (per brand brief §6.3): **Plus Jakarta Sans** (headers/branding) +
  **Inter** (interface/data) + **JetBrains Mono** (data-label accents). Google
  Fonts; preload Jakarta 800 + Inter 400 only.
- **React Router**, client-side only — one route per screen.
- **Styling:** vanilla CSS with custom-property design tokens (§6), co-located
  per component/feature (per `~/.claude/rules/ecc/web/coding-style.md`). No
  Tailwind, no CSS-in-JS — keeps the demo dependency-light and the tokens
  portable into the MVP.
- Data layer: JSON bundle **fetched per-zip on demand, held in memory**
  (TanStack Query `staleTime: Infinity`, or a plain context). Address search
  filters the in-memory set.
- No auth library. Screen 2 sets a fake session flag (`user = "Palmer Holland"`,
  tier `Founding Solo`) and routes to the dashboard.

### `marlin_engine` extraction

FarmSignal (`/Users/justinmason/Claude Code/FarmSignal`) stays **frozen**. Engine
modules are **copied** into `marlin_engine/` (not git-submoduled) and
de-DuckDB'd where they touch the database. FarmSignal's `analytics/` and
`normalize/` tests come along, imports repointed `farmsignal.*` → `marlin_engine.*`
— that suite is the regression net for the lift and must be green before any
change.

---

## 4. `marlin_engine` extraction scope

### 4.1 Modules to lift

| From FarmSignal | Used for | Lift notes |
|---|---|---|
| `analytics/scoring.py` | score formula + per-signal breakdown | Fix `_CONFIG_DIR` (`parents[3]/"config"` → package-local `scoring.yaml`). Apply `out_of_state` edit (§4.2). |
| `analytics/metrics.py` | `compute_parcel_metrics` (all per-parcel flags), `compute_farm_aggregates` (screen-4 distribution + aggregates), `fetch_prior_roll_year_snapshot` | Drop `run_compute_metrics` (does a DuckDB write-back we don't want). The offline script owns orchestration. |
| `normalize/address.py` | `normalize_address`, used by `compute_absentee` and as the search key | Verbatim (~35 lines, no deps). |
| `normalize/owners.py` | `entity_owner_mask` → `owner_is_entity` | Verbatim (~31 lines). |
| `analytics/` + `normalize/` tests | regression net | Repoint imports; run green first. |

### 4.2 The `out_of_state` −10 edit (`docs/scoring-decisions.md` §1)

Three mechanical touch points:

1. `scoring.yaml`: `out_of_state_additional: 10` → `out_of_state: -10`.
2. `scoring.py` (~line 102): contribution key + weights lookup renamed
   `out_of_state_additional` → `out_of_state` (the DataFrame column it multiplies
   is already `df["out_of_state"]`).
3. `scoring.py` `_SIGNAL_LABELS`: key renamed `out_of_state_additional` →
   `out_of_state` (label text "Out-of-state" unchanged).

A lift-time regression test asserts a known out-of-state, non-homestead SFR
parcel scores ~20 points lower than under the old config.

### 4.3 Deliberately NOT lifted for the demo

- **`normalize/subdivision.py` + `subdivision_aliases.yaml` (46 KB)** — the
  DuckDB already carries `subdivision_canon` at 91.5% fill. The demo *displays*
  existing canon values; it does not re-canonicalize. This module is
  MVP-ingest infrastructure (new counties), not demo-scoring infrastructure.
- `ingest/` (except the 2024 spike, §4.5), `enrich/`, `gis/`, `db.py`,
  `export/`, `report/`, `cli.py`, `leads/`.

### 4.4 Offline scoring script — `scripts/build_demo_bundle.py`

Idempotent, re-runnable, **no DB writes**. Pipeline:

```
duckdb.connect(farmsignal.duckdb, read_only=True)
  → SELECT * FROM parcels WHERE situs_zip IN (<7 demo zips>) AND is_sfr
  → compute_parcel_metrics(df, prior=<2024 snapshot or None>)
  → compute_score_breakdown(metrics)              # 0–100 score + breakdown string
  → grades.assign(score)                          # A–F from frozen cutoffs
  → emit web/public/data/{zips.json, parcels-<zip>.json, aggregates.json,
                          grades.json}
```

`alerts.json` and `report-<zip>.json` mover sections are hand-authored in
`fixtures/` and copied in by the same script.

### 4.5 Travis 2024 roll — time-boxed spike, hard fallback

**Plan:** operator starts the TCAD 2024 certified-export download at kickoff
(auto-download is Cloudflare-blocked — manual step). Implementation time-boxes
the ingest to **≤ half a day on Day 1**.

- **If it lands:** `homestead_dropped`, `over65_newly_filed`,
  `ag_exemption_rollback` activate → the drawer's SignalTriggers get their
  dramatic line (*"homestead dropped after 11 years +25"*) and screen-6 computed
  spikes become **real** rather than fixtures.
- **Risk:** `ingest/travis.py` reads fixed-width by byte offset from the *2025*
  layout doc (`config/travis_property_layout.json`). If TCAD bumped the layout
  version for 2024, offsets shift and fields land wrong. Unknown until attempted.
- **Fallback is a supported mode, not breakage:** `scoring._optional_bool_column`
  already treats those columns as absent → 0 contribution. On fallback: the
  drawer sparkline stays staged, screen-6 fully staged (already planned that way).

### 4.6 A–F cutoffs — full-roll single-year run, then frozen

Independent of the 2024 question:

- The full-roll **score** run over ~349k Travis SFR parcels is cheap
  (vectorized pandas, seconds) and low-risk. Single-roll means the three diff
  signals contribute 0 for everyone — which makes the cutoff histogram *cleaner*
  to reason about (pure standing-state signals).
- Inspect the score histogram; place cutoffs at the §10.1 anchors
  (**A ≈ top 3%, B ≈ next 12%, C ≈ 25%, D ≈ 35%, F ≈ 25%**); snap to natural
  gaps; **freeze the score values** into `marlin_engine/grades.py`. This is real
  [GAP-11] Phase B progress.
- When the 2024 roll lands for MVP, cutoffs get the §11.1 silent re-baseline —
  spec-sanctioned.
- The legacy `bands:` block in `scoring.yaml` (`hot_min: 55`, `warm_min: 35`) is
  unused by the demo; leave it or delete it (cosmetic).

`grades.py` default implementation (operator may revisit the boundary
semantics later): grade is a **pure function of the clipped 0–100 score**;
cutoffs are **inclusive lower bounds** (`score >= cutoff_A` → `A`), evaluated
A→F; a score exactly on a boundary takes the **higher** grade.

### 4.7 Phase A validation (spec §10.1, on 78749)

Scoring is "effectively unrun at scale" — the first real run will surface flag
bugs and weight surprises. **Budget ~half a day** to check:

- per-parcel flags vs. ground truth (known rentals → `likely_rental`;
  long-tenured owners → tenure + bonus; entity-owned → `owner_is_entity`);
- `out_of_state` −10 pulls known out-of-state rentals down;
- `recent_sale` catches known recent sales and de-prioritizes them;
- zip aggregates believable (% absentee, median tenure);
- address → parcel lookup resolves correctly.

Fix the engine, not the data.

---

## 5. Screens

### 5.1 Navigation flow

```
1 Landing ──▶ 2 Sign in (fake) ──▶ 3 Farm picker ──▶ 4 Zip dashboard ──┬──▶ 5 Address drawer (right slide-out)
                                                                       ├──▶ 6 Alerts feed
                                                                       └──▶ 7 Monthly report
   sticky global header (all authed screens): centered address search → opens the Address drawer over any screen
8 Roadmap screens — reachable from sidebar / landing, static
```

Persistent app shell on screens 3–7 (§6.4): **sticky global header** (logo
lockup · centered Signal-Cyan address search · **Palmer Holland** identity block)
+ **left icon sidebar** — Dashboard · Tracked Zips · Alerts · Monthly Report ·
Export Logs · Settings.

### 5.2 Real-vs-staged contract

| # | Screen | Real | Staged |
|---|---|---|---|
| 1 | Landing | spec §14 copy | everything (static marketing page) |
| 2 | Sign in | — | one button → fake session as Palmer Holland |
| 3 | Farm picker | Travis zip list | exclusivity availability state |
| 4 | **Zip dashboard** | grade distribution (A–F %), zip aggregates, ranked prospect table, filters, CSV export of the visible list | "exclusivity available" badge only |
| 5 | **Address drawer** | grade gauge (letter + score ring), signal triggers (+/−), ownership/tenure/exemption facts, local percentile | grade-history sparkline |
| 6 | Alerts feed | UI; **real spikes iff Travis 2024 lands** | alert rows + the foreclosure event (fixture) |
| 7 | Monthly report | zip aggregates block, top-A/B table | "movers" / "new A/B" / "cooled off" sections |
| 8 | Roadmap | — | static mockups |

Address search is the header bar, not a screen — a match opens screen 5 (the
drawer) over whatever is behind it.

### 5.3 Screen layouts

- **4 Zip dashboard:** zip context header (zip + area name + subdivisions +
  scored-parcel count; monitored / exclusivity badges; a **Data Green "Export
  CSV"** button that downloads the currently filtered prospect list) → prominent
  **grade-distribution bar** (A–F %, the "a cold farm is information, not a bug"
  device, spec §12) alongside a **zip-aggregates panel** (absentee %,
  likely-rental %, median tenure, out-of-state %) → **filter chips** (grade
  bands; long-tenure 15+; likely rental; owner-occupied; out-of-state) →
  **ranked prospect table**: rank · grade pill (A/B glow, C–F recede) · address ·
  owner type · score (lean — drivers live in the drawer). Sortable; row click →
  opens the Address drawer.
- **5 Address drawer** (right slide-out, workspace dims behind; deep-linkable as
  `/z/<zip>?addr=<slug>` so it stays shareable): **GradeGauge** at the top
  (letter dead-centre, Signal-Cyan score ring, JetBrains-Mono driver flags
  beneath) + local percentile ("Top X% of ZIP 78749") → address / owner /
  exemption header + staged history sparkline → **SignalTriggers**: the
  `compute_score_breakdown` output as a diverging +/− list ("positive /
  negative property triggers", sorted by magnitude) with a total → **ownership &
  property facts** table (owner of record, owner type, mailing address + inline
  out-of-state flag, deed date, tenure, homestead, over-65, subdivision,
  assessed value) → the listing-status disclaimer (§7).
- **1 Landing:** dark hero, spec §14 copy ("Stop farming blind. Start targeting
  listings.") + Signal-Cyan CTA. Then two **clearly separated** blocks with
  distinct formats:
  - **"How it works"** — boxless, airy: three steps (Aggregate → Grade → Alert)
    as a connected row with arrow connectors, no cards, under its own
    kicker + heading.
  - a full-width divider and generous vertical gap, then
  - **"Pricing"** — own kicker + title + subhead (baseline-vs-streams model).
    One **unified comparison table**: each plan is a column whose header stacks
    name / price / description / CTA vertically; comparison rows align beneath
    each plan, grouped into **Capacity · Signal streams · Alerts & history ·
    Export & integrations** (values from parent-spec §4). Market Leader column
    tinted, "Most popular" tag. A **logo placeholder** occupies the top-left
    header cell (left of the Founding Solo column). No-contract + refund wedge
    below.
- **3 Farm picker:** search/select a Travis zip from the real list; each row
  shows monitored / available / held state (state staged). Confirm → dashboard.
- **6 Alerts feed:** reverse-chron rows — grade transition + triggering
  signal(s) + address + timestamp + worked/dismiss control. The foreclosure
  event row is styled distinctly. Fixture data (or real spikes if 2024 lands),
  real UI. A row opens the Address drawer.
- **7 Monthly report:** one scrollable report for the zip — real aggregates
  block, then staged "movers" / "new A/B" / "cooled off" sections, then a real
  top-A/B table. In-app view only; PDF is post-demo.

### 5.4 JSON bundle shape — `web/public/data/`

| File | Contents | Source |
|---|---|---|
| `zips.json` | per zip: code, area name, subdivisions[], scored SFR count, A–F distribution {grade: {pct, count}}, aggregates {absentee_pct, rental_pct, median_tenure, out_of_state_pct}, staged `exclusivity` state | real (dist + aggs) |
| `parcels-<zip>.json` | array; per parcel: `parcel_uid`, `situs_address`, `situs_norm` (search key), `owner_name`, `owner_type` (`occupant`\|`entity`), `grade`, `score`, `breakdown` [{label, points}], `facts` {deed_date, tenure_years, homestead, over65, subdivision, assessed_value, mail_state, out_of_state} | real |
| `grades.json` | frozen A–F cutoff score values (for display: "A ≥ 78") | real |
| `alerts.json` | staged alert-feed rows | fixture |
| `report-<zip>.json` | real aggregates + staged mover sections | mixed |

Per-zip files keep each fetch small (well under 3 MB gzipped). Fetched on demand.

---

## 6. Design language

**Source of truth:** `Branding/Marlin brand brief - gemini.md` ("Deep Analytics"
identity) + the asset sheet in `Branding/`. Archetype: *Palantir / Scale AI /
Bloomberg for elite listing agents* — fast, exclusive, high-density,
authoritative. Dark mode is the default and only mode. Anti-persona: no houses,
roofs, location pins, or literal fish.

### 6.1 Colour tokens ("Deep Analytics" — exact brief values)

| Token | Value | Use |
|---|---|---|
| `--abyssal` | `#0B111E` | primary workspace background |
| `--surface-1` | `#111828` | cards, table header, sidebar (lifted from abyssal) |
| `--surface-2` | `#0E1523` | drawer / overlay ground |
| `--ice` | `#F1F5F9` | primary type, crisp container borders, structural dividers |
| `--cyan` | `#00F0FF` | **Signal Cyan** — interactive controls, focus/target states, A-grade highlights, the grade-gauge ring |
| `--green` | `#00E676` | **Data Green** — *exclusively* export/CSV controls, revenue/volume metrics. Never a generic "positive" colour. |
| `--slate` | `#64748B` | secondary body text, F-grade labels, grid lines |

Borders: `--ice` at 8–12% alpha for hairlines; `--slate` for grid lines inside
tables. One soft shadow reserved for the slide-out drawer and modals.

### 6.2 Grade colour system (A–F, no plus — per parent-spec §10)

Not a rainbow. Per the brief: high-probability grades **flash Signal Cyan**;
lower grades **melt passively into the Abyssal Blue**. The letter is always
rendered, so colour is redundant encoding.

| Grade | Treatment |
|---|---|
| **A** | Signal Cyan `#00F0FF` fill, subtle outer glow — "pulsing target" |
| **B** | Signal Cyan at ~65% (`#3FD9E4`), no glow |
| **C** | Subdued Slate `#64748B` fill, `--ice` text |
| **D** | Slate, dimmed (`#4C596B`), sits back |
| **F** | Slate label on abyssal, no fill — melts into the workspace |

### 6.3 Typography (per brief)

| Role | Family | Notes |
|---|---|---|
| Headers & branding | **Plus Jakarta Sans** (600–800, tight tracking) | hero, section titles, plan names, the wordmark |
| Interface & data | **Inter** | tables, address listings, body, forms — the workhorse |
| Data-label accent | **JetBrains Mono** | *sparingly* — parcel IDs, tax/assessed values, timestamps, the grade-gauge metadata flags, uppercase kickers |

Load via Google Fonts (`fonts.googleapis.com`) the way parlyr.site loads its
faces; preload only the two critical weights (Jakarta 800, Inter 400). Every face
gets a real system fallback stack.

**Scale:** hero `clamp(2.5rem, 6vw, 4.25rem)` · page title 24px · section 18px ·
body 13–14px · meta 12px · label 10px JetBrains Mono uppercase tracked. Scores,
grades, parcel data in JetBrains Mono `tabular-nums`.

### 6.4 Layout archetype — three-section high-density workspace

1. **Sticky global header** — logo lockup left (`marlin watermark.png` wordmark
   crop, or the traced SVG); a **centered address lookup bar** that gets a
   glowing Signal-Cyan border on focus (this *is* the app's address search — no
   separate search screen); the **Palmer Holland** identity block far right.
2. **Left sidebar** — minimalist icon nav: Dashboard · Tracked Zips · Alerts ·
   Monthly Report · Export Logs · Settings. Compact, icon-forward, active item
   in Signal Cyan.
3. **Core workspace** — the data table. A-/B-grade rows carry a glowing Signal
   Cyan pill; C/D/F recede into the background.

### 6.5 The Marlin Grade gauge (signature element)

A standalone widget, not flat text. Used on the address drawer hero, search
result cards, and the dashboard's selected-row peek:

- **circular gauge** — a percentage ring that fills in Signal Cyan proportional
  to the 0–100 score;
- the **letter grade dead-centre**, Plus Jakarta Sans black weight;
- underneath, **micro JetBrains-Mono metadata flags** naming the top breakdown
  drivers — `TENURE: 22 YRS` · `HOMESTEAD: DROPPED` · `OUT-OF-STATE`.

### 6.6 Space / radius / motion

4px base scale (4·8·12·16·24·32·48). Radius 4 (controls) / 8 (cards) / pill
(grade tags). Motion 150 / 250ms `cubic-bezier(0.16, 1, 0.3, 1)`: gauge ring
draws on mount, score counts up, distribution bar animates width, drawer slides
from the right with the workspace dimming behind, A/B pills have a slow cyan
pulse. All gated by `prefers-reduced-motion`.

### 6.7 Brand assets (`Branding/`)

- `marlin watermark.png` (1774×887, full horizontal lockup on abyssal) — source
  for the header/landing wordmark. Crop to tight bounds for the demo.
- `marlin icon options.png` — a 12-variant contact sheet, **not** a usable file.
  Extract the **Primary Mark** cell (cyan-gradient upslanting fin over three
  vertical bars) and the **App Icon** cell. Trace the Primary Mark to a clean
  **inline SVG** for the sidebar collapsed state and the favicon; PNG crops are
  the fallback if tracing runs long.
- Wordmark treatment (when set in live text rather than the asset): all-caps
  Plus Jakarta Sans, "MARLIN" heavy/black, "GRADE" right-aligned beneath in a
  lighter weight with wide tracking; the "A" crossbar removed to a chevron where
  feasible (asset already does this — prefer the asset).

### 6.8 Component inventory

AppShell (StickyHeader + Sidebar + Workspace) · GlobalAddressSearch ·
UserBlock · Sidebar­Nav · **GradeGauge** · GradePill (A/B glow, C–F recede) ·
SignalTriggers (diverging +/− list, "positive / negative property triggers") ·
FactsTable · DistributionBar · AggregatePanel · ProspectTable · FilterChips ·
**AddressDrawer** (right slide-out) · AlertRow / AlertFeed · ReportSection ·
ExportCsvButton (Data Green) · TierTable · Hero · CTAButton · Badge ·
Disclaimer · ZipPickerItem.

---

## 7. Canonical listing-status disclaimer

Appears verbatim in-app on every surface an address appears, in every export, and
in every alert (spec §5, §11):

> **Listing-status disclaimer.** Marlin Grade estimates listing *propensity*
> from public county appraisal and related public records. It is a prediction,
> not a fact about any property or owner, and does not reflect MLS status — a
> graded address may already be listed, under contract, sold, or not for sale.
> Public-record details may be outdated or incorrect. Verify current status and
> ownership independently before outreach or ad spend. No listing or sale is
> guaranteed.

Short form (only where the full text will not fit, e.g. SMS):
*"Marlin scores listing propensity from public records, not MLS status. Verify
before outreach."*

---

## 8. Build sequence (Mon 2026-09-08 PM → Wed 2026-09-10 PM, ~2.5 days)

**Day 0 — Mon remainder · repo + engine spine**
1. `git init` + scaffold (§3 tree), `pyproject.toml`, `.gitignore`.
2. Lift `scoring.py`, `metrics.py`, `normalize/{address,owners}.py` + tests;
   repoint imports; green.
3. Apply `out_of_state` −10 (§4.2) + regression test.
4. `grades.py` and `build_demo_bundle.py` skeletons.
5. **Operator:** start the TCAD 2024 certified-export download (async).

**Day 1 — Tue AM · scoring truth**
6. Full-roll single-year run → histogram → freeze A–F cutoffs into `grades.py`.
7. Phase A validation on 78749; fix engine bugs surfaced.
8. Time-boxed Travis 2024 ingest (≤ ½ day); land → real spikes, else fall back.
9. Run `build_demo_bundle.py`; commit real JSON for the 7 zips.

**Day 1 — Tue PM · frontend spine**
10. Vite + React + TS scaffold, `wrangler.jsonc`, Deep-Analytics design tokens
    (§6.1), fonts (Plus Jakarta Sans / Inter / JetBrains Mono), brand-asset
    crops + traced Primary-Mark SVG (§6.7).
11. AppShell — sticky global header (logo · centered address search · Palmer
    Holland block) + icon sidebar + routing.
12. **GradeGauge** component + Screen 4 dashboard (table, distribution bar,
    aggregates, filters, Data Green Export CSV) wired to the bundle.
13. **AddressDrawer** (right slide-out) wired to the bundle; header search opens it.

**Day 2 — Wed AM · finish + ship**
14. Screen 1 landing (spec §14 copy, boxless "How it works", unified pricing
    table, watermark lockup) + Screen 3 zip picker + Screen 2 fake sign-in.
15. Screens 6 + 7 from fixtures (alerts feed, monthly report).
16. Polish: motion (gauge draw, score count-up, drawer slide, A/B pulse), empty
    states, responsive, disclaimer on every surface.
17. Deploy to `*.workers.dev`; smoke-test the full click-path; send Palmer the URL.

**Cut line:** 1·2·3·4·5 + header search must; 6·7 staged strong want; 8 only if ahead.

---

## 9. Risks & watch-outs

| Risk | Mitigation |
|---|---|
| Scoring effectively unrun at scale — first real run surfaces flag/weight bugs | Half-day Phase A validation budget on 78749 (step 7) before the bundle build |
| Travis 2024 layout drift breaks fixed-width ingest | Time-boxed to ½ day; single-roll fallback is a supported engine mode; drawer sparkline + alerts feed (screen 6) stage cleanly without it |
| `parcel_id` zero-padded string vs. integer `PROP_ID` in GIS | Not relevant to Approach A (no geometry); note only |
| Bundle too large for a snappy load | Split per zip; trimmed field set; fetch on demand; target < 3 MB gzipped/zip |
| Cutoffs fit to SW-Austin only would skew "easy" | Cutoffs are set from the **full Travis roll**, not the 7-zip bundle (step 6) |
| Real owner names from public CAD data shown in a public demo | Public-record data resold as analysis (spec §6.4 legal posture); acceptable. Disclaimer present. Revisit if Palmer's review raises it. |

---

## 10. Resolved this pass / open items

**Resolved (brand-brief reconciliation):**
- **Grade scale:** A–F, no plus. Parent-spec §10 (fixed cutoffs, 5 bands) wins
  over the brand brief's "A+ to F". The brief's grade-scale line is superseded.
- **Typography:** brand brief wins over parlyr.site parity — Plus Jakarta Sans /
  Inter / JetBrains Mono.
- **Grade display + address detail:** adopt the brief's circular **grade gauge**
  and **right-hand slide-out drawer**; address search becomes the sticky global
  header, not a screen.
- **Palette:** exact "Deep Analytics" values (§6.1); Data Green restricted to
  export/revenue per the brief.

**Open:**
- **`grades.py` boundary semantics** — shipping the §4.6 default (pure function
  of score; inclusive lower bounds; boundary → higher grade). Operator may
  revisit.
- **Primary-mark SVG trace** — if tracing overruns, PNG crops of the asset-sheet
  cells are the fallback (§6.7).
- **Citywide exclusive-zip allowance** (parent-spec [GAP-2] minor) — not
  exercised by the demo.
- Parent-spec open gaps 3–7, 10, 12–14, 17–21 — all MVP concerns, none block
  the demo.
