#!/usr/bin/env python3
"""
Unify multiple environmental and shark trajectory datasets
into a single spatiotemporal grid using S2 geometry.

Now robust to column name variations like:
 - 'time', 'date', 'datetime' → time_bin
 - 'lat', 'Latitude' → latitude
 - 'lon', 'long', 'Longitude' → longitude
"""

import os
import glob
import pandas as pd
import numpy as np
import s2sphere
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================
DATA_DIRS = {
    "chlorophyll": "chlorophyll/sample",
    "depth": "depth/sample",
    "eke": "eke/sample",
    "light": "light/sample",
    "sst": "sst/sample",
    "sharks": "sharks/sample"
}

TIME_FREQ = "2H"           # Temporal resolution
S2_LEVEL = 8               # Spatial resolution (~1.2 km)
OUTPUT_DIR = "data"
OUTPUT_FILE = "unified_dataset.parquet"

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def normalize_columns(df):
    """Unify column names for latitude, longitude, and time."""
    rename_map = {}
    for col in df.columns:
        col_lower = col.lower()
        if col_lower in ["lat", "latitude", "lat_deg"]:
            rename_map[col] = "latitude"
        elif col_lower in ["lon", "long", "longitude", "lon_deg"]:
            rename_map[col] = "longitude"
        elif col_lower in ["time", "date", "datetime", "timestamp", "time_bin"]:
            rename_map[col] = "time_bin"
    df = df.rename(columns=rename_map)
    return df


def to_s2_cell(lat, lon, level=S2_LEVEL):
    """Return S2 cell id for given lat/lon."""
    latlng = s2sphere.LatLng.from_degrees(lat, lon)
    return s2sphere.CellId.from_lat_lng(latlng).parent(level).id()


def load_env_data(folder, value_name):
    """Recursively load and standardize environmental data."""
    files = glob.glob(os.path.join(folder, "**", "*.parquet"), recursive=True)
    if not files:
        print(f"⚠️ No files found in {folder}")
        return pd.DataFrame()

    dfs = []
    for f in files:
        try:
            df = pd.read_parquet(f)
            df = normalize_columns(df)
            if not all(c in df.columns for c in ["latitude", "longitude", "time_bin"]):
                print(f"⚠️ Skipping {f}, missing one of lat/lon/time columns")
                continue

            df["time_bin"] = pd.to_datetime(df["time_bin"]).dt.floor(TIME_FREQ)
            df["s2_cell_id"] = [
                to_s2_cell(lat, lon) for lat, lon in zip(df["latitude"], df["longitude"])
            ]
            df = df.groupby(["s2_cell_id", "time_bin"], as_index=False).mean(numeric_only=True)
            # keep only relevant columns
            keep_cols = ["s2_cell_id", "time_bin", value_name]
            if value_name in df.columns:
                df = df[keep_cols]
            else:
                df[value_name] = np.nan
                df = df[keep_cols]
            dfs.append(df)

        except Exception as e:
            print(f"❌ Error reading {f}: {e}")

    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


def load_sharks_data(folder):
    """Recursively load and aggregate shark trajectory data."""
    files = glob.glob(os.path.join(folder, "**", "*.parquet"), recursive=True)
    if not files:
        print(f"⚠️ No shark files found in {folder}")
        return pd.DataFrame()

    dfs = []
    for f in files:
        try:
            df = pd.read_parquet(f)
            df = normalize_columns(df)
            if not all(c in df.columns for c in ["latitude", "longitude", "time_bin"]):
                print(f"⚠️ Skipping {f}, missing one of lat/lon/time columns")
                continue

            df["time_bin"] = pd.to_datetime(df["time_bin"]).dt.floor(TIME_FREQ)
            df["s2_cell_id"] = [
                to_s2_cell(lat, lon) for lat, lon in zip(df["latitude"], df["longitude"])
            ]
            agg = df.groupby(["s2_cell_id", "time_bin"]).size().reset_index(name="shark_count")
            dfs.append(agg)
        except Exception as e:
            print(f"❌ Error reading {f}: {e}")

    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


def get_s2_centers(s2_ids):
    """Return DataFrame with geometric centers (lat, lon) of S2 cells."""
    centers = []
    for cell_id in s2_ids:
        cell = s2sphere.Cell(s2sphere.CellId(cell_id))
        center_point = cell.get_center()
        latlng = s2sphere.LatLng.from_point(center_point)
        lat, lon = latlng.lat().degrees, latlng.lng().degrees
        centers.append((cell_id, lat, lon))
    return pd.DataFrame(centers, columns=["s2_cell_id", "latitude", "longitude"])


# =========================================================
# MAIN
# =========================================================
def main():
    print("🐋 Building unified spatiotemporal dataset (2-hour bins)...")

    chl = load_env_data(DATA_DIRS["chlorophyll"], "measure_chlorophyll")
    depth = load_env_data(DATA_DIRS["depth"], "depth")
    eke = load_env_data(DATA_DIRS["eke"], "eke_information")
    light = load_env_data(DATA_DIRS["light"], "normalized_light")
    sst = load_env_data(DATA_DIRS["sst"], "sst")
    sharks = load_sharks_data(DATA_DIRS["sharks"])

    datasets = [chl, depth, eke, light, sst, sharks]
    datasets = [d for d in datasets if not d.empty]

    if not datasets:
        print("❌ No datasets loaded. Check folder paths.")
        return

    # Merge all datasets
    base = datasets[0]
    for df in datasets[1:]:
        base = base.merge(df, on=["s2_cell_id", "time_bin"], how="outer")

    # Add lat/lon centers for each s2_cell_id
    centers = get_s2_centers(base["s2_cell_id"].dropna().unique())
    base = base.merge(centers, on="s2_cell_id", how="left")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    base.to_parquet(output_path, index=False)

    print(f"✅ Unified dataset saved to {output_path}")
    print(f"📏 Shape: {base.shape}")
    print(base.head())


if __name__ == "__main__":
    main()
