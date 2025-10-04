import numpy as np
import pandas as pd
from typing import Dict, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from features import build_feature_matrix
from sampling import presence_background
from config import MAXENT, SPECIES_COL

def train_maxent_for_species(df: pd.DataFrame, species: str, feature_cfg: Dict):
    pres, back = presence_background(
        df, background_size=MAXENT["background_size"], species=species, use_effort_as_prob=True
    )
    pres = pres.copy(); pres["pb"] = 1
    back = back.copy(); back["pb"] = 0
    d = pd.concat([pres, back], ignore_index=True)

    X, cols = build_feature_matrix(d, **feature_cfg)
    y = d["pb"].values

    # Penalizaciones: C = 1 / (l2 + l1) aprox (sklearn no separa ambos en LogisticRegression)
    # Usamos saga con elasticnet para combinar L1/L2
    l1 = MAXENT["penalty_l1"]
    l2 = MAXENT["penalty_l2"]
    l1_ratio = 0.0 if (l1 + l2) == 0 else l1 / (l1 + l2)
    C = 1.0 / max(l1 + l2, 1e-6)

    clf = LogisticRegression(
        solver="saga",
        penalty="elasticnet",
        l1_ratio=l1_ratio,
        C=C,
        max_iter=500,
        class_weight=MAXENT["class_weight"],
        random_state=MAXENT["random_state"],
    )
    clf.fit(X, y)
    # AUC interno (hold-in)
    auc = roc_auc_score(y, clf.predict_proba(X)[:,1]) if len(np.unique(y))>1 else np.nan
    return clf, cols, auc

def predict_maxent(clf, cols, df: pd.DataFrame, feature_cfg: Dict) -> np.ndarray:
    # Construye las mismas features; limita a las columnas usadas por MAXENT
    _, all_cols = build_feature_matrix(df, **feature_cfg)  # para asegurar fillna
    X = df[cols].astype(float).fillna(df[cols].median(numeric_only=True)).values
    return clf.predict_proba(X)[:, 1]
