# Sharks from Space – Chiwinners (Data + Model Repo)

This repository contains the end-to-end data and modeling stack for the **NASA Space Apps Challenge 2025 – Sharks from Space** (Team: **Chiwinners**).  
It includes: dataset mocks with a final target schema, download & transform pipelines, a hybrid **MaxEnt + BINN** modeling module, lightweight simulation tools, and loaders to publish artifacts for the web app.

---

## Quick Start

### 1) Create and activate a virtual environment
```bash
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies
```
pip install -r requirements.txt
```

### 3) Environment variables

Create a .env file (or set at runtime) with:
```
EARTHDATA_TOKEN=<your_earthdata_token>
AZURE_STORAGE_ACCOUNT_NAME=<your_account>
AZURE_STORAGE_KEY=<your_key>
```

### Modules overview

* data/ – Mock datasets in the final, analysis-ready schema + a data dictionary (data_dictionary.txt).
* downloads/ – Source-specific folders with sample/ files and metadata.txt (download notes, URLs if any).
* transform/ – Notebooks and scripts to inspect raw samples and normalize into the final schema (partitioning by year=/month=).
* model/ – Modeling code:
    * maxent.py: environmental suitability (presence-only, MaxEnt-style).
    * binn.py: Bayesian Inference Neural Network informed by MaxEnt prior.
    * features.py, data_io.py, sampling.py, utils.py: feature engineering & IO.
    * train_maxent.py, train_binn.py: training entry points.
    * predict.py: batch/geo prediction utilities.
    * config.py: central configuration.
* extract/ – Download scripts (Bash/Python) for NASA/OB.DAAC and other sources.
* load/ – Upload/publish artifacts (e.g., GeoJSON) to Azure Blob Storage for the web app.
* simulation/ – Simple mock sensor generator to test the model pipeline.
* docs/ – Diagrams, images, and general documentation assets.