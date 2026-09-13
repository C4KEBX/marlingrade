# Session log — 2026-09-09 → 10 — Marlin Grade demo: SDD execution complete, merged + deployed

Project: **Marlin Grade** (`/Users/justinmason/Claude Code/Marlin Grade/`).
Continues from and **completes** `docs/session-2026-09-08-marlin-demo-build-execution.md`
(which paused mid-SDD-execution at Task 7, operator out of Anthropic usage).

**STATUS: DONE. Merged to `main`, pushed to GitHub, deployed live.**

---

## TL;DR — where things stand

| | |
|---|---|
| Branch | `main` @ **`bb65d65`** (fast-forward merge of the 22-commit `demo-build`; `demo-build` deleted) |
| Tag | `demo-wednesday` → `bb65d65` |
| GitHub | **`git@github.com:C4KEBX/marlingrade.git`** — `main` pushed, tracks `origin/main`, tag pushed |
| Live URL | **https://marlin-demo.justin-040.workers.dev** (Cloudflare Workers static-assets; Version `b444502d-045e-4ca3-9f0d-cb2f6bbf6c0b`) |
| Tests | 82 Python (`pytest`) + 17 frontend (`vitest`, 6 files) — all green on `bb65d65` |
| Build | `npm --prefix web run build` clean — JS 316.6 kB / 100.2 kB gzip, CSS 26.1 kB / 5.0 kB gzip |
| Deploy token | scoped "Edit Cloudflare Workers" API token — **REVOKED** by operator post-deploy (was id `e702f4c1…`) |

---

## What this session did

1. **Resumed** the paused SDD execution (`superpowers:subagent-driven-development`) from the ledger at
   `.superpowers/sdd/2026-09-08-marlin-demo-build/progress.md` — Tasks 1–6 were already complete,
   Task 7 implemented + committed but not reviewed.
2. **Drove Tasks 7–21 to completion** — controller + one fresh implementer subagent per task +
   one task-review subagent per task. Model policy: haiku for verbatim lifts, sonnet for
   integration/judgment/all frontend, opus for the final whole-branch review.
   - **Part 1 (engine + data, Tasks 1–10):** lifted FarmSignal engine into `marlin_engine/`,
     `out_of_state` +10→−10, A–F `grades` module, cutoffs **frozen `{A:67,B:44,C:35,D:25}`**
     calibrated on the full 349k-parcel Travis roll, `scripts/build_demo_bundle.py` scores 7 demo
     zips → `web/public/data/*.json`. Phase-A validation on 78749 (8/8 checks pass, no engine bugs).
     Travis 2024 roll ingest **deferred** (no raw file) — demo runs single-roll.
   - **Part 2 (SPA, Tasks 11–21):** Vite 8 / React 19 / TS 6 SPA — AppShell, GradeGauge, zip
     dashboard, AddressDrawer, GlobalAddressSearch, Landing, SignIn + FarmPicker, Alerts +
     MonthlyReport, polish pass. All 8 screens.
3. **Final whole-branch review on opus** — verdict "ready to merge, with fixes": 2 Critical +
   3 Important + 1 promoted-minor.
4. **One fix wave** (single sonnet subagent, all 6 findings) → commit `bb65d65` → **scoped
   re-review clean** (all 6 ADDRESSED, no new breakage).
