"""CSV parsing and normalization for Alamo YouTube Snapshot reports."""
from __future__ import annotations

import csv
import io
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .config import STATE_NAMES
from .utils import (
    format_generated_date,
    format_header_range,
    nonempty_lines,
    normalize_zip,
    parse_float,
    parse_int,
    read_text_csv,
)

STATE_ABBR_BY_NAME = {name.lower(): abbr for abbr, name in STATE_NAMES.items()}
ZIP_TOKEN_RE = re.compile(r"^\d{5}(?:-\d{4})?$")
CONGRESSIONAL_DISTRICT_RE = re.compile(
    r"(?P<state>.+?)'s\s+(?P<district>\d+)(?:st|nd|rd|th)\s+Congressional District",
    re.IGNORECASE,
)


@dataclass
class SnapshotData:
    client_name: str
    date_range_raw: str
    date_range_header: str
    generated_date: str
    total_reach: int
    avg_frequency: float
    total_spent: float
    avg_cpm: float
    top_channels: List[Tuple[str, int]]
    locations: List[Dict[str, Any]]
    state_abbr: str
    state_name: str
    top_zips: List[Tuple[str, int]]
    zip_impressions: Dict[str, int]
    geo_summary_label: str
    geo_targeting_mode: str
    devices: List[Tuple[str, int]]
    gender: List[Tuple[str, int]]
    age: List[Tuple[str, int]]
    hours: List[Tuple[str, int]]


def _detect_delimiter(line: str) -> str:
    """Pick the delimiter used by an exported Google Ads table header."""
    if line.count("\t") >= line.count(","):
        return "\t"
    return ","


def _dict_rows_from_export(lines: List[str], required_header_terms: List[str]) -> List[Dict[str, Any]]:
    """Return DictReader rows from the first line matching the expected header terms.

    Google Ads exports in this workflow have appeared as UTF-16 tab-delimited
    files and UTF-8 comma-delimited files. This helper keeps category parsers
    content-based instead of relying only on file names or one delimiter.
    """
    header_start = 0
    delimiter = ","
    lowered_terms = [term.lower() for term in required_header_terms]
    for i, line in enumerate(lines):
        lower = line.lower()
        if all(term in lower for term in lowered_terms):
            header_start = i
            delimiter = _detect_delimiter(line)
            break
    reader = csv.DictReader(io.StringIO("\n".join(lines[header_start:])), delimiter=delimiter)
    return list(reader)


def _extract_state_abbr(location: str) -> str | None:
    parts = [p.strip().strip('"').lower() for p in str(location).split(",")]
    for part in parts:
        if part in STATE_ABBR_BY_NAME:
            return STATE_ABBR_BY_NAME[part]
    return None


def _strict_zip_from_location(location: str) -> str | None:
    first = str(location).split(",")[0].strip().strip('"')
    if ZIP_TOKEN_RE.fullmatch(first):
        return normalize_zip(first)
    return None


def _location_type(location: str) -> str:
    first = str(location).split(",")[0].strip().strip('"')
    lower = first.lower()
    if _strict_zip_from_location(location):
        return "zip"
    if "congressional district" in lower:
        return "congressional_district"
    if lower.endswith(" county"):
        return "county"
    if lower in STATE_ABBR_BY_NAME:
        return "state"
    return "other"


def _compact_location_label(location: str) -> str:
    first = str(location).split(",")[0].strip().strip('"')
    state_abbr = _extract_state_abbr(location)

    m = CONGRESSIONAL_DISTRICT_RE.search(first)
    if m:
        state_name = m.group("state").strip().lower()
        abbr = STATE_ABBR_BY_NAME.get(state_name, state_abbr)
        district = int(m.group("district"))
        if abbr:
            return f"{abbr.upper()}-{district:02d} Congressional District"
        return f"District {district:02d} Congressional District"

    if state_abbr and not first.lower().endswith(state_abbr.lower()):
        return f"{first}, {state_abbr.upper()}"
    return first


