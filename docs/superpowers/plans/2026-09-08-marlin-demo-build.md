# Marlin Grade — Demo Build Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a public, navigable Marlin Grade demo for Wednesday 2026-09-10 — real A–F grades on real Southwest-Austin addresses (engine + Travis CAD data, scored offline into a static JSON bundle) presented in a dark "Deep Analytics" React SPA on Cloudflare.

**Architecture:** Two parts sharing one seam — the JSON bundle contract (§5.4 of the spec). **Part 1 (Python):** lift the FarmSignal scoring engine into an importable `marlin_engine` package, apply the `out_of_state` −10 change, add an A–F `grades` module, calibrate cutoffs against the full Travis roll, and score the 7 demo zips offline with `scripts/build_demo_bundle.py` → `web/public/data/*.json`. **Part 2 (React):** a Vite + React + TS SPA with a sticky-header / icon-sidebar / workspace layout, a circular grade gauge, a slide-out address drawer, and staged alerts/report screens, deployed to `*.workers.dev`.

**Tech Stack:** Python 3.11 · pandas · duckdb · pyyaml · rapidfuzz · pytest (engine). Vite · React 18 · TypeScript · React Router · vanilla CSS with custom-property tokens · Cloudflare Workers static-assets / Wrangler (frontend).

**Spec:** `docs/DEMO_BUILD_SPEC.md` (v1.0, brand-brief-reconciled). Parent product spec: `MARLIN_GRADE_BUILD_SPEC.md`. Brand: `Branding/Marlin brand brief - gemini.md` + `Branding/*.png`. Scoring decisions: `docs/scoring-decisions.md`. Data inventory: `data/README.md`.

## Global Constraints

- **Repo:** new git repo, `git init` in place at `/Users/justinmason/Claude Code/Marlin Grade/`. FarmSignal (`/Users/justinmason/Claude Code/FarmSignal`) is **frozen reference** — never modified.
- **Engine language:** all Python. Engine modules are **copied** (not submoduled) into `marlin_engine/`.
- **Grade scale:** exactly **A, B, C, D, F** — no plus, no E. Fixed cutoffs on the absolute 0–100 score, never curved per zip.
- **`out_of_state` weight:** **−10** (renamed from `out_of_state_additional: +10`).
- **Demo data architecture:** Approach A — no runtime backend. All scoring is offline; the SPA reads static JSON.
- **Bundled zips (7):** `78749` (focus) + `78748, 78745, 78739, 78735, 78736, 78652`. SFR parcels only (`is_sfr = true`).
- **Palette (exact — "Deep Analytics"):** `--abyssal #0B111E` · `--ice #F1F5F9` · `--cyan #00F0FF` (Signal Cyan) · `--green #00E676` (Data Green — **only** export/CSV & revenue/volume) · `--slate #64748B`.
- **Fonts:** Plus Jakarta Sans (headers/branding) · Inter (interface/data) · JetBrains Mono (data-label accents only).
- **Listing-status disclaimer** (verbatim, on every surface an address appears + every export): *"Marlin Grade estimates listing propensity from public county appraisal and related public records. It is a prediction, not a fact about any property or owner, and does not reflect MLS status — a graded address may already be listed, under contract, sold, or not for sale. Public-record details may be outdated or incorrect. Verify current status and ownership independently before outreach or ad spend. No listing or sale is guaranteed."*
- **No secrets in the repo.** No paid APIs in the demo path.
- **Commits:** conventional-commit prefixes (`feat:`, `test:`, `chore:`, `fix:`, `refactor:`). Commit at the end of every task. Do not `git push` or deploy until Task 21.
- **File size:** 800-line hard cap; prefer < 400. Many small focused files.

---

## File Structure

### Part 1 — `marlin_engine/` + `scripts/`

| File | Responsibility |
|---|---|
| `pyproject.toml` | package metadata, deps, pytest config |
| `marlin_engine/__init__.py` | package marker |
| `marlin_engine/normalize/__init__.py` | — |
| `marlin_engine/normalize/address.py` | `normalize_address()` — USPS suffix canon + unit strip (lifted verbatim) |
| `marlin_engine/normalize/owners.py` | `is_entity_owner()`, `entity_owner_mask()` (lifted verbatim) |
| `marlin_engine/analytics/__init__.py` | — |
| `marlin_engine/analytics/scoring.py` | `compute_score_breakdown()`, `compute_scores()`, `load_scoring_config()` — weighted-sum score 0–100 + explainability string. Lifted; config path fixed; `out_of_state` renamed. |
| `marlin_engine/analytics/metrics.py` | `compute_parcel_metrics()`, `compute_farm_aggregates()`, `FarmAggregates`, `fetch_prior_roll_year_snapshot()` — per-parcel flags + zip aggregates. Lifted; `run_compute_metrics` + DuckDB-write path dropped. |
| `marlin_engine/scoring.yaml` | Marlin scoring weights (copied from FarmSignal; `out_of_state: -10`) |
| `marlin_engine/grades.py` | `assign(score) -> Literal["A","B","C","D","F"]`, `CUTOFFS`, `cutoffs_for_display()` |
| `marlin_engine/ingest/__init__.py` | — (only if Task 10 runs) |
| `marlin_engine/ingest/base.py` | `CountyAdapter` ABC (lifted, only if Task 10 runs) |
| `marlin_engine/ingest/travis.py` | TCAD fixed-width adapter (lifted, only if Task 10 runs) |
| `marlin_engine/tests/…` | lifted FarmSignal tests, imports repointed |
| `scripts/build_demo_bundle.py` | offline: DuckDB → score 7 zips → emit `web/public/data/*.json` |
| `scripts/calibrate_cutoffs.py` | full-roll score histogram → proposed A–F cutoff values |
| `fixtures/alerts.json` | staged alerts-feed rows |
| `fixtures/report-78749.json` | staged monthly-report mover sections |
| `docs/phase-a-validation.md` | Phase A findings (Task 9) |

### Part 2 — `web/`

| File | Responsibility |
|---|---|
| `web/package.json`, `web/vite.config.ts`, `web/tsconfig.json` | scaffold |
| `web/wrangler.jsonc` | Cloudflare Workers static-assets config |
| `web/index.html` | root, font `<link>`s, `<title>` |
| `web/src/main.tsx` | React root + Router |
| `web/src/styles/tokens.css` | `:root` design tokens (palette, scale, radius, motion) |
| `web/src/styles/global.css` | reset, base type, font-family bindings |
| `web/src/assets/` | cropped brand PNGs + `marlin-mark.svg` (traced) |
| `web/src/lib/bundle.ts` | `useBundle(zip)` — fetch + cache the JSON bundle; TS types for the §5.4 contract |
| `web/src/lib/session.tsx` | fake-auth context (`user`, `tier`, `signIn()`) |
| `web/src/lib/csv.ts` | `downloadCsv(rows, filename)` |
| `web/src/components/AppShell.tsx` | sticky header + sidebar + `<Outlet/>` |
| `web/src/components/GlobalAddressSearch.tsx` | header typeahead → opens drawer |
| `web/src/components/SidebarNav.tsx` | icon nav |
| `web/src/components/UserBlock.tsx` | Palmer Holland identity block |
| `web/src/components/GradeGauge.tsx` | circular ring + letter + mono driver flags |
| `web/src/components/GradePill.tsx` | A/B glow, C–F recede |
| `web/src/components/DistributionBar.tsx` | A–F % bar |
| `web/src/components/AggregatePanel.tsx` | zip aggregates |
| `web/src/components/ProspectTable.tsx` | sortable ranked list |
| `web/src/components/FilterChips.tsx` | client-side filter state |
| `web/src/components/ExportCsvButton.tsx` | Data Green CSV export |
| `web/src/components/AddressDrawer.tsx` | right slide-out: gauge + triggers + facts + disclaimer |
| `web/src/components/SignalTriggers.tsx` | diverging +/− breakdown list |
| `web/src/components/FactsTable.tsx` | ownership/property facts |
| `web/src/components/Disclaimer.tsx` | canonical disclaimer text |
| `web/src/components/AlertFeed.tsx` | staged alert rows |
| `web/src/routes/Landing.tsx` | screen 1 |
| `web/src/routes/SignIn.tsx` | screen 2 |
| `web/src/routes/FarmPicker.tsx` | screen 3 |
| `web/src/routes/Dashboard.tsx` | screen 4 |
| `web/src/routes/Alerts.tsx` | screen 6 |
| `web/src/routes/MonthlyReport.tsx` | screen 7 |
| `web/src/routes/landing/PricingTable.tsx` | unified per-column plan table |
| `web/src/routes/landing/HowItWorks.tsx` | boxless 3-step |

---

# PART 1 — ENGINE & DATA

## Task 1: Repo scaffold + Python tooling

**Files:**
- Create: `.gitignore`, `pyproject.toml`, `marlin_engine/__init__.py`, `marlin_engine/normalize/__init__.py`, `marlin_engine/analytics/__init__.py`, `marlin_engine/tests/__init__.py`, `README.md`
- Commit (pre-existing, currently untracked): `MARLIN_GRADE_BUILD_SPEC.md`, `docs/` (spec, plan, teardown, scoring-decisions, session log), `Branding/`, `data/README.md`, `data/.gitignore`, the two `Marlin Grade - *.md` Gemini session files

**Interfaces:**
- Consumes: nothing.
- Produces: an importable `marlin_engine` package; `pytest` runnable from repo root; a git repo with the design docs + brand assets committed.

- [ ] **Step 1: `git init` and confirm we're not inside the home repo's index**

```bash
cd "/Users/justinmason/Claude Code/Marlin Grade"
git init
git config core.excludesfile ''      # ignore any global ignore surprises
git rev-parse --show-toplevel         # MUST print .../Marlin Grade, not /Users/justinmason
```
If `--show-toplevel` prints the home directory, `git init` did not take — stop and resolve before continuing.

- [ ] **Step 2: Write `.gitignore`**

```gitignore
# Python
__pycache__/
*.pyc
.venv/
.pytest_cache/
*.egg-info/
# Data (large, not versioned)
data/*.duckdb
data/raw/
# Superpowers scratch
.superpowers/
# Node / build
web/node_modules/
web/dist/
web/.wrangler/
.DS_Store
```

