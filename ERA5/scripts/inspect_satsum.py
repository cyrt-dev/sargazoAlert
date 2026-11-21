from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
XLSX = DATA / "SATsum_diaria_serie_completa_2dr_zee_caribbean_2026-11-20_1632 (1).xlsx"


def main():
    xls = pd.ExcelFile(XLSX)
    df = pd.read_excel(XLSX, sheet_name="Datos")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    valid = df[df["Date"].notna()].copy()

    target = "2-day combined product · 2dr · OFFICIAL daily figure (t)"
    dates = pd.DatetimeIndex(valid["Date"])
    expected = pd.date_range(dates.min(), dates.max(), freq="D")

    print(f"sheets={xls.sheet_names}")
    print(f"shape={df.shape}")
    print(f"columns={df.columns.tolist()}")
    print(f"date_min={dates.min().date()} date_max={dates.max().date()}")
    print(f"unique_dates={dates.nunique()} duplicate_dates={dates.duplicated().sum()}")
    print(f"missing_dates={len(expected.difference(dates))}")
    print(f"zones={valid['Zone'].value_counts(dropna=False).to_dict()}")
    print(f"target_missing={valid[target].isna().sum()} target_zero={valid[target].eq(0).sum()} target_negative={(valid[target] < 0).sum()}")
    print(f"target_range=[{valid[target].min()}, {valid[target].max()}]")
    print("metadata:")
    metadata = pd.read_excel(XLSX, sheet_name="Metadatos")
    print(metadata.to_string(index=False))


if __name__ == "__main__":
    main()
