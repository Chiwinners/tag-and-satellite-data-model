# data/

This folder contains **mock datasets** shaped in the **final, analysis-ready schema** used by the modeling pipeline.  
Use them to prototype feature engineering, training, and prediction without heavy raw downloads.

## Contents (examples)

- `example_env_*.csv` — environmental layers sampled to the target grid/time:
  - `example_env_sst.csv`, `example_env_chl.csv`, `example_env_light.csv`
  - `example_env_dsst.csv` (SST gradient), `example_env_eke.csv`
  - `example_env_depth.csv` (bathymetry/seafloor)
- `example_tag_raw.csv` — tag raw points/samples.
- `example_tag_agg_bin.csv` — discretized tag aggregations (space/time bins).
- `example_obt_env_tag.csv` — **One Big Table** (tag + env) for supervised steps.
- `example_maxent.csv` — suitability outputs for bootstrap/training.
- `example_effort.csv` — sampling/effort metadata (if applicable).
- `data_dictionary.txt` — **data dictionary** describing each dataset and field semantics.

> **Final model inputs**: typically the unified OBT tables and/or the MaxEnt suitability layer.

## Tips

- Use these mocks to validate transformations and training scripts in `model/`.
- When replacing mocks with real data, keep the column names/types consistent with `data_dictionary.txt`.