from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


def test_satsum_integrity():
    p = ROOT / "data/raw/satsum/SATsum_diaria_serie_completa_2dr_zee_caribbean_2026-11-20_1632 (1).xlsx"
    df = pd.read_excel(p, sheet_name="Datos")
    df["Date"] = pd.to_datetime(df["Date"])
    assert df["Date"].is_monotonic_increasing
    assert df["Date"].is_unique


def test_processed_outputs():
    era = ROOT / "data/processed/era5_daily.csv"
    model = ROOT / "data/processed/model_dataset.csv"
    if not era.exists():
        return
    df = pd.read_csv(era)
    assert not df.duplicated(["date", "region"]).any()
    if "wind_speed_mean" in df:
        assert (df["wind_speed_mean"] >= 0).all()
    if model.exists():
        merged = pd.read_csv(model)
        assert "target_t_plus_7" in merged
