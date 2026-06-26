"""Locked layout, colors, and map rules for the Alamo Snapshot renderer."""
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCAL_FONT_DIR = PROJECT_ROOT / "fonts"

# The blank template image is 1585x2048 px. Do not change this unless the template changes.
PAGE_WIDTH = 1585
PAGE_HEIGHT = 2048

COLORS = {
    "page_bg": (221, 212, 197),
    "dark_green": (61, 85, 57),
    "cream": (234, 227, 214),
    "row_alt": (218, 210, 194),
    "map_bg": (122, 138, 116),
    "text_green": (47, 84, 50),
    "text_cream": (238, 232, 212),
    "muted": (106, 124, 92),
    "blue": (69, 105, 145),
    "bar_green": (65, 94, 62),
    "bar_green_2": (85, 128, 81),
    "bar_green_3": (164, 201, 156),
    "border_blue": (64, 91, 109),
    "county": (188, 181, 164),
    "state_fill": (197, 192, 174),
    "zip_light": (224, 245, 174),
    "zip_mid": (145, 206, 119),
    "zip_dark": (0, 91, 57),
}

# Coordinate map in template pixels. These are intentionally fixed.
# Only change after measuring a new template and updating validation masks.
BOXES = {
    "client_cover": (585, 38, 430, 130),
    "client_name": (597, 54),
    "date_range": (597, 126),
    "kpis": [
        (604, 207, 210, 90),
        (833, 207, 210, 90),
        (1061, 207, 210, 90),
        (1288, 207, 210, 90),
    ],
    "channels": {
        "start_y": 411,
        "row_h": 35,
        # Exact measured row bands from the locked Base True template.
        # Use these instead of inferred line spacing so all 30 rows stay aligned.
        "row_bands": [
            (411, 446), (448, 481), (483, 518), (521, 554), (556, 591),
            (593, 626), (629, 664), (666, 699), (701, 734), (737, 770),
            (772, 807), (809, 842), (845, 880), (882, 915), (917, 952),
            (955, 988), (990, 1025), (1027, 1060), (1063, 1096), (1098, 1131),
            (1133, 1168), (1171, 1204), (1206, 1241), (1243, 1276), (1279, 1314),
            (1316, 1349), (1351, 1386), (1389, 1422), (1424, 1457), (1459, 1492),
        ],
        "rank_x": 74,
        "name_x": 118,
        "value_right_x": 800,
        "name_max_x": 650,
    },
    "geo_state_text": (1128, 356),
    "map_inner": (835, 413, 683, 1044),
    "map_plot": (855, 450, 638, 880),
    "top_zips": (860, 1469),
    "device_chart": (62, 1586, 465, 350),
    "demo_chart": (552, 1586, 465, 350),
    "time_chart": (1048, 1586, 465, 350),
    "footer_cover": (530, 1970, 560, 40),
    "footer_text": (620, 1983),
}

# Production font policy:
# - The report template appears Lato-like. Lato is the approved working font for dynamic output.
# - Do not silently fall back to DejaVu or Pillow default fonts in client output.
# - If the final brand/template font is confirmed later, replace these paths with that approved font.
REQUIRE_APPROVED_FONTS = True

