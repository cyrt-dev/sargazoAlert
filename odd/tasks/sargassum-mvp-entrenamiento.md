# SARGASSUM MVP — entrenamiento (Excel → modelo)

**Objective:** Local training MVP that loads the single SATsum Excel, trains a regional XGBoost regressor with temporal backtesting for horizons D+1…D+7, and exports artifacts under `outputs/`.
**Branch:** `feat/sargassum-mvp`
**Delivery:** ask-on-risk; commit only when the user explicitly requests one
**Test runner:** notebook self-checks + path/JSON validation

## Specs

### S1 — Naming
Do NOT call it "acelerado" / "accelerated" anywhere in docs, README, comments, or commit messages. Prefer "entrenamiento", "training MVP", "SARGASSUM MVP".

### S2 — Data layout
- `data/raw/` — Excel `SATsum_diaria_serie_completa_2dr_zee_caribbean_2026-11-20_1632.xlsx`
- `data/processed/` — optional processed Parquet/CSV (gitignored content)
- Source sheet: `Datos`; target column: `2-day combined product · 2dr · OFFICIAL daily figure (t)` normalized as `biomass_2dr_t`.

### S3 — Notebook P0
`notebooks/entrenamiento_satsum.ipynb`: load Excel, define target 2dr, features, persistence baseline, XGBoost regressor, temporal backtesting for D+1..D+7 without leakage, save artifacts under `outputs/`.

### S4 — Outputs and deps
- `outputs/{models,metrics,figures,forecasts}/` with `.gitkeep` as needed
- `requirements.txt` ML stack (Python 3.11/3.12): pandas numpy openpyxl pyarrow scikit-learn xgboost matplotlib seaborn joblib jupyter

### S5 — README
Document how to run the notebook locally; coastal arribazón cannot be validated from this file alone.

## Tasks

| ID | Specs | Route | Status | Evidence |
|----|-------|-------|--------|----------|
| T1 | S1 | inline | done | Naming consistent across README/notebook |
| T2 | S2,S4 | inline | done | Excel under `data/raw/`; ML `requirements.txt`; outputs layout |
| T3 | S3 | inline | done | Notebook authored and executed end-to-end |
| T4 | S5 | inline | done | Spanish README for local training MVP |

## Log

### L1 — Scope
Training MVP from a single SATsum Excel; regional forecast only; no coastal-arrival claims.

### L2 — 2026-11-20 — Delivered
- Notebook executed; models h1–h7, metrics, figure, demo forecast under `outputs/`.
- For D+1, persistence MAE beat XGBoost on the held-out test window; D+2…D+7 XGBoost improved MAE (`outputs/metrics/horizon_comparison.csv`).
