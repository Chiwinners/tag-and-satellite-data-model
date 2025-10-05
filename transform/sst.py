import rasterio
import numpy as np
import pandas as pd
import pyproj
from datetime import datetime
from pathlib import Path

def load_file(filename):
    """Load SST data from a single ASTER .tif file and compute its gradient."""
    with rasterio.open(filename) as src:
        sst = src.read(1).astype(float)
        transform = src.transform
        crs = src.crs

    # Mask invalid or missing values
    sst = np.where((sst <= 0) | np.isnan(sst), np.nan, sst)

    # Compute spatial gradient (Kelvin/m)
    dx = transform.a   # pixel width
    dy = -transform.e  # pixel height (negative in geotransform)
    dT_dy, dT_dx = np.gradient(sst, dy, dx)
    sst_gradient = np.sqrt(dT_dx**2 + dT_dy**2)

    # Build coordinate grids
    height, width = sst.shape
    rows, cols = np.meshgrid(np.arange(height), np.arange(width), indexing="ij")
    xs, ys = rasterio.transform.xy(transform, rows, cols)
    xs, ys = np.array(xs), np.array(ys)

    # Convert to lat/lon if projected
    if crs and crs.is_projected:
        transformer = pyproj.Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
        lon, lat = transformer.transform(xs, ys)
    else:
        lon, lat = xs, ys

    # Extract timestamp from filename (e.g. AST_08_00411202019145501_20250906013202_SKT_QA_DataPlane.tif)
    try:
        date_str = filename.stem.split("_")[3]  # '20250906013202'
        bin_time = datetime.strptime(date_str, "%Y%m%d%H%M%S").isoformat()
    except Exception:
        bin_time = None

    # Flatten and mask valid pixels
    mask = ~np.isnan(sst) & ~np.isnan(sst_gradient)
    lat_flat = lat.flatten()[mask.flatten()]
    lon_flat = lon.flatten()[mask.flatten()]
    sst_flat = sst.flatten()[mask.flatten()]
    grad_flat = sst_gradient.flatten()[mask.flatten()]

    # Build two DataFrames
    df_sst = pd.DataFrame({
        "latitude": lat_flat,
        "longitude": lon_flat,
        "bin_time": bin_time,
        "sst": sst_flat
    })

    df_dsst = pd.DataFrame({
        "latitude": lat_flat,
        "longitude": lon_flat,
        "bin_time": bin_time,
        "sst_gradient": grad_flat
    })

    return df_sst, df_dsst


def main():
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "downloads/sst"
    sst_outdir = project_root / "data/sst"
    dsst_outdir = project_root / "data/dsst"
    sst_outdir.mkdir(parents=True, exist_ok=True)
    dsst_outdir.mkdir(parents=True, exist_ok=True)

    all_files = sorted(data_dir.glob("*.tif"))
    if not all_files:
        print("⚠️ No .tif files found in the 'downloads/sst' directory.")
        return

    for file in all_files:
        print(f"🔍 Processing {file.name} ...")
        try:
            df_sst, df_dsst = load_file(file)

            sst_csv = sst_outdir / f"{file.stem}_sst.csv"
            dsst_csv = dsst_outdir / f"{file.stem}_dsst.csv"

            df_sst.to_csv(sst_csv, index=False)
            df_dsst.to_csv(dsst_csv, index=False)

            print(f"✅ Saved: {sst_csv} ({len(df_sst)} rows)")
            print(f"✅ Saved: {dsst_csv} ({len(df_dsst)} rows)")
        except Exception as e:
            print(f"❌ Error processing {file.name}: {e}")

if __name__ == "__main__":
    main()
