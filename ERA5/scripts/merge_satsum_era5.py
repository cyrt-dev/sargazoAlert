import argparse
from pathlib import Path

import pandas as pd

TARGET = "2-day combined product · 2dr · OFFICIAL daily figure (t)"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--excel", default="data/raw/satsum/SATsum_diaria_serie_completa_2dr_zee_caribbean_2026-11-20_1632 (1).xlsx")
    parser.add_argument("--era5", default="data/processed/era5_daily.csv")
    parser.add_argument("--output", default="data/processed/model_dataset.csv")
    args = parser.parse_args()

    satsum = pd.read_excel(args.excel, sheet_name="Datos")
    satsum["date"] = pd.to_datetime(satsum["Date"], errors="coerce", utc=True).dt.normalize()
    satsum = satsum.dropna(subset=["date"]).drop_duplicates("date")
    satsum["region"] = "Mexican Caribbean EEZ"

    era = pd.read_csv(args.era5)
    era["date"] = pd.to_datetime(era["date"], utc=True).dt.normalize()

    merged = satsum.merge(era, on=["date", "region"], how="left", validate="one_to_one")
    merged = merged.sort_values("date").reset_index(drop=True)

    for lag in (1, 3, 7):
        for column in [c for c in era.columns if c not in ("date", "region")]:
            merged[f"{column}_lag_{lag}"] = merged[column].shift(lag)

    for window in (3, 7):
        for column in [c for c in era.columns if c not in ("date", "region")]:
            merged[f"{column}_rollmean_{window}"] = merged[column].shift(1).rolling(window, min_periods=window).mean()

    merged["target_t_plus_7"] = merged[TARGET].shift(-7)
    coverage = merged[[c for c in era.columns if c not in ("date", "region")]].notna().mean().mean()

    expected = pd.date_range(merged["date"].min(), merged["date"].max(), freq="D", tz="UTC")
    missing_dates = len(expected.difference(pd.DatetimeIndex(merged["date"])))
    print(f"sat_rows={len(satsum)} era_rows={len(era)} merged_rows={len(merged)}")
    print(f"era_feature_coverage={coverage:.3%} missing_calendar_dates={missing_dates}")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output, index=False)


if __name__ == "__main__":
    main()
