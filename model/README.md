# model/

Hybrid habitat + foraging modeling stack combining **MaxEnt** (presence-only suitability) and a **Bayesian Inference Neural Network (BINN)** informed by MaxEnt outputs.

## Files and roles

- `maxent.py` — MaxEnt-style suitability model (logistic output S(x,t)).
- `binn.py` — BINN classifier (foraging vs non-foraging) using:
  - **Environmental variables** (SST, CHL, dSST, EKE, DEPTH, LIGHT, …)
  - **Tag variables** (acc/depth/other telemetry)
  - **MaxEnt prior** as an informative input/regularizer.
- `features.py` — feature engineering and spatial/temporal encoding.
- `data_io.py` — loading/saving datasets (Parquet/CSV/GeoJSON).
- `sampling.py` — positive/negative sampling strategies & class balancing.
- `utils.py` — geospatial helpers (projections, grids, shapely ops).
- `config.py` — central hyperparams/paths.
- `train_maxent.py` — training entry point for MaxEnt.
- `train_binn.py` — training entry point for BINN.
- `predict.py` — batch inferencing and GeoJSON exporters.
- `data/` — figures/plots generated during exploration.

## Training

```bash
# 1) Train MaxEnt
python -m model.train_maxent --config model/config.py

# 2) Train BINN (informed by MaxEnt outputs)
python -m model.train_binn --config model/config.py
```

## Prediction
```
python -m model.predict \
  --region seaflower \
  --out load/data/seaflower_zf_prediction.geojson
```

## Notes

The final training table is the unified analysis-ready dataset described in data/data_dictionary.txt (e.g., OBT).

transform/ notebooks/scripts produce the partitioned inputs that map to this final schema.