#!/usr/bin/env python3
import os
import re
import sys
import math
import shutil
import random
from pathlib import Path
from typing import Callable, Dict, List, Tuple

# -------------------------
# CONFIGURATION
# -------------------------
EXCLUDE_FOLDERS = {"sharks", "seaflower"}
DEFAULT_RATIO = 0.0005  # 0.05 %
MAX_FILE_SIZE_MB = 100  # absolute upper limit

# -------------------------
# Grouping methods (per dataset)
# -------------------------

def key_modis_l2_nc(filename: str) -> str:
    """AQUA_MODIS.*.nc → prefix through YYYYMMDDThhmmss"""
    name = Path(filename).name
    m = re.search(r"\d{8}T\d{6}", name)
    return name[:m.end()] if m else Path(filename).stem

def key_ast_sst_tif(filename: str) -> str:
    """AST_08_*_YYYYMMDDhhmmss_* → prefix through 14-digit timestamp"""
    name = Path(filename).name
    m = re.search(r"\d{14}", name)
    return name[:m.end()] if m else Path(filename).stem

def key_icesat2_atl24_h5(filename: str) -> str:
    """ATL24_YYYYMMDDhhmmss_* → group by prefix"""
    name = Path(filename).name
    m = re.match(r"^(ATL24)_(\d{14})", name)
    return f"{m.group(1)}_{m.group(2)}" if m else Path(filename).stem

def key_satellite_nc(filename: str) -> str:
    """satellite-sea-level-global_YYYYMMDD.nc → group by date"""
    name = Path(filename).stem
    m = re.search(r"(\d{8})", name)
    return m.group(1) if m else name

def key_light_par_nc(filename: str) -> str:
    """AQUA_MODIS.YYYYMMDD.L3b.DAY.PAR.x.nc → group by date"""
    name = Path(filename).name
    m = re.search(r"\d{8}", name)
    return m.group(0) if m else Path(filename).stem

def key_generic(filename: str) -> str:
    """Generic fallback."""
    name = Path(filename).name
    m = re.search(r"\d{14}", name)
    return name[:m.end()] if m else Path(filename).stem

# Map folder → grouping method
FOLDER_METHODS: Dict[str, Callable[[str], str]] = {
    "clorophyll": key_modis_l2_nc,
    "sst": key_ast_sst_tif,
    "depth": key_icesat2_atl24_h5,
    "eke": key_satellite_nc,
    "light": key_light_par_nc,
}

# -------------------------
# Helpers
# -------------------------

def iter_files_recursive(root: Path):
    """Yield all files recursively under root."""
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            p = Path(dirpath) / fn
            if p.is_file():
                yield p

def group_files_under_data(data_dir: Path, key_fn: Callable[[str], str]):
    """Group files by item key."""
    groups: Dict[Tuple[Path, str], List[Path]] = {}
    for f in iter_files_recursive(data_dir):
        size_mb = f.stat().st_size / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            # skip large files entirely
            continue
        rel_parent = f.parent.relative_to(data_dir)
        item_key = key_fn(f.name)
        groups.setdefault((rel_parent, item_key), []).append(f)
    return groups

def sample_groups(groups, ratio, seed):
    """Select a random subset of groups based on ratio."""
    keys = list(groups.keys())
    if not keys:
        return []
    n_items = len(keys)
    n_sample = max(1, math.ceil(n_items * ratio))
    rng = random.Random(seed)
    return rng.sample(keys, k=n_sample)

def copy_selected(groups, selected_keys, data_dir, sample_dir):
    """Copy selected groups to sample_dir."""
    copied = 0
    for (rel_parent, _key) in selected_keys:
        for src in groups[(rel_parent, _key)]:
            dst_dir = sample_dir / rel_parent
            dst_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst_dir / src.name)
            copied += 1
    return copied

# -------------------------
# Core logic
# -------------------------

def process_dataset(downloads_root: Path, dataset: str, ratio: float, seed: int | None):
    ds_dir = downloads_root / dataset
    data_dir = ds_dir / "data"
    sample_dir = ds_dir / "sample"

    if not data_dir.is_dir():
        print(f"⚠️ Skipping '{dataset}': '{data_dir}' not found.")
        return

    key_fn = FOLDER_METHODS.get(dataset, key_generic)
    groups = group_files_under_data(data_dir, key_fn)

    n_items = len(groups)
    if n_items == 0:
        print(f"⚠️ No eligible (<{MAX_FILE_SIZE_MB} MB) files in '{data_dir}'.")
        return

    selected = sample_groups(groups, ratio, seed)
    sample_dir.mkdir(parents=True, exist_ok=True)
    copied = copy_selected(groups, selected, data_dir, sample_dir)

    print(
        f"✅ [{dataset}] Sampled {len(selected)}/{n_items} groups "
        f"→ Copied {copied} files (<{MAX_FILE_SIZE_MB} MB)."
    )

# -------------------------
# Entry point
# -------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python sample_downloads.py <downloads_root> [--ratio 0.0005] [--seed 42]")
        sys.exit(1)

    downloads_root = Path(sys.argv[1]).expanduser().resolve()
    ratio = DEFAULT_RATIO
    seed = None

    args = sys.argv[2:]
    if "--ratio" in args:
        try:
            ratio = float(args[args.index("--ratio") + 1])
        except Exception:
            print("⚠️ Invalid ratio; using default 0.0005")
    if "--seed" in args:
        try:
            seed = int(args[args.index("--seed") + 1])
        except Exception:
            pass

    subfolders = [
        f for f in downloads_root.iterdir()
        if f.is_dir() and f.name not in EXCLUDE_FOLDERS
    ]

    print(f"🚀 Sampling {len(subfolders)} datasets under {downloads_root}")
    for folder in subfolders:
        process_dataset(downloads_root, folder.name, ratio, seed)


if __name__ == "__main__":
    main()
