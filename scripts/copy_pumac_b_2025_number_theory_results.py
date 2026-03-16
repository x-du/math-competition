#!/usr/bin/env python3
"""
One-off: Copy PUMaC 2025 Number Theory B results from pumac-b-combinator
into pumac-b-number-theory, preserving team_id and all columns.
"""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "database" / "contests" / "pumac-b-combinator" / "year=2025" / "results_B.csv"
DST_DIR = ROOT / "database" / "contests" / "pumac-b-number-theory" / "year=2025"
DST = DST_DIR / "results_B.csv"


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Source results not found: {SRC}")

    with SRC.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        raise SystemExit(f"No rows in source file: {SRC}")

    DST_DIR.mkdir(parents=True, exist_ok=True)
    with DST.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"Copied {len(rows) - 1} rows from {SRC} to {DST}")


if __name__ == "__main__":
    main()

