# Sharks from Space — MaxEnt + BINN Foraging Model (Clean Markdown)

> **Goal.** Build a space–time model that (1) estimates **habitat suitability** from presence‑only data using **MaxEnt**, and (2) predicts **foraging behavior** with a **Bayesian Inference Neural Network (BINN)** that is informed by the MaxEnt suitability. Outputs: suitability maps `S(s,t)` and foraging probability maps `FH(s,t)`.

---

## 1) Overview

- **Environmental covariates** (gridded, satellite‑derived): SST (sea surface temperature), dSST (thermal gradient), DEPTH (bathymetry), EKE (eddy kinetic energy), LIGHT (PAR/daylength proxy), CHL (chlorophyll‑a).
- **Tag‑derived features** (when available): summaries from biologging (vertical activity, depth dynamics, acceleration, diel patterns), denoted as **z_tag**.
- **Presence data**: shark occurrence points (presence‑only). Background/pseudo‑absence points are sampled for training.
- **Pipeline**: ingest → preprocess → **MaxEnt** suitability → **BINN** foraging (with prior informed by MaxEnt) → expert‑rule validation.

```mermaid
flowchart LR
    A[Earthdata & AVISO downloads] --> B[Env layers: SST, dSST, DEPTH, EKE, LIGHT, CHL]
    A2[Tag records] --> C[Tag features z_tag]
    B --> D[Fit MaxEnt]
    D --> E[S(s,t) suitability]
    E --> F[BINN training with S(s,t) and z_tag]
    C --> F
    F --> G[FH(s,t) foraging probability]
    G --> H[Validate with expert rules and papers]
```

**Repository layout (suggested)**

```
data/
  example_env_{sst,dsst,depth,eke,light,chl}.csv
  example_tag_*                  # tag raw / bins / joined env
  example_maxent.csv             # (optional) precomputed demo

model/
  maxent/                        # fits, beta_hat, diagnostics
  binn/                          # weights, priors, metrics
  outputs/                       # maps: S(s,t), FH(s,t)

notebooks/                       # EDA, sampling, maps
src/                             # python modules & CLI
```

> In your project, you indicated that “models and everything associated will live under `/model/`”. Keep raw/intermediate data under `/data/` and code under `/src/` or `/notebooks/`.

---

## 2) Notation

**Location–time index.** \( (s, t) \)

**Environmental covariate vector.**
$$
\mathbf{x}(s,t)=\big[x_1(s,t),\ldots,x_p(s,t)\big]
=\big[\mathrm{SST},\mathrm{dSST},\mathrm{DEPTH},\mathrm{EKE},\mathrm{LIGHT},\mathrm{CHL}\big]^\top
$$

**Tag‑derived features (when available).**
$$
\mathbf{z}_{\text{tag}}(s,t)\in\mathbb{R}^q
$$

**Presence indicator (foraging label).**
$$
Y_{s,t}\in\{0,1\}
$$

**Logistic function.**
$$
\sigma(z)=\frac{1}{1+e^{-z}}
$$

---

## 3) MaxEnt (presence‑only suitability)

MaxEnt estimates a distribution over space–time that is maximally entropic under feature‑expectation constraints. For presence–background modeling, a logistic approximation yields the **suitability surface**:

**Suitability definition.**
$$
S(s,t)=\mathrm{MaxEnt}\!\big(\mathbf{x}(s,t)\big)
=\sigma\!\left(\beta_0+\sum_{j=1}^{p}\beta_j\,f_j\!\big(x_j(s,t)\big)\right)
$$

Here \( f_j(\cdot) \) are engineered/transformed features (linear, splines, thresholds), and \( \beta \) are fitted to match empirical expectations under presence vs. background. Thus \( S(s,t)\in(0,1) \) and higher values indicate conditions more consistent with observed presences.

**Training objective (logistic approximation with regularization).**
$$
\max_{\beta}
\;\sum_{(s,t)\in\mathcal{P}} \log S(s,t)\;+\;
\sum_{(s,t)\in\mathcal{B}} \log\!\big(1-S(s,t)\big)
\;-\;\lambda\,\Omega(\beta)
$$

**Artifacts (recommended).**
- `model/maxent/beta_hat.csv` — fitted coefficients \( \hat{\beta} \)
- `model/outputs/suitability_map.*` — gridded \( S(s,t) \) (GeoTIFF/Parquet/NetCDF)
- diagnostics: ROC/AUC, response curves, k‑fold CV

---

## 4) BINN (Bayesian Inference Neural Network) for foraging

We predict **foraging** using a BINN that integrates the MaxEnt suitability and tag features.

**Foraging probability.**
$$
\mathrm{FH}(s,t)
=\Pr\!\big(Y_{s,t}=1 \mid S(s,t),\,\mathbf{z}_{\text{tag}}(s,t)\big)
=\mathrm{BINN}\!\Big(S(s,t),\,\mathbf{z}_{\text{tag}}(s,t);\;\theta\Big)
$$

