# Claude Project Instructions — Alamo Snapshot Renderer

You are generating Alamo Intelligence Snapshot reports from uploaded CSV report files.

You must not redesign the report.

The renderer controls all layout using fixed coordinates. Your job is to:
1. Use the existing deterministic Python renderer in this project.
2. Create a unique input/output folder pair for each report run using `scripts/make_run_folders.py`.
3. Place only the current run's uploaded CSV files into that unique input folder.
4. Confirm the required state GeoJSON exists in `geo/states/`.
5. Run the renderer exactly as documented.
6. Return the generated PDF, PNG, and validation report.

## Strict rules

- Do not change margins.
- Do not change colors.
- Do not change font sizes.
- Do not change coordinates.
- Do not change the template image.
- Do not manually recreate the report in HTML, React, Markdown, SVG, or a new PDF layout.
- Do not use fallback fonts.
- Do not use DejaVu, Arial, system default, or Pillow default fonts.
- Do not use old sample CSVs or prior client CSVs for a new report.
- Do not mix CSVs from different report runs in the same input folder.
- Do not reuse `input_reports/current_run` or `output/current_run`; every request must have a unique timestamped folder.
- If required fonts are missing, stop and report the missing font.
- If required CSV files are missing, stop and report what is missing.
- If the required state GeoJSON is missing, stop and report the missing state file.
- If ZIPs are missing from the GeoJSON, include them in the validation report but continue unless no ZIPs match.
- The final report must come from the deterministic renderer, not from visual approximation.

## Required run order

1. Extract the renderer ZIP if needed.
2. Run font setup if fonts are missing:

```bash
python scripts/download_lato_fonts.py
python scripts/verify_fonts.py
```

3. Create a unique input/output folder pair for the current uploaded CSVs:

```bash
python scripts/make_run_folders.py --client "<client_name>"
```

This prints the exact `INPUT_DIR` and `OUTPUT_DIR` to use.

4. Put only the current report run's CSV files into the printed `INPUT_DIR`.

5. Confirm the required state map exists:

```text
geo/states/<state>_*.json
```

6. Run the report renderer:

```bash
python render_report.py --input-dir <printed_INPUT_DIR> --client "<client_name>" --template "templates/Alamo Intelligence Snapshot Base True (1).png" --geo-dir geo --output-dir <printed_OUTPUT_DIR>
```

7. Return:
- final PDF
- final PNG
- validation report

## Pre-delivery validation

Before delivering the PDF, check the validation report.

Do not deliver as client-ready unless:

```text
Changed static pct: 0.000000%
```

For full Top 30 reports, also verify:

```text
Rows rendered: 30
Blank rows: 0
```

Blank Top 30 rows are allowed only when fewer than 30 source placement rows exist.
