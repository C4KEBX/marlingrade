# Marlin Grade — Build Specification (draft v0.2)

**Status:** working draft (v0.2, post coherence review). 8 of 21 gaps resolved
(see §16); the product / data / architecture spine is internally consistent.
Synthesizes the two Gemini sessions
(`Marlin Grade - Gemini handoff session.md` = brand/product/pricing;
`Marlin Grade - full Gemini session.md` = spike-notification architecture),
the FarmSignal → Marlin teardown (`docs/teardown.md`), and the scoring
decisions (`docs/scoring-decisions.md`).

Points still to resolve are tagged **[GAP-n]** inline and collected in §16.
Nothing here is final until those are closed with the operator.

---

## 1. Product in one sentence

A B2B real-estate **predictive intelligence platform** that aggregates scattered
Texas public-record data and assigns every residential address an **A–F "Marlin
Grade"** for how likely it is to come on the market — so a farming agent spends
mailer and door-knock budget only where it will convert.

## 2. Identity & brand

| | |
|---|---|
| Legal name | **Marlin Grade** |
| Marketing name | **Marlin** |
| Domain | `marlin.grade` |
| Persona | "Apex predator" of local real-estate tech — fast, precise, sleek, efficient |
| Palette | Matte black, deep ocean blue; one neon accent — **Signal Cyan** primary (Data Green secondary) — reserved for grades and primary CTAs |
| Theme | Dark, premium enterprise SaaS |
| Voice | Performance-driven, sharp, ROI-focused; a business builder, not a corporate spreadsheet |

## 3. Users & job-to-be-done

- **Buyer:** solo residential listing agent or small boutique team that
  geographically farms one or more Texas metro zip codes; spends $100–$500+/mo
  on mailers and farming tools; technically unsophisticated.
- **JTBD:** "Before I commit this quarter's farming budget, tell me which
  specific addresses in my zip codes are most likely to list — and alert me
  when a new one heats up — so my spend and time concentrate on real prospects."

## 4. Business model

Pure **subscription SaaS**, metered. Three tiers, Austin launch pricing from the
handoff session. **[GAP-1] resolved:** the tiers differ by **which signal
streams reach the subscriber** — and those streams have genuinely different
refresh cadences (§6) — plus capacity and integrations. No tier makes a claim
about data freshness it can't back; every tier sees the same monthly CAD
baseline, and higher tiers add faster external streams on top.

| | **Founding Solo** — $99/mo | **Market Leader** — $199/mo *(most popular)* | **Citywide** — $499/mo |
|---|---|---|---|
| Monitored zips | 1 | 3 | All Austin-metro zips |
| Views inside monitored zips | unlimited | unlimited | unlimited |
| Address lookups outside them / mo | 500 | 3,000 | unlimited |
| **Signal streams** | Monthly CAD baseline (tenure, homestead/exemptions, entity/rental filter) | + **weekly warm-lead streams**: permits, code violations, tax-delinquency changes | + **daily legal-trigger streams**: foreclosure / trustee-sale notices, ag/tax rollback *(probate, expired-MLS — fast-follow, §6)* |
| Monthly zip report | ✓ | ✓ | ✓ |
| Grade history / trend | current grade only | 12-month history | 12-month history + area analytics |
| In-app Alerts feed | ✓ | ✓ | ✓ |
| Outbound alert channels | email digest | email + **SMS** + weekly re-nudge of unworked spikes | priority SMS (within the hour of a run) + **CRM push** |
| CSV export | basic (rank, grade, address, owner) | full breakdown columns | full + bulk/all-zips + API access |
| CRM API sync (kvCORE / LionDesk) | — | — | ✓ |
| Zip exclusivity (§7) | — (not available) | per-zip add-on: **+100% of per-zip rate** (≈ +$66/mo) | add-on; **up to 3** designated exclusive zips |
| Seats | 1 | up to 3 | up to 10 *([GAP-10], effort-gated)* |

Honest alert labels: "spike email digest" (Solo) · "weekly warm-lead alerts"
(Market Leader) · "daily legal-trigger alerts" (Citywide) — never "real-time".

**"Citywide Exclusive" → "Citywide".** The old name implies a whole-city
monopoly, which is impossible. This tier means *monitor every zip* + exclusivity
available on the zips the agent actually works, not exclusive ownership of the
entire market.

- **Metering enforced:** active-zip count, monthly lookup count, signal-stream
  entitlement, notification channels, CRM-sync entitlement, seats. Replaces
  FarmSignal's hard 1,500-parcel per-farm scope cap.
- **Zip-level exclusivity** is a per-zip add-on (Market Leader and up) — pricing
  and mechanic in §7.
- Positioning wedge carried from FarmSignal: **no 12-month contract, no
  auto-renewal, cancel with 30 days' notice.** Keep this visible everywhere.
- Refund posture: unconditional short-window refund on any tier.

## 5. Core product features (MVP)

1. **The Marlin Grade** — an A–F letter grade per residential address (primary
   surface), backed by a 0–100 score + per-signal breakdown on drill-in
   (§9, §10).
2. **Database Search** — instant lookup of any individual address → its grade,
   score, breakdown, owner/ownership facts, and history. Fuzzy address→parcel
   resolution.
