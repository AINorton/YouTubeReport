#!/usr/bin/env python3
"""Download the approved Lato TTF files needed by the renderer.

The renderer is intentionally strict about fonts: it should fail if approved
font files are missing instead of silently falling back to DejaVu/Pillow fonts.

Google Fonts occasionally changes filename casing/names in the repository.
This script maps the local filenames expected by the renderer to one or more
candidate Google Fonts source filenames and saves the successful download under
the renderer's expected local name.
"""
from __future__ import annotations

import sys
import urllib.error
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = PROJECT_ROOT / "fonts"

BASE_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/lato"

# Keys are the exact local filenames expected by alamo_snapshot/config.py.
# Values are candidate upstream filenames to try in order.
REQUIRED_FONTS = {
    "Lato-Regular.ttf": ["Lato-Regular.ttf"],
    "Lato-Medium.ttf": ["Lato-Medium.ttf"],
    "Lato-Semibold.ttf": ["Lato-SemiBold.ttf", "Lato-Semibold.ttf"],
    "Lato-Bold.ttf": ["Lato-Bold.ttf"],
    # Google Fonts currently exposes ExtraBold, while the renderer expects a
    # local Heavy slot. Save ExtraBold as Lato-Heavy.ttf so config stays stable.
    "Lato-Heavy.ttf": ["Lato-ExtraBold.ttf", "Lato-Heavy.ttf", "Lato-Black.ttf"],
    "Lato-Italic.ttf": ["Lato-Italic.ttf"],
    "Lato-SemiboldItalic.ttf": ["Lato-SemiBoldItalic.ttf", "Lato-SemiboldItalic.ttf"],
}


def download_bytes(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()


def download_font(local_filename: str, upstream_candidates: list[str], dest: Path) -> str:
    errors: list[str] = []

    for upstream_name in upstream_candidates:
        url = f"{BASE_URL}/{upstream_name}"
        print(f"Trying {local_filename} <- {upstream_name}...")
        try:
            data = download_bytes(url)
        except urllib.error.HTTPError as exc:
            errors.append(f"{upstream_name}: HTTP {exc.code}")
            continue
        except Exception as exc:  # noqa: BLE001 - surface exact setup failure.
            errors.append(f"{upstream_name}: {exc}")
            continue

        if len(data) < 10_000:
            errors.append(f"{upstream_name}: unexpectedly small file ({len(data)} bytes)")
            continue

        dest.write_bytes(data)
        return upstream_name

    raise RuntimeError("; ".join(errors))


def main() -> int:
    FONT_DIR.mkdir(parents=True, exist_ok=True)

    failures: list[tuple[str, str]] = []
    resolved: list[tuple[str, str]] = []

    for local_filename, upstream_candidates in REQUIRED_FONTS.items():
        dest = FONT_DIR / local_filename
        if dest.exists() and dest.stat().st_size > 10_000:
            print(f"Already present: {dest}")
            resolved.append((local_filename, "already present"))
            continue

        try:
            upstream_used = download_font(local_filename, upstream_candidates, dest)
            print(f"Saved: {dest} from {upstream_used}")
            resolved.append((local_filename, upstream_used))
        except Exception as exc:  # noqa: BLE001 - setup script should report all failures.
            failures.append((local_filename, str(exc)))

    if failures:
        print("\nFailed to download one or more fonts:", file=sys.stderr)
        for filename, error in failures:
            print(f"- {filename}: {error}", file=sys.stderr)
        return 1

    print(f"\nLato fonts ready in: {FONT_DIR}")
    print("Resolved font sources:")
    for local_filename, upstream_used in resolved:
        print(f"- {local_filename}: {upstream_used}")
    print("\nRun `python scripts/verify_fonts.py` next.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
