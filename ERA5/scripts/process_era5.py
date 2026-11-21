import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr


def time_name(ds):
    for name in ("valid_time", "time"):
        if name in ds.coords:
            return name
    raise ValueError("No valid_time/time coordinate found")


def process_file(path: Path):
    ds = xr.open_dataset(path)
    tname = time_name(ds)
    ds = ds.assign_coords({tname: pd.to_datetime(ds[tname].values, utc=True)})
    daily = pd.DataFrame(index=pd.DatetimeIndex(ds[tname].values, tz="UTC").normalize().unique())

    if "u10" in ds:
        spatial_dims = [d for d in ds["u10"].dims if d != tname]
        u10 = ds["u10"].mean(dim=spatial_dims).to_series()
        u10.index = pd.to_datetime(u10.index, utc=True).normalize()
        daily["u10_mean"] = u10.groupby(level=0).mean()
    if "v10" in ds:
        spatial_dims = [d for d in ds["v10"].dims if d != tname]
        v10 = ds["v10"].mean(dim=spatial_dims).to_series()
        v10.index = pd.to_datetime(v10.index, utc=True).normalize()
        daily["v10_mean"] = v10.groupby(level=0).mean()
    if "msl" in ds:
        spatial_dims = [d for d in ds["msl"].dims if d != tname]
        msl = (ds["msl"].mean(dim=spatial_dims) / 100.0).to_series()
        msl.index = pd.to_datetime(msl.index, utc=True).normalize()
        daily["msl_mean_hpa"] = msl.groupby(level=0).mean()

    if "tp" in ds:
        # ERA5 precipitation is accumulated; preserve interval values by differencing hourly cumulative values.
        tp = ds["tp"]
        spatial_dims = [d for d in tp.dims if d != tname]
        spatial_mean = tp.mean(dim=spatial_dims)
        hourly_mm = spatial_mean.to_series().diff()
        hourly_mm.iloc[0] = spatial_mean.to_series().iloc[0]
        hourly_mm = hourly_mm.clip(lower=0) * 1000.0
        hourly_mm.index = pd.to_datetime(hourly_mm.index, utc=True).normalize()
        daily["tp_total_mm"] = hourly_mm.groupby(level=0).sum()

    if "u10_mean" in daily and "v10_mean" in daily:
        daily["wind_speed_mean"] = np.sqrt(daily["u10_mean"] ** 2 + daily["v10_mean"] ** 2)

    daily.index = pd.to_datetime(daily.index, utc=True).normalize()
    daily["region"] = "Mexican Caribbean EEZ"
    daily["date"] = daily.index
    ds.close()
    return daily.reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/era5")
    parser.add_argument("--output", default="data/processed/era5_daily.csv")
    args = parser.parse_args()

    frames = [process_file(p) for p in sorted(Path(args.input).rglob("*.nc"))]
    if not frames:
        raise SystemExit("No NetCDF files found")
    out = pd.concat(frames).sort_values("date")
    numeric_columns = out.select_dtypes(include="number").columns
    out = out.groupby(["date", "region"], as_index=False)[list(numeric_columns)].mean()
    required = pd.date_range(out["date"].min(), out["date"].max(), freq="D", tz="UTC")
    missing = required.difference(pd.DatetimeIndex(out["date"]))
    print(f"rows={len(out)} date_min={out['date'].min()} date_max={out['date'].max()} missing_days={len(missing)}")
    print(f"missing_dates={missing.strftime('%Y-%m-%d').tolist()[:20]}")
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
