"""Locked, deterministic report renderer.

This file implements production-safe item #4:
- use the Base True template as locked background
- draw data, charts, and map only inside approved fixed boxes
- never use auto-layout or LLM-based placement decisions
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
except Exception:  # pragma: no cover
    canvas = None
    ImageReader = None

from .charts import render_demographics_chart, render_device_chart, render_time_chart
from .config import BOXES, COLORS, MAP_CONFIG, PAGE_HEIGHT, PAGE_WIDTH
from .data_parser import SnapshotData, find_state_geojson
from .map_renderer import render_cropped_zip_map
from .utils import fmt_freq, fmt_int, fmt_money, font, trim_text_to_width, validate_required_fonts
from .validation import validate_static_regions


def paste_rgba(base: Image.Image, overlay: Image.Image, x: int, y: int) -> None:
    if overlay.mode != "RGBA":
        overlay = overlay.convert("RGBA")
    base.alpha_composite(overlay, (x, y))


def write_pdf_from_png(output_png: Path, output_pdf: Path) -> None:
    img = Image.open(output_png).convert("RGB")
    if canvas and ImageReader:
        page_w = 792
        page_h = page_w * (img.height / img.width)
        c = canvas.Canvas(str(output_pdf), pagesize=(page_w, page_h))
        c.drawImage(ImageReader(img), 0, 0, width=page_w, height=page_h)
        c.showPage()
        c.save()
    else:
        img.save(output_pdf, "PDF", resolution=300.0)


def render_snapshot(
    *,
    template_path: Path,
    data: SnapshotData,
    geo_dir: Path,
    output_png: Path,
    output_pdf: Path,
    map_output: Optional[Path] = None,
) -> dict:
    # Fail before writing a client report if the approved dynamic-output fonts are unavailable.
    font_audit = validate_required_fonts()

    base = Image.open(template_path).convert("RGBA")
    if base.size != (PAGE_WIDTH, PAGE_HEIGHT):
        raise ValueError(f"Template must be {PAGE_WIDTH}x{PAGE_HEIGHT}px. Got {base.size}.")

    draw = ImageDraw.Draw(base)

    # Header client/date.
    x, y, w0, h0 = BOXES["client_cover"]
    draw.rectangle((x, y, x + w0, y + h0), fill=COLORS["dark_green"])
    draw.text(BOXES["client_name"], data.client_name, fill=COLORS["text_cream"], font=font("heavy", 58))
    draw.text(BOXES["date_range"], data.date_range_header, fill=COLORS["text_cream"], font=font("bold", 31))

    # KPI cards.
    kpi_values = [
        fmt_int(data.total_reach),
        fmt_freq(data.avg_frequency),
        fmt_money(data.total_spent),
        fmt_money(data.avg_cpm),
    ]
    kpi_labels = ["Total Campaign Reach", "Avg. Frequency", "Total Amount Spent", "Avg. CPM"]
    value_font = font("heavy", 31)
    label_font = font("medium", 14)
    for (x, y, w, h), value, label in zip(BOXES["kpis"], kpi_values, kpi_labels):
        draw.text((x + w // 2, y + 25), value, fill=COLORS["text_cream"], font=value_font, anchor="ma")
        draw.text((x + w // 2, y + 64), label, fill=COLORS["text_cream"], font=label_font, anchor="ma")

    # Geo header state name.
    draw.text(BOXES["geo_state_text"], data.state_name, fill=COLORS["text_cream"], font=font("bold", 18), anchor="ma")

    # Top 30 channels: one row per item, vertically centered, with row-local clearing.
    ch = BOXES["channels"]
    channel_font = font("medium", 16)
    value_font_ch = font("bold", 16)
    channels_30 = list(data.top_channels[:30])
    rendered_rows = 0
    blank_rows = 0
    row_bands = ch.get("row_bands") or [
        (ch["start_y"] + i * ch["row_h"], ch["start_y"] + (i + 1) * ch["row_h"] - 1)
        for i in range(30)
    ]

    for i in range(30):
        row_top, row_bottom = row_bands[i]
        row_mid_y = (row_top + row_bottom) // 2
        row_fill = COLORS["row_alt"] if i % 2 == 1 else COLORS["cream"]

        # Remove placeholder guide text underneath dynamic text so rows stay crisp.
        draw.rectangle((ch["name_x"] - 8, row_top + 2, ch["name_max_x"], row_bottom - 2), fill=row_fill)
        draw.rectangle((ch["value_right_x"] - 110, row_top + 2, ch["value_right_x"] + 4, row_bottom - 2), fill=row_fill)

        if i < len(channels_30):
            name, impressions = channels_30[i]
            clean_name = trim_text_to_width(draw, name, channel_font, ch["name_max_x"] - ch["name_x"])
            draw.text((ch["name_x"], row_mid_y), clean_name, fill=COLORS["text_green"], font=channel_font, anchor="lm")
            draw.text((ch["value_right_x"], row_mid_y), fmt_int(impressions), fill=COLORS["text_green"], font=value_font_ch, anchor="rm")
            rendered_rows += 1
        else:
            blank_rows += 1

    # Map.
    state_geojson_path = find_state_geojson(data.state_abbr, geo_dir)
    if map_output is None:
        map_output = output_png.parent / "generated_map.png"
    map_result = render_cropped_zip_map(
        zip_impressions=data.zip_impressions,
        state_geojson_path=state_geojson_path,
        output_path=map_output,
        config=MAP_CONFIG,
    )
    map_img = Image.open(map_output).convert("RGBA")
    mx, my, mw, mh = BOXES["map_plot"]
    if map_img.size != (mw, mh):
        map_img = map_img.resize((mw, mh), Image.Resampling.LANCZOS)
    paste_rgba(base, map_img, mx, my)

    # Top ZIPs line.
    top_zips_text = "  •  Top ZIPs:    " + ", ".join(f"{z} ({fmt_int(v)})" for z, v in data.top_zips)
    draw.text(BOXES["top_zips"], top_zips_text, fill=COLORS["text_green"], font=font("bold", 16))

    # Bottom charts.
    for key, chart_fn, args in [
        ("device_chart", render_device_chart, (data.devices,)),
        ("demo_chart", render_demographics_chart, (data.gender, data.age)),
        ("time_chart", render_time_chart, (data.hours,)),
    ]:
        x, y, w, h = BOXES[key]
        chart = chart_fn(*args, (w, h))
        paste_rgba(base, chart, x, y)

    # Footer generated date.
    fx, fy, fw, fh = BOXES["footer_cover"]
    draw.rectangle((fx, fy, fx + fw, fy + fh), fill=COLORS["page_bg"])
    footer = f"alamointelligence.com  ·     Report Generated: {data.generated_date}"
    draw.text(BOXES["footer_text"], footer, fill=COLORS["text_green"], font=font("medium", 16))

    output_png.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(output_png, quality=95)
    write_pdf_from_png(output_png, output_pdf)

    validation_result = validate_static_regions(template_path, output_png)
    return {
        "output_png": str(output_png),
        "output_pdf": str(output_pdf),
        "map": map_result,
        "validation": validation_result,
        "fonts": font_audit,
        "top30": {
            "source_rows": len(data.top_channels),
            "rendered_rows": rendered_rows,
            "blank_rows": blank_rows,
        },
    }


def write_validation_report(result: dict, output_txt: Path) -> None:
    output_txt.parent.mkdir(parents=True, exist_ok=True)
    map_result = result.get("map", {})
    validation = result.get("validation", {})
    fonts = result.get("fonts", {})
    top30 = result.get("top30", {})
    lines = [
        "Alamo Snapshot Validation",
        "",
        "Top 30 Table:",
        f"- Source rows available: {top30.get('source_rows')}",
        f"- Rows rendered: {top30.get('rendered_rows')}",
        f"- Blank rows: {top30.get('blank_rows')}",
        "- Rule: one channel per row; blanks allowed only when fewer than 30 source rows exist.",
        "",
        "Static Layout:",
        f"- Checked samples: {validation.get('checked_samples')}",
        f"- Changed samples outside dynamic boxes: {validation.get('changed_samples_outside_dynamic_boxes')}",
        f"- Changed static pct: {validation.get('changed_static_pct'):.6f}%",
        "- Expected: 0.000000% or near-zero.",
        "",
        "Fonts:",
        "- Font policy: strict approved-font mode; no DejaVu/Pillow fallback allowed.",
    ]
    for style, path in fonts.items():
        lines.append(f"- {style}: {path}")
    lines.extend([
        "",
        "Map:",
        f"- State GeoJSON: {map_result.get('state_geojson')}",
        f"- Viewport mode: {map_result.get('viewport_mode')}",
        f"- Viewport bounds: {map_result.get('viewport_bounds')}",
        f"- Data bounds: {map_result.get('data_bounds')}",
        f"- Data spread miles: {map_result.get('spread_miles'):.2f}",
        f"- Data ZIPs received: {map_result.get('data_zips_received')}",
        f"- ZIP polygons matched: {map_result.get('matched_zips')}",
        f"- Missing ZIP polygons: {len(map_result.get('missing_zips') or [])}",
        f"- Missing ZIPs: {', '.join(map_result.get('missing_zips') or [])}",
        f"- Visible surrounding ZIPs: {map_result.get('visible_background_zips')}",
        f"- Highlighted ZIPs: {map_result.get('highlighted_zips')}",
        "",
        "Output:",
        f"- PNG: {result.get('output_png')}",
        f"- PDF: {result.get('output_pdf')}",
    ])
    output_txt.write_text("\n".join(lines), encoding="utf-8")
