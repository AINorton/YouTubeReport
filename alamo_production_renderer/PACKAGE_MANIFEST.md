# Package Manifest

## Included

- `render_report.py` — main entrypoint
- `alamo_snapshot/` — deterministic renderer modules
- `templates/Alamo Intelligence Snapshot Base True (1).png` — locked template
- `geo/zip_to_state.json` — ZIP to state lookup
- `geo/states/README.md` — where to add state GeoJSON maps
- `input_reports/README.md` — where to add per-run CSVs
- `scripts/download_lato_fonts.py` — local Lato font setup
- `scripts/verify_fonts.py` — strict font verification
- `scripts/make_run_folders.py` — creates unique per-request input/output folders
- `rules/` — renderer/data/map rules
- `instructions/` — Claude Project operating instructions

## Not included

- No client CSV files
- No sample output files
- No Texas-only sample run
- No bundled font files
- No state-specific GeoJSON map files

This avoids conflicts between report runs and makes the package reusable for future campaigns.