3. **Zip / Farm-Area Monitoring** — subscribe a zip; receive a **monthly
   updated report** for it, plus **alerts** on two kinds of event (§6, §8, §11):
   - *computed spikes* — an address's grade crosses a tier boundary between
     refreshes (e.g. homestead dropped → C to A);
   - *external-event alerts* — a warm-lead or legal-trigger stream flags an
     address in the zip (permit pulled, foreclosure notice filed, probate
     opened). These fire regardless of the numeric grade.
   Which streams reach a subscriber is tier-gated (§4).
4. **Data Quality Filter** — automatic downgrade of institutional / corporate /
   rental-held properties so agents don't spend on landlords who won't sell.
   *This already exists in the ported engine* as `owner_is_entity` (−10) +
   `likely_rental` (−20 / +5 "tired landlord"); MVP work is surfacing it as a
   named, explained feature, not building it.
5. **Monthly report delivery** — every monitored zip gets a refreshed report
   each cycle (format — in-app view, PDF, or both — is **[GAP-3]**).
6. **CSV export** — ranked address list for a zip, `grade` as the lead column
   (feeds mailer vendors / CRMs).
7. **CRM API sync** *(top tier)* — push graded/spiked addresses to kvCORE /
   LionDesk as leads. Field mapping + cadence **[GAP-4]**.

**Explicitly post-MVP (phase 2):** custom polygon / "draw your own farm area"
map drawing. MVP monitoring unit is the **zip code**.

**Carried non-negotiable from FarmSignal:** the listing-status disclaimer.
CAD data has no live-MLS field — a high grade can include a home already listed,
under contract, or just sold. The disclaimer text must appear in-app, in every
export, and in every alert, verbatim, not paraphrased.

## 6. Data sources & cadence

