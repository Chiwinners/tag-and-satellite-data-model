import pandas as pd
import numpy as np
from pathlib import Path
from config import FINAL_TABLE, LABEL_COL, SPECIES_COL, KEYS, AUTO_LABEL

def load_final_table(path: Path = FINAL_TABLE) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Normaliza tipos
    if "time_bin" in df.columns:
        df["time_bin"] = pd.to_datetime(df["time_bin"])
    # Asegura species
    if SPECIES_COL not in df.columns:
        df[SPECIES_COL] = "unknown"
    # Auto-etiquetado si no hay label
    if LABEL_COL not in df.columns and AUTO_LABEL["enable"]:
        df[LABEL_COL] = auto_label(df, **AUTO_LABEL)
    return df

def auto_label(df: pd.DataFrame, odba_q=0.75, min_speed=0.1, max_depth=400.0, **kwargs) -> np.ndarray:
    """Heurística simple (ajústala a tu caso):
       foraging ≈ alta actividad (ODBA), velocidad > umbral, profundidad moderada."""
    odba = df.get("odba", pd.Series([np.nan]*len(df)))
    speed = df.get("speed_ms", pd.Series([np.nan]*len(df)))
    depth = df.get("depth_m", pd.Series([np.nan]*len(df)))
    thr = odba.quantile(odba_q) if odba.notna().any() else np.nan
    cond = (
        (odba >= thr).fillna(False) &
        (speed >= min_speed).fillna(False) &
        (depth <= max_depth).fillna(False)
    )
    return cond.astype(int).values

def ensure_keys(df: pd.DataFrame) -> pd.DataFrame:
    missing = [k for k in KEYS if k not in df.columns]
    if missing:
        raise ValueError(f"Faltan claves {missing} en la tabla final.")
    return df

def train_val_split(df: pd.DataFrame, method="time", val_frac=0.2, time_val_quantile=0.8):
    if method == "time":
        qt = df["time_bin"].quantile(time_val_quantile)
        train_df = df[df["time_bin"] < qt].copy()
        val_df   = df[df["time_bin"] >= qt].copy()
    else:
        # random estratificado por especie
        rng = np.random.default_rng(42)
        mask = rng.random(len(df)) < (1 - val_frac)
        train_df = df[mask].copy()
        val_df   = df[~mask].copy()
    return train_df, val_df