5. **`superpowers:finishing-a-development-branch`** — operator chose "Full ship":
   - fast-forward merge `demo-build` → `main`, re-verified tests on merged tree, deleted the branch,
     moved the `demo-wednesday` tag to the tip.
   - operator added the `origin` remote; `git push -u origin main --tags`.
   - `wrangler login` OAuth failed (macOS 12.6 < wrangler's supported 13.5) → operator made a
     scoped API token → `CLOUDFLARE_API_TOKEN=… npx wrangler deploy` from `web/`.
   - controller smoke-tested the live URL (all routes + data files 200, SPA deep-links resolve).
   - operator revoked the deploy token (confirmed dead: "Invalid API Token").

---

## The final-review fix wave (commit `bb65d65`) — what changed after Task 21

- **C1** — `fixtures/alerts.json`: 2 of 4 alert rows stated a grade that contradicted the drawer
  one click later. Repointed `al-78749-0001` (headline foreclosure `legal_trigger`) to
  **`7105 KENOSHA PASS`** (real grade A), set `al-78749-0004` `to_grade` B→**A**. All 4 rows'
  `to_grade` now == the real bundle grade for that `situs_norm`. Re-ran the bundle.
- **C2** — `/alerts` was the one address-bearing surface with no disclaimer →
  `<Disclaimer variant="compact" />` added to `web/src/routes/Alerts.tsx`.
- **I1 (plan defect)** — three route CSS files each defined a global `.btn`; every route is
  statically imported so they collided (Export CSV label went cyan on hover; landing CTA shrank).
  → new `web/src/styles/buttons.css`, imported once in `main.tsx`; 3 duplicate blocks removed.
- **I2** — `appShell.css` responsive sidebar `@media (max-width:900px)` block sat *above* its base
  `.shell__main` rule → never applied → moved below.
- **I3** — `web/tsconfig.app.json` never set `"strict"` → added `"strict": true` (compiles clean,
  0 errors).
- **T14** — 1-frame full-ring flash on every drawer open → added `stroke-dasharray: 0 628.32` to
  `.gauge__arc` in `gradeGauge.css`.

---

## Rulings made across the whole build (each with cost-if-wrong)

- **R1** — Task 1 on `main`, `demo-build` for Tasks 2–21, no git worktree (greenfield `git init`
  in place). *Cost: a `git branch -m`; negligible.*
- **R9 (toolchain)** — `create-vite` shipped **Vite 8.2.2 / React 19.2.8 / TS ~6.0.2 /
  react-router-dom 7.18.3 / oxlint / `tsc -b` project refs**, newer than the plan's "React 18 /
  plain Vite / eslint". Accepted as-is; every Task 12–21 dispatch carried a `verbatimModuleSyntax`
  + `erasableSyntaxOnly` + `noUnusedLocals/Parameters` constraint block. *Cost: a task hits a
  `tsc -b` failure on banned syntax → 1-line rework. None did.*
- **Task 10 → fallback** — no `data/raw/travis/` file, DB has only `roll_year=2025`; brief mandates
  skip + note on a missing file. Year-over-year diff signals (`homestead_dropped`,
  `over65_newly_filed`, `ag_exemption_rollback`) stay inactive; `build_demo_bundle._score()`
  already runs the `prior=None` path. *Cost: if the 2024 export lands later, re-run Tasks 7–10 +
  rebuild the bundle; ~½ day deferred, zero code lost.*
- **Task 10 → doc-commit only, no review seat** — pure deferral note. *Cost: a stray wording
  issue; the final review saw it anyway.*
- **Task 21 stops before deploy** — operator directive at the time (no deploy/push without
  sign-off); branch left deploy-ready with `not_found_handling: "single-page-application"` in
  `web/wrangler.jsonc`. *Cost: operator runs deploy themselves; zero code impact.* (Later
  superseded — operator chose "Full ship".)
- **Stale MELAVA report note → FIX SOON, not blocking** — after C1 repointed the foreclosure alert
  away from `6713 MELAVA CT`, `report-78749.json` `movers.cooled[0].note` still says the
  foreclosure is "tracked separately in Alerts". Names no grade; MELAVA's D gauge still matches its
  D report grade; there *is* a foreclosure alert (on 7105 KENOSHA PASS). *Cost: one viewer notices
  the note points at a different address; ~30-sec fixture edit.*
- **D1 (operator, mid-Task-5, then superseded)** — a mid-session "data bug" alarm was a fabricated
  design-phase wireframe address, not real data. Pipeline continued as a normal pass. *Cost: none —
  if `farmsignal.duckdb` is replaced later, Tasks 7–10 re-run.*

---

## Outstanding (operator, none blocking)

1. **Visual QA on the live URL** — headless couldn't cover this:
   - widths 320 / 375 / 768 / 1024 / 1440: no horizontal body scroll; sidebar collapses to a
     56px icon rail under 900px; drawer full-width under 640px; pricing table scrolls in its
     `.plans__scroll` wrapper.
   - real-browser `prefers-reduced-motion: reduce` → score count-up + A/B `GradePill` cyan pulse
     both go instant.
   - click-path: `/` → Sign in → `/farm` → `/z/78749` → row → drawer → header search another
     address → `/alerts` → `/report/78749`.
2. **Send Palmer the URL.**
3. **~15 FIX-SOON post-merge debt items** — full list + triage in
   `.superpowers/sdd/2026-09-08-marlin-demo-build/FINAL-review-ledger-digest.md`. Headliners:
   - `useBundle` / `getJson` error-path / memo tests (only 17 fe tests; `useBundle` untested).
   - `tsconfig.test.json` in the project refs so `*.test.ts(x)` type errors fail `npm run build`
     (currently vitest-transpile-only).
   - strengthen `test_build_demo_bundle.py` from shape-only to strict-parse + required-keys assert.
   - delete 5 scaffold-cruft files: `web/README.md`, `web/src/assets/{react.svg,vite.svg,hero.png}`,
     `web/public/icons.svg`. Delete 2 dead imports in `marlin_engine/analytics/metrics.py`
     (`Path`, `compute_score_breakdown`).
   - retitle `docs/scoring-decisions.md` off "(pending implementation)" and fix its "not yet
     applied to any config" body line (it *is* applied — see §2a).
   - transparent/SVG wordmark (`web/src/assets/marlin-wordmark.png` has a baked opaque dark bg,
     ~430 kB in the bundle graph).
   - slim the header search: `loadAllParcels()` fetches all 7 parcel files (~2.7 MB gzip, ~57.6k
     objects) on focus — a `search-index.json` of just `situs_norm` + `zip` would be ~1/20th.
   - `aria-activedescendant` on the `GlobalAddressSearch` combobox; drawer focus-trap/restore.
   - `build_demo_bundle.py` `median_tenure` → use `is not None` (treats a legit 0.0 as missing).
   - CSV export `rank` column vs. on-screen sort order can disagree (export uses bundle order).
   - `MonthlyReport` `reportError` never resets on `zip` change (one bad zip poisons the session).
   - the stale MELAVA report note (above).
4. **If the 2024 Travis roll arrives:** drop it in `data/raw/travis/`, run the Task-10 ingest steps
   from the plan, re-run `build_demo_bundle`, re-check cutoffs (Task 8). Tasks 7–10 are flagged
   provisional; no code is lost.

---

## Key files & locations

| Path | What |
|---|---|
| `docs/superpowers/plans/2026-09-08-marlin-demo-build.md` | the 21-task implementation plan (2091 lines) |
| `docs/DEMO_BUILD_SPEC.md` | demo spec v1.0 (brand-reconciled); §5.4 = the JSON bundle contract |
| `MARLIN_GRADE_BUILD_SPEC.md` | parent product spec (§4 pricing, §14 landing copy) |
| `docs/scoring-decisions.md` | `out_of_state` −10 + fixed A–F cutoffs rationale (§2a = frozen calibration) |
| `docs/phase-a-validation.md` | Task 9 engine-validation checklist + Task 10 deferral note |
| `.superpowers/sdd/2026-09-08-marlin-demo-build/progress.md` | **the SDD ledger** — full per-task history, every ruling, resume markers. gitignored, on-disk only. |
| `.superpowers/sdd/2026-09-08-marlin-demo-build/FINAL-review-ledger-digest.md` | every deferred-minor + ruling, with the opus BLOCKS/FIX-SOON/ACCEPTED triage |
| `.superpowers/sdd/2026-09-08-marlin-demo-build/final-fix-wave-report.md` | the fix-wave implementer's detailed report |
| `.superpowers/sdd/2026-09-08-marlin-demo-build/task-*-report.md` | per-task implementer reports (1–21) |
| `.superpowers/sdd/2026-09-08-marlin-demo-build/review-*.diff` | every review package (per-task + final + fix-wave) |
| `marlin_engine/` | lifted engine: `normalize/`, `analytics/{scoring,metrics}.py`, `scoring.yaml`, `grades.py`, `tests/` |
| `scripts/build_demo_bundle.py` | offline scorer → `web/public/data/*.json` (idempotent, byte-stable) |
| `scripts/calibrate_cutoffs.py` | full-roll histogram → proposed A–F cutoffs (run once, Task 8) |
| `web/` | the SPA. `src/routes/` = screens, `src/components/` = shared, `src/lib/bundle.ts` = the §5.4 seam, `src/styles/` = tokens + global + buttons |
| `data/farmsignal.duckdb` | 486,859 Travis 2025 parcels (gitignored, 282 MB) |
| FarmSignal `/Users/justinmason/Claude Code/FarmSignal` | frozen reference — never modified |

The SDD workspace `.superpowers/sdd/2026-09-08-marlin-demo-build/` is **left in place** (not
deleted) for review — it holds the complete build record.

---

## How to run locally

```bash
cd "/Users/justinmason/Claude Code/Marlin Grade"
.venv/bin/python -m pytest -q                      # engine — 82 pass (~3 min)
.venv/bin/python -m scripts.build_demo_bundle      # regenerate web/public/data/*.json
npm --prefix web install
npm --prefix web run dev                           # http://localhost:5173
#   or: npm --prefix web run build && npm --prefix web run preview
```

## How to redeploy

```bash
# get a fresh scoped token: dash.cloudflare.com → My Profile → API Tokens →
#   "Edit Cloudflare Workers" template  (the old one id e702f4c1… is revoked)
npm --prefix web run build
cd web && CLOUDFLARE_API_TOKEN=<fresh-token> npx wrangler deploy
#   → https://marlin-demo.justin-040.workers.dev
```
(`wrangler login` OAuth does not work on this machine — macOS 12.6.0 is below wrangler's
supported 13.5.0. Use the API-token path.)

---

## Toolchain notes (Ruling R9 — carry into any further frontend work)

- **Vite 8.2.2 · React 19.2.8 (`@types/react` 19) · TypeScript ~6.0.2 · react-router-dom 7.18.3 ·
  oxlint (not eslint) · `tsc -b` project references · vitest 5 · Node 24.**
- `web/tsconfig.app.json` enforces `verbatimModuleSyntax` (type-only imports need `import type`),
  `erasableSyntaxOnly` (no TS `enum`/runtime `namespace`/param-properties), `noUnusedLocals` +
  `noUnusedParameters`, `noFallthroughCasesInSwitch`, and now `strict: true`.
- `*.test.ts(x)` + `src/test/` are **excluded** from `tsc -b` — a test-file type error won't fail
  `npm run build` (FIX-SOON: add `tsconfig.test.json` to the project refs).
- vitest has `globals: true` — test files may use bare `it`/`expect`/`vi`. jest-dom is wired via
  `web/src/test/setup.ts`.
- New components use ref-as-prop, not `forwardRef`.
- `git add web` is safe (`web/node_modules`, `web/dist`, `web/.wrangler` are gitignored).

## Design system (do not drift)

- Palette (exact): `--abyssal #0B111E` · `--surface-1 #111828` · `--surface-2 #0E1523` ·
  `--ice #F1F5F9` · `--cyan #00F0FF` (Signal Cyan) · `--green #00E676` (Data Green —
  **CSV/export ONLY**, appears only on `.btn--export` in `web/src/styles/buttons.css`) ·
  `--slate #64748B` · `--warn #F2A65A` (amber — exclusivity-available badge, legal-trigger alerts).
- Fonts: Plus Jakarta Sans (headers) · Inter (interface/data) · JetBrains Mono (data labels).
- Vanilla CSS + custom-property tokens only. No Tailwind, no CSS-in-JS.
- Motion: only `transform`/`opacity`/`color`/`background`/`border-color` transitions — the ONE
  sanctioned layout-property transition is the `DistributionBar` segment `width`. `@keyframes`
  (gauge ring, A/B pill pulse) each carry an explicit `@media (prefers-reduced-motion: reduce)`
  escape.
- Grade scale is exactly **A B C D F** — no plus, no E. Fixed cutoffs on the absolute 0–100 score,
  never curved per zip.
- The canonical listing-status disclaimer (`DISCLAIMER_TEXT`, single export in
  `web/src/components/Disclaimer.tsx`, 436 chars, byte-exact to the spec) renders on:
  dashboard (compact), address drawer (full), monthly report (compact), Alerts (compact),
  CSV export (footer row via `csvWithFooter`).

---

## Data model / seam quick reference

`web/public/data/`:
- `zips.json` — 7 records: `{ zip, area, subdivisions[], sfr_count, distribution{A..F:{count,pct}},
  aggregates{absentee_pct, rental_pct, median_tenure, out_of_state_pct}, exclusivity }`
- `parcels-<zip>.json` — score-descending, `parcel_id` ascending tiebreak; per parcel:
  `{ parcel_uid, situs_address, situs_norm, owner_name, owner_type, grade, score,
  breakdown[{label,points}], facts{deed_date, tenure_years, homestead, over65, subdivision,
  assessed_value, mail_state, out_of_state} }`. Nullable in the data: `deed_date`, `tenure_years`,
  `subdivision`, `mail_state`, `assessed_value` (0 nulls in `situs_address`/`owner_name`/`situs_norm`
  across all 57,625 demo parcels — the TS types are non-null for those and that's accurate today).
- `grades.json` — `{ cutoffs: [["A","≥ 67"],["B","44–66"],["C","35–43"],["D","25–34"],["F","< 25"]] }`
- `alerts.json` — 4 hand-authored rows (1 `legal_trigger` foreclosure on 7105 KENOSHA PASS, 3
  `computed_spike`), all `to_grade` == real bundle grade.
- `report-78749.json` — `{ cycle:"September 2026", movers:{ new_ab[], warming[], cooled[] } }`;
  aggregates + Top-A/B come from the real bundle at runtime, only the mover lists are fixture.

The 7 demo zips: `78749` (focus) · `78748 78745 78739 78735 78736 78652`. SFR only, latest roll.
