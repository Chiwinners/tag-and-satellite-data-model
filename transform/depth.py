import h5py
import datetime
import pandas as pd
from pathlib import Path

def return_date(gps_epoch, delta_time):
    """Convert GPS epoch + delta_time into UTC datetime objects."""
    leap_seconds = 18
    gps_start_times = gps_epoch + delta_time
    base_time = datetime.datetime(1980, 1, 6)
    return [
        base_time + datetime.timedelta(seconds=float(t) - leap_seconds)
        for t in gps_start_times
    ]

def load_file(filename):
    # Open the HDF5 file
    with h5py.File(filename, "r") as f:
        beam = "gt1l"  # choose one beam; can be changed

        # Extract required datasets
        lat = f[beam]["lat_ph"][:]
        lon = f[beam]["lon_ph"][:]
        surface_h = f[beam]["surface_h"][:]
        delta_time = f[beam]["delta_time"][:]
        gps_epoch = f["ancillary_data"]["atlas_sdp_gps_epoch"][()]

        # Compute UTC times
        utc_times = return_date(gps_epoch, delta_time)

        # Ensure consistent lengths
        min_len = min(len(lat), len(lon), len(surface_h), len(utc_times))
        lat, lon, surface_h, utc_times = lat[:min_len], lon[:min_len], surface_h[:min_len], utc_times[:min_len]

        # Create DataFrame
        df = pd.DataFrame({
            "latitude": lat,
            "longitude": lon,
            "utc_time": [t.isoformat() for t in utc_times],
            "surface_height": surface_h
        })

        # Save to CSV
        df.to_csv("env_depth.csv", index=False)
    
    return df

def main():
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "downloads/depth"
    output_dir = project_root / "data/depth"
    output_dir.mkdir(exist_ok=True)

    all_files = sorted(data_dir.glob("*.h5"))
    if not all_files:
        print("⚠️ No .h5 files found in the 'data' directory.")
        return

    for file in all_files:
        print(f"🔍 Processing {file.name} ...")
        try:
            df = load_file(file)
            output_csv = output_dir / f"{file.stem}.csv"
            df.to_csv(output_csv, index=False)
            print(f"✅ Saved: {output_csv} ({len(df)} rows).")
        except Exception as e:
            print(f"❌ Error processing {file.name}: {e}")

if __name__ == "__main__":
    main()
