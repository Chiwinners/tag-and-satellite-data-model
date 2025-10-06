# load/

Publish and loading utilities to **Azure Blob Storage** for the web app.

## Layout

- `data/` — example GeoJSON artifacts to publish:
  - `seaflower.geojson` — AOI polygon.
  - `seaflower_convexhull.geojson` — convex hull for the region.
  - `seaflower_zf_prediction.geojson` — foraging-zone predictions (example).
- `load.py` — CLI uploader for `.json`/`.geojson` files.
- `seaflower.py`, `seaflower_convex_hull.py` — AOI helpers.

## Environment

Set: AZURE_STORAGE_ACCOUNT_NAME=<your_account> AZURE_STORAGE_KEY=<your_key>

## Example

```bash
python load/load.py \
  --file load/data/seaflower_zf_prediction.geojson \
  --blob-key seaflower_zf_prediction.geojson