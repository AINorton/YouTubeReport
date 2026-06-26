# Operator Runbook

## 1. Put CSVs in one folder

The folder should contain:

```text
Campaign report*.csv
Automatic placements report*.csv
Matched locations report*.csv
Devices*.csv
Demographics(Gender*.csv
Demographics(Age*.csv
Day_&_hour*.csv
```

## 2. Confirm geo files exist

```text
geo/zip_to_state.json
geo/states/<state>_*.json
```

Example for Texas:

```text
geo/states/tx_texas_zip_codes_geo.min.json
```

## 3. Run the renderer

```bash
python render_report.py \
  --input-dir sample_data \
  --client "Client Name" \
  --template "templates/Alamo Intelligence Snapshot Base True (1).png" \
  --geo-dir geo \
  --output-dir output
```

## 4. Check validation

Open:

```text
output/Alamo_YouTube_Snapshot_deterministic.validation.txt
```

Confirm:

```text
Changed static pct: 0.000000%
```

Review the map section for missing ZIPs and viewport mode.

## 5. Send client files

Send only:

```text
output/Alamo_YouTube_Snapshot_deterministic.pdf
```

Keep the PNG and validation file internally.
