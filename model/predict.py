import joblib
import numpy as np
import pandas as pd
from pathlib import Path
import torch as T
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from config import OUT_DIR, SPECIES_COL
from data_io import load_final_table, ensure_keys
from features import build_feature_matrix
from maxent import predict_maxent
from utils import optimal_threshold

FEATURE_CFG = dict(use_env_raw=True, use_env_z=True, use_tag=True, use_priors=True)

def load_binn(sp: str):
    path = OUT_DIR / f"binn_{sp}.joblib"
    obj = joblib.load(path)
    return obj["state"], obj["used_cols"]

def pred_species(df_sp: pd.DataFrame, sp: str):
    # MAXENT prior prob
    maxent_path = OUT_DIR / f"maxent_{sp}.joblib"
    if maxent_path.exists():
        clf, cols, cfg = joblib.load(maxent_path)
        prior = predict_maxent(clf, cols, df_sp, cfg)
    else:
        prior = df_sp["S_maxent"].fillna(0.5).values if "S_maxent" in df_sp.columns else np.full(len(df_sp),0.5)

    # Build features and align to used_cols for BINN
    X_all, cols_all = build_feature_matrix(df_sp, **FEATURE_CFG)

    # Drop Effort & S_maxent because BINN los recibe por fuera (add_logit + weights)
    drop_cols = [c for c in ["Effort", "S_maxent"] if c in cols_all]
    use_mask = [c not in drop_cols for c in cols_all]
    X = X_all[:, use_mask]
    used_cols = [c for c,m in zip(cols_all,use_mask) if m]

    # Load BINN
    state, used_cols_trained = load_binn(sp)
    assert used_cols == used_cols_trained, f"Desfase de columnas para {sp}. Reentrena o alinea columnas."

    from binn import BINNNet
    net = BINNNet(in_dim=X.shape[1])
    net.load_state_dict(state)
    net.eval()

    with T.no_grad():
        p = T.sigmoid(net(T.tensor(X, dtype=T.float32),
                          T.tensor(prior, dtype=T.float32).view(-1,1))).numpy().ravel()
    return p

def main():
    df = load_final_table()
    df = ensure_keys(df)

    pred_rows = []
    species_list = sorted(df[SPECIES_COL].unique())
    for sp in species_list:
        d = df[df[SPECIES_COL]==sp].copy()
        if len(d)==0: continue
        p = pred_species(d, sp)
        pred_rows.append(pd.DataFrame({
            "lat": d["lat"].values,
            "lon": d["lon"].values,
            "time_bin": d["time_bin"].values,
            "species": sp,
            "P_forage": p,
            "model_version": "binn_v1",
            "features_hash": "auto"
        }))

    pred = pd.concat(pred_rows, ignore_index=True)
    pred.to_csv(OUT_DIR / "PRED_GRID.csv", index=False)
    print(f"PRED_GRID guardado: {OUT_DIR / 'PRED_GRID.csv'}")

    # Opcional: calcula threshold por especie (si hay labels)
    thr = []
    if "label" in df.columns:
        for sp in species_list:
            m = pred["species"]==sp
            join = pred[m].merge(df[df[SPECIES_COL]==sp][["lat","lon","time_bin","label"]], on=["lat","lon","time_bin"], how="left")
            if join["label"].notna().any():
                y = join["label"].fillna(0).values
                p = join["P_forage"].values
                t = optimal_threshold(y, p, "youden")
                thr.append({"species": sp, "threshold": float(t)})
    pd.DataFrame(thr).to_csv(OUT_DIR / "thresholds.csv", index=False)

if __name__ == "__main__":
    main()