def parse_campaign_report(path: Path) -> Dict[str, Any]:
    text = read_text_csv(path)
    lines = nonempty_lines(text)
    date_range = lines[1].strip().strip('"') if len(lines) > 1 else ""

    reader = csv.DictReader(io.StringIO("\n".join(lines[2:])), delimiter="\t")
    rows = list(reader)
    total = None
    for r in rows:
        status = str(r.get("Campaign status", "")).strip()
        if status == "Total: Filtered campaigns":
            total = r
            break
    if total is None:
        for r in rows:
            if str(r.get("Campaign status", "")).strip().startswith("Total:"):
                total = r
                break
    if total is None:
        total = rows[-1] if rows else {}

    return {
        "date_range": date_range,
        "reach": parse_int(total.get("Unique users")),
        "impressions": parse_int(total.get("Impr.")),
        "cost": parse_float(total.get("Cost")),
        "avg_cpm": parse_float(total.get("Avg. CPM")),
        "frequency": parse_float(total.get("Avg. impr. freq. / user")),
    }


def parse_placements(path: Path, n: int = 30) -> List[Tuple[str, int]]:
    text = read_text_csv(path)
    lines = nonempty_lines(text)
    reader = csv.DictReader(io.StringIO("\n".join(lines)), delimiter="\t")
    agg = Counter()
    for r in reader:
        name = str(r.get("Placement", "")).strip()
        if not name or name.startswith("Total:"):
            continue
        agg[name] += parse_int(r.get("Impr."))
    return agg.most_common(n)


def parse_locations(path: Path) -> List[Dict[str, Any]]:
    text = read_text_csv(path)
    lines = nonempty_lines(text)
    rows = _dict_rows_from_export(lines, ["Location", "Impr."])

    out: List[Dict[str, Any]] = []
    for r in rows:
        loc = str(r.get("Matched location") or r.get("Location") or "").strip().strip('"')
        if not loc or loc.startswith("Total:"):
            continue

        zip_code = _strict_zip_from_location(loc)
        location_type = _location_type(loc)
        state_abbr = _extract_state_abbr(loc)
        impressions = parse_int(r.get("Impr.") or r.get("Impressions"))

        out.append({
            "location": loc,
            "display_location": _compact_location_label(loc),
            "location_type": location_type,
            "state_abbr": state_abbr,
            "zip": zip_code,
            "impressions": impressions,
        })
    return out


def parse_simple_csv(path: Path, label_col: str, value_col: str = "Impressions") -> List[Tuple[str, int]]:
    text = read_text_csv(path)
    lines = nonempty_lines(text)
    reader = csv.DictReader(io.StringIO("\n".join(lines)))
    out: List[Tuple[str, int]] = []
    for r in reader:
        label = str(r.get(label_col, "")).strip()
        if label:
            out.append((label, parse_int(r.get(value_col))))
    return out


def find_one(input_dir: Path, pattern: str) -> Path:
    matches = sorted(input_dir.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"Missing required CSV matching: {pattern}")
    return matches[0]


def find_first(input_dir: Path, patterns: List[str]) -> Path:
    for pattern in patterns:
        matches = sorted(input_dir.glob(pattern))
        if matches:
            return matches[0]
    raise FileNotFoundError(f"Missing required CSV matching one of: {', '.join(patterns)}")


def load_zip_to_state(geo_dir: Path) -> Dict[str, str]:
    path = geo_dir / "zip_to_state.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing ZIP-to-state lookup: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return {normalize_zip(k): str(v).lower() for k, v in data.items() if normalize_zip(k)}


def build_zip_impressions(locations: List[Dict[str, Any]]) -> Dict[str, int]:
    out: Counter[str] = Counter()
    for row in locations:
        z = normalize_zip(row.get("zip"))
        if z:
            out[z] += int(row.get("impressions") or 0)
    return dict(out)


