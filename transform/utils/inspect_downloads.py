import os
import random
import humanize
from pathlib import Path
from tqdm import tqdm

# === CONFIGURATION ===
ROOT_DIR = Path("downloads")
EXCLUDE_FOLDERS = {"sharks", "seaflower"}
SAMPLE_LIMIT = 20  # number of files to show per folder


def summarize_folder(folder: Path):
    """Return total files, subdirs, and size in bytes for a folder (recursively)."""
    total_files = 0
    total_size = 0
    subdirs = set()

    for dirpath, dirnames, filenames in os.walk(folder):
        subdirs.update(Path(dirpath).relative_to(folder).parts[:1])
        total_files += len(filenames)
        for f in filenames:
            try:
                total_size += (Path(dirpath) / f).stat().st_size
            except FileNotFoundError:
                pass
    return total_files, len(subdirs), total_size


def sample_files(folder: Path, limit: int = SAMPLE_LIMIT):
    """Return up to 'limit' random files from a folder (recursively)."""
    all_files = []
    for dirpath, _, filenames in os.walk(folder):
        for f in filenames:
            all_files.append(Path(dirpath) / f)
    if not all_files:
        return []
    sample = random.sample(all_files, min(limit, len(all_files)))
    return sample


def inspect_downloads():
    print(f"🔍 Inspecting folders under: {ROOT_DIR.resolve()}")
    print("---------------------------------------------------------")

    if not ROOT_DIR.exists():
        print(f"❌ Folder '{ROOT_DIR}' not found.")
        return

    subfolders = [
        f for f in ROOT_DIR.iterdir()
        if f.is_dir() and f.name not in EXCLUDE_FOLDERS
    ]

    if not subfolders:
        print("⚠️ No subfolders found.")
        return

    for folder in tqdm(subfolders, desc="Inspecting", unit="folder"):
        total_files, total_subdirs, total_size = summarize_folder(folder)
        samples = sample_files(folder)

        print(f"\n📁 Folder: {folder.name}")
        print(f"   Subfolders: {total_subdirs}")
        print(f"   Files: {total_files}")
        print(f"   Size: {humanize.naturalsize(total_size)}")
        print("   Sample of files:")
        if not samples:
            print("     (no files found)")
        else:
            for s in samples[:SAMPLE_LIMIT]:
                rel = s.relative_to(ROOT_DIR)
                print(f"     - {rel}")


if __name__ == "__main__":
    inspect_downloads()