FONT_PATHS = {
    # Local project fonts are checked first. Run scripts/download_lato_fonts.py
    # in the target environment to populate the fonts/ folder.
    "regular": [
        LOCAL_FONT_DIR / "Lato-Regular.ttf",
        "/usr/share/fonts/truetype/lato/Lato-Regular.ttf",
    ],
    "medium": [
        LOCAL_FONT_DIR / "Lato-Medium.ttf",
        "/usr/share/fonts/truetype/lato/Lato-Medium.ttf",
    ],
    "semibold": [
        LOCAL_FONT_DIR / "Lato-Semibold.ttf",
        LOCAL_FONT_DIR / "Lato-Bold.ttf",
        "/usr/share/fonts/truetype/lato/Lato-Semibold.ttf",
        "/usr/share/fonts/truetype/lato/Lato-Bold.ttf",
    ],
    "bold": [
        LOCAL_FONT_DIR / "Lato-Bold.ttf",
        "/usr/share/fonts/truetype/lato/Lato-Bold.ttf",
    ],
    "heavy": [
        LOCAL_FONT_DIR / "Lato-Heavy.ttf",
        LOCAL_FONT_DIR / "Lato-Black.ttf",
        "/usr/share/fonts/truetype/lato/Lato-Heavy.ttf",
        "/usr/share/fonts/truetype/lato/Lato-Black.ttf",
    ],
    "italic": [
        LOCAL_FONT_DIR / "Lato-Italic.ttf",
        "/usr/share/fonts/truetype/lato/Lato-Italic.ttf",
    ],
    "semibold_italic": [
        LOCAL_FONT_DIR / "Lato-SemiboldItalic.ttf",
        LOCAL_FONT_DIR / "Lato-BoldItalic.ttf",
        "/usr/share/fonts/truetype/lato/Lato-SemiboldItalic.ttf",
        "/usr/share/fonts/truetype/lato/Lato-BoldItalic.ttf",
    ],
}


STATE_NAMES = {
    "al": "Alabama", "ak": "Alaska", "az": "Arizona", "ar": "Arkansas", "ca": "California",
    "co": "Colorado", "ct": "Connecticut", "de": "Delaware", "fl": "Florida", "ga": "Georgia",
    "hi": "Hawaii", "id": "Idaho", "il": "Illinois", "in": "Indiana", "ia": "Iowa",
    "ks": "Kansas", "ky": "Kentucky", "la": "Louisiana", "me": "Maine", "md": "Maryland",
    "ma": "Massachusetts", "mi": "Michigan", "mn": "Minnesota", "ms": "Mississippi", "mo": "Missouri",
    "mt": "Montana", "ne": "Nebraska", "nv": "Nevada", "nh": "New Hampshire", "nj": "New Jersey",
    "nm": "New Mexico", "ny": "New York", "nc": "North Carolina", "nd": "North Dakota", "oh": "Ohio",
    "ok": "Oklahoma", "or": "Oregon", "pa": "Pennsylvania", "ri": "Rhode Island", "sc": "South Carolina",
    "sd": "South Dakota", "tn": "Tennessee", "tx": "Texas", "ut": "Utah", "vt": "Vermont",
    "va": "Virginia", "wa": "Washington", "wv": "West Virginia", "wi": "Wisconsin", "wy": "Wyoming",
    "dc": "District of Columbia",
}

MAP_CONFIG = {
    # Must match BOXES["map_plot"] size. The report box never moves.
    "map_width": BOXES["map_plot"][2],
    "map_height": BOXES["map_plot"][3],

    # Viewport/crop behavior.
    "padding_percent": 0.25,
    "min_padding_miles": 20,
    "max_padding_miles": 90,
    "spread_full_state_threshold_miles": 250,

    # GeoJSON property names. The uploaded Texas file uses ZCTA5CE10.
    "zip_property_candidates": [
        "ZCTA5CE10",
        "ZCTA5CE20",
        "ZCTA5CE",
        "GEOID10",
        "GEOID20",
        "GEOID",
        "ZIP",
        "ZIPCODE",
        "zip",
    ],

    # Styling must stay close to the Base True image.
    "background_zip_fill": "#c7c0ad",
    "background_zip_outline": "#b5ae9e",
    "highlight_outline": "#e9ead2",
    "highlight_palette": [
        "#eef8cf",
        "#c9ec9b",
        "#8fd36e",
        "#3fa75a",
        "#006b3b",
        "#00482f",
    ],
    "map_background": "#7a8a74",
}

DEFAULT_TEMPLATE = Path("templates") / "Alamo Intelligence Snapshot Base True (1).png"
DEFAULT_GEO_DIR = Path("geo")
DEFAULT_OUTPUT_DIR = Path("output")
