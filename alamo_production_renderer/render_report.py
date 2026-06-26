#!/usr/bin/env python3
"""Main report script for deterministic Alamo Snapshot generation."""
from __future__ import annotations

import argparse
from pathlib import Path

from alamo_snapshot.config import DEFAULT_GEO_DIR, DEFAULT_OUTPUT_DIR, DEFAULT_TEMPLATE
from alamo_snapshot.data_parser import load_snapshot
from alamo_snapshot.report_renderer import render_snapshot, write_validation_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a deterministic Alamo Intelligence YouTube Snapshot report.")
    parser.add_argument("--input-dir", type=Path, required=True, help="Folder containing Google Ads CSV exports.")
    parser.add_argument("--client", required=True, help="Client name to place in the report header.")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="Locked blank Base True template PNG.")
    parser.add_argument("--geo-dir", type=Path, default=DEFAULT_GEO_DIR, help="Folder containing zip_to_state.json and states/*.json.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output folder.")
    parser.add_argument("--output-name", default="Alamo_YouTube_Snapshot_deterministic", help="Base name for PNG/PDF/validation outputs.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    data = load_snapshot(args.input_dir, args.geo_dir, args.client)

    output_png = args.output_dir / f"{args.output_name}.png"
    output_pdf = args.output_dir / f"{args.output_name}.pdf"
    output_validation = args.output_dir / f"{args.output_name}.validation.txt"

    result = render_snapshot(
        template_path=args.template,
        data=data,
        geo_dir=args.geo_dir,
        output_png=output_png,
        output_pdf=output_pdf,
    )
    write_validation_report(result, output_validation)

    print(f"PNG: {output_png}")
    print(f"PDF: {output_pdf}")
    print(f"Validation: {output_validation}")


if __name__ == "__main__":
    main()
