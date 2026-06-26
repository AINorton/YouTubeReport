# State ZIP/ZCTA GeoJSON files

Add state ZIP/ZCTA GeoJSON files here before running a report.

Expected naming pattern:

```text
tx_texas_zip_codes_geo.min.json
sc_south_carolina_zip_codes_geo.min.json
fl_florida_zip_codes_geo.min.json
```

The renderer determines the campaign state from the matched-location ZIPs, then loads the matching file by state abbreviation.

Examples:

```text
geo/states/tx_texas_zip_codes_geo.min.json
geo/states/sc_south_carolina_zip_codes_geo.min.json
```

The GeoJSON features must include a ZIP/ZCTA property compatible with one of the configured candidates in `alamo_snapshot/config.py`, such as `ZCTA5CE10`, `ZCTA5CE20`, `GEOID10`, `GEOID20`, `ZIP`, or `zip`.

If a matching state GeoJSON is missing, the renderer should stop and report the missing state file.
