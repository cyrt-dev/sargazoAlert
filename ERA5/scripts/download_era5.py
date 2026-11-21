import argparse
import calendar
import logging
import time
import zipfile
from datetime import date
from pathlib import Path

import cdsapi

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

VARIABLES = [
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "mean_sea_level_pressure",
    "total_precipitation",
]


def month_dates(year: int, month: int):
    last = calendar.monthrange(year, month)[1]
    return f"{year:04d}-{month:02d}-01", f"{year:04d}-{month:02d}-{last:02d}"


def download_month(year: int, month: int, area, destination: Path, variables, retries: int, day: int | None = None):
    destination.mkdir(parents=True, exist_ok=True)
    start, end = month_dates(year, month)
    target = destination / f"era5_{year:04d}_{month:02d}.nc"
    if target.exists() and target.stat().st_size > 0:
        logging.info("Already exists: %s", target)
        return target

    zip_target = destination / f"era5_{year:04d}_{month:02d}.zip"
    if zip_target.exists() and zip_target.stat().st_size > 0:
        extract_dir = destination / f"{year:04d}_{month:02d}"
        with zipfile.ZipFile(zip_target) as archive:
            archive.extractall(extract_dir)
        logging.info("Already extracted: %s", zip_target)
        return zip_target

    request = {
        "product_type": "reanalysis",
        "variable": variables,
        "year": str(year),
        "month": f"{month:02d}",
        "day": ([f"{day:02d}"] if day is not None else [f"{day_num:02d}" for day_num in range(1, calendar.monthrange(year, month)[1] + 1)]),
        "time": [f"{hour:02d}:00" for hour in range(24)],
        "area": area,
        "format": "netcdf",
    }
    client = cdsapi.Client()
    for attempt in range(1, retries + 1):
        try:
            logging.info("Downloading %s", target.name)
            client.retrieve("reanalysis-era5-single-levels", request, str(target))
            if target.stat().st_size == 0:
                raise RuntimeError("Downloaded file is empty")
            if zipfile.is_zipfile(target):
                zip_target = target.with_suffix(".zip")
                target.rename(zip_target)
                extract_dir = destination / f"{year:04d}_{month:02d}"
                with zipfile.ZipFile(zip_target) as archive:
                    archive.extractall(extract_dir)
                return zip_target
        except Exception as exc:
            logging.exception("Attempt %d/%d failed: %s", attempt, retries, exc)
            if target.exists():
                target.unlink()
            if attempt < retries:
                time.sleep(30 * attempt)
    raise RuntimeError(f"Could not download {target.name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, help="YYYY-MM")
    parser.add_argument("--end", required=True, help="YYYY-MM")
    parser.add_argument("--area", nargs=4, type=float, default=[21.5, -90.0, 17.5, -86.0],
                        metavar=("NORTH", "WEST", "SOUTH", "EAST"))
    parser.add_argument("--dest", default="data/raw/era5")
    parser.add_argument("--variables", nargs="*", default=VARIABLES)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--day", type=int, default=None, help="Día concreto dentro de --start y --end")
    args = parser.parse_args()

    start = date.fromisoformat(args.start + "-01")
    end = date.fromisoformat(args.end + "-01")
    if end < start:
        raise ValueError("--end precedes --start")

    destination = Path(args.dest)
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        download_month(year, month, args.area, destination, args.variables, args.retries, args.day)
        if month == 12:
            year, month = year + 1, 1
        else:
            month += 1


if __name__ == "__main__":
    main()
