# extract/

Download utilities for NASA/OB.DAAC and related sources.

## Layout

- `bash/` — shell scripts for batch downloads (with retries, cookies, netrc handling).
- `python/` — Python downloaders (e.g., `clorophyll.py`, `sst.py`, `eke.py`, `depth.py`).
- `s3/` — references or lists of S3/object keys.

## Environment

Requires:
- `EARTHDATA_TOKEN` in `.env` (or configured via netrc for some scripts).
- Dependencies from `requirements.txt` (e.g., `earthaccess`, `requests`, etc.).

## Usage examples

```bash
# Bash
bash extract/bash/download_sst.sh

# Python
python extract/python/sst.py
python extract/python/clorophyll.py
python extract/python/eke.py
python extract/python/depth.py
