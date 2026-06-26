#!/usr/bin/env python3
"""Verify that the renderer can resolve every approved report font."""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from alamo_snapshot.utils import validate_required_fonts  # noqa: E402


def main() -> int:
    audit = validate_required_fonts()
    print("Approved report fonts resolved:")
    for style, path in audit.items():
        print(f"- {style}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
