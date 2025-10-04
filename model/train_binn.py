import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import roc_auc_score
from config import OUT_DIR, SPECIES_COL, PRIOR_COLS, SPLIT
from data_io import load_final_table, ensure_keys, train_val_split
from features import build_feature_matrix, get_Xy
from maxent import predict_maxent
from binn import train_binn
from utils import optimal_threshold

FEATURE_CFG = dict(use_env_raw=True, use_env_z=True, use_tag=True, use_priors=True)  # incluye Effort, S_maxent

def load_maxent_prior_prob(df_sp: pd.DataFrame, sp: str) -> np.ndarray:
    path = OUT_DIR / f"maxent_{sp}.joblib"
    if not path.exists():
        # Si no existe MAXENT para la especie, usa S_maxent si está; si no, 0.5
        if "S_maxent" in df_sp.columns:
            return df_sp["S_maxent"].fillna(0.5).values
        return np.full(len(df_sp), 0.5)
    clf, cols, cfg = joblib.load(path)
    p = predict_maxent(clf, cols, df_sp, cfg)
    return p

def main():
    df = load_final_table()
    df = ensure_keys(df)

    # Split (por tiempo o random)
    train_df, val_df = train_val_split(df, **SPLIT)

    species_list = sorted(df[SPECIES_COL].unique())
    summary = []
    for sp in species_list:
        tr = train_df[train_df[SPECIES_COL]==sp].copy()
        va = val_df[val_df[SPECIES_COL]==sp].copy()
        if len(tr) < 100 or len(va) < 50:
            print(f"[BINN] {sp}: pocos datos, se omite.")
            continue

        # Construye features completas (incluye PRIOR_COLS para esfuerzo/peso)
        Xtr_all, cols_all = build_feature_matrix(tr, **FEATURE_CFG)
        Xva_all, _ = build_feature_matrix(va, **FEATURE_CFG)

        # Separa Effort (peso) si está
        def get_col(a, name):
            return a[:, cols_all.index(name)] if name in cols_all else None

        effort_tr = get_col(Xtr_all, "Effort")
        effort_va = get_col(Xva_all, "Effort")

        # S_maxent prior probabilístico:
        # - si existe MAXENT entrenado: usar su prob como prior_informado
        # - sino: usa columna S_maxent del dataset o 0.5
        prior_tr = load_maxent_prior_prob(tr, sp)
        prior_va = load_maxent_prior_prob(va, sp)

        # Quita columnas de PRIORS del vector X de la red (si usamos prior como logit add)
        # Mantén Effort como peso, no como feature (opcional)
        drop_cols = []
        # S_maxent como prior externo (no feature)
        if "S_maxent" in cols_all:
            drop_cols.append("S_maxent")
        # Effort solo para weights (no feature)
        if "Effort" in cols_all:
            drop_cols.append("Effort")

        use_mask = [c not in drop_cols for c in cols_all]
        Xtr = Xtr_all[:, use_mask]
        Xva = Xva_all[:, use_mask]
        used_cols = [c for c,m in zip(cols_all,use_mask) if m]

        ytr = tr["label"].astype(int).values
        yva = va["label"].astype(int).values

        net = train_binn(
            Xtr, ytr, Xva, yva,
            prior_tr=prior_tr, prior_va=prior_va,
            effort_tr=effort_tr, effort_va=effort_va,
            in_dim=Xtr.shape[1]
        )

        # Eval
        import torch
        net.eval()
        with torch.no_grad():
            import torch as T
            Xva_t = T.tensor(Xva, dtype=T.float32)
            pva = T.sigmoid(net(Xva_t, T.tensor(prior_va, dtype=T.float32).view(-1,1))).numpy().ravel()

        auc = roc_auc_score(yva, pva) if len(np.unique(yva))>1 else np.nan
        th = optimal_threshold(yva, pva, method="youden")
        joblib.dump(
            dict(state=net.state_dict(), used_cols=used_cols),
            OUT_DIR / f"binn_{sp}.joblib"
        )
        pd.DataFrame({
            "lat": va["lat"], "lon": va["lon"], "time_bin": va["time_bin"],
            "species": sp, "P_forage": pva
        }).to_csv(OUT_DIR / f"val_pred_{sp}.csv", index=False)

        summary.append({"species": sp, "val_auc": auc, "threshold": th, "n_train": len(tr), "n_val": len(va)})
        print(f"[BINN] {sp}: valAUC={auc:.4f}, thr={th:.3f}, features={len(used_cols)}")

    pd.DataFrame(summary).to_csv(OUT_DIR / "binn_summary.csv", index=False)
    print(f"Listo. Artefactos en {OUT_DIR}")

if __name__ == "__main__":
    main()
