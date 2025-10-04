import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from typing import Tuple, List
from config import ENV_COLS_RAW, ENV_COLS_Z, TAG_COLS, PRIOR_COLS, LABEL_COL, SPECIES_COL

def build_feature_matrix(df: pd.DataFrame,
                         use_env_raw=True, use_env_z=True,
                         use_tag=True, use_priors=True) -> Tuple[np.ndarray, List[str]]:
    cols = []
    if use_env_raw:
        cols += [c for c in ENV_COLS_RAW if c in df.columns]
    if use_env_z:
        cols += [c for c in ENV_COLS_Z if c in df.columns]
    if use_tag:
        cols += [c for c in TAG_COLS if c in df.columns]
    if use_priors:
        cols += [c for c in PRIOR_COLS if c in df.columns]
    X = df[cols].astype(float).replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median(numeric_only=True))  # imputación simple
    return X.values, cols

def standardize_per_species(train_df, val_df, feature_cols):
    scalers = {}
    for sp in train_df[SPECIES_COL].unique():
        scalers[sp] = StandardScaler()
        idx = train_df[SPECIES_COL] == sp
        train_df.loc[idx, feature_cols] = scalers[sp].fit_transform(train_df.loc[idx, feature_cols].astype(float))
        # aplica a val con el mismo scaler
        idxv = val_df[SPECIES_COL] == sp
        val_df.loc[idxv, feature_cols] = scalers[sp].transform(val_df.loc[idxv, feature_cols].astype(float))
    return train_df, val_df, scalers

def get_Xy(df: pd.DataFrame, cols: List[str]):
    X = df[cols].astype(float).values
    y = df[LABEL_COL].astype(int).values
    return X, y
