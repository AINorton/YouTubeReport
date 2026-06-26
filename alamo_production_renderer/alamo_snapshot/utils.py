"""Shared helpers for parsing, formatting, fonts, and drawing."""
from __future__ import annotations

import csv
import io
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, List

from PIL import ImageDraw, ImageFont

from .config import FONT_PATHS, REQUIRE_APPROVED_FONTS


def read_text_csv(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")) or raw[:200].count(b"\x00") > 20:
        return raw.decode("utf-16", errors="replace")
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def nonempty_lines(text: str) -> List[str]:
    return [ln for ln in text.splitlines() if ln.strip()]


def parse_int(value: Any) -> int:
    if value is None:
        return 0
    s = str(value).strip().replace('"', '').replace(',', '').replace('%', '')
    if s in ("", "--", " -", "-"):
        return 0
    try:
        return int(float(s))
    except ValueError:
        return 0


def parse_float(value: Any) -> float:
    if value is None:
        return 0.0
    s = str(value).strip().replace('"', '').replace(',', '').replace('$', '').replace('%', '')
    if s in ("", "--", " -", "-"):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def normalize_zip(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip().split("-")[0].split(".")[0]
    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return None
    return digits.zfill(5)[-5:]


def fmt_int(n: int | float) -> str:
    return f"{int(round(n)):,}"


def fmt_money(n: int | float) -> str:
    return f"${float(n):,.2f}"


def fmt_freq(n: int | float) -> str:
    return f"{float(n):.1f}×"


def format_header_range(date_range: str) -> str:
    parts = [p.strip().strip('"') for p in date_range.split("-")]
    if len(parts) < 2:
        return date_range
    try:
        start = datetime.strptime(parts[0], "%B %d, %Y")
        end = datetime.strptime(parts[1], "%B %d, %Y")
        if start.year == end.year:
            return f"{start.strftime('%B')} {start.day} - {end.strftime('%B')} {end.day}"
        return f"{start.strftime('%B')} {start.day}, {start.year} - {end.strftime('%B')} {end.day}, {end.year}"
    except Exception:
        return date_range


def format_generated_date(date_range: str) -> str:
    parts = [p.strip().strip('"') for p in date_range.split("-")]
    if len(parts) < 2:
        return datetime.now().strftime("%B %-d, %Y") if hasattr(datetime.now(), "strftime") else ""
    try:
        end = datetime.strptime(parts[1], "%B %d, %Y")
        return f"{end.strftime('%B')} {end.day}, {end.year}"
    except Exception:
        return parts[-1]


def resolve_font_path(style: str) -> Path:
    """Return the approved font path for a style, or fail loudly.

    Production reports must not silently fall back to a different font because that
    changes text width and visual appearance.
    """
    candidates = FONT_PATHS.get(style) or FONT_PATHS["regular"]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return path

    message = (
        f"Required approved font missing for style '{style}'. "
        f"Checked: {', '.join(str(c) for c in candidates)}. "
        "Install the approved font or update FONT_PATHS in alamo_snapshot/config.py."
    )
    if REQUIRE_APPROVED_FONTS:
        raise FileNotFoundError(message)

    return Path(candidates[0])


def get_font_audit() -> dict:
    """Return the resolved font paths for the validation report."""
    audit = {}
    for style in FONT_PATHS:
        try:
            audit[style] = str(resolve_font_path(style))
        except FileNotFoundError as exc:
            audit[style] = f"MISSING: {exc}"
    return audit


def validate_required_fonts() -> dict:
    """Fail before rendering if any configured font style cannot be resolved."""
    audit = get_font_audit()
    missing = {k: v for k, v in audit.items() if str(v).startswith("MISSING:")}
    if missing:
        details = "\n".join(f"- {style}: {msg}" for style, msg in missing.items())
        raise FileNotFoundError(f"Approved report fonts are missing:\n{details}")
    return audit


def font(style: str, size: int) -> ImageFont.FreeTypeFont:
    path = resolve_font_path(style)
    return ImageFont.truetype(str(path), size=size)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_centered(draw: ImageDraw.ImageDraw, center: tuple[int, int], text: str, fnt: ImageFont.ImageFont, fill) -> None:
    w, h = text_size(draw, text, fnt)
    draw.text((center[0] - w // 2, center[1] - h // 2), text, font=fnt, fill=fill)


def trim_text_to_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont, max_width: int) -> str:
    if text_size(draw, text, fnt)[0] <= max_width:
        return text
    ell = "..."
    out = text
    while out and text_size(draw, out + ell, fnt)[0] > max_width:
        out = out[:-1]
    return out + ell
