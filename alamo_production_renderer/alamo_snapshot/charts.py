"""Deterministic chart renderers for the bottom panels."""
from __future__ import annotations

import math
from typing import List, Tuple

from PIL import Image, ImageDraw

from .config import COLORS
from .utils import draw_centered, fmt_int, font


def render_device_chart(devices: List[Tuple[str, int]], size: Tuple[int, int]) -> Image.Image:
    w, h = size
    im = Image.new("RGBA", size, COLORS["cream"] + (0,))
    d = ImageDraw.Draw(im)
    small_font = font("medium", 14)
    pct_font = font("bold", 18)

    order = ["TV screens", "Mobile phones", "Tablets", "Computers"]
    vals = {k: v for k, v in devices}
    items = [(k, vals[k]) for k in order if k in vals]
    for k, v in devices:
        if k not in dict(items):
            items.append((k, v))
    items = items[:4]

    total = sum(v for _, v in items) or 1
    colors = [COLORS["bar_green"], COLORS["bar_green_2"], COLORS["bar_green_3"], COLORS["blue"]]

    bbox = (90, 25, 310, 245)
    start = -95
    cx, cy = 200, 135
    radius = (bbox[2] - bbox[0]) / 2
    for (name, val), col in zip(items, colors):
        extent = 360 * val / total
        d.pieslice(bbox, start, start + extent, fill=col)
        mid = math.radians(start + extent / 2)
        pct = 100 * val / total
        if pct >= 3:
            tx = cx + math.cos(mid) * (radius * 0.72)
            ty = cy + math.sin(mid) * (radius * 0.72)
            draw_centered(d, (int(tx), int(ty)), f"{pct:.1f}%", pct_font, COLORS["text_cream"])
        start += extent

    d.ellipse((150, 85, 250, 185), fill=COLORS["cream"])

    legend_xs = [95, 260, 95, 260]
    legend_ys = [275, 275, 313, 313]
    for i, ((name, val), col) in enumerate(zip(items, colors)):
        x, y = legend_xs[i], legend_ys[i]
        d.rectangle((x, y, x + 22, y + 13), fill=col)
        label = name.replace("phones", "Phones").replace("screens", "Screens")
        d.text((x + 30, y - 5), label, fill=COLORS["text_green"], font=small_font)
        d.text((x + 30, y + 12), fmt_int(val), fill=COLORS["text_green"], font=small_font)
    return im


def render_demographics_chart(gender: List[Tuple[str, int]], age: List[Tuple[str, int]], size: Tuple[int, int]) -> Image.Image:
    w, h = size
    im = Image.new("RGBA", size, COLORS["cream"] + (0,))
    d = ImageDraw.Draw(im)
    title_font = font("bold", 15)
    label_font = font("medium", 13)
    value_font = font("bold", 12)

    d.text((w // 2, 5), "Gender", font=title_font, fill=COLORS["text_green"], anchor="ma")
    g_colors = {"Male": COLORS["bar_green"], "Female": COLORS["blue"]}
    max_g = max([v for _, v in gender] + [1])
    gx = [125, 345]
    base_y = 135
    max_h = 92
    for i, (name, val) in enumerate(gender[:2]):
        bh = max(8, int(max_h * val / max_g))
        x = gx[i]
        d.rectangle((x - 48, base_y - bh, x + 48, base_y), fill=g_colors.get(name, COLORS["bar_green_2"]))
        d.text((x, base_y - bh - 20), fmt_int(val), fill=COLORS["text_green"], font=value_font, anchor="ma")
        d.text((x, base_y + 12), name, fill=COLORS["muted"], font=label_font, anchor="ma")

    d.text((w // 2, 178), "Age Range", font=title_font, fill=COLORS["text_green"], anchor="ma")
    max_a = max([v for _, v in age] + [1])
    base_y2 = 315
    max_h2 = 100
    n = len(age)
    left, right = 55, w - 45
    gap = 18
    bw = max(24, int((right - left - gap * (n - 1)) / max(n, 1)))
    age_colors = [COLORS["bar_green_3"], COLORS["bar_green_2"], COLORS["bar_green"], COLORS["bar_green_2"], COLORS["bar_green"], COLORS["bar_green"]]
    for i, (name, val) in enumerate(age):
        x0 = left + i * (bw + gap)
        x1 = x0 + bw
        bh = max(4, int(max_h2 * val / max_a))
        d.rectangle((x0, base_y2 - bh, x1, base_y2), fill=age_colors[i % len(age_colors)])
        d.text(((x0 + x1) // 2, base_y2 - bh - 18), fmt_int(val), fill=COLORS["text_green"], font=value_font, anchor="ma")
        d.text(((x0 + x1) // 2, base_y2 + 12), name, fill=COLORS["muted"], font=label_font, anchor="ma")
    return im


def render_time_chart(hours: List[Tuple[str, int]], size: Tuple[int, int]) -> Image.Image:
    w, h = size
    im = Image.new("RGBA", size, COLORS["cream"] + (0,))
    d = ImageDraw.Draw(im)
    label_font = font("medium", 10)
    value_font = font("medium", 9)
    max_v = max([v for _, v in hours] + [1])
    top = 15
    row_h = 13
    x_label = 75
    x_bar = 116
    max_bar_w = w - 195
    for i, (label, val) in enumerate(hours[:24]):
        y = top + i * row_h
        d.text((x_label, y + 1), label, fill=COLORS["muted"], font=label_font, anchor="ra")
        bw = max(2, int(max_bar_w * val / max_v))
        shade = COLORS["bar_green"] if val > max_v * 0.65 else COLORS["bar_green_2"]
        d.rectangle((x_bar, y + 3, x_bar + bw, y + row_h - 2), fill=shade)
        d.text((x_bar + bw + 8, y + 1), fmt_int(val), fill=COLORS["muted"], font=value_font)
    return im
