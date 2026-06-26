#!/usr/bin/env python3
"""Create unique per-report input/output folders for the Alamo renderer.

This prevents uploaded CSV files from different client/report runs from mixing.
"""
from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "client"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create unique input/output folders for one report run.")
    parser.add_argument("--client", required=True, help="Client/campaign name used to name folders.")
    parser.add_argument(
        "--timestamp",
        default=None,
        help="Optional timestamp override in YYYYMMDD_HHMM format. Defaults to current local time.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stamp = args.timestamp or datetime.now().strftime("%Y%m%d_%H%M")
    if not re.fullmatch(r"\d{8}_\d{4}", stamp):
        raise ValueError("Timestamp must be in YYYYMMDD_HHMM format.")

    run_name = f"{slugify(args.client)}_{stamp}"

    input_dir = Path("input_reports") / run_name
    output_dir = Path("output") / run_name

    input_dir.mkdir(parents=True, exist_ok=False)
    output_dir.mkdir(parents=True, exist_ok=False)

    print(f"RUN_NAME={run_name}")
    print(f"INPUT_DIR={input_dir}")
    print(f"OUTPUT_DIR={output_dir}")
    print("")
    print("Place only the current report run's CSV files in INPUT_DIR.")
    print("Then run:")
    print(
        "python render_report.py "
        f"--input-dir {input_dir} "
        f"--client \"{args.client}\" "
        "--template \"templates/Alamo Intelligence Snapshot Base True (1).png\" "
        "--geo-dir geo "
        f"--output-dir {output_dir}"
    )


if __name__ == "__main__":
    main()
