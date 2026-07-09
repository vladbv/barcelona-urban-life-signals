"""Print a lightweight, column-agnostic profile of a CSV file."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect a CSV's observed columns, types, missingness, and sample rows."
    )
    parser.add_argument("csv_path", type=Path, help="path to a CSV under data/raw")
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="text encoding passed to pandas (default: utf-8)",
    )
    parser.add_argument(
        "--separator",
        default=",",
        help=r"field separator passed to pandas (default: ',')",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.csv_path.is_file():
        raise SystemExit(f"File not found: {args.csv_path}")

    frame = pd.read_csv(
        args.csv_path,
        encoding=args.encoding,
        sep=args.separator,
        low_memory=False,
    )

    print(f"File: {args.csv_path}")
    print(f"Shape: {frame.shape[0]:,} rows x {frame.shape[1]:,} columns")
    print(f"Exact duplicate rows: {frame.duplicated().sum():,}")
    print("\nColumns and inferred types:")
    print(frame.dtypes.to_string())
    print("\nMissing values:")
    missing = pd.DataFrame(
        {
            "count": frame.isna().sum(),
            "percent": (frame.isna().mean() * 100).round(2),
        }
    )
    print(missing.to_string())
    print("\nFirst 5 rows:")
    print(frame.head().to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