def build_non_zip_geo_summary(locations: List[Dict[str, Any]], n: int = 3) -> List[Tuple[str, int]]:
    out: Counter[str] = Counter()
    for row in locations:
        if row.get("zip"):
            continue
        label = str(row.get("display_location") or row.get("location") or "").strip()
        if label:
            out[label] += int(row.get("impressions") or 0)
    return out.most_common(n)


def determine_primary_state(zip_impressions: Dict[str, int], zip_to_state: Dict[str, str]) -> str:
    state_weights: Counter[str] = Counter()
    for z, impressions in zip_impressions.items():
        state = zip_to_state.get(normalize_zip(z) or "")
        if state:
            state_weights[state.lower()] += int(impressions)
    if not state_weights:
        raise ValueError("Could not determine state from ZIP data. Check zip_to_state.json and matched location ZIPs.")
    return state_weights.most_common(1)[0][0]


def determine_primary_state_from_locations(locations: List[Dict[str, Any]]) -> str:
    state_weights: Counter[str] = Counter()
    for row in locations:
        state = str(row.get("state_abbr") or "").lower()
        if state:
            state_weights[state] += int(row.get("impressions") or 0)
    if not state_weights:
        raise ValueError(
            "Could not determine state from matched locations. "
            "Expected ZIP, county, state, or congressional district locations with a state name."
        )
    return state_weights.most_common(1)[0][0]


def find_state_geojson(state_abbr: str, geo_dir: Path) -> Path:
    state_abbr = state_abbr.lower()
    matches = sorted((geo_dir / "states").glob(f"{state_abbr}_*.json"))
    if not matches:
        raise FileNotFoundError(
            f"No GeoJSON file found for state '{state_abbr}'. Expected geo/states/{state_abbr}_*.json"
        )
    return matches[0]


def load_snapshot(input_dir: Path, geo_dir: Path, client_name: str) -> SnapshotData:
    campaign = parse_campaign_report(find_one(input_dir, "Campaign report*.csv"))
    channels = parse_placements(find_one(input_dir, "Automatic placements report*.csv"), 30)
    locations = parse_locations(find_first(input_dir, ["Matched locations report*.csv", "Location report*.csv"]))
    zip_impressions = build_zip_impressions(locations)

    zip_to_state = load_zip_to_state(geo_dir)
    if zip_impressions:
        state_abbr = determine_primary_state(zip_impressions, zip_to_state)
        top_geos = sorted(zip_impressions.items(), key=lambda x: x[1], reverse=True)[:3]
        geo_summary_label = "Top ZIPs"
        geo_targeting_mode = "zip"
    else:
        state_abbr = determine_primary_state_from_locations(locations)
        top_geos = build_non_zip_geo_summary(locations, 3)
        geo_summary_label = "Top Geos"
        geo_targeting_mode = "non_zip"

    state_name = STATE_NAMES.get(state_abbr.lower(), state_abbr.upper())

    devices = parse_simple_csv(find_one(input_dir, "Devices*.csv"), "Device")
    gender = parse_simple_csv(find_one(input_dir, "Demographics(Gender*.csv"), "Gender")
    age = parse_simple_csv(find_one(input_dir, "Demographics(Age*.csv"), "Age Range")
    hours = parse_simple_csv(find_one(input_dir, "Day_&_hour*.csv"), "Start Hour")

    return SnapshotData(
        client_name=client_name,
        date_range_raw=campaign["date_range"],
        date_range_header=format_header_range(campaign["date_range"]),
        generated_date=format_generated_date(campaign["date_range"]),
        total_reach=campaign["reach"],
        avg_frequency=campaign["frequency"],
        total_spent=campaign["cost"],
        avg_cpm=campaign["avg_cpm"],
        top_channels=channels,
        locations=locations,
        state_abbr=state_abbr,
        state_name=state_name,
        top_zips=top_geos,
        zip_impressions=zip_impressions,
        geo_summary_label=geo_summary_label,
        geo_targeting_mode=geo_targeting_mode,
        devices=devices,
        gender=gender,
        age=age,
        hours=hours,
    )
