from pathlib import Path

# --- Rutas locales ---
#   data/: CSVs
#   model/: modelos, métricas y predicciones
BASE_DIR = Path(".").resolve()
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "model"   # carpeta de salida pedida
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Dataset final integrado (ONE BIG TABLE)
FINAL_TABLE = DATA_DIR / "example_obt_env_tag.csv"

# Claves
KEYS = ["lat", "lon", "time_bin"]

# Variables (según tu diccionario)
ENV_COLS_RAW = [
    "SST_raw", "CHL_raw", "dSST_raw", "EKE_raw", "Depth_raw", "Light_raw"
]
ENV_COLS_Z = [c + "_z" for c in ["SST_raw","CHL_raw","dSST_raw","EKE_raw","Depth_raw","Light_raw"]]
TAG_COLS = [
    "pressure_dbar","depth_m","temperature_C","odba","speed_ms","heading_deg",
    "pH","battery_soc_%","capacitive"
]
PRIOR_COLS = ["Effort", "S_maxent"]

# Objetivo y metadatos
LABEL_COL = "label"         # 1=foraging, 0=otro
SPECIES_COL = "species"     # si no existe, se crea "unknown"

# Auto-etiquetado (si no existe label)
AUTO_LABEL = dict(
    enable=True,
    odba_q=0.75,
    min_speed=0.1,      # m/s
    max_depth=400.0     # m
)

# MAXENT
MAXENT = dict(
    random_state=42,
    background_size=20000,
    penalty_l1=0.0,
    penalty_l2=1.0,
    class_weight=None
)

# BINN (PyTorch)
BINN = dict(
    seed=42,
    epochs=30,
    batch_size=1024,
    lr=1e-3,
    weight_decay=1e-4,
    hidden_sizes=[128, 64],
    prior_mode="add_logit",   # "add_logit" | "feature" | "none"
    prior_scale=1.0,
    lambda_prior_reg=0.0,
    use_effort_as_weight=True
)

# Split train/val
SPLIT = dict(
    method="time",             # "time" | "random"
    val_frac=0.2,              # si "random"
    time_val_quantile=0.8      # si "time"
)

# Salidas (todo a ./model)
OUT_DIR = MODEL_DIR
