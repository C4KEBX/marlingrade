# Session log — 2026-09-08 — Marlin Grade demo build: design → plan → SDD execution (Tasks 1–7)

Project: **Marlin Grade** (`/Users/justinmason/Claude Code/Marlin Grade/`).
Continues from `docs/session-2026-09-08-app-build-brainstorm.md`.
**Paused mid-execution** — operator out of Anthropic usage; OmniRoute checked and
ruled out (only provider is the same exhausted `anthropic` upstream). Everything
is checkpointed on disk; resume instructions below.

---

## What this session did

1. **Resumed the brainstorm** from the prior session log, re-grounded in
   `MARLIN_GRADE_BUILD_SPEC.md` + the FarmSignal engine modules.
2. **Ran the visual companion** — produced full wireframes for all 9 demo
   screens (`.superpowers/brainstorm/` — HTML, gitignored). Iterated the landing
   page 3×: boxless "how it works", separated pricing section, unified per-column
   comparison table, logo placeholder cell.
   - **NB:** wireframe addresses ("Kestrel Ridge Dr", "Puccoon Cv", etc.) were
     **fabricated placeholders**, not real data. The build itself
     (`build_demo_bundle.py`) uses only real DuckDB rows.
3. **Wrote + approved the demo build spec:** `docs/DEMO_BUILD_SPEC.md` (v1.0).
4. **Brand-brief reconciliation** — read `Branding/Marlin brand brief - gemini.md`
   + the two PNG assets, found the spec's design section diverged, and rewrote
   §6 + restructured the screens (see "Decisions locked" below).
5. **Wrote the implementation plan:** `docs/superpowers/plans/2026-09-08-marlin-demo-build.md`
   — 21 tasks, TDD-shaped, self-reviewed against the spec.
6. **Started SDD execution** (`superpowers:subagent-driven-development`) —
   controller + fresh implementer subagent per task + task-review per task.
   **Completed Tasks 1–6 (reviewed clean). Task 7 implemented + committed,
   review pending.**

---

## Current state

**Branch `demo-build`** (off `main` @ `94a91c8`). `main` holds only the repo
scaffold + design docs (Task 1). All feature work is on `demo-build`.

| Task | State | Commit(s) |
|---|---|---|
| 1 · repo scaffold + tooling | ✅ complete, reviewed | `main`: `d4d8008`, `94a91c8` |
| 2 · lift `normalize/{address,owners}` | ✅ complete, reviewed | `4e59261` |
| 3 · lift `analytics/scoring` + yaml, package-local path | ✅ complete, reviewed | `4a61be5` |
| 4 · `out_of_state` +10 → −10 (TDD) | ✅ complete, reviewed | `3e27d43` |
| 5 · lift `analytics/metrics`, drop DuckDB write path | ✅ complete, reviewed (unblocked via R8) | `391f1ca` |
| 6 · `grades.py` — A–F from score (TDD, placeholder cutoffs) | ✅ complete, reviewed | `64b4a75` |
| 7 · `scripts/build_demo_bundle.py` — score 7 zips → JSON | ⏳ **implemented + committed, REVIEW PENDING** | `ccf9965` |
| 8–21 | not started | — |

- Full test suite: **82 passing** as of Task 7. Engine lift (1–6) is done and green.
- `web/public/data/{zips.json, parcels-<zip>.json, grades.json}` generated + committed.
  Real run: 78749 = 10,423 SFR. **A% is near-zero across all 7 zips — expected**,
  `grades.CUTOFFS` are still the placeholders `{A:75,B:55,C:35,D:18}`; Task 8
  calibrates them from the full Travis roll.
- Working tree: only `design/` untracked (5 PNG design references, not in the
  plan — leave or fold into Task 11/18).

---

## >>> HOW TO RESUME <<<

The SDD workspace is **on disk but gitignored** (`.superpowers/` is in
`.gitignore`), so it lives only on this machine at:
`/Users/justinmason/Claude Code/Marlin Grade/.superpowers/sdd/2026-09-08-marlin-demo-build/`
It contains: `progress.md` (the ledger — authoritative), `task-{1..13}-brief.md`,
`task-{1..7}-report.md`, `review-*.diff`.

**To resume in a fresh session:**
1. `cd "/Users/justinmason/Claude Code/Marlin Grade"` — confirm on branch `demo-build`.
2. Invoke `superpowers:subagent-driven-development`. It reads
   `.superpowers/sdd/2026-09-08-marlin-demo-build/progress.md`, sees Tasks 1–6
   `complete`, and picks up at the **`>>> RESUME HERE <<<`** block in that ledger.
3. **Next action:** review Task 7 —
   `scripts/review-package <plan> 64b4a750c64db64d93aac19bddcaa142e7584132 ccf9965174013d61c219dde8339b2e1f1ef80dfb`
   then dispatch the task-reviewer (sonnet). Scrutinize: JSON shapes vs spec §5.4;
   the score-sort tiebreak deviation (see minors); idempotency (run the script
   twice, `web/public/data` must be byte-identical); `_parse_breakdown`.
