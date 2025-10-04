import joblib
import pandas as pd
from pathlib import Path
from config import OUT_DIR, SPECIES_COL
from data_io import load_final_table, ensure_keys, train_val_split
from features import build_feature_matrix
from maxent import train_maxent_for_species, predict_maxent

FEATURE_CFG = dict(use_env_raw=True, use_env_z=True, use_tag=True, use_priors=False)

def main():
    df = load_final_table()
    df = ensure_keys(df)

    species_list = sorted(df[SPECIES_COL].unique())
    results = []
    for sp in species_list:
        clf, cols, auc = train_maxent_for_species(df, sp, FEATURE_CFG)
        joblib.dump((clf, cols, FEATURE_CFG), OUT_DIR / f"maxent_{sp}.joblib")
        results.append({"species": sp, "train_auc": auc})
        print(f"[MAXENT] {sp}: AUC_in={auc:.4f}, features={len(cols)}")

    pd.DataFrame(results).to_csv(OUT_DIR / "maxent_summary.csv", index=False)
    print(f"Guardado en {OUT_DIR}")

if __name__ == "__main__":
    main()
