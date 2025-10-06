# simulation/

Lightweight tools to generate **mock sensor data** for testing the pipeline end-to-end (from features to predictions).

## Contents

- `mockup_sensor_data.py` — produces synthetic tag/telemetry traces consistent with the target schema for quick demos.

## Usage

```bash
python simulation/mockup_sensor_data.py --out data/example_tag_raw.csv
Use the generated data to validate transforms and run model training/prediction without real tags.

---