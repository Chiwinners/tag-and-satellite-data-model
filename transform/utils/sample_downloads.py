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
# Grouping methods per dataset
# -------------------------

def key_modis_l2_nc(filename: str) -> str:
    """AQUA_MODIS.*.nc → prefix through YYYYMMDDThhmmss"""
    name = Path(filename).name
    m = re.search(r"\d{8}T\d{6}", name)
    if m:
        return name[: m.end()]
    idx = name.find(".L2")
    return name[:idx] if idx != -1 else Path(filename).stem

def key_ast_sst_tif(filename: str) -> str:
    """AST_08_*_YYYYMMDDhhmmss_* → prefix through 14-digit timestamp"""
    name = Path(filename).name
    m = re.search(r"\d{14}", name)
    if m:
        return name[: m.end()]
    stem = Path(filename).stem
    return stem.rsplit("_", 1)[0] if "_" in stem else stem

def key_icesat2_atl24_h5(filename: str) -> str:
    """ATL24_YYYYMMDDhhmmss_* → group by prefix"""
    name = Path(filename).name
    m = re.match(r"^(ATL24)_(\d{14})", name)
    if m:
        return f"{m.group(1)}_{m.group(2)}"
    stem = Path(filename).stem
    parts = stem.split("_")
    return "_".join(parts[:2]) if len(parts) >= 2 else stem

def key_satellite_nc(filename: str) -> str:
    """satellite-sea-level-global_YYYYMMDD.nc → group by YYYYMMDD"""
    name = Path(filename).stem
    m = re.search(r"(\d{8})", name)
    return m.group(1) if m else name

def key_light_par_nc(filename: str) -> str:
    """AQUA_MODIS.YYYYMMDD.L3b.DAY.PAR.x.nc → group by date"""
    name = Path(filename).name
    m = re.search(r"\d{8}", name)
    return m.group(0) if m else Path(filename).stem

def key_generic(filename: str) -> str:
    """Generic fallback: try any timestamp, else stem"""
    name = Path(filename).name
    m = re.search(r"\d{8}T\d{6}", name)
    if m:
        return name[: m.end()]
    m = re.search(r"\d{14}", name)
    if m:
        return name[: m.end()]
    return Path(filename).stem

# -------------------------
# Folder → grouping method mapping
# -------------------------
FOLDER_METHODS: Dict[str, Callable[[str], str]] = {
    "clorophyll": key_modis_l2_nc,    # AQUA_MODIS.*.nc
    "sst":        key_ast_sst_tif,    # AST_08_*_YYYYMMDDhhmmss_*.tif
    "depth":      key_icesat2_atl24_h5, # ATL24_*.h5
    "eke":        key_satellite_nc,   # satellite-sea-level-global_YYYYMMDD.nc
    "light":      key_light_par_nc,   # AQUA_MODIS.YYYYMMDD.L3b.DAY.PAR.x.nc
}

EXCLUDE_FOLDERS = {"sharks", "seaflower"}
DEFAULT_RATIO = 0.0005  # 0.05%

# -------------------------
# Helpers
# -------------------------

def iter_files_recursive(root: Path):
    """Yield all regular files under root (recursive)."""
    for dirpath, _, filenames in os.walk(root):
        d = Path(dirpath)
        for fn in filenames:
            p = d / fn
            if p.is_file():
                yield p

def group_files_under_data(data_dir: Path, key_fn: Callable[[str], str]) -> Dict[Tuple[Path, str], List[Path]]:
    """Group files under data_dir by (relative_parent_dir_from_data, item_key)."""
    groups: Dict[Tuple[Path, str], List[Path]] = {}
    for f in iter_files_recursive(data_dir):
        rel_parent = f.parent.relative_to(data_dir)
        item_key = key_fn(f.name)
        groups.setdefault((rel_parent, item_key), []).append(f)
    return groups

def sample_groups(groups: Dict[Tuple[Path, str], List[Path]], ratio: float, seed: int | None) -> List[Tuple[Path, str]]:
    """Pick ~ratio of group keys (at least 1 if any exist)."""
    keys = list(groups.keys())
    if not keys:
        return []
    n_items = len(keys)
    n_sample = max(1, math.ceil(n_items * ratio))
    rng = random.Random(seed)
    return rng.sample(keys, k=n_sample)

def copy_selected(groups, selected_keys, data_dir: Path, sample_dir: Path) -> int:
    """Copy selected groups to sample_dir preserving structure."""
    copied = 0
    for (rel_parent, _key) in selected_keys:
        for src in groups[(rel_parent, _key)]:
            dst_dir = sample_dir / rel_parent
            dst_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst_dir / src.name)
            copied += 1
    return copied

# -------------------------
# Core pipeline
# -------------------------

def process_dataset(downloads_root: Path, dataset: str, ratio: float, seed: int | None):
    """Sample dataset under downloads/<dataset>/data → downloads/<dataset>/sample."""
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
        print(f"⚠️ No files found in '{data_dir}'.")
        return

    selected = sample_groups(groups, ratio, seed)
    sample_dir.mkdir(parents=True, exist_ok=True)
    copied = copy_selected(groups, selected, data_dir, sample_dir)

    print(
        f"✅ [{dataset}] Sampled {len(selected)}/{n_items} groups (~{ratio*100:.3f}%) "
        f"and copied {copied} files → {sample_dir}"
    )

# -------------------------
# Main entry point
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
            print("⚠️ Invalid --ratio value; using default 0.0005")
            ratio = DEFAULT_RATIO
    if "--seed" in args:
        try:
            seed = int(args[args.index("--seed") + 1])
        except Exception:
            print("⚠️ Invalid --seed value; ignoring.")
            seed = None

    # Iterate through subfolders
    subfolders = [
        f for f in downloads_root.iterdir()
        if f.is_dir() and f.name not in EXCLUDE_FOLDERS
    ]

    if not subfolders:
        print("⚠️ No subfolders found to process.")
        return

    print(f"🚀 Sampling {len(subfolders)} datasets from: {downloads_root}")
    for folder in subfolders:
        process_dataset(downloads_root, folder.name, ratio, seed)


if __name__ == "__main__":
    main()
