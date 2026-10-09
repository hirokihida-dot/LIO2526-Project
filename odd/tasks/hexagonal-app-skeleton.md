# Feature: hexagonal-app-skeleton

## Objective
Create the concrete hexagonal skeleton of the Dash app (`app/`, `tests/`, `pyproject.toml`,
`Makefile`) defined in the approved proposal, bootable and testable, without touching
`prototipo/`, `design/` o `data/`.

## Problem / Why
The repo has the full spec (README.md) but no code. The user approved creating the
skeleton (v1 session: migration from `prevision-ventas-handoff/`). The app must boot and
pass tests as proof the layout is valid, without fake results (gbm stub honest).

## Scope
- pyproject.toml (dash, pandas, statsmodels, lightgbm, flask-caching, plotly, openpyxl, pytest)
- Makefile (run/test with `env -u PYTHONPATH` — isolation from ROS 2)
- app/core (entities, params, metricas, ports, 6 usecases)
- app/adapters (csv_reader, naive, ets, bass, scrublands, export manager, caching; gbm stub)
- app/presentation (app.py entrypoint, sidebar, 6 pages with path, components, ui formatting)
- app/assets/industry.css (byte-copy from design/)
- tests (core, adapters, e2e boot)
- README.md: replace section "Recommended Dash project Structure" with the hexagonal one

## Constraints
- Do not commit (the parent does so at the end, only when everything passes).
- Do not touch prototipo/, design/, data/, LICENSE, .gitignore of ROS.
- Run everything with `env -u PYTHONPATH .venv/bin/...` (ROS 2 PYTHONPATH leak).
- Dash 4.4.1: `app.run()` (NO `run_server`), `use_pages` + `pages_folder` available,
  `register_page(module, path=...)`, importable `page_container`.
- UI copy in Spanish; code, identifiers and comments in English.
- Forecast contract: DataFrame `periodo, prevision, ic_inf, ic_sup` (95% CI).

## Tasks
- [x] T1 scaffold: pyproject.toml, Makefile, .venv with deps, .gitignore (.venv/)
- [x] T2 tests-first for core logic (metricas, dataset agg, naive, ets, bass, escenarios,
      csv_reader, exportador, e2e boot) — observed RED
- [x] T3 implement core/ (domain entities+params+metricas, ports, 6 usecases)
- [x] T4 implement adapters/ (gbm as documented NotImplementedError stub)
- [x] T5 implement presentation/ (app.py, sidebar layout, 6 placeholder pages with register_page)
- [x] T6 GREEN: all tests pass; boot smoke of the app; README hexagonal section applied

## Route (per ODD)
- All delegated to one writer (35+ files) with tests-first; parent verifies by spot check
  (pytest + boot + prototype integrity), commits and pushes once ready.

## Acceptance criteria
1. `env -u PYTHONPATH .venv/bin/pytest -q` — all green.
2. `env -u PYTHONPATH .venv/bin/python app/app.py` boots and serves HTTP 200 at 127.0.0.1:8050.
3. `page_registry` contains the 6 spec routes (/ and /datos /modelos /lanzamiento /escenarios /exportar).
4. prototipo/ files untouched and self-consistent (deps css/js intact).
5. No legacy paths (datos/, dash_assets/) anywhere in docs; app/assets css identical to design/.

## Progress / Evidence
- 2026-10-09 (v1): handoff migrated to repo root, prototype verified autonomous (relative deps),
  README.md + CLAUDE.md path purge (datos/ → data/, dash_assets/ → design/). Commit pending
  (user asked single commit when everything ready) — DONE in this feature.
- T1 DONE: .venv (python 3.12.12) with dash 4.4.1, pandas 3.0.6, statsmodels 0.15.0, lightgbm 4.7.0,
  scikit-learn 1.9.1, flask-caching 2.5.1, openpyxl 3.1.5, pytest 9.1.1, plotly 7.1.0. Dash API
  verified in env (run/use_pages/pages_folder/register_page/page_container — run_server REMOVED).
- Discovered: `venv/` (repo root) is a ROS 2 Jazzy env — DO NOT use; use `.venv`. PYTHONPATH
  leak via ~/.bashrc; sanitize with `env -u PYTHONPATH`.
- T2 DONE (2026-10-09): tests written first across tests/core, tests/adapters, tests/presentation,
  tests/e2e (85 tests). RED observed: first run `env -u PYTHONPATH .venv/bin/pytest -q`
  → "9 errors during collection" (ModuleNotFoundError: No module named 'app'); mid-run
  "15 failed, 68 passed, 2 errors" before implementations were fixed/stabilized.
- T3 DONE (2026-10-09): core/domain (dataset.py + entities.py ForecastFrame + granularity.py
  params.py metricas.py), core/ports (forecaster, dataset_reader, exporters), core/usecases (6).
- T4 DONE (2026-10-09): adapters csv_reader (sniffer+aliases+Excel), naive_stacional, holt_winters
  (statsmodels), bass, escenario_palancas, exportador (CSV «;» / JSON es-ES), caching (SimpleCache);
  gbm_exogenas.py = HONEST STUB raising NotImplementedError("Phase 3 (GBM) is not implemented yet")
  in its constructor — explicitly PENDING work, no fabricated results.
- T5 DONE (2026-10-09): app/app.py create_app() (use_pages, absolute pages/assets folders),
  root_shell grid 232px+minmax, sidebar from page_registry with lucide icons, dcc.Store
  (store-dataset / store-filtros local), 6 pages registered (paths: /, /datos, /modelos,
  /lanzamiento, /escenarios, /exportar), charts.py LAYOUT template + ci_band, ui/formatting es-ES.
- T6 DONE (2026-10-09): `env -u PYTHONPATH .venv/bin/pytest -q: 85 passed in 1.11s` (GREEN);
  boot smoke `env -u PYTHONPATH timeout 20 .venv/bin/python app/app.py` + `curl -s -o /dev/null
  -w "%{http_code}" http://127.0.0.1:8050` → 200 (SPV served, /_dash-layout → 200);
  import check `env -u PYTHONPATH .venv/bin/python -c "import app.app; import app.adapters;
  import app.core; ..."` → "imports ok"; README hexagonal structure section applied.
- Note: weekly ISO-Monday aggregation implemented with a explicit Monday floor
  (`fecha - weekday days`): pandas `to_period("W-MON")` anchors weeks Tue→Mon, which split
  Mondays out of their ISO week. Complete weeks = 7 unique dates per Monday group.