**Final logistic layer.**
$$
\mathrm{FH}(s,t)=\sigma\!\left(w^\top h_L(s,t)+b\right)
$$

**Hidden layers (schematic).**
$$
h_{k+1}(s,t)=\phi_{k+1}\!\Big(W_k\,h_k(s,t)\;\oplus\;U_k\,g_k\!\big(\mathbf{z}_{\text{tag}}(s,t)\big)+b_k\Big)
$$

**Input lift.**
$$
h_1(s,t)=\phi_1\!\big(c_1\,S(s,t)+d_1\big)
$$

**Bayesian prior informed by MaxEnt.**
$$
\theta \sim \mathcal{N}\!\big(\mu_0,\Sigma_0\big)
$$

**Prior mean from MaxEnt.**
$$
\mu_0 = A\,\hat{\beta}_{\text{MaxEnt}}
$$

**MAP objective (negative log‑posterior minimization).**
$$
\max_{\theta}\;
\sum_{(s,t)} \log \mathrm{Bernoulli}\!\left(Y_{s,t}\,;\,\mathrm{FH}(s,t)\right)
-\tfrac{1}{2}\,\big(\theta-\mu_0\big)^\top \Sigma_0^{-1}\big(\theta-\mu_0\big)
$$

**Functional composition (acronyms explicit).**
$$
\mathrm{FH}(s,t)=\mathrm{BINN}\!\Big(\underbrace{\mathrm{MaxEnt}\!\big(\mathbf{x}(s,t)\big)}_{S(s,t)},\,\mathbf{z}_{\text{tag}}(s,t);\theta\Big)
$$

**Artifacts (recommended).**
- `model/binn/weights/` — posterior means (or samples) of \( \theta \)
- `model/binn/metrics.json` — PR/ROC, calibration
- `model/outputs/foraging_map.*` — gridded \( \mathrm{FH}(s,t) \)

---

## 5) Data expectations

Minimum required inputs (time‑referenced and spatially indexed to \( (s,t) \)):

- `data/example_env_sst.csv` — `lat, lon, time_bin, SST`
- `data/example_env_dsst.csv` — `lat, lon, time_bin, dSST`
- `data/example_env_depth.csv` — `DEPTH`
- `data/example_env_eke.csv` — `EKE`
- `data/example_env_light.csv` — `LIGHT`
- `data/example_env_chl.csv` — `CHL`
- `data/example_tag_*` — tag raw and aggregated bins (optional but recommended)
- `data/example_obt_env_tag.csv` — One Big Table joining env + tag (optional convenience)
- `data/example_maxent.csv` — precomputed demo suitability (optional)

> Keep heavy raw downloads under `downloads/`, transformed tiles under `transform/`, and model‑ready tables under `data/`.

---

## 6) Quickstart (pseudo‑CLI)

```bash
# 1) Fit MaxEnt (presence‑only)
python -m src.maxent.fit \
  --env-root data \
  --presence data/example_tag_agg_bin.csv \
  --out model/maxent

# 2) Produce suitability map
python -m src.maxent.predict \
  --env-root data \
  --beta model/maxent/beta_hat.csv \
  --out model/outputs/suitability_map.parquet

# 3) Fit BINN (foraging) with MaxEnt prior
python -m src.binn.fit \
  --suit model/outputs/suitability_map.parquet \
  --tag  data/example_obt_env_tag.csv \
  --prior-from-maxent model/maxent/beta_hat.csv \
  --out model/binn

# 4) Predict foraging probability
python -m src.binn.predict \
  --suit model/outputs/suitability_map.parquet \
  --tag  data/example_obt_env_tag.csv \
  --weights model/binn/weights \
  --out model/outputs/foraging_map.parquet
```

---

## 7) Validation against expert rules

After generating both `S(s,t)` and `FH(s,t)` maps, contrast them with rule‑based expectations from the literature (e.g., temperature ranges, front strengths, depth bands, productivity regimes). Store validations in `model/outputs/validation/` with summaries and overlays.

---

## 8) Rendering tips

- **Math:** Use `$$ ... $$` for block equations and keep important formulas in their own block. Avoid spacing commands like `\;`, `\,`, `\!`, `\:`.
- **Mermaid:** Use fenced code blocks with the `mermaid` identifier and simple, single‑line node labels for maximum compatibility.

---

## 9) Dependencies (suggested)

- Python ≥ 3.10
- `numpy`, `pandas`, `xarray`, `scipy`
- `geopandas`, `shapely`, `pyproj`, `rasterio`
- `scikit-learn` (feature transforms, CV utilities)
- Deep learning: `pytorch` **or** `tensorflow` (choose one for BINN)
- Data access: `earthaccess` (NASA Earthdata)
- Plotting: `matplotlib`, `cartopy`

---

## 10) Citation

If you use this model in a scientific context, please cite NASA/AVISO data sources accordingly and your repository release (Zenodo DOI recommended).