Marlin runs **three refresh cadences**, not one. The base CAD data is monthly
(the operator's decision — no daily CAD scraping); other public sources
legitimately update faster and are polled on their own schedule. Tier
entitlement (§4) decides which streams reach a subscriber. Every stream feeds
the diff/spike engine (§8); the tier a subscriber is on filters what surfaces.

### 6.1 Monthly — CAD baseline (all tiers)

- **County Appraisal District bulk exports** — Travis (TCAD), Williamson (WCAD),
  Hays. Free, public, bulk-downloadable. Adapter-per-county (schemas not
  standardized). `ingest/travis.py` is built; **WCAD + Hays adapters must be
  built** for launch (`config/counties.yaml` has the recon — deed-date
  availability confirmed for all three).
- Drives: tenure, homestead/exemption status, owner/entity, assessed value,
  subdivision, deed date → the full grade recompute each cycle.
- **[GAP-5] narrowed:** with weekly/daily streams now carrying the
  time-sensitive signal, the monthly CAD report is explicitly the *slow* layer —
  updated aggregates + "changes since last month" + a clean "no material CAD
  changes" state in a quiet month is acceptable, because the warm/legal streams
  are where velocity lives.
- **Baseline / history depth — RESOLVED [GAP-15]:** load **current + one prior
  certified roll per county**, done when each county's adapter goes live.
  - Travis: have 2025 (`data/farmsignal.duckdb`); **download + load 2024**
    (TCAD publishes prior-year certified exports; same fixed-width family —
    verify byte offsets against the 2024 layout doc).
  - Williamson / Hays: current + immediately-prior, in the same pass as building
    those adapters.
  - **Not** 3+ years — older rolls drift to different layout versions (adapter
    friction) for only marginal gain; `homestead_dropped` etc. only need N−1.
  - Two prior annual rolls immediately activate `homestead_dropped`,
    `over65_newly_filed`, `ag_exemption_rollback` — the strongest event signals —
    so the **first monthly report has real "movers" content**, not an empty
    baseline.

### 6.2 Weekly — warm-lead streams (Market Leader +)

| Stream | Source | Status | Notes |
|---|---|---|---|
| Building / MEP permits | `data.austintexas.gov` Socrata API | **MVP** — FarmSignal already integrates this (`enrich/permits.py`); needs promoting to a scheduled county-wide weekly pull | Feeds *alerts*. The "small hurried permit = prepping to sell" thesis **contradicts** the engine's existing major-permit = −15 ("just invested") logic — see §10. Do **not** wire into the numeric grade until validated (**[GAP-19]**). |
| Code violations | same Socrata portal | **MVP** — already integrated (`enrich/code_violations.py`) | Defensible distress/neglect signal; mild positive contribution is reasonable. |
| Tax-delinquency changes | Travis Tax Office bulk CSV | **MVP** — already integrated (`enrich/tax_delinquency.py`); diff week-over-week for *new* delinquencies | Travis-only today; WCAD/Hays equivalents = **[GAP-6]**. |
| **Expired / cancelled / withdrawn MLS** | MLS — **not public data** | **FAST-FOLLOW, not MVP** | Highest-value warm-lead signal, but requires MLS membership + a data license that includes off-market statuses (most IDX feeds exclude expired), or a sponsoring-broker relationship, or a licensed vendor (Trestle / Bridge / SimplyRETS) *plus* MLS auth. Portal scraping is ToS-prohibited and doesn't work (expired listings leave public sites). Its own mini-project with licensing + compliance + recurring cost — **[GAP-17]**. Tier 2 stands without it at launch. |

### 6.3 Daily — legal-trigger streams (Citywide)

| Stream | Source | Status | Notes |
|---|---|---|---|
| Notice of Substitute Trustee Sale / pre-foreclosure | County Clerk **Official Public Records** (Texas non-judicial foreclosure; notice filed ≥21 days before the first-Tuesday sale) | **MVP — Travis only** | **Address-keyed match → reliable.** Poll daily (volume clusters near month-end). Light legal check on outreach framing needed (**[GAP-20]**). |
| Ag / wildlife (D1) exemption rollback | CAD roll (`land_state_cd`) | **MVP** — already in the engine as `ag_exemption_rollback`; needs ≥2 roll years | **Monthly cadence, not a daily poll** — listed here only because it's a legal-tier entitlement + alert (Citywide). Detected on the monthly CAD diff. |
| Probate / wills filings | County Probate/Clerk court records (Travis statutory probate court; Odyssey public access or a records vendor) | **FAST-FOLLOW** pending a Travis sourcing spike | **Name-keyed match → noisy** (common names). Needs address corroboration from the filing or it produces false "your prospect died" alerts. Per-county systems differ. |
| Williamson / Hays legal triggers | their clerk systems | **FAST-FOLLOW** | Launch Travis-first; W'son/Hays legal triggers are a documented launch gap (**[GAP-18]**, ties to [GAP-6]). |

### 6.4 Legal posture

Carried from FarmSignal §2.3: all data is public record resold as analysis (same
category as title plants / PropStream). Exclusivity is an **exclusive service
commitment, not a data monopoly** — never claim "exclusive data." Per-county
scraping ToS review (TCAD is Cloudflare-protected; clerk OPR portals vary) is
**[GAP-7]**. Foreclosure/probate outreach framing under Texas
foreclosure-consultant law (licensed agents listing the home are generally
exempt) + respectful-language rules is **[GAP-20]**.

## 7. Zip-level exclusivity — RESOLVED [GAP-2]

Re-scoped from FarmSignal's per-subdivision registry to **per zip code**. It is a
per-zip **add-on**, not a tier.

### Who / how much

- **Available to Market Leader and Citywide only.** Founding Solo ($99) cannot
  buy exclusivity — it's a serious-farmer feature, and a $99 lock on a
  competitive zip underprices the demand Marlin forgoes.
- **Price = +100 % of the subscriber's effective per-zip rate** for that zip
  (Offrs' proven ~2× territory-exclusivity premium). Effective per-zip rate =
  tier price ÷ included zips (Market Leader $199 / 3 ≈ $66/zip → exclusive on
  one zip = **+$66/mo**, that zip costs 2×). The operator may override the
  quote *up* for known-hot zips.
- **Citywide** monitors every zip but does **not** get blanket exclusivity — it
  may designate **up to 3** monitored zips as exclusive (default; adjustable),
  each at the multiplier or a bundled allowance — TBD, minor.

### Mechanic

- One **exclusive holder** per zip. While held, Marlin will **not activate that
  zip's monitoring or alerts for any other subscriber**.
- **Commitment language (verbatim, everywhere it appears):** *"While you hold
  ZIP X, Marlin will not activate that zip's monitoring or alerts for any other
  subscriber. Public records remain public — this is an exclusive service
  commitment, not exclusive data."*
- **Claimable only on a zip with ≤ 1 active monitor** (the would-be claimant).
  A zip already monitored by 2+ orgs cannot be taken exclusive — the requester
  goes on the waitlist for "exclusive when it clears."
- Contested/held zips: `zip_waitlist` row; **first-reply-wins** when the zip
  opens (manual notify at launch, automated in Phase 2).
- **Terms carried from FarmSignal:** `min_hold_until = claimed_date + 3 months`;
  no auto-renew; after the minimum, cancel with 30 days' notice; a
  claimed-but-dormant holder (paying, not logging in) is a manual monthly
  check-in, **not** auto-release.

### MVP scope (what to actually build)

- `zip_claims` + `zip_waitlist` tables (§9), enforced with **one check at
  zip-add time**: adding a monitored zip fails if another org holds it exclusive
  → offer a waitlist signup.
- The **≤ 1-monitor gate** on granting a claim.
- **Granting is a manual operator action** + a Stripe line item — no self-serve
  claim/checkout flow at launch.
- Waitlist notification is manual.

### Phase 2

- Self-serve claim + checkout.
- Automated first-reply-wins waitlist notification.
- Real **demand-banded pricing** (hot/warm/cold from waitlist length +
  population + subscriber history) replacing the flat multiplier.
- Renewal-based transition path for contested zips (honor existing monitors to
  their renewal, then don't renew that zip + offer an adjacent one).

## 8. Architecture

Hosted, multi-tenant. Decoupled asynchronous batch pipeline feeding a
notification engine (per `Marlin Grade - full Gemini session.md`).

Three ingest schedules (§6) feed one shared diff/event layer.

```
MONTHLY                     WEEKLY                        DAILY
[ CADs: Travis/W'son/Hays ] [ Socrata permits/violations, [ County Clerk OPR:
        │                     Tax Office delinquency ]        foreclosure notices,
        │                            │                        probate (fast-follow) ]
        ▼                            ▼                            │
[ Ingest Engine ]            [ Stream pullers ]                   │
  per-county adapters               │                             │
        │                           ▼                             ▼
        ▼                    [ staging tables ]  ◀───────  [ legal-filing puller ]
[ PostgreSQL staging ]              │                             │
        │                          └──────────┬──────────────────┘
        ▼                                     ▼
[ Diff Engine ] ── new vs prior snapshot per stream; emits typed change events
        │            (homestead T→F, new deed, exemption rollback, mailing-addr
        │             change; new permit; new violation; new delinquency;
        │             foreclosure notice filed; probate opened)
        ├───────────────────────────────────────────────┐
        ▼                                               │  external-event alerts
[ Marlin Grading Algorithm ]  ── ported engine          │  bypass the score math —
  normalize/ · analytics/metrics.py ·                   │  a filed foreclosure or
  analytics/scoring.py + scoring.yaml (0–100 → A–F)     │  a pulled permit is a
  full-roll rescore on the MONTHLY cycle;               │  spike on its own
  incremental rescore of parcels touched by a           │
  weekly/daily change event                             │
        ▼                                               │
[ parcel_score_history ] (score, grade, breakdown, as_of)
        │                                               │
        ▼                                               │
[ Event Generator ] ── classes (§11.1):                  │
   • urgent computed spike: event-driven signal →   ◀───┘
     grade now A/B (+ score Δ≥N + 6-mo cooldown)
   • external-event alert: warm-lead / legal-trigger stream hit an address
   • report-only movers: passive A/B crossings, warming, downgrades,
     new parcels → monthly report sections, no push
        ▼
[ Subscription Matcher ]
   SELECT org_id FROM subscriptions
   WHERE <zip> = ANY(active_zips) AND <event.stream> = ANY(entitled_streams)
        ▼
[ In-app Alerts feed ]  (all tiers — the primary surface, §11)
        │
        ▼
[ Notification Queue: Redis + Dramatiq / arq (Python) ]  ── outbound, tier-gated
        ├──▶ Twilio       ──▶ SMS (batched per zip, never per-house)
        ├──▶ Resend/Postmark ──▶ HTML email digest (dark-themed)
        └──▶ CRM push     ──▶ kvCORE / LionDesk (Citywide)
```

Plus, outside the batch pipeline:
- **Web app** (dark premium SaaS UI) + **service API** (`/score`,
  `/parcels/{uid}`, `/areas/{zip}/report`, subscription/alert CRUD).
- **Auth + multi-tenancy** — agents, and teams/brokerages ([GAP-10]).
- **Billing** — Stripe subscriptions for the 3 tiers + metering + limit
  enforcement.
- **Object storage** — generated monthly reports.
- **Background workers** — ingest, diff, rescore, spike eval, report
  generation, notification fan-out.

### Tech stack — RESOLVED [GAP-9]: all Python

Backend + engine language: **Python** (operator decision). The entire grading
engine is Python; keeping the app on the same stack means it ports as a package
with its test suite, and one runtime/ecosystem/deploy story for a small
operation. The engine is never in the request path (address lookup is a Postgres
read of pre-computed grades), so Node's web-throughput edge is moot.

- **API:** FastAPI
- **Workers / queue:** Dramatiq or arq + Redis (simpler than Celery; replaces
  the "Celery / BullMQ" fork in the architecture session)
- **ORM / migrations:** SQLAlchemy or SQLModel + Alembic
- **DB:** PostgreSQL · **Cache/queue broker:** Redis
- **Notifications:** Twilio (SMS) · Resend or Postmark (email)
- **Billing:** Stripe · **Storage:** object store for generated reports
- **Frontend:** React + TypeScript (Vite or Next), separate SPA — independent of
  the backend-language choice
- **Engine package:** the ported FarmSignal modules (`normalize/`, `analytics/`,
  `ingest/`, `enrich/`, `gis/`) become an importable `marlin_engine` package the
  worker jobs call; the only structural change is swapping the DuckDB write path
  for Postgres.

## 9. Canonical data model

**Port from FarmSignal (system-of-record moves DuckDB → Postgres):**
- `parcels` — the canonical parcel columns from FarmSignal §4 / `db.py`
  (`county, parcel_id, roll_year, situs_*, owner_*, mail_*, subdivision_raw/canon,
  legal_description, deed_date, homestead, over65_exempt, property_class, is_sfr,
  assessed_value, geo_id, jan1_owner_name, land_state_cd, …` + computed flag
  columns). Add a stable surrogate **`parcel_uid`** that survives re-ingest.
  Normalize the zero-padded `parcel_id` ↔ integer `PROP_ID` mismatch at ingest.
- Keep DuckDB (or a Postgres columnar path) as the **batch analytics** layer for
  the full-roll rescore if that's faster than in-Postgres.

**New tables:**
- `parcel_score_history(parcel_uid, as_of_date, score, grade, breakdown)`
- `orgs`, `users`, `user_orgs` (roles)
- `subscriptions(org_id, tier, active_zips[], entitled_streams[], lookups_used,
  seats, period_start, stripe_sub_id, …)` — `entitled_streams` is the §4
  stream-gate (`cad`, `permits`, `violations`, `tax_delinquency`,
  `foreclosure`, `probate`, `mls_status`, …)
- `zip_claims(zip, status open|claimed, holder_org_id, claimed_date,
  min_hold_until, stripe_line_id)` — §7 exclusivity
- `zip_waitlist(zip, org_id, added_date, notified)`
- `saved_areas(org_id, zip, …)` — a monitored zip per org
- `signal_events(id, stream, parcel_uid, zip, event_type, payload jsonb,
  source_ref, observed_at, cycle)` — one row per detected change from **any**
  stream (permit pulled, violation opened, new delinquency, foreclosure notice
  filed, probate opened, CAD field changed). The Diff Engine writes here.
- `alerts(id, org_id, zip, class 'computed_spike'|'external_event'|'report_mover',
  urgent bool, signal_event_id, parcel_uid, from_grade, to_grade, trigger_signal,
  headline, status new|worked|dismissed, created_at, report_cycle)` — the in-app
  Alerts feed (§11). `urgent=true` rows push per entitlement; `class='report_mover'`
  rows (passive A/B cross, warming, cooled-off, new parcel) never push and are
  grouped into that cycle's monthly report. Written by the Event Generator +
  Subscription Matcher, one row per (org, event).
- `alert_prefs(org_id, zip, sms bool, email bool, digest_cadence, muted bool)` —
  outbound only; the feed always populates
- `notifications(org_id, channel, payload, alert_ids[], sent_at, status)` —
  outbound send log
- `legal_filings(id, county, filing_type foreclosure|probate|…, filed_date,
  raw_name, raw_address, matched_parcel_uid, match_method address|name,
  match_confidence)` — landing table for §6.3 clerk-record pulls before they
  become `signal_events`
- `staging_*` — raw per-stream snapshots for the Diff Engine

## 10. The Marlin Grade — scoring

Ported wholesale from FarmSignal `analytics/scoring.py` + `config/scoring.yaml`
(see `docs/teardown.md` §5 and `docs/scoring-decisions.md`).

- **Model:** weighted sum of ~15 public-record signals, clipped 0–100, with a
  deterministic per-signal explainability breakdown. Signal list + weights are
  in `docs/scoring-decisions.md` / FarmSignal's yaml.
- **Decision 1 (applied in Marlin's config):** `out_of_state` **+10 → −10**
  (rename from `out_of_state_additional`). An out-of-state, non-homestead SFR
  owner is a rental-investor profile — less motivated to sell.
- **Decision 2:** the **letter grade is fixed A–F cutoffs on the absolute 0–100
  score** — not curved per zip. Rationale: a curve drifts as neighbours change,
  which would fire false spike alerts; fixed bands make "grade changed" a real
  event, keep grades comparable across zips/metros, and stay honest about cold
  areas. Grades: **A B C D F** (no E).
- **Cutoff values — methodology RESOLVED [GAP-11], numbers pending the run.**
  See §10.1.
- **Dormant signals to activate:** `homestead_dropped`, `over65_newly_filed`,
  `ag_exemption_rollback` require ≥2 roll years loaded — load a prior year per
  county at launch. These are also the strongest spike triggers.
- **Data Quality Filter** (feature 4 in §5) is `owner_is_entity` +
  `likely_rental` surfaced with plain-language labelling.
- **New-stream discipline (weekly/daily sources, §6.2–6.3):** a stream feeds
  **alerts** the moment it lands (a filed foreclosure notice or a pulled permit
  is a spike on its own — it does not wait on the score). It feeds the **numeric
  grade** only after its weight is validated against real data. Specifically:
  - `foreclosure_notice`, `probate_open`, `tax_delinquency` (new) — defensible
    motivation/distress signals; may take a positive grade weight once tuned.
  - `code_violation` — mild positive is reasonable.
  - `minor_permit` (the "hurried repair = prepping to sell" thesis) — **not**
    wired to the grade until **[GAP-19]** validation; it contradicts the
    existing `recent_permit_activity` = −15 ("just invested, staying") logic,
    which stays as-is for major permits.

### 10.1 A–F cutoffs & the `N` threshold — methodology [GAP-11]

Numbers can't be set until the engine scores a real population; this is the
procedure for setting them. Prereqs: `marlin_engine` extracted (§8), Travis 2024
roll loaded (§6.1).

**The model is nearly a step function.** Almost every signal is boolean;
`assessed_value` doesn't feed the score; the only continuous input is
`tenure_bonus_per_year` (+1/yr past 15). A parcel's score barely moves between
cycles unless a flag flips or tenure crosses 9/15. Consequence: the
boundary-jitter risk that fixed cutoffs normally carry is small here, and `N`
(§11.1) is a backstop for future continuous signals, not load-bearing today —
the §11.1 event-driven gate does the real anti-noise work (every event trigger
is a ≥20-pt jump).

**Phase A — one-zip engine validation** *(operator's home zip — noted for the
first run).* Correctness, not calibration:
- per-parcel flags match ground truth the operator knows (known rentals →
  `likely_rental`; long-tenured owners → tenure + bonus; entity-owned →
  `owner_is_entity`);
- `out_of_state` −10 flip pulls known out-of-state rentals *down*;
- 2024-roll join → `homestead_dropped` fires on real known move-outs;
- `recent_sale` catches known recent sales and de-prioritises them;
- zip aggregates believable (% absentee, median tenure — the sanity check from
  FarmSignal's old build sequence);
- address → parcel lookup resolves correctly.

**Phase B — full-roll distribution run** (all ~486k Travis SFR parcels). A single
zip is not a representative distribution — cutoffs fit to one stable
owner-occupied zip would miscalibrate everywhere else.

**Placement: distribution-anchored, then frozen.** Inspect the full-roll score
histogram, place cutoffs at target percentiles *once*, read off the score values,
and freeze those score values as the permanent fixed cutoffs (still Decision #2 —
percentile is a one-time tool, not a per-zip curve). Snap to natural
gaps/clusters in the histogram.

| Grade | Starting anchor (share of scored SFR) |
|---|---|
| A | top ~3% |
| B | next ~12% (A+B ≈ 15% = the "worked" set) |
| C | next ~25% |
| D | next ~35% |
| F | bottom ~25% |

**`N`:** provisional **10 points**; confirm from the actual roll-to-roll score-
delta distribution once two rolls are scored.

**Outcome-anchoring (Phase 2):** once "did this address list within 12 months"
is measurable (ties to [GAP-17]), re-fit so each band has a distinct real
listing rate.

**Re-fit cadence:** frozen at launch; revisited only after a full year, on a
major weight change, or when outcome data arrives — each revisit is a §11.1
silent re-baseline.

## 11. Notifications

Every cycle, each parcel in a monitored zip resolves to exactly one outcome:

| Outcome | Surface | Channel |
|---|---|---|
| **Urgent computed spike** (§11.1) | feed + email; SMS at Market Leader+ | push, as soon as the monthly cycle completes |
| **Legal-trigger external event** (§6.3, Citywide) | feed + SMS + CRM push | push, at cycle completion / daily poll |
| **Warm-lead external event** (§6.2, Market Leader+) | feed + weekly email digest — **no SMS** | weekly digest |
| **Report-only mover** — passive A/B crossing, "warming" (still C/D), downgrade ("cooled off"), brand-new A/B parcel | monthly report section + feed entry within the report | no push |
| No change | — | — |

All alerts are gated by the subscriber's `entitled_streams` (§4) and zip list.
**Batched per zip** — one digest, never one message per house (a supplement or a
bulk clerk filing can move hundreds of parcels at once; per-house sends get the
number blocked).

- **In-app Alerts feed is the primary surface (all tiers).** Every alert —
  computed spike or external-event — lands in a dashboard feed/inbox: per-zip,
  per-cycle; each address with its grade transition and triggering signal(s);
  persistent, filterable, mark-as-worked / dismiss. Email / SMS / CRM push are
  delivery channels layered *on top* of the feed. An agent who mutes every
  outbound channel still sees everything in-app.
- **Outbound channels by entitlement:**
  - *Urgent computed spikes* (§11.1) → feed + email; **SMS** at Market Leader+;
    **priority SMS (within the hour) + CRM push** at Citywide.
  - *Legal-trigger external events* (§6.3, Citywide) → feed + **SMS** + CRM push
    — the SMS-worthy external events.
  - *Warm-lead external events* (§6.2, Market Leader+) → feed + the **weekly
    email digest**. **No SMS** — permit/violation volume would train agents to
    ignore it.
  - Per-zip **mute toggle** (outbound only — the feed still populates) and
    per-user **digest cadence**. A monthly mailer can drop all outbound and just
    work the feed.
- **Monthly report** — every monitored/claimed zip, every cycle, regardless of
  alert activity (format = [GAP-3]).
- **Payload style** (from the architecture session): minimal, high-urgency,
  dark-themed, one Signal-Cyan CTA back into the platform.
  - SMS: `[Marlin Alert] 🎯 New A-grade listing-propensity spike in ZIP 78702 —
    an address on Willow St dropped its homestead exemption after 11 years.
    View: marlin.grade/alerts/78702`
  - Email digest subject: `[Marlin] ⚡ 14 new propensity spikes in your Austin
    farm areas` → body: per-zip counts + `[ Open Today's Workspace ]`.
  - Exact copy + direct-mail postcard templates = **[GAP-12]**.

### 11.1 Computed-spike rule — RESOLVED [GAP-8]

A parcel in a monitored zip fires an **urgent computed spike** when **all** of:

1. **`to_grade ∈ {A, B}`** — the grade landed in an actionable tier.
2. **Event-driven** — the score movement this cycle was dominated by an *event*
   signal: `homestead_dropped`, `ag_exemption_rollback`, a **new**
   `tax_delinquent`, or a `recent_sale` / deed / owner-of-record change.
   (Passive drift — tenure ticking past a threshold, out-of-state discovered
   from a mailing-address update — does **not** qualify.)
3. **Real movement** — score rose by **≥ N points** since the prior snapshot.
   With today's near-boolean model this rarely excludes anything (§10.1), so `N`
   is mainly a guard for future continuous signals; `N` calibrated with
   [GAP-11]'s run.
4. **Not in cooldown** — this parcel has not fired a computed spike in the
   trailing **6 months**.

The alert headline names the dominant `score_breakdown` delta —
*"homestead exemption dropped after 11 years (+25)"*.

**Everything else is report-only (no push):**
- grade crossed into A/B via **passive drift** → "new A/B addresses this cycle"
- grade improved but stayed **C/D** → "warming" watchlist
- grade **downgraded** → "cooled off" list (helps prune mail lists)
- **brand-new parcel** graded A/B → "new to the data" list — never a spike
  (nothing changed; monitoring just started)

**Safety rules:**
- An A–F **cutoff recalibration** ([GAP-11]) or a **new annual roll import**
  triggers a **silent re-baseline**: recompute all grades, write
  `parcel_score_history`, but **suppress spike generation for that cycle**
  (otherwise a threshold change mass-fires false spikes).
- **Missing prior snapshot** (parcel wasn't monitored last cycle, ingest gap) →
  treat as "no prior," show current grade only, not a spike.

This keeps SMS volume tied to genuinely rare behavioral events. The §6.3
legal-trigger streams are the external-event analogue — event-driven and
SMS-eligible; whether they also require an A/B grade is [GAP-21].

### 11.2 Month-1 behavior — RESOLVED [GAP-15]

The first production monthly run for a market is a **baseline run**:

- It establishes the first monthly snapshot — so there is nothing to diff
  against and **zero computed spikes fire** (consistent with §11.1's
  "missing prior snapshot" rule). Between-refresh computed spikes begin month 2.
- The **multi-year annual-roll-diff signals** (`homestead_dropped`,
  `over65_newly_filed`, `ag_exemption_rollback`) *do* populate from the two
  annual rolls loaded per §6.1, so the **first monthly report has real content**
  — its "movers" / "new A/B" sections are driven by year-over-year changes, not
  left empty.
- **Warm-lead + legal-trigger streams (§6.2–6.3) fire from day one** — they run
  on their own external cadence, independent of any Marlin prior snapshot. At
  launch, **backfill ~90 days** of these streams so month-1 subscribers see
  genuinely active events: foreclosure notices especially (the 21-day-to-sale
  window means a 90-day pull surfaces live foreclosures, not just post-launch
  filings), plus recent permits / violations / new delinquencies. Cheap API
  pulls, materially better first-month value.

## 12. Grading presentation (UI)

- **Letter grade is the primary element** everywhere an address appears.
- Drill-in reveals: 0–100 score, per-signal breakdown (+/− contributions),
  ownership/tenure/exemption facts, and — **at Market Leader+** (§4) — a grade
  history sparkline. Solo sees the current grade + breakdown only.
- Per-zip **grade distribution** view ("this zip: 3% A, 9% B, …") so a cold farm
  reads as information, not a bug.
- **"Top N in this zip"** ranked list regardless of absolute grade — always
  gives the agent something to work.
- **Local percentile** shown as *secondary* context ("top 6% of this zip"). This
  is display context only — the grade itself stays absolute (§10 Decision 2 —
  no per-zip curving of the grade).

## 13. Regional expansion

- **Launch:** **Travis complete** (CAD + weekly warm-lead + daily foreclosure).
  Williamson + Hays CAD adapters are the immediate next build; their
  enrichment / legal-trigger streams run degraded until per-county sources are
  wired ([GAP-6], [GAP-18]).
- **Phase 1 (full Austin metro):** Travis + Williamson + Hays at parity.
- **Phase 2:** DFW, Houston, San Antonio.
- **Growth mechanic:** regional landing pages (`/dfw`, `/houston`, …) capture
  waitlist sign-ups; **scrape-onboarding priority is allocated to the zips with
  the highest concentration of waiting agents** (gamified launch).

## 14. Landing page framework (from handoff session)

- **Hero:** "Stop farming blind. Start targeting listings."
- **Subhead:** "Marlin analyzes millions of scattered off-market data points to
  score the exact listing probability of every residential address in your zip
  code. Dominate your geographic farm before your competitors even see the sign
  go up." *(drop "daily" from any earlier copy — cadence is monthly)*
- **Local hook:** "National data brokers use generic algorithms. Marlin analyzes
  Texas public records every cycle to calculate listing propensity from actual
  hyper-local neighborhood tenure trends."

## 15. What carries over from FarmSignal

Full detail in `docs/teardown.md`. Summary:

| Carry as-is | Adapt | Cut |
|---|---|---|
| `normalize/` (subdivision, owners, address) · `analytics/scoring.py` + `metrics.py` · `ingest/travis.py` · `subdivision_aliases.yaml` · TCAD layout JSONs · analytics/normalize/enrich tests | `db.py` schema (DuckDB→Postgres, +`parcel_uid`, +history) · `ingest/` cadence + diff · `enrich/` + `gis/` (tri-county, scheduled) · `export/csv_export.py` columns · CSV/PDF as *export* not primary | `cli.py` command surface (→ API) · `report/` as primary deliverable · `config/brand.yaml` · `leads/` · FarmSignal tiers + subdivision registry + 1,500 cap · `$0 infra / no paid API / local` constraints |

Build WCAD + Hays adapters (empty stubs today). Load ≥2 roll years per county.

## 16. Open gaps to close with the operator

- ~~**[GAP-1]** Tier feature rows vs. monthly data cadence~~ — **RESOLVED.**
  Tiers gate **which signal streams reach the subscriber** (monthly CAD /
  weekly warm-lead / daily legal-trigger — §6), plus capacity (zips, lookups,
  seats), channels, and integrations. No data-freshness claims. Tier table in
  §4; three-cadence pipeline in §6/§8. "Citywide Exclusive" → "Citywide". New
  sub-gaps spun out: [GAP-17]–[GAP-20].
- ~~**[GAP-2]** Zip exclusivity~~ — **RESOLVED (§7).** Per-zip add-on, Market
  Leader+ only, priced at **+100% of the effective per-zip rate** (operator can
  override up for hot zips). One holder per zip; claimable only on a zip with
  ≤1 active monitor; waitlist + first-reply-wins; 3-month min hold, no
  auto-renew. **MVP builds enforcement + manual grant** (Stripe line item, no
  self-serve). Self-serve + demand-banded pricing = Phase 2. Minor sub-decision
  left: Citywide's exact exclusive-zip allowance (default 3).
- **[GAP-3]** Monthly report format — in-app only, PDF, or both? Per zip?
- **[GAP-4]** CRM sync — which records push (all graded? spikes only?), field
  mapping, cadence, one-way vs two-way.
- **[GAP-5]** *Narrowed (§6.1).* The monthly CAD report is now explicitly the
  slow layer (velocity lives in the weekly/daily streams), so a "no material CAD
  changes" state is acceptable — but still confirm what the quiet-month report
  shows (refreshed aggregates? month-over-month deltas? nothing?).
- **[GAP-6]** Enrichment/GIS tri-county parity — build WCAD/Hays equivalents, or
  launch Austin-rich / other-counties-degraded and backfill?
- **[GAP-7]** Scraping ToS / legal review per county (TCAD Cloudflare, etc.).
- ~~**[GAP-8]** Exact computed-spike rule~~ — **RESOLVED (§11.1).** Urgent
  computed spike = `to_grade ∈ {A,B}` + event-driven signal (`homestead_dropped`,
  `ag_exemption_rollback`, new `tax_delinquent`, deed/owner change) + score
  Δ ≥ N + 6-month cooldown. Passive A/B crossings, warming (stayed C/D),
  downgrades, and new parcels are **report-only, no push**. Cutoff
  recalibration / new-roll import → silent re-baseline (spikes suppressed that
  cycle). `N` calibrated with [GAP-11].
- ~~**[GAP-9]** Backend language / stack~~ — **RESOLVED: all Python** (FastAPI +
  Dramatiq/arq + Redis + Postgres; React/TS frontend). See §8.
- **[GAP-10]** Auth model — individual agents only, or teams/brokerages with
  seats? **Team support in MVP is effort-gated** — decision pending a
  lift/effort estimate. Seat pricing TBD.
- **[GAP-11]** A–F cutoff values + `N` — **methodology RESOLVED (§10.1)**;
  numbers pending the engine run. Two phases: (A) one-zip engine validation
  against ground truth — *operator's home zip, noted for the first run*;
  (B) full-roll distribution run → distribution-anchored-then-frozen cutoffs.
  Starting anchors: A ≈ top 3%, B ≈ next 12%, C ≈ 25%, D ≈ 35%, F ≈ 25%;
  `N` provisional 10.
- **[GAP-12]** Alert copy + direct-mail postcard templates for spiked addresses.
- **[GAP-13]** Trial / freemium — how does an agent evaluate before subscribing?
  (FarmSignal used a watermarked sample.)
- **[GAP-14]** "Lookup" definition for metering — single address search only, or
  does browsing a monitored zip's list consume lookups?
- ~~**[GAP-15]** Month-1 baseline~~ — **RESOLVED (§6.1, §11.2).** Load
  **current + one prior certified roll per county** (Travis: add 2024). First
  monthly run is a baseline — zero computed spikes, but multi-year signals +
  a ~90-day backfill of the warm-lead/legal streams give the first report real
  content. Computed spikes start month 2.
- ~~**[GAP-16]** Rewrite vs. evolve~~ — **RESOLVED: new Marlin repo.** The
  FarmSignal engine modules (`normalize/`, `analytics/`, `ingest/`, `enrich/`,
  `gis/`) are lifted into an importable `marlin_engine` package; FarmSignal is
  frozen as reference. Follows from the all-Python decision (§8).

### Spun out of [GAP-1] (signal-stream restructure, §6)

- **[GAP-17]** Expired/cancelled-MLS access path — MLS membership + off-market
  data license, sponsoring-broker partnership, or licensed vendor (Trestle /
  Bridge / SimplyRETS) + MLS auth? Recurring cost, compliance, timeline. This is
  the gate on the highest-value warm-lead stream; **fast-follow, not MVP.**
- **[GAP-18]** Williamson / Hays legal-trigger sourcing — per-county clerk
  systems for foreclosure + probate. Launch is Travis-only for §6.3; W'son/Hays
  legal triggers are a documented gap (ties to [GAP-6]).
- **[GAP-19]** Validate the "minor/hurried permit ⇒ prepping to sell" thesis
  before it touches the numeric grade. It contradicts the existing
  `recent_permit_activity` = −15 logic. Until validated, permits feed alerts
  only, not the score (§10).
- **[GAP-20]** Legal check on foreclosure/probate outreach framing — Texas
  foreclosure-consultant law (licensed-agent-listing-the-home exemption),
  respectful-language rules, TREC ethics. Cheap check, do before launching §6.3
  streams.

### From the v0.2 coherence review

- **[GAP-21]** Do external-event alerts (§6.2–6.3) respect the numeric grade?
  Recommendation: **legal triggers** (foreclosure, probate) alert **regardless
  of grade** — hard public-record events; **the permit stream is grade-gated**
  (surface only on parcels already ≥ C — a permit on an F-grade rental is
  noise); **violations / new delinquency** alert at any grade (distress signals
  meaningful anywhere). Confirm before wiring the Event Generator's
  external-event path.
