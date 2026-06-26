# Map Viewport Rules

The map renderer must never decide to draw a full state unless the data is genuinely spread too far across the state.

## Primary rule

Draw the ZIP/ZCTA region surrounding the campaign's matched ZIPs, using the state GeoJSON only as source geometry.

## Required algorithm

1. Normalize campaign ZIPs to five digits.
2. Use `geo/zip_to_state.json` to determine the primary campaign state by impression weight.
3. Load the matching state GeoJSON from `geo/states/`.
4. Match campaign ZIPs to GeoJSON features using one of these properties:
   - `ZCTA5CE10`
   - `ZCTA5CE20`
   - `ZCTA5CE`
   - `GEOID10`
   - `GEOID20`
   - `GEOID`
   - `ZIP`
   - `ZIPCODE`
5. Compute the bounding box around only matched ZIP polygons.
6. If the data spread is less than the spread threshold, use `data_crop` mode:
   - add `padding_percent`
   - enforce `min_padding_miles`
   - cap at `max_padding_miles`
   - expand to the report map panel aspect ratio
7. If the data spread is over the threshold, use `full_state_due_to_spread` mode.
8. Render muted surrounding ZIP polygons that intersect the viewport.
9. Render campaign ZIPs on top with the green intensity palette.
10. Log missing ZIPs in the validation report.

## Current config

Defined in `alamo_snapshot/config.py`:

```python
MAP_CONFIG = {
    "padding_percent": 0.25,
    "min_padding_miles": 20,
    "max_padding_miles": 90,
    "spread_full_state_threshold_miles": 250,
}
```

## Texas example

If the matched ZIPs are mostly Houston ZIPs, the map should crop to Houston plus surrounding ZIPs. It should not show the full state of Texas.

## Missing ZIP policy

- Missing ZIP polygons should be logged.
- Missing ZIPs should still appear in Top ZIPs if they are among the highest values.
- Rendering should continue unless zero ZIPs match the GeoJSON.