4. Then Tasks 8 → 21. Briefs 8–13 are pre-generated; 14–21 need
   `scripts/task-brief <plan> N`.

**Model policy** (from the ledger): haiku for verbatim lifts / transcription,
sonnet for integration / judgment / all frontend tasks, opus for the final
whole-branch review.

**If the DuckDB data gets replaced** (operator's separate data-fix plan):
Tasks 1–6 (engine) and 11–21 (SPA) are data-independent and stand. Re-run
Tasks **7, 8, 9, 10** against the corrected data — the JSON bundle, the frozen
cutoffs, the Phase A validation doc, and the 2024 ingest are all provisional on
the current `data/farmsignal.duckdb`. No code is thrown away.

---

## Decisions locked this session (brand reconciliation)

Folded into `docs/DEMO_BUILD_SPEC.md` §3, §5, §6, §8, §10:

- **Grade scale:** exactly **A B C D F** — no plus, no E. Build spec §10 (fixed
  0–100 cutoffs, 5 bands) wins over the brand brief's "A+ to F".
- **Palette — exact "Deep Analytics" values:** `--abyssal #0B111E` · `--ice
  #F1F5F9` · `--cyan #00F0FF` (Signal Cyan) · `--green #00E676` (Data Green —
  **export/CSV & revenue ONLY**, never a generic positive) · `--slate #64748B`.
  Grade colours flash cyan for A/B, recede into abyssal for C–F (not a rainbow).
- **Typography:** **Plus Jakarta Sans** (headers/branding) · **Inter**
  (interface/data) · **JetBrains Mono** (data-label accents only). Brand brief
  wins over parlyr.site parity; build tooling still mirrors parlyr.site.
- **Signature UI:** the **circular grade gauge** (Signal-Cyan score ring, letter
  dead-centre, JetBrains-Mono driver flags beneath) + a **right-hand slide-out
  address drawer** over the workspace. **Address search is the sticky global
  header**, not a screen.
- **Layout archetype:** sticky global header (logo · centered cyan-glow search ·
  Palmer Holland identity block) + left icon sidebar (Dashboard · Tracked Zips ·
  Alerts · Monthly Report · Export Logs · Settings) + core workspace.
- **Screens renumbered:** 1 Landing · 2 Sign-in · 3 Farm picker · 4 Zip
  dashboard · 5 Address **drawer** · 6 Alerts feed · 7 Monthly report · 8
  Roadmap. Cut line: 1–5 + header search must; 6–7 staged strong want; 8 if ahead.
- **Seeded account = "Palmer Holland"** in a persistent identity block (real
  build layout, not demo-only).
- **Styling:** vanilla CSS + custom-property tokens, no Tailwind/CSS-in-JS.
- **Canonical listing-status disclaimer** drafted (spec §7) — verbatim on every
  surface an address appears + every export.
- **Data architecture = Approach A** (offline scoring → static JSON bundle → SPA
  on Cloudflare Workers static-assets, its own `*.workers.dev`). No runtime
  backend in the demo.

---

## Rulings made this session (SDD ledger — read if reworking)

- **R1** — Task 1 on `main` (repo bootstrap only); `demo-build` branch for Tasks
  2–21; no git worktree (greenfield).
- **R2** — added `scripts/__init__.py` so `python -m scripts.*` + pytest imports resolve.
- **R3** — `Disclaimer.tsx` + `DISCLAIMER_TEXT` (constant + `compact` variant)
  folds into Task 15; Task 16 adds the `full` variant. (Task 15's `Dashboard.tsx`
  imports it.)
- **R4** — Task 11 runs `npm create vite` inside the already-populated `web/`
  (Task 7 wrote `web/public/data/`); choose "Ignore files and continue", verify
  the bundle survives.
- **R5** — Tasks 13/15/17/19/20 overwrite the placeholder route/component files
  Task 13 stubs; do not error on existing paths.
- **R6** — Task 16 `percentileIn` must be a real calc (`100·count(score>s)/n`
  over the zip's parcels), NOT the plan text's constant-0.5 stub. Load-bearing —
  it's on the marquee screen.
- **R7** — Task 11 implementer reports the actual brand-mark asset filename
  (`marlin-mark.svg` or `.png`); controller carries it into Task 18.
- **R8** — `db.py` is out of demo scope; delete the 2 `fetch_prior_roll_year_snapshot`
  DuckDB-file integration tests + the `get_connection` import from the lifted
  `test_analytics_metrics.py`; replaced with one in-memory duckdb test. Applied,
  reviewed non-tautological.
- **D1** (relaxed) — operator flagged `data/farmsignal.duckdb` has quality issues
  and may be replaced via another session's plan. The alarm was a fabricated
  wireframe address (not a real bug). Continue the pipeline normally; if the data
  is replaced, re-run Tasks 7–10 (see resume note above).

---

## Deferred minors (final whole-branch review should triage)

- **T4** — 2 pre-existing pandas `FutureWarning`s from `scoring.py:59`
  `_optional_bool_column` `.fillna` downcasting. Inherited from FarmSignal, not
  introduced. Candidate for a lint/cleanup pass. (Did not fire in Task 7's run.)
- **T5** — `Path` + `compute_score_breakdown` now-unused imports in `metrics.py`
  (only the deleted `run_compute_metrics` used them). F401. Lint pass.
- **T5** — the R8 replacement test asserts column names + row scoping but not
  per-column data round-trip (deleted test had `homestead==True`,
  `land_state_cd=="D1"`). 1-line add restores it; `fetch_prior_roll_year_snapshot`
  feeds the computed-spike narrative.
- **T5** — stale `farmsignal enrich tax-delinquency` comment at `metrics.py:290`
  (inside a verbatim-kept function).
- **T7** — parcel sort changed from bare `score` desc to `["score","parcel_id"]`
  desc/asc (≈1,199 parcels/zip tie on a score → non-stable sort churned the
  committed JSON). Accepted: score-descending contract preserved, output now
  byte-stable. **Carry to Task 12:** `parcels-<zip>.json` is score-desc,
  parcel_id asc tiebreak.
- **T1/T7** — untracked `design/` dir (5 PNG references). Not in the plan.

---

## Key files

| Path | What |
|---|---|
| `docs/DEMO_BUILD_SPEC.md` | **The demo spec, v1.0** (brand-reconciled). 10 sections. |
| `docs/superpowers/plans/2026-09-08-marlin-demo-build.md` | **The 21-task implementation plan.** |
| `MARLIN_GRADE_BUILD_SPEC.md` | Parent product spec (v0.2) — the binding authority above the demo spec. |
| `Branding/Marlin brand brief - gemini.md` | "Deep Analytics" identity brief (source of truth for §6). |
| `Branding/marlin watermark.png` | Full horizontal lockup (wordmark source). |
| `Branding/marlin icon options.png` | 12-variant contact sheet — crop the "Primary Mark" cell, trace to SVG. |
| `docs/scoring-decisions.md` | `out_of_state` −10 + fixed A–F cutoffs rationale. |
| `docs/teardown.md` | FarmSignal → Marlin KEEP/ADAPT/CUT/NEW. |
| `data/farmsignal.duckdb` | 486,859 Travis 2025 parcels (gitignored, 282 MB). **Quality issues — see D1.** |
| `.superpowers/sdd/2026-09-08-marlin-demo-build/progress.md` | **SDD ledger — gitignored, on-disk only. Authoritative for resume.** |
| `.superpowers/sdd/2026-09-08-marlin-demo-build/task-*-brief.md` | Per-task briefs (1–13 generated). |
| `marlin_engine/` | The lifted engine: `normalize/`, `analytics/{scoring,metrics}.py`, `scoring.yaml`, `grades.py`, `tests/`. |
| `scripts/build_demo_bundle.py` | Offline scorer → `web/public/data/*.json`. |
| FarmSignal `/Users/justinmason/Claude Code/FarmSignal` | **Frozen reference.** Never modify. |

---

## What's left (Tasks 8–21, from the plan)

**Part 1 (data — provisional per D1):**
- **8** full-roll score histogram → freeze real A–F cutoffs into `grades.py`
- **9** Phase A engine validation on 78749 → `docs/phase-a-validation.md`
- **10** Travis 2024 roll ingest (time-boxed ½ day, hard fallback to single-roll)

**Part 2 (SPA — data-independent):**
- **11** Vite+React+TS scaffold, Deep-Analytics tokens, fonts, brand assets
- **12** bundle data layer (`useBundle`, TS types) — note the T7 sort tiebreak
- **13** AppShell (sticky header + icon sidebar + routing + session context)
- **14** `GradeGauge` (animated cyan ring + letter + driver flags)
- **15** Screen 4 dashboard (distribution bar, aggregates, filters, prospect
  table, Data Green CSV export) — folds in `Disclaimer.tsx` per R3
- **16** Screen 5 `AddressDrawer` (right slide-out) — real percentile per R6
- **17** `GlobalAddressSearch` (header typeahead → drawer)
- **18** Screen 1 landing (hero, boxless how-it-works, unified pricing table, logo)
- **19** Screen 2 fake sign-in + Screen 3 farm picker
- **20** Screen 6 alerts feed + Screen 7 monthly report (hand-authored fixtures)
- **21** polish pass (motion, empty states, responsive, disclaimer audit) + deploy

Then: final whole-branch review (opus) → `superpowers:finishing-a-development-branch`.
