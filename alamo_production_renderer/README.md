# Alamo Production Renderer — Clean Foundation

This is the reusable foundation package for generating Alamo Intelligence Snapshot reports.

It contains the locked renderer and template, but it intentionally does not include report-run CSV files or state-specific GeoJSON map files.

## First-time setup

```bash
python scripts/download_lato_fonts.py
python scripts/verify_fonts.py
```

## Add state map files

Add required ZIP/ZCTA GeoJSON files to:

```text
geo/states/
```

Example:

```text
geo/states/tx_texas_zip_codes_geo.min.json
geo/states/sc_south_carolina_zip_codes_geo.min.json
```

## Add report CSVs

Create a unique input/output folder pair per report run:

```bash
python scripts/make_run_folders.py --client "Client Name"
```

This creates folders like:

```text
input_reports/client_name_YYYYMMDD_HHMM/
output/client_name_YYYYMMDD_HHMM/
```

Place the current report's CSV exports in the new input folder only.

Required CSV types:

- Campaign report
- Automatic placements report
- Matched locations report
- Devices report
- Demographics Gender report
- Demographics Age report
- Day & hour report

## Run

```bash
python render_report.py \
  --input-dir input_reports/client_name_YYYYMMDD_HHMM \
  --client "Client Name" \
  --template "templates/Alamo Intelligence Snapshot Base True (1).png" \
  --geo-dir geo \
  --output-dir output/client_name_YYYYMMDD_HHMM
```

## Deliverable rule

Only deliver the PDF if the validation report shows:

```text
Changed static pct: 0.000000%
```

The report is deterministic. Do not edit layout coordinates, template image, font rules, margins, or colors unless intentionally creating a new versioned template.
