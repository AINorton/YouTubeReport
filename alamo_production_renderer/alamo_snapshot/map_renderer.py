"""Data-cropped ZIP/ZCTA GeoJSON map renderer.

This file implements production-safe item #3:
- use state GeoJSON as source geometry
- compute viewport from ZIPs with campaign data
- add deterministic surrounding area
- preserve the report panel aspect ratio
- render into a fixed-size image for the locked report renderer
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from PIL import Image, ImageDraw

from .utils import normalize_zip

Bounds = Tuple[float, float, float, float]


def load_json(path: str | Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_feature_zip(feature: dict, candidates: List[str]) -> str | None:
    props = feature.get("properties", {})
    for key in candidates:
        if key in props:
            z = normalize_zip(props[key])
            if z:
                return z[-5:]
    return None


def iter_coords(geometry: dict):
    geom_type = geometry.get("type")
    coords = geometry.get("coordinates", [])

    if geom_type == "Polygon":
        for ring in coords:
            for lon, lat in ring:
                yield float(lon), float(lat)

    elif geom_type == "MultiPolygon":
        for polygon in coords:
            for ring in polygon:
                for lon, lat in ring:
                    yield float(lon), float(lat)


def geometry_bounds(geometry: dict) -> Bounds:
    xs: List[float] = []
    ys: List[float] = []
    for lon, lat in iter_coords(geometry):
        xs.append(lon)
        ys.append(lat)
    if not xs:
        raise ValueError("Geometry has no coordinates.")
    return min(xs), min(ys), max(xs), max(ys)


def combine_bounds(bounds_list: List[Bounds]) -> Bounds:
    return (
        min(b[0] for b in bounds_list),
        min(b[1] for b in bounds_list),
        max(b[2] for b in bounds_list),
        max(b[3] for b in bounds_list),
    )


def bounds_intersect(a: Bounds, b: Bounds) -> bool:
    return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])


def miles_to_lat_degrees(miles: float) -> float:
    return miles / 69.0


def miles_to_lon_degrees(miles: float, latitude: float) -> float:
    cos_lat = max(math.cos(math.radians(latitude)), 0.2)
    return miles / (69.0 * cos_lat)


def bounds_diagonal_miles(bounds: Bounds) -> float:
    minx, miny, maxx, maxy = bounds
    center_lat = (miny + maxy) / 2
    dx = (maxx - minx) * 69.0 * max(math.cos(math.radians(center_lat)), 0.2)
    dy = (maxy - miny) * 69.0
    return math.sqrt(dx * dx + dy * dy)


def expand_bounds_with_padding(
    bounds: Bounds,
    padding_percent: float,
    min_padding_miles: float,
    max_padding_miles: float,
) -> Bounds:
    minx, miny, maxx, maxy = bounds
    width = max(maxx - minx, 0.01)
    height = max(maxy - miny, 0.01)
    center_lat = (miny + maxy) / 2

    pad_x = max(width * padding_percent, miles_to_lon_degrees(min_padding_miles, center_lat))
    pad_y = max(height * padding_percent, miles_to_lat_degrees(min_padding_miles))
    pad_x = min(pad_x, miles_to_lon_degrees(max_padding_miles, center_lat))
    pad_y = min(pad_y, miles_to_lat_degrees(max_padding_miles))

    return minx - pad_x, miny - pad_y, maxx + pad_x, maxy + pad_y


def expand_to_aspect_ratio(bounds: Bounds, target_aspect: float) -> Bounds:
    minx, miny, maxx, maxy = bounds
    width = max(maxx - minx, 0.01)
    height = max(maxy - miny, 0.01)
    current_aspect = width / height
    cx = (minx + maxx) / 2
    cy = (miny + maxy) / 2

    if current_aspect < target_aspect:
        new_width = height * target_aspect
        half = new_width / 2
        minx = cx - half
        maxx = cx + half
    else:
        new_height = width / target_aspect
        half = new_height / 2
        miny = cy - half
        maxy = cy + half

    return minx, miny, maxx, maxy


def lonlat_to_pixel(lon: float, lat: float, bounds: Bounds, width: int, height: int) -> tuple[int, int]:
    minx, miny, maxx, maxy = bounds
    x = int(round((lon - minx) / (maxx - minx) * width))
    y = int(round((maxy - lat) / (maxy - miny) * height))
    return x, y


def geometry_to_pixel_rings(geometry: dict, bounds: Bounds, width: int, height: int) -> List[List[tuple[int, int]]]:
    geom_type = geometry.get("type")
    coords = geometry.get("coordinates", [])
    rings_out: List[List[tuple[int, int]]] = []

    if geom_type == "Polygon":
        for ring in coords:
            rings_out.append([lonlat_to_pixel(float(lon), float(lat), bounds, width, height) for lon, lat in ring])
    elif geom_type == "MultiPolygon":
        for polygon in coords:
            for ring in polygon:
                rings_out.append([lonlat_to_pixel(float(lon), float(lat), bounds, width, height) for lon, lat in ring])

    return rings_out


def color_for_value(value: int, min_value: int, max_value: int, palette: List[str]) -> str:
    if max_value <= min_value:
        return palette[-1]
    ratio = (value - min_value) / (max_value - min_value)
    idx = int(round(ratio * (len(palette) - 1)))
    return palette[max(0, min(idx, len(palette) - 1))]


def render_cropped_zip_map(
    zip_impressions: Dict[str, int],
    state_geojson_path: str | Path,
    output_path: str | Path,
    config: dict,
) -> dict:
    geo = load_json(state_geojson_path)
    width = int(config["map_width"])
    height = int(config["map_height"])
    target_aspect = width / height

    features_by_zip: Dict[str, dict] = {}
    feature_bounds: Dict[str, Bounds] = {}

    for feature in geo.get("features", []):
        z = get_feature_zip(feature, config["zip_property_candidates"])
        if not z:
            continue
        geometry = feature.get("geometry")
        if not geometry:
            continue
        try:
            b = geometry_bounds(geometry)
        except Exception:
            continue
        features_by_zip[z] = feature
        feature_bounds[z] = b

    normalized_impressions: Dict[str, int] = {}
    for z, value in zip_impressions.items():
        nz = normalize_zip(z)
        if nz:
            normalized_impressions[nz] = normalized_impressions.get(nz, 0) + int(value)

    matched_zips = [z for z in normalized_impressions if z in features_by_zip]
    missing_zips = [z for z in normalized_impressions if z not in features_by_zip]

    if not matched_zips:
        raise ValueError("No report ZIPs matched the selected state GeoJSON.")

    data_bounds = combine_bounds([feature_bounds[z] for z in matched_zips])
    state_bounds = combine_bounds(list(feature_bounds.values()))
    spread_miles = bounds_diagonal_miles(data_bounds)

    if spread_miles > config["spread_full_state_threshold_miles"]:
        viewport_mode = "full_state_due_to_spread"
        viewport = expand_to_aspect_ratio(state_bounds, target_aspect)
    else:
        viewport_mode = "data_crop"
        viewport = expand_bounds_with_padding(
            data_bounds,
            padding_percent=config["padding_percent"],
            min_padding_miles=config["min_padding_miles"],
            max_padding_miles=config["max_padding_miles"],
        )
        viewport = expand_to_aspect_ratio(viewport, target_aspect)

    visible_zips = [z for z, b in feature_bounds.items() if bounds_intersect(b, viewport)]

    img = Image.new("RGB", (width, height), config["map_background"])
    draw = ImageDraw.Draw(img)

    # Draw muted surrounding ZIPs first.
    for z in visible_zips:
        rings = geometry_to_pixel_rings(features_by_zip[z]["geometry"], viewport, width, height)
        for ring in rings:
            if len(ring) >= 3:
                draw.polygon(
                    ring,
                    fill=config["background_zip_fill"],
                    outline=config["background_zip_outline"],
                    width=int(config.get("background_zip_outline_width", 1)),
                )

    values = [normalized_impressions[z] for z in matched_zips]
    min_value = min(values)
    max_value = max(values)

    # Draw campaign ZIPs on top.
    for z in matched_zips:
        value = normalized_impressions[z]
        fill = color_for_value(value, min_value, max_value, config["highlight_palette"])
        rings = geometry_to_pixel_rings(features_by_zip[z]["geometry"], viewport, width, height)
        for ring in rings:
            if len(ring) >= 3:
                draw.polygon(
                    ring,
                    fill=fill,
                    outline=config["highlight_outline"],
                    width=int(config.get("highlight_outline_width", 1)),
                )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)

    return {
        "map_output": str(output_path),
        "state_geojson": str(state_geojson_path),
        "viewport_mode": viewport_mode,
        "viewport_bounds": viewport,
        "data_bounds": data_bounds,
        "spread_miles": spread_miles,
        "data_zips_received": len(normalized_impressions),
        "matched_zips": len(matched_zips),
        "missing_zips": sorted(missing_zips),
        "visible_background_zips": len(visible_zips),
        "highlighted_zips": len(matched_zips),
    }


def render_state_context_map(
    state_geojson_path: str | Path,
    output_path: str | Path,
    config: dict,
) -> dict:
    """Render a non-ZIP fallback map for broad geo targeting.

    Congressional-district, county, and state targeting exports may not include
    ZIP-level matched locations. Without separate congressional/county boundary
    geometry, the safest behavior is to render the state ZIP/ZCTA basemap as
    context and avoid falsely highlighting ZIPs that were not present in the
    source data.
    """
    geo = load_json(state_geojson_path)
    width = int(config["map_width"])
    height = int(config["map_height"])
    target_aspect = width / height

    features_by_zip: Dict[str, dict] = {}
    feature_bounds: Dict[str, Bounds] = {}

    for feature in geo.get("features", []):
        z = get_feature_zip(feature, config["zip_property_candidates"])
        if not z:
            continue
        geometry = feature.get("geometry")
        if not geometry:
            continue
        try:
            b = geometry_bounds(geometry)
        except Exception:
            continue
        features_by_zip[z] = feature
        feature_bounds[z] = b

    if not feature_bounds:
        raise ValueError("Selected state GeoJSON contains no usable ZIP/ZCTA polygons.")

    state_bounds = combine_bounds(list(feature_bounds.values()))
    viewport = expand_to_aspect_ratio(state_bounds, target_aspect)
    visible_zips = [z for z, b in feature_bounds.items() if bounds_intersect(b, viewport)]

    img = Image.new("RGB", (width, height), config["map_background"])
    draw = ImageDraw.Draw(img)

    for z in visible_zips:
        rings = geometry_to_pixel_rings(features_by_zip[z]["geometry"], viewport, width, height)
        for ring in rings:
            if len(ring) >= 3:
                draw.polygon(
                    ring,
                    fill=config["background_zip_fill"],
                    outline=config["background_zip_outline"],
                    width=int(config.get("background_zip_outline_width", 1)),
                )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)

    return {
        "map_output": str(output_path),
        "state_geojson": str(state_geojson_path),
        "viewport_mode": "state_context_no_zip_data",
        "viewport_bounds": viewport,
        "data_bounds": state_bounds,
        "spread_miles": 0.0,
        "data_zips_received": 0,
        "matched_zips": 0,
        "missing_zips": [],
        "visible_background_zips": len(visible_zips),
        "highlighted_zips": 0,
        "map_note": "No ZIP-level matched-location data was available; rendered state context map only.",
    }
