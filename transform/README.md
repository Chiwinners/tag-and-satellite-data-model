# transform/

Inspection and transformation of raw samples into the **final analysis-ready schema** (partitioned Parquet).

## Layout

Per-variable subfolders with notebooks and partitioned outputs, e.g.:

- `clorophyll/`
  - `inspect.ipynb` — QC, coverage checks, sample reading.
  - `sample/year=/month=/...parquet` — partitioned extractions.
  - `transform.ipynb` — normalization into the unified schema.
- `depth/`, `eke/`, `light/`, `sst/` — follow the same pattern.
- Top-level helpers: `depth.py`, etc. for shared logic.

## Typical steps

1. **Inspect** raw `downloads/<var>/sample/*` to understand coverage/flags.
2. **Transform** to Parquet partitioned by `year=/month=` with standardized columns:
   - spatial keys: `lat`, `lon`
   - temporal key: `time_bin`
   - value columns: e.g., `sst`, `chl`, `eke`, `light`, `depth`, `dsst`
3. **Unify** multiple variables into the OBT (see `data/example_obt_env_tag.csv`).

> Notebook `sst/create_dsst.ipynb` shows how to derive **SST gradients (dSST)** from SST tiles/rasters.