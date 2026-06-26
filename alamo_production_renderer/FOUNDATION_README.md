# Alamo Snapshot Renderer — Clean Foundation Package

This package is the reusable foundation for future Alamo Intelligence Snapshot reports.

It intentionally does **not** include client CSV files or state-specific GeoJSON maps.

## What is included

- Locked report template
- Deterministic report renderer
- Top 30 row rendering fix
- Static-layout validation fix
- Strict local-font validation
- ZIP/state lookup file
- Empty input/output folders
- Empty `geo/states/` folder for state GeoJSONs

## What each user/run must provide

1. The 7 campaign CSV exports for the specific report run.
2. The state ZIP/ZCTA GeoJSON file for the campaign state.
3. The client name to print in the header.
4. Local Lato fonts, installed by running the included font setup script.

## Required setup

```bash
python scripts/download_lato_fonts.py
python scripts/verify_fonts.py
```

## Required run pattern

Create a unique folder for each report run:

```bash
python scripts/make_run_folders.py --client "Client Name"
```

This creates:

```text
input_reports/client_name_YYYYMMDD_HHMM/
output/client_name_YYYYMMDD_HHMM/
```

Put the run's CSV files in the new input folder only.

Put needed state map files in:

```text
geo/states/
```

Then run:

```bash
python render_report.py \
  --input-dir input_reports/client_name_YYYYMMDD_HHMM \
  --client "Client Name" \
  --template "templates/Alamo Intelligence Snapshot Base True (1).png" \
  --geo-dir geo \
  --output-dir output/client_name_YYYYMMDD_HHMM
```

## Client-ready rule

Only deliver the PDF if the validation report shows:

```text
Changed static pct: 0.000000%
```

For a full 30-row placement report, also confirm:

```text
Rows rendered: 30
Blank rows: 0
```

Blanks are allowed only when fewer than 30 source rows exist.
