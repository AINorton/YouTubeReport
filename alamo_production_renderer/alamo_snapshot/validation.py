"""Static-layout validation for the locked renderer."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Tuple

from PIL import Image

from .config import BOXES

Rect = Tuple[int, int, int, int]


def dynamic_rectangles() -> list[Rect]:
    rects: list[Rect] = []
    x, y, w, h = BOXES["client_cover"]
    rects.append((x, y, x + w, y + h))
    for x, y, w, h in BOXES["kpis"]:
        rects.append((x, y, x + w, y + h))

    # Left table data area.
    # If explicit measured row bands are configured, use the true first/last
    # row bounds. This prevents row 30 from being falsely treated as static.
    ch = BOXES["channels"]
    row_bands = ch.get("row_bands") or []
    if row_bands:
        y0 = min(b[0] for b in row_bands) - 6
        y1 = max(b[1] for b in row_bands) + 10
    else:
        y0 = ch["start_y"] - 6
        y1 = ch["start_y"] + ch["row_h"] * 30 + 10
    rects.append((95, y0, 810, y1))

    # Geo header state name, map plot, and top ZIPs.
    rects.append((995, 340, 1260, 380))
    x, y, w, h = BOXES["map_plot"]
    rects.append((x, y, x + w, y + h))
    rects.append((850, 1450, 1510, 1495))

    # Bottom chart areas.
    for key in ("device_chart", "demo_chart", "time_chart"):
        x, y, w, h = BOXES[key]
        rects.append((x, y, x + w, y + h))

    # Footer generated date.
    x, y, w, h = BOXES["footer_cover"]
    rects.append((x, y, x + w, y + h))
    return rects


def inside_any(x: int, y: int, rects: list[Rect]) -> bool:
    for x0, y0, x1, y1 in rects:
        if x0 <= x <= x1 and y0 <= y <= y1:
            return True
    return False


def validate_static_regions(template_path: Path, output_png: Path, sample_step: int = 5) -> dict:
    template = Image.open(template_path).convert("RGBA")
    output = Image.open(output_png).convert("RGBA")
    if template.size != output.size:
        raise ValueError(f"Template/output size mismatch: {template.size} vs {output.size}")

    rects = dynamic_rectangles()
    checked = 0
    changed = 0
    width, height = template.size
    pix_a = template.load()
    pix_b = output.load()

    for y in range(0, height, sample_step):
        for x in range(0, width, sample_step):
            if inside_any(x, y, rects):
                continue
            checked += 1
            if pix_a[x, y] != pix_b[x, y]:
                changed += 1

    return {
        "checked_samples": checked,
        "changed_samples_outside_dynamic_boxes": changed,
        "changed_static_pct": (changed / checked * 100) if checked else 0,
    }
