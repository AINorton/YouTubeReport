# Data Validation Rules

## Required CSVs

The input directory must include files matching these patterns:

- `Campaign report*.csv`
- `Automatic placements report*.csv`
- `Matched locations report*.csv`
- `Devices*.csv`
- `Demographics(Gender*.csv`
- `Demographics(Age*.csv`
- `Day_&_hour*.csv`

## Required geo files

The geo directory must include:

- `geo/zip_to_state.json`
- one or more state GeoJSON files under `geo/states/`

For a Texas report, this file must exist:

```text
geo/states/tx_texas_zip_codes_geo.min.json
```

## Stop conditions

Stop and report an error if:

- a required CSV is missing
- `zip_to_state.json` is missing
- the primary state cannot be determined from ZIPs
- the required state GeoJSON does not exist
- no campaign ZIPs match the state GeoJSON
- the template image is not the expected size

## Non-stop warnings

Continue rendering but log warnings if:

- some ZIPs do not match GeoJSON polygons
- ZIPs span multiple states
- data spread triggers full-state map mode
- static validation returns non-zero changes
