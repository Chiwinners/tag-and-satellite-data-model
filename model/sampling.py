import numpy as np
import pandas as pd
from typing import Tuple
from config import LABEL_COL, SPECIES_COL, PRIOR_COLS

def presence_background(df: pd.DataFrame,
                        background_size=20000,
                        species=None,
                        use_effort_as_prob=True) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Devuelve (presences, background) para una especie dada (o todas)."""
    if species is not None:
        d = df[df[SPECIES_COL] == species].copy()
    else:
        d = df.copy()

    pres = d[d[LABEL_COL] == 1].copy()
    # background: sample across all grid-cells / times (no importa label)
    bg_pool = d.copy()
    if use_effort_as_prob and "Effort" in d.columns:
        p = d["Effort"].fillna(0).values.astype(float)
        if p.sum() <= 0:
            p = None
    else:
        p = None

    n = min(background_size, len(bg_pool))
    idx = np.random.default_rng(42).choice(len(bg_pool), size=n, replace=(n > len(bg_pool)), p=(p / p.sum()) if p is not None else None)
    back = bg_pool.iloc[idx].copy()
    return pres, back
