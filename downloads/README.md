# downloads/

Source-specific raw downloads. Each subfolder groups metadata and sample files for a given variable/source.

## Common sub-structure

- `<source>/`
  - `metadata.txt` — notes/links to the official source and product IDs.
  - `nasa.txt`, `s3.txt` — optional helper notes/paths for OB.DAAC/S3 endpoints.
  - `sample/` — **raw sample files** (e.g., `.nc`, `.h5`, `.tif`) used in notebooks.
  - `data/` — (optional, heavy) full raw mirrors; **excluded from docs/tree**.

## Examples

- `clorophyll/sample/*.L2.OC.nc` — MODIS L2 Ocean Color samples.
- `light/sample/*.L3b.DAY.PAR.x.nc` — PAR/Light L3b samples.
- `sst/sample/*.tif` — AST L2/3 sample tiles (skin temperature).
- `eke/sample/*.nc` — sea-level derived EKE samples.
- `depth/sample/*.h5` — altimetry/bathymetry products (as available).
- `seaflower/` — AOI resources (WDPA geodatabase, PDFs, timestamps, etc.).
- `sharks/` — shark/tag specific resources.

## How to download

See `extract/` for Bash/Python scripts to authenticate with **EARTHDATA_TOKEN** and fetch files in parallel with retries.

> Keep large datasets out of version control; consider storing them in `downloads/*/data` or external storage.