- [ ] **Step 3: Write `pyproject.toml`**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "marlin-engine"
version = "0.1.0"
description = "Marlin Grade scoring engine (ported from FarmSignal) + demo bundle builder."
requires-python = ">=3.11"
dependencies = [
    "duckdb>=1.0",
    "pandas>=2.2",
    "pyyaml>=6.0",
    "rapidfuzz>=3.9",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-cov>=5.0"]

[tool.hatch.build.targets.wheel]
packages = ["marlin_engine"]

[tool.pytest.ini_options]
testpaths = ["marlin_engine/tests"]
```

- [ ] **Step 4: Create the empty package markers**

`marlin_engine/__init__.py`, `marlin_engine/normalize/__init__.py`, `marlin_engine/analytics/__init__.py`, `marlin_engine/tests/__init__.py` — all empty files. `README.md` — one paragraph pointing at `docs/DEMO_BUILD_SPEC.md`.

- [ ] **Step 5: Install and verify**

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -c "import marlin_engine; print('ok')"
pytest -q            # expect: "no tests ran"
```
Expected: `ok`; pytest exits 5 ("no tests collected") — acceptable at this stage.

- [ ] **Step 6: First commit — the pre-existing design docs & brand assets**

```bash
git add MARLIN_GRADE_BUILD_SPEC.md "Marlin Grade - Gemini handoff session.md" \
        "Marlin Grade - full Gemini session.md" docs/ Branding/ data/README.md data/.gitignore
git status                     # confirm data/*.duckdb and .superpowers/ are NOT staged (gitignored)
git commit -m "chore: initial commit — build spec, demo spec + plan, brand brief, data inventory"
```

- [ ] **Step 7: Second commit — the package scaffold**

```bash
git add .gitignore pyproject.toml marlin_engine/ README.md
git commit -m "chore: scaffold marlin_engine package + tooling"
```

---

## Task 2: Lift `normalize/` modules + their tests

**Files:**
- Create: `marlin_engine/normalize/address.py`, `marlin_engine/normalize/owners.py`, `marlin_engine/tests/test_normalize_address.py`, `marlin_engine/tests/test_normalize_owners.py`

**Interfaces:**
- Consumes: nothing (leaf modules).
- Produces:
  - `normalize_address(addr: str) -> str`
  - `is_entity_owner(owner_name: str | None) -> bool`
  - `entity_owner_mask(owner_names: pd.Series) -> pd.Series`

- [ ] **Step 1: Copy the two source modules verbatim**

```bash
SRC="/Users/justinmason/Claude Code/FarmSignal/src/farmsignal"
cp "$SRC/normalize/address.py"  marlin_engine/normalize/address.py
cp "$SRC/normalize/owners.py"   marlin_engine/normalize/owners.py
```
No content edits — neither file imports from `farmsignal.*` (verified: both only import `re` and `pandas`).

- [ ] **Step 2: Copy the two test files and repoint imports**

```bash
ST="/Users/justinmason/Claude Code/FarmSignal/tests"
cp "$ST/test_normalize_address.py" marlin_engine/tests/test_normalize_address.py
cp "$ST/test_normalize_owners.py"  marlin_engine/tests/test_normalize_owners.py
```
In both copied test files, replace `from farmsignal.normalize.` → `from marlin_engine.normalize.`.

- [ ] **Step 3: Run the lifted tests**

```bash
pytest marlin_engine/tests/test_normalize_address.py marlin_engine/tests/test_normalize_owners.py -q
```
Expected: all PASS (these modules are pure and were green in FarmSignal).

- [ ] **Step 4: Commit**

```bash
git add marlin_engine/normalize marlin_engine/tests
git commit -m "feat: lift normalize/address + normalize/owners from FarmSignal"
```

---

## Task 3: Lift `analytics/scoring.py` + config, fix the config path

**Files:**
- Create: `marlin_engine/analytics/scoring.py`, `marlin_engine/scoring.yaml`, `marlin_engine/tests/test_analytics_scoring.py`
- Modify (on copy): `marlin_engine/analytics/scoring.py` lines 11–12 (config path constants)

**Interfaces:**
- Consumes: `marlin_engine/scoring.yaml`.
- Produces:
  - `load_scoring_config(path: Path = _DEFAULT_CONFIG_PATH) -> dict`
  - `compute_score_breakdown(df: pd.DataFrame, config: dict | None = None) -> tuple[pd.Series, pd.Series, pd.Series]` — returns `(score, band, breakdown)`; `breakdown[i]` is a pipe-delimited string like `"Tenure 9+ yrs:+25|Likely rental:-20"`.
  - `compute_scores(df, config=None) -> tuple[pd.Series, pd.Series]`
  - Required input columns on `df`: `tenure_years, absentee, out_of_state, likely_rental, senior_longtenure, owner_is_entity` (+ optional `homestead_dropped, over65_newly_filed, ag_exemption_rollback, recent_sale, recent_permit_activity, tax_delinquent`).

- [ ] **Step 1: Copy the source module + config**

```bash
SRC="/Users/justinmason/Claude Code/FarmSignal/src/farmsignal"
cp "$SRC/analytics/scoring.py" marlin_engine/analytics/scoring.py
cp "/Users/justinmason/Claude Code/FarmSignal/config/scoring.yaml" marlin_engine/scoring.yaml
```

- [ ] **Step 2: Fix the config-path constants in `marlin_engine/analytics/scoring.py`**

Replace lines 11–12:
```python
_CONFIG_DIR = Path(__file__).resolve().parents[3] / "config"
_DEFAULT_CONFIG_PATH = _CONFIG_DIR / "scoring.yaml"
```
with:
```python
# scoring.yaml sits at the package root: marlin_engine/scoring.yaml
_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "scoring.yaml"
```
(`parents[1]` of `marlin_engine/analytics/scoring.py` is `marlin_engine/`.)

- [ ] **Step 3: Copy the test file and repoint imports**

```bash
cp "/Users/justinmason/Claude Code/FarmSignal/tests/test_analytics_scoring.py" \
   marlin_engine/tests/test_analytics_scoring.py
```
Replace `from farmsignal.analytics.scoring` → `from marlin_engine.analytics.scoring`.

- [ ] **Step 4: Run the lifted scoring tests**

```bash
pytest marlin_engine/tests/test_analytics_scoring.py -q
```
Expected: all PASS **except** any test asserting on the `out_of_state` weight (still `+10` here — Task 4 flips it). If such a test fails now, note the test name; do not fix it in this task.

- [ ] **Step 5: Commit**

```bash
git add marlin_engine/analytics/scoring.py marlin_engine/scoring.yaml marlin_engine/tests/test_analytics_scoring.py
git commit -m "feat: lift analytics/scoring + scoring.yaml, package-local config path"
```

---

## Task 4: Apply the `out_of_state` −10 change

**Files:**
- Modify: `marlin_engine/scoring.yaml`, `marlin_engine/analytics/scoring.py`
- Modify/Create: `marlin_engine/tests/test_analytics_scoring.py` (fix/add the `out_of_state` expectation)

**Interfaces:**
- Consumes: Task 3's `compute_score_breakdown`.
- Produces: no signature change; `out_of_state=True` now contributes **−10** and the breakdown label key is `out_of_state`.

- [ ] **Step 1: Write the failing test**

Add to `marlin_engine/tests/test_analytics_scoring.py`:
```python
def test_out_of_state_now_subtracts_ten() -> None:
    df = pd.DataFrame([_row(out_of_state=True)])
    scores, bands, breakdown = compute_score_breakdown(df, load_scoring_config())
    assert scores.iloc[0] == 0.0                     # clipped at 0 (−10 → 0)
    assert "Out-of-state:-10" in breakdown.iloc[0]

def test_out_of_state_pulls_a_borderline_parcel_down() -> None:
    base = pd.DataFrame([_row(tenure_years=9.0)])                 # +25 → 25
    oos  = pd.DataFrame([_row(tenure_years=9.0, out_of_state=True)])  # +25 −10 → 15
    s_base, _ = compute_scores(base, load_scoring_config())
    s_oos, _  = compute_scores(oos, load_scoring_config())
    assert s_base.iloc[0] - s_oos.iloc[0] == pytest.approx(10.0)
```
If a pre-existing test asserts `out_of_state` adds `+10` (from the FarmSignal lift), update its expected value to the −10 result now.

- [ ] **Step 2: Run to verify it fails**

```bash
pytest marlin_engine/tests/test_analytics_scoring.py -q -k out_of_state
```
Expected: FAIL — current config still has `out_of_state_additional: 10` and the breakdown key is `out_of_state_additional`.

- [ ] **Step 3: Edit `marlin_engine/scoring.yaml`**

Under `weights:`, replace:
```yaml
  out_of_state_additional: 10
```
with:
```yaml
  # Decision (docs/scoring-decisions.md §1): an out-of-state, non-homestead SFR
  # owner is a rental-investor profile — less motivated to sell. Was +10.
  out_of_state: -10
```

- [ ] **Step 4: Edit `marlin_engine/analytics/scoring.py`**

(a) In `_SIGNAL_LABELS`, rename the key:
```python
    "out_of_state_additional": "Out-of-state",
```
→
```python
    "out_of_state": "Out-of-state",
```
(b) In the `contributions` DataFrame constructor, rename the entry (the multiplied column is already `df["out_of_state"]`):
```python
            "out_of_state_additional": weights["out_of_state_additional"] * df["out_of_state"],
```
→
```python
            "out_of_state": weights["out_of_state"] * df["out_of_state"],
```

- [ ] **Step 5: Run the full scoring test module**

```bash
pytest marlin_engine/tests/test_analytics_scoring.py -q
```
Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add marlin_engine/scoring.yaml marlin_engine/analytics/scoring.py marlin_engine/tests/test_analytics_scoring.py
git commit -m "feat: flip out_of_state weight +10 -> -10 and rename key"
```

---

## Task 5: Lift `analytics/metrics.py` (per-parcel flags + aggregates)

**Files:**
- Create: `marlin_engine/analytics/metrics.py`, `marlin_engine/tests/test_analytics_metrics.py`, `marlin_engine/tests/test_metrics.py`
- Modify (on copy): remove `run_compute_metrics`, `_METRICS_UPDATE_COLUMNS`, and the `from farmsignal.db import get_connection` import from `metrics.py`

**Interfaces:**
- Consumes: `marlin_engine.analytics.scoring.compute_score_breakdown`, `marlin_engine.normalize.address.normalize_address`, `marlin_engine.normalize.owners.entity_owner_mask`.
- Produces:
  - `compute_parcel_metrics(df: pd.DataFrame, prior: pd.DataFrame | None = None) -> pd.DataFrame` — adds `owner_is_entity, tenure_years, absentee, out_of_state, senior_longtenure, likely_rental, recent_sale, data_gap` always; adds `homestead_dropped, over65_newly_filed, ag_exemption_rollback` only when `prior` is a non-empty frame with columns `parcel_id, over65_exempt, homestead, land_state_cd`.
  - `compute_farm_aggregates(df: pd.DataFrame) -> FarmAggregates` (frozen dataclass; fields per the source).
  - `fetch_prior_roll_year_snapshot(con, county: str, parcel_ids: list[str], prior_roll_year: int) -> pd.DataFrame`.

- [ ] **Step 1: Copy the source module**

```bash
cp "/Users/justinmason/Claude Code/FarmSignal/src/farmsignal/analytics/metrics.py" \
   marlin_engine/analytics/metrics.py
```

- [ ] **Step 2: Repoint imports and strip the DuckDB write path**

In `marlin_engine/analytics/metrics.py`:
- Replace the three `from farmsignal.` imports with `from marlin_engine.` equivalents.
- **Delete** `from farmsignal.db import get_connection` (only `run_compute_metrics` used it).
- **Delete** the `_METRICS_UPDATE_COLUMNS = [...]` list and the entire `run_compute_metrics(...)` function (lines from `_METRICS_UPDATE_COLUMNS` to end of file). `fetch_prior_roll_year_snapshot` **stays** (it takes an already-open `con`, imports nothing).
- Keep `compute_parcel_metrics`, `fetch_prior_roll_year_snapshot`, `FarmAggregates`, `compute_farm_aggregates`, and all `compute_*` helper functions.

- [ ] **Step 3: Copy both metrics test files, repoint, prune**

```bash
cp "/Users/justinmason/Claude Code/FarmSignal/tests/test_analytics_metrics.py" marlin_engine/tests/
cp "/Users/justinmason/Claude Code/FarmSignal/tests/test_metrics.py" marlin_engine/tests/
```
- Repoint `from farmsignal.` → `from marlin_engine.` in both.
- **Delete any test that references `run_compute_metrics`** (it needed a DuckDB file + the write-back path we removed). Note their names in the commit body.

- [ ] **Step 4: Run**

```bash
pytest marlin_engine/tests/test_analytics_metrics.py marlin_engine/tests/test_metrics.py -q
```
Expected: all remaining tests PASS.

- [ ] **Step 5: Full suite green**

```bash
pytest -q
```
Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add marlin_engine/analytics/metrics.py marlin_engine/tests
git commit -m "feat: lift analytics/metrics (parcel flags + aggregates), drop DuckDB write path"
```

---

## Task 6: `grades.py` — score → A–F

**Files:**
- Create: `marlin_engine/grades.py`, `marlin_engine/tests/test_grades.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `CUTOFFS: dict[str, int]` — lower-bound score for each of `"A","B","C","D"` (F is the implicit floor). Placeholder values here; **Task 8 overwrites them** with the calibrated numbers.
  - `assign(score: float) -> str` — returns `"A"|"B"|"C"|"D"|"F"`. Pure function of the clipped 0–100 score; inclusive lower bounds; a score exactly on a boundary takes the **higher** grade; evaluated A→F.
  - `assign_series(scores: pd.Series) -> pd.Series`
  - `cutoffs_for_display() -> list[tuple[str, str]]` — e.g. `[("A", "≥ 78"), ("B", "62–77"), …, ("F", "< 20")]` for the UI legend / `grades.json`.

- [ ] **Step 1: Write the failing tests**

```python
# marlin_engine/tests/test_grades.py
from __future__ import annotations
import pandas as pd
from marlin_engine.grades import assign, assign_series, CUTOFFS, cutoffs_for_display

def test_each_band_returns_its_letter() -> None:
    assert assign(CUTOFFS["A"]) == "A"
    assert assign(CUTOFFS["A"] - 1) == "B"
    assert assign(CUTOFFS["B"]) == "B"
    assert assign(CUTOFFS["C"]) == "C"
    assert assign(CUTOFFS["D"]) == "D"
    assert assign(CUTOFFS["D"] - 1) == "F"

def test_boundary_takes_higher_grade() -> None:
    assert assign(CUTOFFS["B"]) == "B"      # exactly on B's floor -> B, not C

def test_clip_range() -> None:
    assert assign(0) == "F"
    assert assign(100) == "A"
    assert assign(-5) == "F"                # defensive: below 0
    assert assign(150) == "A"               # defensive: above 100

def test_assign_series_matches_scalar() -> None:
    s = pd.Series([0, 40, 70, 95])
    assert list(assign_series(s)) == [assign(v) for v in s]

def test_display_has_five_bands_in_order() -> None:
    disp = cutoffs_for_display()
    assert [d[0] for d in disp] == ["A", "B", "C", "D", "F"]
```

- [ ] **Step 2: Run to verify it fails**

```bash
pytest marlin_engine/tests/test_grades.py -q
```
Expected: FAIL — `marlin_engine.grades` does not exist.

- [ ] **Step 3: Implement `marlin_engine/grades.py`**

```python
"""Fixed A–F letter grade from the absolute 0–100 Marlin score.

Decision (docs/scoring-decisions.md §2): fixed cutoffs on the absolute score,
never curved per zip. Grades are exactly A, B, C, D, F — no plus, no E.

CUTOFFS below are PLACEHOLDERS. Task 8 (scripts/calibrate_cutoffs.py) replaces
them with values read off the full-Travis-roll score histogram at the anchors
A≈top 3%, B≈next 12%, C≈next 25%, D≈next 35%, F≈bottom 25%.
"""
from __future__ import annotations

import pandas as pd

# Lower-bound score for each band. F is the implicit floor (anything below D).
CUTOFFS: dict[str, int] = {"A": 75, "B": 55, "C": 35, "D": 18}

_ORDER = ("A", "B", "C", "D")


def assign(score: float) -> str:
    s = max(0.0, min(100.0, float(score)))
    for letter in _ORDER:
        if s >= CUTOFFS[letter]:
            return letter
    return "F"


def assign_series(scores: pd.Series) -> pd.Series:
    return scores.map(assign)


def cutoffs_for_display() -> list[tuple[str, str]]:
    a, b, c, d = (CUTOFFS[k] for k in _ORDER)
    return [
        ("A", f"≥ {a}"),
        ("B", f"{b}–{a - 1}"),
        ("C", f"{c}–{b - 1}"),
        ("D", f"{d}–{c - 1}"),
        ("F", f"< {d}"),
    ]
```

- [ ] **Step 4: Run to verify it passes**

```bash
pytest marlin_engine/tests/test_grades.py -q
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add marlin_engine/grades.py marlin_engine/tests/test_grades.py
git commit -m "feat: add grades.assign (A-F from 0-100 score, placeholder cutoffs)"
```

---

## Task 7: `scripts/build_demo_bundle.py` — offline scorer → JSON bundle

**Files:**
- Create: `scripts/build_demo_bundle.py`, `marlin_engine/tests/test_build_demo_bundle.py`

**Interfaces:**
- Consumes: `compute_parcel_metrics`, `compute_score_breakdown`, `compute_farm_aggregates`, `grades.assign_series`, `grades.cutoffs_for_display`. Reads `data/farmsignal.duckdb` (read-only).
- Produces these files in `web/public/data/` (contract = spec §5.4):
  - `zips.json`: `[{ "zip", "area", "subdivisions": [str], "sfr_count", "distribution": {"A": {"pct","count"}, …}, "aggregates": {"absentee_pct","rental_pct","median_tenure","out_of_state_pct"}, "exclusivity": "available"|"held"|"monitored" }]`
  - `parcels-<zip>.json`: `[{ "parcel_uid", "situs_address", "situs_norm", "owner_name", "owner_type": "occupant"|"entity", "grade", "score", "breakdown": [{"label","points"}], "facts": {"deed_date","tenure_years","homestead","over65","subdivision","assessed_value","mail_state","out_of_state"} }]`
  - `grades.json`: `{ "cutoffs": [["A","≥ 78"], …] }`
  - Also copies `fixtures/alerts.json` and `fixtures/report-*.json` into `web/public/data/` **if present** (created in Task 20).

- [ ] **Step 1: Write the integration test (skips cleanly if the DB is absent)**

```python
# marlin_engine/tests/test_build_demo_bundle.py
from __future__ import annotations
import json
from pathlib import Path
import pytest

DB = Path("data/farmsignal.duckdb")
pytestmark = pytest.mark.skipif(not DB.exists(), reason="demo DuckDB not present")

def test_bundle_builds_and_has_expected_shape(tmp_path: Path) -> None:
    from scripts.build_demo_bundle import build
    out = tmp_path / "data"
    build(db_path=DB, out_dir=out)

    zips = json.loads((out / "zips.json").read_text())
    assert {z["zip"] for z in zips} == {"78749","78748","78745","78739","78735","78736","78652"}
    focus = next(z for z in zips if z["zip"] == "78749")
    assert focus["sfr_count"] > 9000
    assert set(focus["distribution"]) == {"A","B","C","D","F"}
    assert sum(b["pct"] for b in focus["distribution"].values()) == pytest.approx(100, abs=1.0)

    parcels = json.loads((out / "parcels-78749.json").read_text())
    assert len(parcels) == focus["sfr_count"]
    p = parcels[0]
    assert p["grade"] in {"A","B","C","D","F"}
    assert 0 <= p["score"] <= 100
    assert isinstance(p["breakdown"], list)
    assert p["owner_type"] in {"occupant","entity"}

    grades = json.loads((out / "grades.json").read_text())
    assert [c[0] for c in grades["cutoffs"]] == ["A","B","C","D","F"]
```

- [ ] **Step 2: Run to verify it fails**

```bash
pytest marlin_engine/tests/test_build_demo_bundle.py -q
```
Expected: FAIL — `scripts.build_demo_bundle` does not exist (or SKIP if you're on a machine without the DB — then run it where the DB is present).

- [ ] **Step 3: Implement `scripts/build_demo_bundle.py`**

```python
"""Offline: score the 7 demo zips from the FarmSignal DuckDB into a static JSON
bundle for the SPA. Approach A — no runtime backend. Idempotent; no DB writes.

Usage:  python -m scripts.build_demo_bundle
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import duckdb
import pandas as pd

from marlin_engine.analytics.metrics import (
    compute_parcel_metrics,
    compute_farm_aggregates,
    fetch_prior_roll_year_snapshot,
)
from marlin_engine.analytics.scoring import compute_score_breakdown, load_scoring_config
from marlin_engine import grades

DEMO_ZIPS = ["78749", "78748", "78745", "78739", "78735", "78736", "78652"]
FOCUS_ZIP = "78749"

# Static area labels (situs_city is only 43% populated). Subdivisions are read
# live from the data (top N by parcel count).
ZIP_AREA = {
    "78749": "Southwest Austin",
    "78748": "Far South Austin",
    "78745": "South Austin",
    "78739": "Circle C Ranch",
    "78735": "West Oak Hill",
    "78736": "Oak Hill",
    "78652": "Manchaca",
}
# Staged for the demo (spec §5.2). 78749 is the monitored/exclusivity-available one.
ZIP_EXCLUSIVITY = {z: ("available" if z == FOCUS_ZIP else "held") for z in DEMO_ZIPS}
ZIP_EXCLUSIVITY[FOCUS_ZIP] = "available"

_DEFAULT_DB = Path("data/farmsignal.duckdb")
_DEFAULT_OUT = Path("web/public/data")
_FIXTURES = Path("fixtures")


def _parse_breakdown(s: str | None) -> list[dict]:
    """'Tenure 9+ yrs:+25|Likely rental:-20' -> [{'label':..., 'points':int}]."""
    if not s:
        return []
    out = []
    for chunk in s.split("|"):
        label, _, pts = chunk.rpartition(":")
        out.append({"label": label, "points": int(pts)})
    return out


def _load_demo_parcels(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    placeholders = ", ".join("?" for _ in DEMO_ZIPS)
    df = con.execute(
        f"""
        SELECT * FROM parcels
        WHERE situs_zip IN ({placeholders})
          AND is_sfr = TRUE
          AND roll_year = (SELECT MAX(roll_year) FROM parcels)
        """,
        DEMO_ZIPS,
    ).fetchdf()
    return df


def _score(df: pd.DataFrame, con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    # Prior roll year (Task 10): if a second roll_year exists, diff against it so
    # homestead_dropped / over65_newly_filed / ag_exemption_rollback activate.
    years = con.execute("SELECT DISTINCT roll_year FROM parcels ORDER BY roll_year DESC").fetchall()
    prior = None
    if len(years) >= 2:
        prior_year = years[1][0]
        prior = fetch_prior_roll_year_snapshot(
            con, "travis", df["parcel_id"].tolist(), prior_year
        )
    metrics = compute_parcel_metrics(df, prior)
    score, band, breakdown = compute_score_breakdown(metrics, load_scoring_config())
    metrics = metrics.assign(score=score, score_breakdown=breakdown)
    metrics["grade"] = grades.assign_series(score)
    return metrics


def _zip_record(zip_code: str, g: pd.DataFrame) -> dict:
    agg = compute_farm_aggregates(g.assign(score_band=None))
    n = len(g)
    dist = {}
    for letter in ("A", "B", "C", "D", "F"):
        c = int((g["grade"] == letter).sum())
        dist[letter] = {"count": c, "pct": round(100 * c / n, 1) if n else 0.0}
    subs = (
        g["subdivision_canon"].dropna().value_counts().head(4).index.tolist()
    )
    return {
        "zip": zip_code,
        "area": ZIP_AREA[zip_code],
        "subdivisions": subs,
        "sfr_count": n,
        "distribution": dist,
        "aggregates": {
            "absentee_pct": agg.absentee_pct,
            "rental_pct": agg.likely_rental_pct,
            "median_tenure": round(agg.median_tenure_years, 1) if agg.median_tenure_years else None,
            "out_of_state_pct": agg.out_of_state_pct,
        },
        "exclusivity": ZIP_EXCLUSIVITY[zip_code],
    }


def _parcel_record(row: pd.Series) -> dict:
    from marlin_engine.normalize.address import normalize_address
    return {
        "parcel_uid": f"travis-{row['parcel_id']}",
        "situs_address": row["situs_address"],
        "situs_norm": normalize_address(row["situs_address"] or ""),
        "owner_name": row["owner_name"],
        "owner_type": "entity" if bool(row["owner_is_entity"]) else "occupant",
        "grade": row["grade"],
        "score": float(row["score"]),
        "breakdown": _parse_breakdown(row["score_breakdown"]),
        "facts": {
            "deed_date": str(row["deed_date"]) if pd.notna(row["deed_date"]) else None,
            "tenure_years": round(float(row["tenure_years"]), 1) if pd.notna(row["tenure_years"]) else None,
            "homestead": bool(row["homestead"]),
            "over65": bool(row["over65_exempt"]),
            "subdivision": row["subdivision_canon"],
            "assessed_value": int(row["assessed_value"]) if pd.notna(row["assessed_value"]) else None,
            "mail_state": row["mail_state"],
            "out_of_state": bool(row["out_of_state"]),
        },
    }


def build(db_path: Path = _DEFAULT_DB, out_dir: Path = _DEFAULT_OUT) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        scored = _score(_load_demo_parcels(con), con)
    finally:
        con.close()

    zips = []
    for zip_code in DEMO_ZIPS:
        g = scored[scored["situs_zip"] == zip_code]
        zips.append(_zip_record(zip_code, g))
        parcels = [_parcel_record(r) for _, r in g.sort_values("score", ascending=False).iterrows()]
        (out_dir / f"parcels-{zip_code}.json").write_text(json.dumps(parcels))
    (out_dir / "zips.json").write_text(json.dumps(zips, indent=2))
    (out_dir / "grades.json").write_text(json.dumps({"cutoffs": grades.cutoffs_for_display()}, indent=2))

    for fx in ("alerts.json", "report-78749.json"):
        src = _FIXTURES / fx
        if src.exists():
            shutil.copy(src, out_dir / fx)

    print(f"wrote bundle for {len(DEMO_ZIPS)} zips to {out_dir}")


if __name__ == "__main__":
    build()
```

- [ ] **Step 4: Run the test**

```bash
pytest marlin_engine/tests/test_build_demo_bundle.py -q
```
Expected: PASS (on a machine with `data/farmsignal.duckdb`).

- [ ] **Step 5: Generate the bundle for real and eyeball it**

```bash
python -m scripts.build_demo_bundle
python -c "import json; z=json.load(open('web/public/data/zips.json')); print([(x['zip'], x['sfr_count'], x['distribution']['A']['pct']) for x in z])"
```
Sanity: 78749 ≈ 10,423 SFR; A% is single digits (with placeholder cutoffs it may be off — Task 8 fixes calibration).

- [ ] **Step 6: Commit (script + generated bundle)**

```bash
git add scripts/build_demo_bundle.py marlin_engine/tests/test_build_demo_bundle.py web/public/data
git commit -m "feat: build_demo_bundle.py — score 7 demo zips into static JSON"
```

---

## Task 8: Calibrate A–F cutoffs against the full Travis roll

**Files:**
- Create: `scripts/calibrate_cutoffs.py`
- Modify: `marlin_engine/grades.py` (`CUTOFFS` values), `marlin_engine/tests/test_grades.py` (update any hard-coded expectations), `web/public/data/*` (regenerated)

**Interfaces:**
- Consumes: `compute_parcel_metrics`, `compute_score_breakdown`. Reads `data/farmsignal.duckdb`.
- Produces: `scripts/calibrate_cutoffs.py` prints a histogram + proposed cutoffs; `grades.CUTOFFS` is updated with the frozen values.

- [ ] **Step 1: Implement `scripts/calibrate_cutoffs.py`**

```python
"""Score every Travis SFR parcel (latest roll) and propose A–F cutoffs at the
spec §10.1 anchors. Run once; copy the printed values into marlin_engine/grades.py.

Usage:  python -m scripts.calibrate_cutoffs
"""
from __future__ import annotations

from pathlib import Path

import duckdb
import numpy as np

from marlin_engine.analytics.metrics import compute_parcel_metrics
from marlin_engine.analytics.scoring import compute_score_breakdown, load_scoring_config

# anchors: cumulative share from the TOP. A = top 3%, B = next 12% (top 15), etc.
ANCHORS = {"A": 0.03, "B": 0.15, "C": 0.40, "D": 0.75}  # F = remainder


def main(db_path: Path = Path("data/farmsignal.duckdb")) -> None:
    con = duckdb.connect(str(db_path), read_only=True)
    df = con.execute(
        "SELECT * FROM parcels WHERE is_sfr = TRUE "
        "AND roll_year = (SELECT MAX(roll_year) FROM parcels)"
    ).fetchdf()
    con.close()

    metrics = compute_parcel_metrics(df, prior=None)          # single-roll: diff signals = 0
    score, _, _ = compute_score_breakdown(metrics, load_scoring_config())
    s = np.sort(score.to_numpy())[::-1]                        # descending

    print(f"n = {len(s)}   min={s.min():.0f}  median={np.median(s):.0f}  max={s.max():.0f}")
    # histogram
    hist, edges = np.histogram(s, bins=range(0, 105, 5))
    for h, lo in zip(hist, edges[:-1]):
        print(f"{lo:>3}-{lo+4:<3} | {'#' * (h * 60 // hist.max())} {h}")

    cut = {}
    for letter, top_share in ANCHORS.items():
        idx = int(top_share * len(s)) - 1
        cut[letter] = int(round(s[idx]))
    # snap so bands strictly decrease
    for a, b in (("A", "B"), ("B", "C"), ("C", "D")):
        if cut[a] <= cut[b]:
            cut[a] = cut[b] + 1
    print("\nproposed CUTOFFS =", cut)
    print("copy into marlin_engine/grades.py, then re-run build_demo_bundle + update test_grades expectations")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it and record the output**

```bash
python -m scripts.calibrate_cutoffs | tee /tmp/marlin-cutoffs.txt
```
Read the histogram. If there is a natural gap/cluster within ±2 points of a proposed cutoff, nudge that cutoff to the gap. Write the final dict down.

- [ ] **Step 3: Freeze the values in `marlin_engine/grades.py`**

Replace the placeholder line:
```python
CUTOFFS: dict[str, int] = {"A": 75, "B": 55, "C": 35, "D": 18}
```
with the calibrated dict from Step 2, e.g.:
```python
# Frozen 2026-09-09 from scripts/calibrate_cutoffs.py over 349k Travis SFR parcels
# (single-roll). Anchors A≈3% / B≈15% / C≈40% / D≈75%. See docs/phase-a-validation.md.
CUTOFFS: dict[str, int] = {"A": <a>, "B": <b>, "C": <c>, "D": <d>}
```

- [ ] **Step 4: Update `test_grades.py` and re-run**

Adjust any test that hard-codes a numeric expectation (the `CUTOFFS[...]`-relative tests keep working as written).
```bash
pytest marlin_engine/tests/test_grades.py -q
```
Expected: PASS.

- [ ] **Step 5: Regenerate the bundle**

```bash
python -m scripts.build_demo_bundle
python -c "import json; z=json.load(open('web/public/data/zips.json')); [print(x['zip'], x['distribution']) for x in z]"
```
Sanity: across the 7 SW-Austin zips A+B is a modest minority (these are stable owner-occupied areas — expect more A/B than the county average, that's fine and on-narrative).

- [ ] **Step 6: Commit**

```bash
git add scripts/calibrate_cutoffs.py marlin_engine/grades.py marlin_engine/tests/test_grades.py web/public/data
git commit -m "feat: freeze A-F cutoffs from full Travis-roll score distribution"
```

---

## Task 9: Phase A engine-correctness validation on 78749

**Files:**
- Create: `docs/phase-a-validation.md`
- Modify: `marlin_engine/*` only if a real bug is found (each fix = its own test + commit)

**Interfaces:**
- Consumes: the generated bundle + direct DuckDB queries.
- Produces: `docs/phase-a-validation.md` — a checklist with PASS/FAIL + notes, plus links to any fix commits.

This task is validation, not feature work. Budget ~half a day. It is **not** red/green/refactor — it is "run the checks, write findings, fix what's broken."

- [ ] **Step 1: Create `docs/phase-a-validation.md` with the checklist skeleton**

```markdown
# Phase A — engine correctness on ZIP 78749 (spec §10.1)

Roll year: <n>   ·   Cutoffs: <CUTOFFS>   ·   Bundle built: <date>

| Check | Method | Expected | Result | Notes |
|---|---|---|---|---|
| Entity owners flagged | query owner_name LIKE '% LLC%' etc. vs owner_is_entity | all match | | |
| Known rentals → likely_rental | operator's known-rental addresses | flagged | | |
| Long-tenured owners → tenure + bonus | deed_date < 2005 sample | tenure_years correct, +25/+10/bonus | | |
| out_of_state −10 applied | mail_state NOT IN ('TX','') sample | score 10 lower than same profile in-state | | |
| recent_sale de-prioritises | jan1_owner_name != owner_name, tenure < 2 | recent_sale True, −25 | | |
| Zip aggregates believable | zips.json 78749 aggregates | absentee ~25–35%, median tenure ~9–13 yr | | |
| Address→parcel resolves | 10 hand-picked 78749 addresses via situs_norm | exact 1 match each | | |
| Grade distribution sane | zips.json 78749 distribution | A single digits, F non-trivial | | |
```

- [ ] **Step 2: Run the queries**

For each row, run a DuckDB query or inspect `web/public/data/parcels-78749.json`. Example:
```bash
python - <<'PY'
import duckdb
c = duckdb.connect("data/farmsignal.duckdb", read_only=True)
print(c.execute("""
  SELECT count(*) FILTER (WHERE owner_name ~ '(LLC|L L C| LP | LTD | INC | TRUST | TR |PARTNERS|PROPERTIES|HOLDINGS)')  AS kw,
         count(*) AS total
  FROM parcels WHERE situs_zip='78749' AND is_sfr
""").fetchall())
PY
```
Fill in Result + Notes for every row.

- [ ] **Step 3: Fix real bugs, one at a time**

If a check fails because the engine is wrong (not because the data is thin): write a failing unit test in `marlin_engine/tests/`, fix the engine module, green, commit `fix: <what>`. If a check "fails" only because a signal needs the 2024 roll (Task 10), record that and move on — not a bug.

- [ ] **Step 4: Commit the validation doc**

```bash
git add docs/phase-a-validation.md
git commit -m "docs: Phase A engine validation on 78749"
```

---

## Task 10: Travis 2024 roll ingest — time-boxed, hard fallback

**Files:**
- Create (only if proceeding): `marlin_engine/ingest/__init__.py`, `marlin_engine/ingest/base.py`, `marlin_engine/ingest/travis.py`, `marlin_engine/tests/fixtures/travis_row_builder.py`, `marlin_engine/tests/test_ingest_travis.py`, `marlin_engine/config/travis_property_layout.json`, `marlin_engine/config/travis_abstract_subdv_layout.json`
- Modify: `data/farmsignal.duckdb` (adds 2024 `roll_year` rows); `docs/phase-a-validation.md` (record outcome)

**Interfaces:**
- Consumes: the operator-downloaded TCAD 2024 certified export in `data/raw/travis/`.
- Produces: 2024 `parcels` rows in the DuckDB → `build_demo_bundle._score()` picks them up as `prior` automatically → `homestead_dropped` / `over65_newly_filed` / `ag_exemption_rollback` activate in the bundle.

**⏱ Hard time-box: 4 hours. If not green by then, STOP, leave the DB single-roll, note it, proceed. The bundle + SPA work unchanged with `prior=None`.**

- [ ] **Step 1: Confirm the raw file exists**

```bash
ls -la data/raw/travis/
```
Expected: a `.zip` or `.TXT` TCAD 2024 export. If absent, the operator hasn't delivered it — skip this task, note in `phase-a-validation.md`.

- [ ] **Step 2: Lift the ingest modules + layout configs + row-builder fixture**

```bash
SRC="/Users/justinmason/Claude Code/FarmSignal"
mkdir -p marlin_engine/ingest marlin_engine/config marlin_engine/tests/fixtures
cp "$SRC/src/farmsignal/ingest/base.py"    marlin_engine/ingest/base.py
cp "$SRC/src/farmsignal/ingest/travis.py"  marlin_engine/ingest/travis.py
cp "$SRC/config/travis_property_layout.json"       marlin_engine/config/
cp "$SRC/config/travis_abstract_subdv_layout.json" marlin_engine/config/
cp "$SRC/tests/fixtures/travis_row_builder.py"     marlin_engine/tests/fixtures/
cp "$SRC/tests/test_ingest_travis.py"              marlin_engine/tests/test_ingest_travis.py
touch marlin_engine/ingest/__init__.py
```
Edit `marlin_engine/ingest/travis.py`: `from farmsignal.ingest.base` → `from marlin_engine.ingest.base`; `_CONFIG_DIR = Path(__file__).resolve().parents[3] / "config"` → `parents[1] / "config"`. Edit the row-builder fixture + test: repoint imports and the two `parents[2] / "config"` layout paths to `marlin_engine/config`.

- [ ] **Step 3: Run the lifted adapter unit tests**

```bash
pytest marlin_engine/tests/test_ingest_travis.py -q
```
Expected: PASS (synthetic rows built from the 2025 layout). If PASS, the adapter mechanics are intact.

- [ ] **Step 4: Ingest the 2024 export into the DuckDB**

```bash
python - <<'PY'
from pathlib import Path
import duckdb, pandas as pd
from marlin_engine.ingest.travis import TravisAdapter

raw = sorted(Path("data/raw/travis").glob("*"))[ -1 ]
a = TravisAdapter()
canon = a.map_to_canonical(a.parse(raw))
canon = canon[canon["roll_year"] == 2024]
print("parsed 2024 rows:", len(canon))
print(canon[["parcel_id","situs_address","owner_name","deed_date","homestead"]].head(10).to_string())

con = duckdb.connect("data/farmsignal.duckdb")
con.execute("DELETE FROM parcels WHERE county='travis' AND roll_year=2024")
con.register("c2024", canon)
con.execute("INSERT INTO parcels BY NAME SELECT * FROM c2024")
con.unregister("c2024")
print("db roll years:", con.execute("SELECT DISTINCT roll_year FROM parcels ORDER BY 1").fetchall())
con.close()
PY
```
**Verification gate:** the printed 10-row sample must show sane `situs_address` (has a house number), real `owner_name`, plausible `deed_date`. If fields are shifted/garbled → the 2024 layout differs from 2025 → **STOP**, `DELETE ... roll_year=2024`, fall back.

- [ ] **Step 5: Rebuild the bundle and confirm diff signals fired**

```bash
python -m scripts.build_demo_bundle
python -c "
import json; ps=json.load(open('web/public/data/parcels-78749.json'))
hits=[p for p in ps if any(b['label']=='Homestead dropped' for b in p['breakdown'])]
print('homestead_dropped parcels in 78749:', len(hits))
"
```
Expected: a non-zero count. Record it in `phase-a-validation.md`.

- [ ] **Step 6: Commit (whichever outcome)**

Success:
```bash
git add marlin_engine/ingest marlin_engine/config marlin_engine/tests web/public/data docs/phase-a-validation.md
git commit -m "feat: ingest Travis 2024 roll, activate year-over-year diff signals"
```
Fallback:
```bash
git add docs/phase-a-validation.md
git commit -m "docs: Travis 2024 ingest deferred (layout drift / no file) — demo runs single-roll"
```

---

# PART 2 — FRONTEND SPA

## Task 11: SPA scaffold + design tokens + fonts + brand assets

**Files:**
- Create: `web/package.json`, `web/vite.config.ts`, `web/tsconfig.json`, `web/index.html`, `web/wrangler.jsonc`, `web/src/main.tsx`, `web/src/styles/tokens.css`, `web/src/styles/global.css`, `web/src/App.tsx`, `web/src/assets/marlin-wordmark.png`, `web/src/assets/marlin-mark.svg`

**Interfaces:**
- Consumes: `Branding/*.png`.
- Produces: `npm run dev` serves a themed empty shell at `/`; `npm run build` emits `web/dist/`.

- [ ] **Step 1: Scaffold Vite React-TS**

```bash
cd "/Users/justinmason/Claude Code/Marlin Grade/web"
npm create vite@latest . -- --template react-ts
npm install
npm install react-router-dom
```

- [ ] **Step 2: `web/index.html` — fonts + title**

In `<head>` add:
```html
<title>Marlin</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
```

- [ ] **Step 3: `web/src/styles/tokens.css` — Deep Analytics tokens**

```css
:root {
  color-scheme: dark;
  --abyssal:   #0B111E;
  --surface-1: #111828;
  --surface-2: #0E1523;
  --ice:       #F1F5F9;
  --cyan:      #00F0FF;   /* Signal Cyan — interactive, A-grade, gauge ring */
  --green:     #00E676;   /* Data Green — export/CSV & revenue ONLY */
  --slate:     #64748B;
  --hairline:  rgba(241,245,249,0.10);

  --grade-a: #00F0FF;
  --grade-b: #3FD9E4;
  --grade-c: #64748B;
  --grade-d: #4C596B;
  --grade-f: #3A4453;

  --font-head: 'Plus Jakarta Sans', system-ui, sans-serif;
  --font-ui:   'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;

  --step-0: 13px; --step-1: 14px; --step-2: 18px; --step-3: 24px;
  --hero: clamp(2.5rem, 6vw, 4.25rem);
  --label: 10px;

  --r-ctl: 4px; --r-card: 8px;
  --space: 4px;
  --ease: cubic-bezier(0.16, 1, 0.3, 1);
  --dur-1: 150ms; --dur-2: 250ms;

  --sidebar-w: 208px;
  --header-h: 60px;
}
@media (prefers-reduced-motion: reduce) {
  :root { --dur-1: 0ms; --dur-2: 0ms; }
}
```

- [ ] **Step 4: `web/src/styles/global.css` — reset + base**

```css
*, *::before, *::after { box-sizing: border-box; }
html, body, #root { height: 100%; }
body {
  margin: 0;
  background: var(--abyssal);
  color: var(--ice);
  font-family: var(--font-ui);
  font-size: var(--step-1);
  -webkit-font-smoothing: antialiased;
}
h1, h2, h3, .head { font-family: var(--font-head); letter-spacing: -0.01em; }
.mono { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
.label {
  font-family: var(--font-mono); font-size: var(--label);
  letter-spacing: 0.14em; text-transform: uppercase; color: var(--slate);
}
a { color: var(--cyan); text-decoration: none; }
button { font: inherit; }
[hidden] { display: none !important; }
```

- [ ] **Step 5: Wire styles + a placeholder route in `web/src/main.tsx`**

```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider, createBrowserRouter } from "react-router-dom";
import "./styles/tokens.css";
import "./styles/global.css";

const router = createBrowserRouter([
  { path: "/", element: <div style={{ padding: 40 }}>Marlin — shell up</div> },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode><RouterProvider router={router} /></React.StrictMode>,
);
```

- [ ] **Step 6: `web/wrangler.jsonc`**

```jsonc
{
  "name": "marlin-demo",
  "compatibility_date": "2025-09-01",
  "assets": { "directory": "./dist" }
}
```

- [ ] **Step 7: Brand assets**

- Crop the wordmark: from `Branding/marlin watermark.png`, trim to the tight lockup bounds, save `web/src/assets/marlin-wordmark.png`. (Use any image tool; Preview crop is fine.)
- Trace the Primary Mark: from `Branding/marlin icon options.png`, take the top-left "PRIMARY MARK" cell and hand-author `web/src/assets/marlin-mark.svg` — an upward-slanting fin (single filled path) over three ascending parallelogram bars, cyan gradient `#00F0FF → #1E90C8`. If tracing overruns 45 min, crop that cell to `marlin-mark.png` instead and reference the PNG.

- [ ] **Step 8: Verify build + dev**

```bash
npm run dev     # visit http://localhost:5173 — dark bg, "shell up"
npm run build   # emits web/dist
```

- [ ] **Step 9: Commit**

```bash
cd "/Users/justinmason/Claude Code/Marlin Grade"
git add web -- ':!web/node_modules'
git commit -m "feat(web): Vite+React+TS scaffold, Deep Analytics tokens, fonts, brand assets"
```

---

## Task 12: Bundle data layer — types + `useBundle`

**Files:**
- Create: `web/src/lib/bundle.ts`, `web/src/lib/bundle.test.ts` (Vitest), `web/src/test/fixtures/*.json`
- Modify: `web/package.json` (add `vitest`), `web/vite.config.ts` (test config)

**Interfaces:**
- Consumes: `web/public/data/*.json` (Task 7 output) at runtime via `fetch`.
- Produces:
  - types `ZipRecord`, `ParcelRecord`, `BreakdownItem`, `GradeCutoffs`
  - `loadZips(): Promise<ZipRecord[]>`
  - `loadParcels(zip: string): Promise<ParcelRecord[]>` — memoised per zip
  - `loadGrades(): Promise<GradeCutoffs>`
  - `useBundle(zip: string): { zips, parcels, grades, loading, error }` React hook

- [ ] **Step 1: Add Vitest**

```bash
cd web && npm i -D vitest @testing-library/react @testing-library/jest-dom jsdom
```
`vite.config.ts` → add `test: { environment: "jsdom", setupFiles: [] }`.

- [ ] **Step 2: Write the failing test**

```ts
// web/src/lib/bundle.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { loadZips, loadParcels, _resetCache } from "./bundle";
import zipsFx from "../test/fixtures/zips.json";
import parcelsFx from "../test/fixtures/parcels-78749.json";

beforeEach(() => { _resetCache(); vi.restoreAllMocks(); });

describe("bundle loader", () => {
  it("parses zips.json into ZipRecord[]", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      new Response(JSON.stringify(zipsFx), { status: 200 }),
    );
    const zips = await loadZips();
    expect(zips.find((z) => z.zip === "78749")?.distribution.A).toBeDefined();
  });

  it("memoises parcels per zip (one fetch for two calls)", async () => {
    const spy = vi.spyOn(global, "fetch").mockResolvedValue(
      new Response(JSON.stringify(parcelsFx), { status: 200 }),
    );
    await loadParcels("78749");
    await loadParcels("78749");
    expect(spy).toHaveBeenCalledTimes(1);
  });
});
```
Create `web/src/test/fixtures/zips.json` and `parcels-78749.json` — copy the first 20 parcels of the real generated bundle so shapes are exact.

- [ ] **Step 3: Run to verify it fails**

```bash
npx vitest run src/lib/bundle.test.ts
```
Expected: FAIL — `./bundle` not found.

- [ ] **Step 4: Implement `web/src/lib/bundle.ts`**

```ts
import { useEffect, useState } from "react";

export interface BreakdownItem { label: string; points: number; }
export interface ParcelRecord {
  parcel_uid: string;
  situs_address: string;
  situs_norm: string;
  owner_name: string;
  owner_type: "occupant" | "entity";
  grade: "A" | "B" | "C" | "D" | "F";
  score: number;
  breakdown: BreakdownItem[];
  facts: {
    deed_date: string | null;
    tenure_years: number | null;
    homestead: boolean;
    over65: boolean;
    subdivision: string | null;
    assessed_value: number | null;
    mail_state: string | null;
    out_of_state: boolean;
  };
}
export interface ZipRecord {
  zip: string;
  area: string;
  subdivisions: string[];
  sfr_count: number;
  distribution: Record<"A"|"B"|"C"|"D"|"F", { count: number; pct: number }>;
  aggregates: { absentee_pct: number; rental_pct: number; median_tenure: number | null; out_of_state_pct: number };
  exclusivity: "available" | "held" | "monitored";
}
export type GradeCutoffs = { cutoffs: [string, string][] };

const BASE = `${import.meta.env.BASE_URL}data`;
let _zips: Promise<ZipRecord[]> | null = null;
let _grades: Promise<GradeCutoffs> | null = null;
const _parcels = new Map<string, Promise<ParcelRecord[]>>();

export function _resetCache() { _zips = null; _grades = null; _parcels.clear(); }

async function getJson<T>(path: string): Promise<T> {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path} → ${r.status}`);
  return r.json() as Promise<T>;
}

export function loadZips() { return (_zips ??= getJson<ZipRecord[]>(`${BASE}/zips.json`)); }
export function loadGrades() { return (_grades ??= getJson<GradeCutoffs>(`${BASE}/grades.json`)); }
export function loadParcels(zip: string) {
  if (!_parcels.has(zip)) _parcels.set(zip, getJson<ParcelRecord[]>(`${BASE}/parcels-${zip}.json`));
  return _parcels.get(zip)!;
}

export function useBundle(zip: string) {
  const [state, setState] = useState<{
    zips?: ZipRecord[]; parcels?: ParcelRecord[]; grades?: GradeCutoffs;
    loading: boolean; error?: string;
  }>({ loading: true });

  useEffect(() => {
    let alive = true;
    setState({ loading: true });
    Promise.all([loadZips(), loadParcels(zip), loadGrades()])
      .then(([zips, parcels, grades]) => alive && setState({ zips, parcels, grades, loading: false }))
      .catch((e) => alive && setState({ loading: false, error: String(e) }));
    return () => { alive = false; };
  }, [zip]);

  return state;
}
```

- [ ] **Step 5: Run to verify it passes**

```bash
npx vitest run src/lib/bundle.test.ts
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
cd .. && git add web -- ':!web/node_modules'
git commit -m "feat(web): bundle data layer — typed loaders + useBundle hook"
```

---

## Task 13: AppShell — sticky header + icon sidebar + routing

**Files:**
- Create: `web/src/components/AppShell.tsx`, `web/src/components/SidebarNav.tsx`, `web/src/components/UserBlock.tsx`, `web/src/lib/session.tsx`, `web/src/components/appShell.css`
- Modify: `web/src/main.tsx` (real route tree)

**Interfaces:**
- Consumes: `react-router-dom`, `session` context.
- Produces:
  - `<AppShell/>` — renders sticky header (logo · `<GlobalAddressSearch/>` slot · `<UserBlock/>`) + `<SidebarNav/>` + `<main><Outlet/></main>`.
  - `SessionProvider`, `useSession(): { user: string | null; tier: string; signIn(): void }`
  - route tree: `/` `/signin` then AppShell-wrapped `/farm` `/z/:zip` `/alerts` `/report/:zip`; unknown → `/`.

- [ ] **Step 1: `web/src/lib/session.tsx`**

```tsx
import { createContext, useContext, useState, ReactNode } from "react";

interface Session { user: string | null; tier: string; signIn: () => void; }
const Ctx = createContext<Session>({ user: null, tier: "Founding Solo", signIn: () => {} });

export function SessionProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<string | null>(null);
  return <Ctx.Provider value={{ user, tier: "Founding Solo", signIn: () => setUser("Palmer Holland") }}>{children}</Ctx.Provider>;
}
export const useSession = () => useContext(Ctx);
```

- [ ] **Step 2: `UserBlock.tsx`**

```tsx
import { useSession } from "../lib/session";
export function UserBlock() {
  const { user, tier } = useSession();
  return (
    <div className="userblock">
      <span className="userblock__avatar" aria-hidden />
      <span>
        <span className="userblock__name">{user ?? "Guest"}</span>
        <span className="label">{tier} · 1 zip</span>
      </span>
    </div>
  );
}
```

- [ ] **Step 3: `SidebarNav.tsx`**

```tsx
import { NavLink } from "react-router-dom";
const ITEMS = [
  { to: "/z/78749", icon: "◧", label: "Dashboard" },
  { to: "/farm", icon: "⌗", label: "Tracked Zips" },
  { to: "/alerts", icon: "◔", label: "Alerts" },
  { to: "/report/78749", icon: "▤", label: "Monthly Report" },
  { to: "#", icon: "⇩", label: "Export Logs" },
  { to: "#", icon: "⚙", label: "Settings" },
];
export function SidebarNav() {
  return (
    <nav className="sidebar" aria-label="Primary">
      {ITEMS.map((it) => (
        <NavLink key={it.label} to={it.to} className={({ isActive }) => "sidebar__item" + (isActive ? " is-active" : "")}>
          <span aria-hidden>{it.icon}</span> {it.label}
        </NavLink>
      ))}
    </nav>
  );
}
```

- [ ] **Step 4: `AppShell.tsx`**

```tsx
import { Outlet } from "react-router-dom";
import { SidebarNav } from "./SidebarNav";
import { UserBlock } from "./UserBlock";
import { GlobalAddressSearch } from "./GlobalAddressSearch";
import wordmark from "../assets/marlin-wordmark.png";
import "./appShell.css";

export function AppShell() {
  return (
    <div className="shell">
      <header className="shell__header">
        <img className="shell__logo" src={wordmark} alt="Marlin" height={22} />
        <GlobalAddressSearch />
        <UserBlock />
      </header>
      <SidebarNav />
      <main className="shell__main"><Outlet /></main>
    </div>
  );
}
```
Until Task 17 lands, `GlobalAddressSearch` can be a stub input.

- [ ] **Step 5: `appShell.css`** — grid: `header` full width (`--header-h`, sticky, `background: var(--surface-1)`, bottom `--hairline`), `sidebar` fixed `--sidebar-w` left, `main` offset by both, `padding: calc(var(--space)*6)`. Active sidebar item text `var(--cyan)`. Header search centered via `flex: 1; display: flex; justify-content: center`.

- [ ] **Step 6: Real route tree in `main.tsx`**

```tsx
const router = createBrowserRouter([
  { path: "/", element: <Landing /> },
  { path: "/signin", element: <SignIn /> },
  {
    element: <AppShell />,
    children: [
      { path: "/farm", element: <FarmPicker /> },
      { path: "/z/:zip", element: <Dashboard /> },
      { path: "/alerts", element: <Alerts /> },
      { path: "/report/:zip", element: <MonthlyReport /> },
    ],
  },
  { path: "*", element: <Navigate to="/" replace /> },
]);
```
Wrap `<RouterProvider>` in `<SessionProvider>`. Create one-line placeholder components for any route not yet built so the tree compiles.

- [ ] **Step 7: Verify**

```bash
cd web && npm run dev
# visit /z/78749 — sticky header + sidebar render; main shows placeholder
```

- [ ] **Step 8: Commit**

```bash
cd .. && git add web -- ':!web/node_modules'
git commit -m "feat(web): AppShell — sticky header, icon sidebar, session context, routes"
```

---

## Task 14: GradeGauge component

**Files:**
- Create: `web/src/components/GradeGauge.tsx`, `web/src/components/gradeGauge.css`, `web/src/components/GradeGauge.test.tsx`

**Interfaces:**
- Consumes: nothing.
- Produces: `<GradeGauge grade={Grade} score={number} flags={string[]} size?: "lg" | "sm" />` — SVG ring (arc length = `score/100` of a circle, stroke `var(--cyan)`), letter centered (`var(--font-head)`, weight 800), up to 3 `flags` rendered beneath in `var(--font-mono)` at `var(--label)` size. Ring animates from 0 on mount; respects reduced motion. Exported helper `arcDashArray(score, radius): [number, number]`.

- [ ] **Step 1: Write the failing test**

```tsx
import { render, screen } from "@testing-library/react";
import { GradeGauge, arcDashArray } from "./GradeGauge";

it("dash array is proportional to score", () => {
  const [on, off] = arcDashArray(50, 100);           // circumference 2πr = 628.3
  expect(on).toBeCloseTo(314.16, 1);
  expect(on + off).toBeCloseTo(628.32, 1);
});

it("renders the letter and up to three flags", () => {
  render(<GradeGauge grade="A" score={88} flags={["TENURE: 22 YRS", "HOMESTEAD: DROPPED", "OUT-OF-STATE", "EXTRA"]} />);
  expect(screen.getByText("A")).toBeInTheDocument();
  expect(screen.getByText("HOMESTEAD: DROPPED")).toBeInTheDocument();
  expect(screen.queryByText("EXTRA")).toBeNull();
});
```

- [ ] **Step 2: Run — expect FAIL** (`npx vitest run src/components/GradeGauge.test.tsx`).

- [ ] **Step 3: Implement**

```tsx
import { useEffect, useRef } from "react";
import "./gradeGauge.css";

export type Grade = "A" | "B" | "C" | "D" | "F";
const R = 100;
export function arcDashArray(score: number, radius = R): [number, number] {
  const c = 2 * Math.PI * radius;
  const on = (Math.max(0, Math.min(100, score)) / 100) * c;
  return [on, c - on];
}

export function GradeGauge({
  grade, score, flags = [], size = "lg",
}: { grade: Grade; score: number; flags?: string[]; size?: "lg" | "sm" }) {
  const ref = useRef<SVGCircleElement>(null);
  const [on, off] = arcDashArray(score);
  useEffect(() => {
    const el = ref.current; if (!el) return;
    el.style.transition = "none";
    el.style.strokeDasharray = `0 ${on + off}`;
    requestAnimationFrame(() => {
      el.style.transition = `stroke-dasharray var(--dur-2) var(--ease)`;
      el.style.strokeDasharray = `${on} ${off}`;
    });
  }, [on, off]);

  return (
    <div className={`gauge gauge--${size} gauge--${grade.toLowerCase()}`}>
      <svg viewBox="0 0 240 240" className="gauge__svg">
        <circle cx="120" cy="120" r={R} className="gauge__track" />
        <circle ref={ref} cx="120" cy="120" r={R} className="gauge__arc"
          transform="rotate(-90 120 120)" />
      </svg>
      <div className="gauge__center">
        <span className="gauge__letter head">{grade}</span>
        <span className="gauge__score mono">{Math.round(score)}</span>
      </div>
      {flags.length > 0 && (
        <ul className="gauge__flags mono">
          {flags.slice(0, 3).map((f) => <li key={f}>{f}</li>)}
        </ul>
      )}
    </div>
  );
}
```
`gradeGauge.css`: `.gauge__track { stroke: var(--hairline); fill: none; stroke-width: 10; }` · `.gauge__arc { stroke: var(--cyan); fill: none; stroke-width: 10; stroke-linecap: round; }` · center absolutely positioned · `.gauge--a .gauge__letter { color: var(--cyan); }` etc. per §6.2 · `.gauge--a` adds `filter: drop-shadow(0 0 6px rgba(0,240,255,.5))`.

- [ ] **Step 4: Run — expect PASS.**

- [ ] **Step 5: Commit**

```bash
git add web -- ':!web/node_modules'
git commit -m "feat(web): GradeGauge — animated cyan score ring + letter + driver flags"
```

---

## Task 15: Screen 4 — Zip dashboard

**Files:**
- Create: `web/src/routes/Dashboard.tsx`, `web/src/components/DistributionBar.tsx`, `web/src/components/AggregatePanel.tsx`, `web/src/components/ProspectTable.tsx`, `web/src/components/FilterChips.tsx`, `web/src/components/GradePill.tsx`, `web/src/components/ExportCsvButton.tsx`, `web/src/lib/csv.ts`, `web/src/routes/dashboard.css`
- Modify: `web/src/main.tsx` (Dashboard already routed)

**Interfaces:**
- Consumes: `useBundle(zip)`, `useParams`, `useNavigate`.
- Produces:
  - `<GradePill grade={Grade} />` — A/B glow, C–F recede (per §6.2)
  - `<DistributionBar dist={ZipRecord["distribution"]} />` — animated width per band
  - `<FilterChips value={FilterState} onChange={...} />` + `applyFilters(parcels, FilterState): ParcelRecord[]` (exported, unit-tested)
  - `<ProspectTable parcels={...} onRowClick={(p) => ...} />` — columns rank · `<GradePill>` · address · owner type · score; sortable by score/grade/address
  - `<ExportCsvButton rows={ParcelRecord[]} zip={string} />` — Data Green; calls `downloadCsv`
  - `downloadCsv(rows: Record<string,unknown>[], filename: string): void`

- [ ] **Step 1: Write failing tests for the pure bits**

```tsx
// web/src/components/FilterChips.test.tsx
import { applyFilters } from "./FilterChips";
import parcels from "../test/fixtures/parcels-78749.json";

it("grade filter keeps only selected grades", () => {
  const out = applyFilters(parcels as any, { grades: new Set(["A"]), longTenure: false, likelyRental: false, ownerOccupied: false, outOfState: false });
  expect(out.every((p) => p.grade === "A")).toBe(true);
});
it("ownerOccupied filter excludes entities", () => {
  const out = applyFilters(parcels as any, { grades: new Set(), longTenure: false, likelyRental: false, ownerOccupied: true, outOfState: false });
  expect(out.every((p) => p.owner_type === "occupant")).toBe(true);
});
```
```ts
// web/src/lib/csv.test.ts
import { toCsv } from "./csv";
it("quotes fields with commas", () => {
  expect(toCsv([{ a: "x,y", b: 1 }])).toBe('a,b\r\n"x,y",1');
});
```

- [ ] **Step 2: Run — expect FAIL.**

- [ ] **Step 3: Implement `csv.ts`**

```ts
export function toCsv(rows: Record<string, unknown>[]): string {
  if (rows.length === 0) return "";
  const cols = Object.keys(rows[0]);
  const esc = (v: unknown) => {
    const s = v == null ? "" : String(v);
    return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  return [cols.join(","), ...rows.map((r) => cols.map((c) => esc(r[c])).join(","))].join("\r\n");
}
export function downloadCsv(rows: Record<string, unknown>[], filename: string): void {
  const blob = new Blob([toCsv(rows)], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}
```

- [ ] **Step 4: Implement `FilterChips.tsx`** (`FilterState` interface + `applyFilters` + the chip row UI), `GradePill.tsx`, `DistributionBar.tsx` (flex row of 5 segments, width `pct%`, `transition: width var(--dur-2)`), `AggregatePanel.tsx` (label/value rows in `.mono`), `ProspectTable.tsx` (sortable `<table>`; `onRowClick`), `ExportCsvButton.tsx`:

```tsx
import { downloadCsv } from "../lib/csv";
import type { ParcelRecord } from "../lib/bundle";
export function ExportCsvButton({ rows, zip }: { rows: ParcelRecord[]; zip: string }) {
  return (
    <button className="btn btn--export" onClick={() =>
      downloadCsv(
        rows.map((p, i) => ({ rank: i + 1, grade: p.grade, address: p.situs_address, owner_type: p.owner_type, score: p.score })),
        `marlin-${zip}-prospects.csv`,
      )}>
      ⇩ Export CSV
    </button>
  );
}
```
`.btn--export { background: var(--green); color: #062b18; font-weight: 700; }` — the only place `--green` is used.

- [ ] **Step 5: Implement `Dashboard.tsx`**

```tsx
import { useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useBundle } from "../lib/bundle";
import { DistributionBar } from "../components/DistributionBar";
import { AggregatePanel } from "../components/AggregatePanel";
import { FilterChips, applyFilters, type FilterState } from "../components/FilterChips";
import { ProspectTable } from "../components/ProspectTable";
import { ExportCsvButton } from "../components/ExportCsvButton";
import { Disclaimer } from "../components/Disclaimer";
import "./dashboard.css";

const EMPTY: FilterState = { grades: new Set(), longTenure: false, likelyRental: false, ownerOccupied: false, outOfState: false };

export function Dashboard() {
  const { zip = "78749" } = useParams();
  const nav = useNavigate();
  const { zips, parcels, loading, error } = useBundle(zip);
  const [filters, setFilters] = useState<FilterState>(EMPTY);
  const meta = zips?.find((z) => z.zip === zip);
  const rows = useMemo(() => (parcels ? applyFilters(parcels, filters) : []), [parcels, filters]);

  if (loading) return <p className="label">Loading {zip}…</p>;
  if (error || !meta || !parcels) return <p>Could not load {zip}.</p>;

  return (
    <div className="dash">
      <header className="dash__head">
        <div>
          <h1>ZIP {zip} · {meta.area}</h1>
          <p className="label">{meta.subdivisions.join(" · ")} — {meta.sfr_count.toLocaleString()} scored SFR</p>
        </div>
        <div className="dash__badges">
          <span className="badge badge--mon">Monitored</span>
          {meta.exclusivity === "available" && <span className="badge badge--exc">Exclusivity available</span>}
          <ExportCsvButton rows={rows} zip={zip} />
        </div>
      </header>

      <section className="dash__stats">
        <DistributionBar dist={meta.distribution} />
        <AggregatePanel agg={meta.aggregates} />
      </section>

      <FilterChips value={filters} onChange={setFilters} />
      <ProspectTable parcels={rows} onRowClick={(p) => nav(`/z/${zip}?addr=${encodeURIComponent(p.situs_norm)}`)} />
      <Disclaimer variant="compact" />
    </div>
  );
}
```

- [ ] **Step 6: Run tests + eyeball**

```bash
cd web && npx vitest run && npm run dev   # /z/78749 — full dashboard against the real bundle
```

- [ ] **Step 7: Commit**

```bash
cd .. && git add web -- ':!web/node_modules'
git commit -m "feat(web): Screen 4 zip dashboard — distribution, aggregates, filters, prospect table, CSV export"
```

---

## Task 16: Screen 5 — AddressDrawer (right slide-out)

**Files:**
- Create: `web/src/components/AddressDrawer.tsx`, `web/src/components/SignalTriggers.tsx`, `web/src/components/FactsTable.tsx`, `web/src/components/Disclaimer.tsx`, `web/src/components/addressDrawer.css`
- Modify: `web/src/routes/Dashboard.tsx` (mount the drawer, read `?addr=`)

**Interfaces:**
- Consumes: `ParcelRecord`, `useSearchParams`.
- Produces:
  - `<Disclaimer variant="compact" | "full" />` — renders the Global-Constraints disclaimer text verbatim from a single exported constant `DISCLAIMER_TEXT`.
  - `<SignalTriggers items={BreakdownItem[]} />` — diverging list: label left, bar from center (`points > 0` → cyan to the right, `points < 0` → slate to the left), signed points right; sorted by `|points|` desc; total row.
  - `<FactsTable facts={ParcelRecord["facts"]} owner={string} ownerType={string} />`
  - `<AddressDrawer parcel={ParcelRecord | null} zipMeta={ZipRecord} onClose={() => void} />` — fixed right panel, `transform: translateX(100%)` when closed → `0` open, `--dur-2 --ease`; backdrop dims workspace; `Esc` + backdrop click close; deep-linked via `?addr=`.

- [ ] **Step 1: Failing test for `SignalTriggers` ordering + `DISCLAIMER_TEXT`**

```tsx
import { render, screen } from "@testing-library/react";
import { SignalTriggers } from "./SignalTriggers";
import { DISCLAIMER_TEXT } from "./Disclaimer";

it("sorts triggers by absolute magnitude, negative and positive interleaved", () => {
  render(<SignalTriggers items={[{label:"a",points:5},{label:"b",points:-25},{label:"c",points:10}]} />);
  const labels = screen.getAllByTestId("trigger-label").map((n) => n.textContent);
  expect(labels).toEqual(["b", "c", "a"]);
});
it("disclaimer text matches the canonical constant", () => {
  expect(DISCLAIMER_TEXT).toContain("does not reflect MLS status");
  expect(DISCLAIMER_TEXT).toContain("No listing or sale is guaranteed.");
});
```

- [ ] **Step 2: Run — expect FAIL.**

- [ ] **Step 3: Implement `Disclaimer.tsx`** (export `DISCLAIMER_TEXT` = the exact Global-Constraints string; `variant="compact"` renders it at `--label` size in `--slate`, `"full"` in a bordered callout), **`SignalTriggers.tsx`**, **`FactsTable.tsx`**, **`AddressDrawer.tsx`**:

```tsx
import { useEffect } from "react";
import { GradeGauge } from "./GradeGauge";
import { SignalTriggers } from "./SignalTriggers";
import { FactsTable } from "./FactsTable";
import { Disclaimer } from "./Disclaimer";
import type { ParcelRecord, ZipRecord } from "../lib/bundle";
import "./addressDrawer.css";

function driverFlags(p: ParcelRecord): string[] {
  return [...p.breakdown].sort((a, b) => Math.abs(b.points) - Math.abs(a.points)).slice(0, 3)
    .map((b) => b.label.toUpperCase().replace(/\s+/g, " "));
}

export function AddressDrawer({ parcel, zipMeta, onClose }: {
  parcel: ParcelRecord | null; zipMeta: ZipRecord; onClose: () => void;
}) {
  useEffect(() => {
    const h = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [onClose]);

  const open = parcel != null;
  const rank = open
    ? // local percentile from the score vs the zip's scored population
      Math.max(1, Math.round(100 * (1 - percentileIn(zipMeta, parcel!.score))))
    : 0;

  return (
    <>
      <div className={`drawer__backdrop${open ? " is-open" : ""}`} onClick={onClose} />
      <aside className={`drawer${open ? " is-open" : ""}`} aria-hidden={!open}>
        {parcel && (
          <div className="drawer__body">
            <button className="drawer__close" onClick={onClose} aria-label="Close">✕</button>
            <GradeGauge grade={parcel.grade} score={parcel.score} flags={driverFlags(parcel)} />
            <p className="label">Top {rank}% of ZIP {zipMeta.zip}</p>
            <h2>{parcel.situs_address}</h2>
            <p className="label">
              {parcel.facts.subdivision ?? "—"} · owner {parcel.owner_type}
            </p>
            <div className="drawer__spark label">GRADE HISTORY — staged (needs 2 roll years)</div>
            <SignalTriggers items={parcel.breakdown} />
            <FactsTable facts={parcel.facts} owner={parcel.owner_name} ownerType={parcel.owner_type} />
            <Disclaimer variant="full" />
          </div>
        )}
      </aside>
    </>
  );
}

function percentileIn(_zip: ZipRecord, _score: number): number {
  // approximate: use the distribution buckets; refined if needed
  return 0.5;
}
```
(Replace `percentileIn` with a real calc using the parcels array passed from Dashboard if precision matters; approximate is acceptable for the demo.)

- [ ] **Step 4: Mount in `Dashboard.tsx`**

```tsx
const [sp, setSp] = useSearchParams();
const addr = sp.get("addr");
const selected = addr ? parcels.find((p) => p.situs_norm === addr) ?? null : null;
// …render <AddressDrawer parcel={selected} zipMeta={meta} onClose={() => { sp.delete("addr"); setSp(sp); }} />
```

- [ ] **Step 5: Run tests + eyeball the slide-out** (`/z/78749?addr=<a real situs_norm>`).

- [ ] **Step 6: Commit**

```bash
git add web -- ':!web/node_modules'
git commit -m "feat(web): Screen 5 AddressDrawer — gauge, signal triggers, facts, disclaimer"
```

---

## Task 17: GlobalAddressSearch — header typeahead → drawer

**Files:**
- Create: `web/src/components/GlobalAddressSearch.tsx`, `web/src/components/globalAddressSearch.css`
- Modify: `web/src/lib/bundle.ts` (`loadAllParcels()` helper), `web/src/components/AppShell.tsx` (already slots it)

**Interfaces:**
- Consumes: `loadParcels` for each of the 7 zips (lazy, on first focus).
- Produces:
  - `loadAllParcels(): Promise<(ParcelRecord & { zip: string })[]>` — memoised
  - `<GlobalAddressSearch/>` — input with a Signal-Cyan focus glow; on input ≥3 chars, fuzzy-filter `situs_norm` (`startsWith` on the numeric prefix + `includes` on the rest), show ≤6 results; selecting one → `navigate(/z/<zip>?addr=<situs_norm>)`.

- [ ] **Step 1: Failing test for the match function**

```ts
import { matchAddresses } from "./GlobalAddressSearch";
const rows = [
  { situs_norm: "5209 PUCCOON CV", zip: "78749" },
  { situs_norm: "5219 PUCCOON CV", zip: "78749" },
  { situs_norm: "100 SLAUGHTER LN", zip: "78748" },
] as any;
it("prefixes street number, matches street name substring", () => {
  const out = matchAddresses(rows, "5209 pucc");
  expect(out).toHaveLength(1);
  expect(out[0].situs_norm).toBe("5209 PUCCOON CV");
});
it("returns [] under 3 chars", () => {
  expect(matchAddresses(rows, "52")).toEqual([]);
});
```

- [ ] **Step 2: Run — expect FAIL.**

- [ ] **Step 3: Implement.** `matchAddresses(rows, q)` — normalise `q` with the same upper/space rules, require `length >= 3`, score by (numeric prefix exact) then (token includes), cap 6. Component: controlled input, `onFocus` triggers `loadAllParcels()`, results dropdown, click/Enter → `navigate`.

`globalAddressSearch.css`: `input:focus { outline: none; border-color: var(--cyan); box-shadow: 0 0 0 3px rgba(0,240,255,.18); }`.

- [ ] **Step 4: Run — expect PASS — eyeball from any authed screen.**

- [ ] **Step 5: Commit**

```bash
git add web -- ':!web/node_modules'
git commit -m "feat(web): GlobalAddressSearch — sticky-header typeahead opens the address drawer"
```

---

## Task 18: Screen 1 — Landing

**Files:**
- Create: `web/src/routes/Landing.tsx`, `web/src/routes/landing/HowItWorks.tsx`, `web/src/routes/landing/PricingTable.tsx`, `web/src/routes/landing/landing.css`

**Interfaces:**
- Consumes: `marlin-wordmark.png`, `marlin-mark.svg`.
- Produces: static marketing page. `PLAN_ROWS` data drives the comparison grid.

- [ ] **Step 1: Implement `HowItWorks.tsx`** — boxless: a `<div className="steps">` of 3 `<div className="step">` (number in `.mono`, title in `.head`, one line of copy), CSS `::after` arrow connectors between them, generous padding, own kicker + `<h2>`. Copy from spec §5.3 / brand brief.

- [ ] **Step 2: Implement `PricingTable.tsx`** — one `<table className="plans">`:
  - `<colgroup>`: label col + 3 plan cols (Market Leader col tinted).
  - `<thead>`: first cell holds `<img src={mark} className="plans__logo" alt="Marlin" />`; each plan cell stacks name / price (`.mono`) / description `<p>` / CTA button vertically.
  - `<tbody>`: grouped rows with `.grp` section labels — **Capacity** (Monitored zips 1/3/All · Lookups outside 500/3,000/Unlimited · Seats 1/3/10) · **Signal streams** (Monthly CAD baseline ✓/✓/✓ · Weekly warm-lead —/✓/✓ · Daily legal-trigger —/—/✓) · **Alerts & history** (In-app feed ✓/✓/✓ · Channels "Email digest"/"Email + SMS + re-nudge"/"Priority SMS + CRM push" · Grade history "Current only"/"12 months"/"12 mo + area analytics") · **Export & integrations** (CSV "Basic"/"Full breakdown"/"Full + bulk + API" · CRM sync —/—/✓ · Per-zip exclusivity —/"Add-on (+100% per-zip rate)"/"Add-on · up to 3 zips").
  - Values verbatim from parent spec §4.

- [ ] **Step 3: Implement `Landing.tsx`** — top nav (wordmark + "Pricing" + "Sign in" → `/signin`), hero (`<h1>` spec §14 copy with the cyan second line, subhead, CTA → `/signin`), `<HowItWorks/>`, a `<hr className="section-divider">`, `<section id="pricing">` kicker + `<h2>Plans that scale with your farm</h2>` + subhead + `<PricingTable/>`, wedge line ("No 12-month contract. No auto-renewal. Cancel with 30 days' notice. Unconditional short-window refund on any plan.").

- [ ] **Step 4: Eyeball at `/`** — the two blocks read as clearly separate; pricing columns align; logo cell filled.

- [ ] **Step 5: Commit**

```bash
git add web -- ':!web/node_modules'
git commit -m "feat(web): Screen 1 landing — hero, boxless how-it-works, unified pricing table"
```

---

## Task 19: Screen 2 sign-in + Screen 3 farm picker

**Files:**
- Create: `web/src/routes/SignIn.tsx`, `web/src/routes/FarmPicker.tsx`, `web/src/routes/farmPicker.css`

**Interfaces:**
- Consumes: `useSession().signIn`, `loadZips`.
- Produces: `/signin` → any submit calls `signIn()` then `navigate("/farm")`; `/farm` lists the 7 zips from `zips.json` with `exclusivity` state, "Select" → `navigate("/z/<zip>")`.

- [ ] **Step 1: `SignIn.tsx`** — centered card, wordmark, email + password inputs (non-functional), "Sign in" button → `signIn(); navigate("/farm")`. Small note: "Demo: any input signs you in as Palmer Holland."

- [ ] **Step 2: `FarmPicker.tsx`** — `useBundle` not needed; call `loadZips()`. Table: zip · area · scored SFR · exclusivity badge (`available` amber / `held` slate) · Select button. 78749 row highlighted. Select → `/z/<zip>`.

- [ ] **Step 3: Eyeball the flow** `/` → Sign in → `/farm` → `/z/78749`.

- [ ] **Step 4: Commit**

```bash
git add web -- ':!web/node_modules'
git commit -m "feat(web): Screens 2-3 fake sign-in + Travis farm picker"
```

---

## Task 20: Screen 6 alerts feed + Screen 7 monthly report (fixtures)

**Files:**
- Create: `fixtures/alerts.json`, `fixtures/report-78749.json`, `web/src/routes/Alerts.tsx`, `web/src/components/AlertFeed.tsx`, `web/src/routes/MonthlyReport.tsx`, `web/src/routes/report.css`
- Modify: `scripts/build_demo_bundle.py` already copies `fixtures/*` (Task 7 Step 3) — just re-run it

**Interfaces:**
- Consumes: `web/public/data/alerts.json`, `web/public/data/report-78749.json`, `useBundle` (for the real aggregates block).
- Produces:
  - `alerts.json`: `[{ "id", "kind": "computed_spike"|"legal_trigger", "from_grade", "to_grade", "address", "situs_norm", "zip", "headline", "detail", "age", "worked": false }]`
  - `report-78749.json`: `{ "cycle": "September 2026", "movers": { "new_ab": [...], "warming": [...], "cooled": [...] } }` (top-A/B + aggregates come from the real bundle, not the fixture)

- [ ] **Step 1: Hand-author `fixtures/alerts.json`** — 3–5 rows. Include exactly one `legal_trigger` (foreclosure, styled distinctly) and two `computed_spike` rows whose `headline` mirrors real breakdown phrasing ("Homestead exemption dropped after 11 years (+25)"). Use real 78749 street names from `parcels-78749.json`.

- [ ] **Step 2: Hand-author `fixtures/report-78749.json`** — a handful of addresses in each mover bucket, again pulled from the real parcel list so they resolve in the drawer.

- [ ] **Step 3: `AlertFeed.tsx` + `Alerts.tsx`** — reverse-chron rows; `legal_trigger` gets a left border in a warning hue (not `--green`, not `--cyan` — use a dedicated `--warn: #F2A65A` token added to `tokens.css`); each row: kind label · `from_grade → to_grade` with `<GradePill>` · address · `detail` · `age` · "Mark worked" / "Dismiss" (local state only). Row click → `/z/78749?addr=<situs_norm>`.

- [ ] **Step 4: `MonthlyReport.tsx`** — real aggregates block from `useBundle("78749").zips`, then three mover sections from the fixture (label + address list), then a real "Top A/B" table computed from `parcels` (grade A or B, sorted by score, top 10). Footer: `<Disclaimer variant="compact" />`.

- [ ] **Step 5: Re-run the bundle build so fixtures land in `web/public/data/`**

```bash
cd .. && python -m scripts.build_demo_bundle && ls web/public/data
```

- [ ] **Step 6: Eyeball `/alerts` and `/report/78749`.**

- [ ] **Step 7: Commit**

```bash
git add web fixtures scripts -- ':!web/node_modules'
git commit -m "feat(web): Screens 6-7 alerts feed + monthly report (staged fixtures + real aggregates)"
```

---

## Task 21: Polish pass + deploy

**Files:**
- Modify: assorted CSS; `web/src/routes/*` empty/loading states
- Create: none

**Interfaces:**
- Consumes: everything.
- Produces: a deployed public URL.

- [ ] **Step 1: Motion pass** — confirm on mount: gauge ring draws, score counts up (add a `useCountUp` hook if not already), distribution bar animates width, drawer slides from the right with backdrop fade, A/B `GradePill` has a slow cyan pulse (`@keyframes` 2s). Everything inside `@media (prefers-reduced-motion: reduce)` collapses to instant.

- [ ] **Step 2: Empty / loading / error states** — every route: a `.label` "Loading…" while `useBundle` is pending; a readable message on error; `ProspectTable` with 0 filtered rows shows "No parcels match these filters."

- [ ] **Step 3: Responsive check** — at 320 / 375 / 768 / 1024 / 1440: no horizontal body scroll; the prospect table scrolls inside its own `overflow-x:auto` wrapper; sidebar collapses to icons-only under 900px; drawer goes full-width under 640px; pricing table scrolls inside a wrapper under 820px.

- [ ] **Step 4: Disclaimer audit** — grep the build for the canonical text; confirm it renders on: dashboard (compact), address drawer (full), monthly report (compact), and the CSV export (prepend a comment row or a trailing line in `toCsv` caller for exports). Fix any surface missing it.

- [ ] **Step 5: Build + local preview**

```bash
cd web && npm run build && npx vite preview
```
Click the full path: `/` → Sign in → `/farm` → `/z/78749` → row → drawer → header search → another address → `/alerts` → `/report/78749`.

- [ ] **Step 6: Deploy to Cloudflare**

```bash
npx wrangler deploy
```
(Operator runs `npx wrangler login` first if needed — flag this.) Note the `*.workers.dev` URL.

- [ ] **Step 7: Smoke-test the deployed URL** on a fresh browser (Palmer is remote — verify it works with no local state). Check fonts load, bundle fetches, drawer deep-link works.

- [ ] **Step 8: Commit + tag**

```bash
cd .. && git add web -- ':!web/node_modules'
git commit -m "chore(web): polish pass — motion, empty states, responsive, disclaimer audit, deploy"
git tag demo-wednesday
```

- [ ] **Step 9: Send Palmer the URL.**

---

## Self-Review

**Spec coverage (`docs/DEMO_BUILD_SPEC.md`):**

| Spec section | Task(s) |
|---|---|
| §3 repo structure + frontend stack | 1, 11 |
| §4.1 modules to lift | 2, 3, 5 |
| §4.2 `out_of_state` −10 | 4 |
| §4.3 not-lifted (subdivision etc.) | 2/3/5 (by omission — explicit) |
| §4.4 `build_demo_bundle.py` + bundle shape §5.4 | 7 |
| §4.5 Travis 2024 time-boxed | 10 |
| §4.6 full-roll cutoff calibration | 8 |
| §4.7 Phase A validation on 78749 | 9 |
| §5.1–5.3 screens + layout archetype | 13 (shell), 15, 16, 17, 18, 19, 20 |
| §5.4 JSON bundle contract | 7 (produce), 12 (consume/type) |
| §6.1 palette | 11 |
| §6.2 grade colour system | 11 (tokens), 14/15 (pill+gauge) |
| §6.3 typography | 11 |
| §6.4 three-section workspace | 13 |
| §6.5 grade gauge | 14 |
| §6.6 motion | 11 (tokens), 21 (pass) |
| §6.7 brand assets | 11 |
| §6.8 component inventory | 13–20 |
| §7 canonical disclaimer | 16 (`DISCLAIMER_TEXT`), 21 (audit) |
| §8 build sequence | task order mirrors it |
| §9 risks | 9, 10 (mitigations built in) |

No spec section is uncovered.

**Placeholder scan:** `grades.CUTOFFS` ships with explicit placeholder values in Task 6 and is deliberately overwritten with real numbers in Task 8 (Step 3) — this is a sequenced two-step, not an unfilled placeholder. `percentileIn` in Task 16 has a stated approximate default with a note on how to make it exact — acceptable for a demo, explicitly flagged. No `TODO`/`TBD`/"handle errors appropriately"/"similar to Task N" left in the plan.

**Type consistency:** `ParcelRecord` / `ZipRecord` / `BreakdownItem` / `GradeCutoffs` defined in Task 12 and consumed unchanged in 14–20. `Grade` union (`"A"|"B"|"C"|"D"|"F"`) consistent across `grades.py` (`_ORDER` + `"F"`), `bundle.ts`, `GradeGauge`, `GradePill`. `applyFilters` / `FilterState` defined in Task 15, no other definition. `downloadCsv` / `toCsv` defined once in Task 15. `DISCLAIMER_TEXT` single source in Task 16. `build()` signature `(db_path, out_dir)` consistent between Task 7 implementation and its test. `fetch_prior_roll_year_snapshot` signature matches FarmSignal source and the Task 7 call site.
