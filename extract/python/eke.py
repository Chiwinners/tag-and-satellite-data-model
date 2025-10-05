import cdsapi
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import multiprocessing
import time

# === CONFIGURATION ===
DATASET = "satellite-sea-level-global"
OUTPUT_DIR = "downloads/eke/data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

YEARS = ["2014", "2015", "2016", "2017"]
MONTHS = [f"{m:02d}" for m in range(1, 13)]
DAYS = [f"{d:02d}" for d in range(1, 32)]

MAX_RETRIES = 3
MAX_WORKERS = min(8, multiprocessing.cpu_count())  # Limit threads to 8 or CPU cores

# === CLIENT INSTANCE ===
client = cdsapi.Client()


def download_day(year: str, month: str, day: str) -> tuple[str, bool]:
    """
    Download a single day of data. Returns (filename, success_flag)
    """
    filename = f"{DATASET}_{year}{month}{day}.nc"
    filepath = os.path.join(OUTPUT_DIR, filename)

    # Skip if already exists
    if os.path.exists(filepath):
        return (filename, True)

    request = {
        "variable": ["daily"],
        "year": [year],
        "month": [month],
        "day": [day],
        "version": "vdt2018",
    }

    # Retry mechanism
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client.retrieve(DATASET, request).download(filepath)
            return (filename, True)
        except Exception as e:
            time.sleep(2 * attempt)  # exponential backoff
            if attempt == MAX_RETRIES:
                return (filename, False)
    return (filename, False)


def main():
    # Prepare all tasks
    tasks = [(y, m, d) for y in YEARS for m in MONTHS for d in DAYS]
    total = len(tasks)

    print(f"🚀 Starting downloads to {OUTPUT_DIR}")
    print(f"Using {MAX_WORKERS} parallel threads and retry={MAX_RETRIES}")

    # Run downloads in parallel with progress bar
    success_count = 0
    fail_count = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(download_day, y, m, d): (y, m, d) for (y, m, d) in tasks}

        for future in tqdm(as_completed(futures), total=total, desc="Downloading", unit="file"):
            filename, success = future.result()
            if success:
                success_count += 1
            else:
                fail_count += 1

    print(f"\n✅ Completed downloads.")
    print(f"   Successful: {success_count}")
    print(f"   Failed:     {fail_count}")
    print(f"   Files saved in: {os.path.abspath(OUTPUT_DIR)}")


if __name__ == "__main__":
    main()
